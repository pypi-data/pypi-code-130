import code
import os
from typing import Any
from codegaze.datamodel import ExperimentConfig, ModelConfig
from codegaze.experiment import Experiment
from datasets import load_dataset
from tqdm import tqdm

from codegaze import CodeBlockParser, OpenAICodeGenerator
from codegaze.codegen import CodeGenerator, OpenAICodeGenerator, HFCodeGenerator
from codegaze.utils import save_json
from dataclasses import asdict


base_data_path = "experiments/data"

block_parser = CodeBlockParser()
human_eval_problems = load_dataset("openai_humaneval")["test"]

max_exp = 200
os.environ["TOKENIZERS_PARALLELISM"] = "false"  # prevent tokenizers error


def get_model(model: ModelConfig) -> CodeGenerator:
    codegen = None
    if model.type == "openai":
        codegen = OpenAICodeGenerator(model.name, model=model.path)
    elif model.type == "huggingface":
        codegen = HFCodeGenerator(model.name, model=model.path)
    else:
        assert False, f"unknown model type - {model.type}"
    return codegen


def cat_completions(config: ExperimentConfig, model: ModelConfig) -> None:

    codegen = get_model(model)

    dir = f"{base_data_path}/{config.dataset}"
    save_file_dir = f"{dir}/{config.slug}/{model.name}/completions/cat"
    os.makedirs(save_file_dir, exist_ok=True)

    i = 0
    for problem in tqdm(human_eval_problems, desc="cat"):
        i += 1
        # check if results have been saved
        save_file_name = f"{save_file_dir}/{problem['task_id'].replace('/','')}.json"
        if os.path.exists(save_file_name):
            i += 1
            continue
        problem_name = problem["task_id"]
        problem_prompt = problem["prompt"]
        solution = problem["canonical_solution"]
        code_bytes = bytes(solution, "utf8")
        extracted_blocks = block_parser.extract_blocks(
            solution,
            skip_parent_block=True,
            max_lines_per_block=config.max_lines_per_block,
            error_retry=config.parser_retry,
        )
        completion_holder = []
        equiv_holder = []
        block_prompts = []
        for extracted_block in extracted_blocks:
            next_prompt_tokens = " ".join(
                extracted_block.text.split(" ")[0 : config.prompt_tokens]
            )
            block_prompt = (
                code_bytes[0 : extracted_block.start_byte].decode("utf-8")
                + next_prompt_tokens
            )
            suffix = None
            if model.suffix:
                if model.name != "code-davinci-002":
                    assert False, "suffix only works with code-davinci-002"
                suffix = code_bytes[extracted_block.end_byte :].decode("utf-8")
                # block_prompt = code_bytes[0 : extracted_block.start_byte].decode("utf-8")
            completions = codegen.generate(
                problem_prompt + block_prompt + " ",
                max_tokens=model.max_tokens,
                n=model.n_completions,
                suffix=suffix,
                temperature=model.temperature,
            )

            equivalent_blocks = []
            for completion in completions:
                completion_blocks = block_parser.extract_blocks(
                    block_prompt + " " + completion.text,
                    skip_parent_block=True,
                    max_lines_per_block=config.max_lines_per_block,
                    error_retry=config.parser_retry,
                )
                equivalent_block = None
                if extracted_block.block_index < len(completion_blocks):
                    equivalent_block = completion_blocks[extracted_block.block_index]
                if equivalent_block is None:
                    continue
                equivalent_blocks.append(asdict(equivalent_block))
            completion_holder.append([asdict(x) for x in completions])
            block_prompts.append(block_prompt)
            equiv_holder.append(equivalent_blocks)

        result = {
            "problem": problem_name,
            "problem_prompt": problem_prompt,
            "solution": solution,
            "completions": completion_holder,
            "extracted_blocks": [asdict(block) for block in extracted_blocks],
            "block_prompts": block_prompts,
            "equivalent_blocks": equiv_holder,
        }
        save_json(result, save_file_name)
        # break


def get_first_function_block(blocks):
    for block in blocks:
        if block.type == "function_definition":
            return block
    return None


def trim_code_body(prompt_comp: str, prompt: str):
    code_byte = bytes(prompt_comp, "utf8")
    extracted_blocks = block_parser.extract_blocks(
        prompt_comp, skip_parent_block=True, max_lines_per_block=800, error_retry=True
    )
    first_function_block = get_first_function_block(extracted_blocks)
    if first_function_block is None:
        return ""
    start_to_function_end = code_byte[0 : first_function_block.end_byte].decode("utf-8")
    generated_body = start_to_function_end[len(prompt) :]
    return generated_body


def prep_test(problem: Any):
    entry_point = f"check({problem['entry_point']})"
    test_func = problem["test"]
    test = "\n" + test_func + "\n" + entry_point
    return test


def function_completions(config: ExperimentConfig, model: ModelConfig) -> None:

    codegen = get_model(model)
    dir = f"{base_data_path}/{config.dataset}"
    save_file_dir = f"{dir}/{config.slug}/{model.name}/completions/function"
    os.makedirs(save_file_dir, exist_ok=True)

    i = 0
    for problem in tqdm(human_eval_problems, desc="function"):
        i += 1
        # check if results have been saved
        save_file_name = f"{save_file_dir}/{problem['task_id'].replace('/','')}.json"
        if os.path.exists(save_file_name):
            continue
        prompt: str = problem["prompt"]
        problem_name: str = problem["task_id"]
        completions = codegen.generate(
            prompt,
            max_tokens=model.max_tokens,
            n=model.n_completions,
            temperature=model.temperature,
        )
        # print(completions)

        generated_bodies = []
        for completion in completions:
            prompt_comp = prompt + completion.text
            generated_body = trim_code_body(prompt_comp, prompt)
            generated_bodies.append(generated_body)

        result = {
            "problem": problem_name,
            "prompt": problem["prompt"],
            "generated_bodies": generated_bodies,
            "solution": problem["canonical_solution"],
            "test": prep_test(problem),
        }

        save_json(result, save_file_name)

        # break


exp = Experiment("completion_experiment")

config = ExperimentConfig(
    name="High vs Low Temperature",
    description="Compare models with High vs Low Temperature",
    dataset="humaneval",
)


config_save_dir = f"{base_data_path}/{config.dataset}/{config.slug}"
os.makedirs(config_save_dir, exist_ok=True)
exp.save_config(config, f"{config_save_dir}/config.json")

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


for model in model_list:
    print(f"Generating completions for model {model.name}")
    model_dir = f"{config_save_dir}/{model.name}"
    os.makedirs(model_dir, exist_ok=True)
    save_json(asdict(model), f"{model_dir}/model.json")
    cat_completions(config=config, model=model)
    function_completions(config=config, model=model)
