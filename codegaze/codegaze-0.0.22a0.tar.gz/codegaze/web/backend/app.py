 
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles 
import os
from codegaze.datamodel import ExperimentConfig
from fastapi.middleware.cors import CORSMiddleware
from codegaze.experiment import Experiment


app = FastAPI()
# allow cross origin requests for testing on localhost:8000 only
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
api = FastAPI(root_path="/api")
app.mount("/api", api)


root_file_path = os.path.dirname(os.path.abspath(__file__))
static_folder_root = os.path.join(root_file_path, "build")

if not os.path.exists(static_folder_root):
    assert False, "Static folder not found: {}. Ensure the front end is built".format(
        static_folder_root
    )
app.mount("/ui", StaticFiles(directory=static_folder_root, html=True), name="ui")

exp = Experiment("general")


@api.get("/experiments")
def list_experiments(dataset: str = "humaneval") -> list[ExperimentConfig]:
    """List all experiments for a given dataset"""
    return exp.list_experiments(dataset)


@api.post("/experiment/results")
def list_experiment_results(config: ExperimentConfig) -> list[dict]:
    """List a summary of results for an experiment"""
    models = exp.list_models(config.dataset, config.slug)

    model_results = []
    for model in models:
        metrics = exp.get_aggregate_results(config, model)
        if metrics:
            model_results.append({"model": model, "metrics": metrics})
    model_rankings = exp.get_rankings(model_results)
    results = {"results": model_results, "rankings": model_rankings}
    return results


@api.post("/experiment/problems")
def list_problems(config: ExperimentConfig, model: str, metric_type: str) -> list[str]:
    """List all problems in a an experiment dataset"""
    problems = exp.list_dataset_problems(config, model, metric_type)
    return problems


@api.post("/experiment/problem/results")
def list_problem_results(
    config: ExperimentConfig, model: str, metric_type: str, problem: str
) -> list[dict]:
    """List completions and metrics for a given problem"""
    results = exp.get_problem_results(
        config, model=model, problem=problem, metric_type=metric_type
    )
    return results


@api.get("/models")
def list_models(dataset: str = "humaneval", slug: str = "pt1_ml10_t0.8") -> list[str]:
    """List all models for a given experiment config."""
    return exp.list_models(dataset, slug)


@api.get("/datasets")
def list_datasets() -> list[str]:
    """List all datasets"""
    return exp.list_datasets()

 
