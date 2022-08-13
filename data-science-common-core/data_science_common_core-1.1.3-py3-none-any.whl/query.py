"""Query related functions."""
from .io import get_bq_client


def q_runs(params):
    """Query parameters from previous runs."""
    query = f"""
    SELECT
        parameters
    FROM `{params['google_project_id']}.{params['gbq_db_schema_metrics']}.{params['gbq_db_table_metrics']}`

    WHERE session_id = '{params['model_id']}'
    """

    client, job_config = get_bq_client(params)
    res = client.query(query, job_config=job_config).to_dataframe(
        progress_bar_type="tqdm"
    )

    return res
