from ast import Mod
from codegaze.codeparser import CodeBlockParser
from codegaze.datamodel import CodeBlock, ExperimentConfig, ModelConfig
from codegaze.experiment import Experiment
from codegaze import metrics
import os
from evaluate import load
from datasets import load_dataset
from tqdm import tqdm
import pandas as pd
import numpy as np
from codegaze.utils import load_json, save_json
import json
import multiprocessing
from dataclasses import asdict

cpu_count = multiprocessing.cpu_count()
os.environ["TOKENIZERS_PARALLELISM"] = "false"  # prevent tokenizers error

humaneval_problems = load_dataset("openai_humaneval")["test"]
humaneval_problem_files: list[str] = [
    problem["task_id"].replace("/", "") + ".json" for problem in humaneval_problems
]

block_parser = CodeBlockParser()
edit_metric = metrics.EditMetric()
ast_metric = metrics.ASTMetric(block_parser)
jw_metric = metrics.JaroWinklerMetric()
neural_metric = metrics.NeuralMetric()

code_eval_metric = load("code_eval")

base_data_path = "experiments/data"
completion_path = f"{base_data_path}/completions"

completion_dir = "experiments/data/completions"
metric_dir = "experiments/data/metrics"
os.environ["HF_ALLOW_CODE_EVAL"] = "1"


def compute_metrics(a: str, b: str, prefix: str = "cat") -> dict[str, float]:
    return {
        f"{prefix}_edit": edit_metric.compute(a, b),
        f"{prefix}_ast": ast_metric.compute(a, b),
        f"{prefix}_jw": jw_metric.compute(a, b),
        f"{prefix}_neural": neural_metric.compute(a, b),
        f"{prefix}_charlen": {"len_eq": len(a), "len_ex": len(b)},
    }


def run_function_eval(config: ExperimentConfig, model: ModelConfig) -> None:

    dir = f"{base_data_path}/{config.dataset}"
    save_file_dir = f"{dir}/{config.slug}/{model.name}/metrics/function"
    os.makedirs(save_file_dir, exist_ok=True)

    completion_prefix = f"{base_data_path}/{config.dataset}/{config.slug}/{model.name}/completions/function"

    for task_file in tqdm(humaneval_problem_files, desc="function"):
        save_file_name = f"{save_file_dir}/{task_file}"
        if os.path.exists(save_file_name):
            continue
        task_data = load_json(f"{completion_prefix}/{task_file}")
        prompt = task_data["prompt"]
        bodies = task_data["generated_bodies"]
        # create candidates as prompts + bodies
        candidates = [prompt + body for body in (bodies)]
        candidates = [candidates]
        test_cases = [task_data["test"]]
        holder = {}
        pass_at_k, results = code_eval_metric.compute(
            references=test_cases,
            k=[1, 10, 50, len(bodies)],
            predictions=candidates,
            num_workers=cpu_count,
        )
        # compute similarity metrics at function level
        sim_holder = []
        for body in bodies:
            sim_metrics = compute_metrics(task_data["solution"], body, prefix="func")
            sim_holder.append(sim_metrics)

        min_sim = dict(pd.DataFrame(sim_holder).select_dtypes(include=np.number).min())

        # merge dict pass_at_k and mean_sim

        holder["problem"] = task_data["problem"]
        holder["metrics_arr"] = {"function": results, "cat": sim_holder}
        holder["metrics"] = {**pass_at_k, **min_sim}

        save_json(holder, save_file_name)
        # break


def aggregate_blocks(metrics: list) -> dict:
    metric_df = pd.DataFrame(metrics)
    # TODO apply weights to the metrics before mean
    agg_metric = dict(metric_df.select_dtypes(include=np.number).mean())
    return agg_metric


def run_cat_eval(config: ExperimentConfig, model: ModelConfig) -> None:

    dir = f"{base_data_path}/{config.dataset}"
    save_file_dir = f"{dir}/{config.slug}/{model.name}/metrics/cat"
    os.makedirs(save_file_dir, exist_ok=True)

    completion_prefix = (
        f"{base_data_path}/{config.dataset}/{config.slug}/{model.name}/completions/cat"
    )

    for problem_path in tqdm(humaneval_problem_files, desc="cat"):
        save_file_name = f"{save_file_dir}/{problem_path}"
        # if os.path.exists(save_file_name):
        #     continue
        problem = load_json(f"{completion_prefix}/{problem_path}")
        block_holder = []
        metric_holder = []
        for i in range(len(problem["extracted_blocks"])):  # for each block
            extracted_block = problem["extracted_blocks"][i]
            # remove key "__initialised__" from the block if present
            if "__initialised__" in extracted_block:
                del extracted_block["__initialised__"]
            extracted_block = CodeBlock(**extracted_block)
            # block_prompt = problem["block_prompts"][i]
            # completions = problem["completions"][i]
            equivalent_blocks = problem["equivalent_blocks"][i]
            metrics = []
            for (
                equivalent_block
            ) in equivalent_blocks:  # for each completion, compute block metrics
                equivalent_block = CodeBlock(**equivalent_block)
                a = equivalent_block.text
                b = extracted_block.text
                sim_met = compute_metrics(a, b, prefix="cat")
                sim_met = {**sim_met, **{"type": extracted_block.type}}
                metrics.append(sim_met)
            metrics_df = pd.DataFrame(metrics)
            # select metric from 1 of n completions for block
            # option 1 get min of numeric metrics in metric_df
            # option 2 get first row of  metric of numeric metrics in metric_df
            # first_metric = metrics_df.select_dtypes(include=np.number).iloc[0]
            # mean_metric = metrics_df.select_dtypes(include=np.number).mean()

            if metrics_df.shape[0] > 0:
                # use the best block from all completions
                metric_sum = dict(metrics_df.select_dtypes(include=np.number).mean())
            else:
                metric_sum = {}
            block_metrics = dict(metric_sum)
            block_metrics["type"] = extracted_block.type
            block_holder.append(block_metrics)
            metric_holder.append(metrics)
        holder = {}
        holder["metrics"] = aggregate_blocks(block_holder)
        holder["problem"] = problem["problem"]
        holder["metrics_arr"] = metric_holder
        save_json(holder, save_file_name)
        # break


exp = Experiment("completion_experiment")

config = ExperimentConfig(
    name="High vs Low Temperature",
    description="Compare models with High vs Low Temperature",
    dataset="humaneval",
)

model_list = [
    ModelConfig(
        type="huggingface",
        name="Salesforce350MMulti",
        path="Salesforce/codegen-350M-multi",
        temperature=0.8,
        n_completions=10,
        max_tokens=400,
        description="Salesforce CodeGen 350M trained on C, C++, Go, Java, JavaScript, and Python",
    ),
    ModelConfig(
        type="huggingface",
        name="Salesforce2BMulti",
        path="Salesforce/codegen-2B-multi",
        temperature=0.8,
        n_completions=10,
        max_tokens=400,
        description="Salesforce CodeGen 2B trained on C, C++, Go, Java, JavaScript, and Python",
    ),
    ModelConfig(
        type="openai",
        name="code-cushman-001",
        path="code-cushman-001",
        temperature=0.8,
        n_completions=10,
        description="OpenAI Codex Cushman 001 model trained on Github",
    ),
    ModelConfig(
        type="openai",
        name="code-davinci-001",
        path="code-davinci-001",
        temperature=0.8,
        n_completions=10,
        description="OpenAI Codex Davinci 001 model trained on Github",
    ),
]

if __name__ == "__main__":
    for model in model_list:
        print(f"Running evaluation for model {model.name}")
        run_cat_eval(config, model)
        run_function_eval(config, model)
