"""Contains project setup parameters and initialization functions."""
import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime

# Add top folder to access parent project
sys.path.insert(0, "..")

from dotenv import dotenv_values  # noqa: E402

# Parent repos are imported without .
from src.constants import project_parameters  # noqa: E402

from .io import insert_logs  # noqa: E402
from .query import q_runs  # noqa: E402
from .utils import ulid  # noqa: E402

logging.Formatter.converter = time.gmtime
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)


def parse_input(parent_parser=None):
    """Manage input parameters."""
    parser = (
        argparse.ArgumentParser(parents=[parent_parser], description="")
        if parent_parser
        else argparse.ArgumentParser(description="")
    )
    parser.add_argument(
        "--model_type",
        type=str,
        dest="model_type",
        required=False,
        help="Type of the model (either 'hgb' or 'nn')",
    )
    parser.add_argument(
        "--model_id",
        type=str,
        dest="model_id",
        default="",
        required=False,
        help="ulid of the model",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        dest="debug_mode",
        help="turn on debug mode",
    )
    parser.add_argument(
        "--train",
        action="store_true",
        dest="train_mode",
        help="turn on model training",
    )
    parser.add_argument(
        "--date_cutoff",
        type=str,
        dest="date_cutoff",
        default="",
        required=False,
        help="cutoff date for testing (validation) in format YYYY-MM-DD",
    )
    parser.add_argument(
        "--dry_run",
        action="store_true",
        dest="dry_run",
        help="Dry run mode, will not upload the results",
    )
    parser.add_argument(
        "--plot",
        action="store_true",
        dest="plot",
        help="Plot mode, will plot the results",
    )
    parser.add_argument(
        "--isolation",
        action="store_true",
        dest="isolation",
        help="Outlier detection with Isolation Forest",
    )

    return vars(parser.parse_args())


def setup_params(args=None):
    """Manage setup parameters."""
    if args is None:
        args = {}

    # Get program call arguments
    params = args.copy()

    # Update parameters with constants
    params.update(project_parameters)
    params["session_id"] = ulid(params["project_hash"])
    runtime_keys = (
        list(args.keys())
        + [
            "session_id",
            "version",
        ]
        + [key for key in args.keys() if key != "model_type"]
    )

    # Convert cutoff date to string
    if len(params["date_cutoff"]) > 10:
        params["date_cutoff"] = datetime.strptime(
            params["date_cutoff"], params["datetime_fmt"]
        )
        params["date_cutoff"] = params["date_cutoff"].strftime(params["date_fmt"])

    # Directories and paths
    os.makedirs(params["folder_data"], exist_ok=True)
    params[
        "path_g_app_cred"
    ] = f"{params['folder_secrets']}/{params['file_g_app_cred']}"

    for file in ["train_data_file", "test_data_file"]:
        params[f"path_{file}"] = f"{params['folder_data']}/{params[file]}"

    # Create a model paths
    if params["model_type"] in ["hgb", "nn", "cat"]:
        m_t = params["model_type"]
        params[f"model_params_{m_t}"][
            "path_model_file"
        ] = f"{params['folder_data']}/{params[f'model_params_{m_t}']['model_file']}"

    # Create a path for feature transformer if needed
    if "ft_file" in params:
        params["path_feat_trans_file"] = f"{params['folder_data']}/{params['ft_file']}"

    # Derived parameters and format checks (depends on train / test mode)
    if params["train_mode"]:
        # Force stop run if model_type is not specified
        if "model_type" not in params or params["model_type"] not in [
            "hgb",
            "nn",
            "cat",
        ]:
            msg = "Model_type is not properly specified: cannot run train mode"
            logging.error(msg)
            insert_logs(params, msg)
            sys.exit(1)

        params["model_id"] = params["session_id"]

    else:
        # Force stop run if model_id is not specified
        if not params["model_id"]:
            msg = "Model_id is not specified: cannot run test mode"
            logging.error(msg)
            insert_logs(params, msg)
            sys.exit(1)

        # Force stop run if date_cutoff is not in the right format
        try:
            datetime.strptime(params["date_cutoff"], params["date_fmt"])

        except Exception:
            msg = (
                f"Invalid format for param date_cutoff: "
                f"Expected {params['date_fmt']} but received {params['date_cutoff']}"
            )
            logging.error(msg)
            insert_logs(params, msg)
            sys.exit(1)

        # Fetch model parameters from GBQ
        logging.info("Getting model parameters from DWH")
        run_list = q_runs(params)
        params_gbq = json.loads(run_list.parameters.iloc[0])

        # Keep runtime parameters from test run
        for field in runtime_keys:
            if not field.startswith("path"):
                params_gbq[field] = params[field]
        params.update(params_gbq)

        # Update parameters from env file
        if os.path.exists(params["env_file"]):
            import_env = dotenv_values(params["env_file"])
            import_env = {k.lower(): v for k, v in import_env.items()}
            params.update(import_env)

        else:
            # Return an error if the file doesn't exist
            logging.warning(f"File {params['env_file']} does not exist...")

    # Model_id dependent paths
    params[
        "path_base_gcs"
    ] = f"{params['gcs_model_folder']}/{params['model_id']}-{params['project_name']}"
    params[
        "path_base_gcs_train_data"
    ] = f"{params['gcs_train_data_folder']}/{params['model_id']}-{params['project_name']}"
    params[
        "path_base_gcs_test_data"
    ] = f"{params['gcs_test_data_folder']}/{params['model_id']}-{params['project_name']}"
    params[
        "path_bucket_test_data"
    ] = f"{params['path_base_gcs_test_data']}-{params['test_data_file']}"
    params[
        "path_bucket_train_data"
    ] = f"{params['path_base_gcs_train_data']}-{params['train_data_file']}"

    # Create a bucket path for model based on the model_type
    if params["model_type"] in ["hgb", "nn", "cat"]:
        m_t = params["model_type"]
        params[f"model_params_{m_t}"][
            "path_bucket_model"
        ] = f"{params['path_base_gcs']}-{params[f'model_params_{m_t}']['model_file']}"

    # Create a bucket path for feature transformer if needed
    if "path_feat_trans_file" in params:
        params["path_bucket_ft"] = f"{params['path_base_gcs']}-{params['ft_file']}"

    return params


def train_to_test(u_args, params):
    """Convert input parameters from train to test setup."""
    u_args["model_id"] = params["session_id"]
    u_args["train_mode"] = False
    u_args["date_cutoff"] = datetime.today().strftime(params["date_fmt"])
    u_args["dry_run"] = True
    return u_args
