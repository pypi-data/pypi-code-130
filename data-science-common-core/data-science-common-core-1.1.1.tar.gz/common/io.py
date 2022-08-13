"""Manage API calls and IO procedures."""
import gzip
import json
import logging
import os
import pickle
from datetime import datetime

import google
import google.auth
import gspread
import gspread_dataframe
import pandas as pd
from google.cloud import bigquery, storage
from tqdm import tqdm


def auth_gsheets(params):
    """Authenticate within Google Spreadsheet."""
    return gspread.service_account(params["path_g_app_cred"])


def get_bq_client(params):
    """Get Google BigQuery client."""
    if os.path.exists(params["path_g_app_cred"]):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = params["path_g_app_cred"]
    options = google.api_core.client_options.ClientOptions()
    bq_client = bigquery.Client(
        project=params["google_project_id"], client_options=options
    )
    job_config = bigquery.QueryJobConfig(
        allow_large_results=True,
        flatten_results=True,
        labels={"project-name": params["project_name"]},
    )

    return bq_client, job_config


def get_storage_client(params):
    """Get Google Storage client."""
    if os.path.exists(params["path_g_app_cred"]):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = params["path_g_app_cred"]
    return storage.Client(project=params["google_project_id"])


def get_data_bucket(params, storage_client):
    """Get Google Storage bucket."""
    return storage_client.bucket(params["gcs_bucket"])


def upload_to_bucket(params, file_path, bucket_folder):
    """Upload file to Google blob storage.

    file_path: Pass the path of the file to upload from.

    bucket_folder: Name of the bucket folder.
        - model: To upload model pickle file.
        - ft: To upload feature transformer pickle file.
        - train_data: To upload the train and validation data during training mode.
        - test_data: To upload the test data during test mode.
    """
    # Select path on blob storage
    blob_path = (
        params[f"path_bucket_{bucket_folder}"]
        if bucket_folder != "model"
        else params[f"model_params_{params['model_type']}"]["path_bucket_model"]
    )
    msg = f"{params['session_id']} - {params['project_name']}: Uploading file to bucket"
    logging.info(msg)
    insert_logs(params, msg)

    # Fetch client
    client = get_storage_client(params)
    bucket = get_data_bucket(params, client)
    blob = bucket.blob(blob_path)

    # Upload file as blob
    blob.upload_from_filename(file_path, timeout=120)
    msg = f"{params['session_id']} - {params['project_name']}: File uploaded to bucket: {blob_path}"
    logging.info(msg)
    insert_logs(params, msg)

    return True


def download_from_bucket(params, blob_path):
    """Download file from Google blob storage.

    blob_path: Pass the path of the file to download from.

    returns: A file path of a downloaded file.
    """
    if os.path.exists(blob_path):
        msg = f"File exists {blob_path}"
        logging.warning(msg)
        insert_logs(params, msg)
        return ""

    else:
        # Fetch client
        client = get_storage_client(params)
        bucket = get_data_bucket(params, client)
        blob = bucket.blob(blob_path)

        # Download blob from bucket
        file_path = f"{params['folder_data']}/{blob_path.split('/')[-1]}"
        blob.download_to_filename(file_path)

        msg = f"File downloaded {file_path}"
        logging.info(msg)
        insert_logs(params, msg)
        return file_path


def insert_by_chunks(params, table_string, df):
    """Insert df to table with specified chunk size.

    table_string: Address of the table in DWH to insert the values.

    df: Table/DataFrame to insert the data from.

    """
    # Fetch client and output table
    client, _ = get_bq_client(params)
    table = client.get_table(table_string)

    n = df.shape[0]
    chunk_size = params["insertion_chunk_size"]
    chunk_num = n // chunk_size + 1

    msg = "Inserting to DWH"
    logging.info(msg)
    insert_logs(params, msg)

    for c in tqdm(range(chunk_num)):
        st = c * chunk_size
        ed = min(n, st + chunk_size)

        # Try insert data to output_table, then log status
        query_status = client.insert_rows(table, [*df.values[st:ed]])
        if len(query_status):
            msg = f"{params['session_id']} - {params['project_name']}: Insertion failed: {query_status}"
            logging.warning(msg)
            insert_logs(params, msg)

    return


