# importing packages
from google.cloud import bigquery
from google.oauth2 import service_account


def get_bq_data(query, sa_file_location=None):
    """
       Executes the SQL query and coverts the results into a df

       Parameters
       ----------
       query: SQL query to execute
       sa_file_location: location of service account json file if it needs to be used to connect to bigquery
   """
    if sa_file_location is None:
        bq_client = bigquery.Client()
    else:
        bq_credentials = service_account.Credentials.from_service_account_file(sa_file_location)
        bq_client = bigquery.Client(credentials=bq_credentials)

    query_job = bq_client.query(query)
    df = query_job.result().to_dataframe()
    return df