def insert_logs(params: dict, message: str):
    """Create log entry to BigQuery."""
    # Fetch client and output table
    client, _ = get_bq_client(params)
    log_table = client.get_table(
        f"{params['gbq_db_schema_log']}.{params['gbq_db_table_log']}"
    )

    row = [params["session_id"], datetime.utcnow(), params["project_name"], message]
    query_status = client.insert_rows(log_table, [row])
    if len(query_status):
        msg = f"{params['session_id']} - {params['project_name']}: Insertion failed: {query_status}"
        logging.warning(msg)
        insert_logs(params, msg)


def insert_metrics(params, results):
    """Insert training run's metrics to the DWH."""
    # Create a dataframe with 1 element as metrics
    out_dict = pd.DataFrame.from_records(
        [
            {
                "session_id": params["session_id"],
                "project_name": params["project_name"],
                "upload_date": datetime.utcnow(),
                "parameters": json.dumps(params),
                "metrics": json.dumps(results),
            }
        ]
    )

    client, _ = get_bq_client(params)
    out_table = client.get_table(
        f"{params['gbq_db_schema_metrics']}.{params['gbq_db_table_metrics']}"
    )

    # Insert row to the database
    client.insert_rows(out_table, list(out_dict.values))

    return


def read_from_sheet(params, mode="or"):
    """Insert data to Google Spreadsheet."""
    # Authenticate to Google Spreadsheet
    gsheet = auth_gsheets(params)

    # Identify file and sheet
    sheet_file = gsheet.open_by_key(params[f"gsheet_{mode}_file"])
    sheet = sheet_file.worksheet(params[f"gsheet_{mode}_sheet"])

    return sheet.get_all_values()


def insert_to_sheet(
    params,
    data,
    mode="dest",
    replace=False,
    sheet_offset=None,
    include_index=True,
    include_col_header=True,
):
    """Insert data to Google Spreadsheet."""
    msg = "Insert new predictions to Gsheet"
    logging.info(msg)
    insert_logs(params, msg)

    # Authenticate to Google Spreadsheet
    gsheet = auth_gsheets(params)

    # Identify file and sheet
    sheet_file = gsheet.open_by_key(params[f"gsheet_{mode}_file"])
    sheet = sheet_file.worksheet(params[f"gsheet_{mode}_sheet"])

    # Clean the sheet if required
    if replace:
        sheet_file.del_worksheet(sheet)
        sheet_file.add_worksheet(
            title=params[f"gsheet_{mode}_sheet"], rows=data.shape[0], cols=data.shape[1]
        )

    # Fill either a range of cells (as list) or the entire worksheet
    if sheet_offset:
        gspread_dataframe.set_with_dataframe(
            sheet,
            data,
            row=sheet_offset[0],
            col=sheet_offset[1],
            include_index=include_index,
            include_column_header=include_col_header,
        )

    else:
        gspread_dataframe.set_with_dataframe(
            sheet,
            data,
            include_index=include_index,
            include_column_header=include_col_header,
        )

    return


def loader(params, target):
    """Load object from blob storage.

    - target: Name of the target file.
        - model: To download pre-trained model file.
        - ft: To download feature transformer file.
        - train_data: To download the train and validation data.
        - test_data: To download the test data.
    """
    # Select a target bucket path
    bucket_path = (
        params[f"model_params_{params['model_type']}"]["path_bucket_model"]
        if target == "model"
        else params[f"path_bucket_{target}"]
    )

    # Download the file path of a target
    logging.info(f"Downloading {bucket_path}...")
    file_path = download_from_bucket(params, bucket_path)

    # Load pickle if it is not deep learning model
    if target == "model" and params["model_type"] == "nn":
        # Return nn model file path
        return file_path

    else:
        logging.info(f"Loading in memory {file_path}...")
        obj = pickle.load(gzip.open(file_path, "rb"))

        return obj


def fetch_from_bucket(params, to_download=("train_data", "ft", "model", "test_data")):
    """Download object(s) from google blob storage."""
    if isinstance(to_download, str):
        to_download = [to_download]

    # Store result objects
    return {target: loader(params, target) for target in to_download}


def ml_ft_upload(params):
    """Model-agnostic upload to bucket."""
    upload_to_bucket(params, params["path_feat_trans_file"], bucket_folder="ft")
    upload_to_bucket(
        params,
        params[f"model_params_{params['model_type']}"]["path_model_file"],
        bucket_folder="model",
    )

    return
