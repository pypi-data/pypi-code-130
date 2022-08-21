import os
import sys
import requests
import json
import pandas as pd

#initial logging

import logging
 
import google.cloud.logging
from google.cloud.logging.handlers import CloudLoggingHandler

log_name = "BOT_SPOT_REBALANCE"

# # Create a handler for Google Cloud Logging.
gcloud_logging_client = google.cloud.logging.Client()
gcloud_logging_handler = CloudLoggingHandler(
     gcloud_logging_client, name=log_name
)

# Create a stream handler to log messages to the console.
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)

# Now create a logger and add the handlers:
logger = logging.getLogger(log_name)
logger.setLevel(logging.DEBUG)
logger.addHandler(gcloud_logging_handler)
logger.addHandler(stream_handler)

# live=production run on gcp otherwise, run on localhost 
mode = "live"

GCLOUD_PROJECT=os.getenv("CLOUD_PROJECT_ID")
BUCKET_NAME=os.getenv("BUCKET_NAME") #'crypto-342815.appspot.com'
LINE_NOTI_ENDPOINT=os.getenv("LINE_NOTI_ENDPOINT") #'https://notify-api.line.me/api/notify'
BACKEND_API_GATEWAY_ENDPOINT=os.getenv("BACKEND_API_GATEWAY_ENDPOINT") 
BACKEND_API_GATEWAY_APIKEY=os.getenv("BACKEND_API_GATEWAY_APIKEY") 
NOTIFICATION_PUBSUB_TOPIC=os.getenv("NOTIFICATION_PUBSUB_TOPIC") 

def send_admin_line(line_token_api, payload):
    try:
        r= requests.post(LINE_NOTI_ENDPOINT
                    , headers={'Authorization' : 'Bearer {}'.format(line_token_api)}
                    , params = payload)
    
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(f'-send_line. Error: {e}, Line no.:{exc_tb.tb_lineno}')

def get_secret_by_apikey(apiKey):
    # Import the Secret Manager client library.
    try:
        url = f'{BACKEND_API_GATEWAY_ENDPOINT}/getTradeApi'
        secret = requests.post( url, json={"apiKey": apiKey}, headers={"Content-Type": "application/json", "x-api-key": BACKEND_API_GATEWAY_APIKEY })
        return secret.text
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(f'-get_secret_by_apikey. Error: {e}, Line no.:{exc_tb.tb_lineno}')
        return 

def local_broadcast_signal(signal_data):
    url = "http://grid_subscriber:8889/main"
    result_data = {}
    result_data.update({"system_status": signal_data["system_status"]})
    result_data.update({"exe": signal_data["exe"]})
    result_data.update({"signal_data": signal_data["grid_data"]})
    f = open('mocks/grid_subscriber_data.json')
    docs = json.load(f)
    for doc in docs:
        data = doc
        key = list(data.keys())[0]
        json_data = {}
        datas = {
                "userId": data[key]["user_id"],
                "strategyId": data[key]["strategy_id"],
                "apiKey": data[key]["apiKey"],
                "exchange": data[key]["exchange"],
                "testNet": data[key]["testNet"],
                "accountName": data[key]["sub_account_name"],
                "subAccountFlag": data[key]["subAccountFlag"],
                "line_token": data[key]["line_token"],
                "admin_line_token": signal_data["admin_line_token"],#data.get("admin_Line_token"),
                "bot_status": data[key]["system_status"]
            }
        result_data.update({"subscribe_info": datas})
        #async_request.append(requests.get( url ))
        json_data.update({"message": {"data": {"data": {"message": result_data}}}})
        # async_request.append( post_signal( json_data ) )
        requests.post( url, json=json_data)

#push pubsub
def push_notificatoin_pubsub(json_data):    
    # Instantiates a Pub/Sub client
    from google.cloud import pubsub_v1
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(GCLOUD_PROJECT, NOTIFICATION_PUBSUB_TOPIC)
    message_json = json.dumps({
        'data': {'message': json_data},
    })
    message_bytes = message_json.encode('utf-8')
    print('message_json>>', message_json)
    # Publishes a message
    try:
        publish_future = publisher.publish(topic_path, data=message_bytes)
        publish_future.result()  # Verify the publish succeeded
        return 'Message published.'
    except Exception as e:
        print(e)
        return (e, 500)


def write_csv_to_tmp(df,file_name):  
    df.to_csv('/tmp/'+file_name+'.csv',index=False)

def upload_csv_to_storage(prefix, csv_file_name):
    from google.cloud import storage
    try:
        #path to keep file by each account on cloud storage
        if mode == "live":
            dest_file = f'{prefix}/{csv_file_name}'
            source_csv_file = f'/tmp/{csv_file_name}'

            df =pd.read_csv(
                    os.path.join('/tmp/',csv_file_name),
                )
            #Upload to Google cloud storage
            client = storage.Client()
            bucket = client.get_bucket(BUCKET_NAME)
            blob = bucket.blob(dest_file)
            blob.upload_from_filename(source_csv_file)
        else:
            pass
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(f'upload_csv_to_storage. Error: {e}, Line no.:{exc_tb.tb_lineno}')
        # send_line_error(f'{BOT_ID}-{dt.isoformat()} - write_csv.', "Error: {}, Line no.:{}".format(e,exc_tb.tb_lineno ),admin_Line_token,sub_account_name)
        return None

def upload_excel_to_storage(prefix, excel_file_name):
    from google.cloud import storage
    try:
        #path to keep file by each account on cloud storage
        if mode == "live":
            dest_file = f'{prefix}/{excel_file_name}'
            source_xls_file = f'/tmp/{excel_file_name}'

            df =pd.read_excel(
                    os.path.join('/tmp/',excel_file_name),
                )
            #Upload to Google cloud storage
            client = storage.Client()
            bucket = client.get_bucket(BUCKET_NAME)
            blob = bucket.blob(dest_file)
            blob.upload_from_filename(source_xls_file)
        else:
            pass
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(f'upload_excel_to_storage. Error: {e}, Line no.:{exc_tb.tb_lineno}')
        # send_line_error(f'{BOT_ID}-{dt.isoformat()} - write_csv.', "Error: {}, Line no.:{}".format(e,exc_tb.tb_lineno ),admin_Line_token,sub_account_name)
        return None
    

# #xls_file = excel file in cloud storage bucket
def download_csv_from_storage(prefix, csv_file):
    from google.cloud import storage
    import io
    try:
        blob_name = f"{prefix}/{csv_file}"

        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(blob_name)

        data_bytes = blob.download_as_bytes()

        df = pd.read_csv( io.BytesIO(data_bytes), encoding='utf8')
        return df
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(f'download_csv_from_storage. Error: {e}, Line no.:{exc_tb.tb_lineno}')
        # send_line_error(f'{BOT_ID}-{dt.isoformat()} - prepare_csv_file_for_running.', "Error: {}, Line no.:{}".format(e,exc_tb.tb_lineno ),admin_Line_token,sub_account_name)
        return None

# #xls_file = excel file in cloud storage bucket
def download_excel_from_storage(prefix, excel_file):
    from google.cloud import storage
    import io
    try:
        blob_name = f"{prefix}/{excel_file}"

        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(blob_name)

        data_bytes = blob.download_as_bytes()

        df = pd.read_excel( data_bytes )

        return df
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(f'download_csv_from_storage. Error: {e}, Line no.:{exc_tb.tb_lineno}')
        # send_line_error(f'{BOT_ID}-{dt.isoformat()} - prepare_csv_file_for_running.', "Error: {}, Line no.:{}".format(e,exc_tb.tb_lineno ),admin_Line_token,sub_account_name)
        return None

# #read file from cloud storage then write file to /tmp path in cloud function
def prepare_csv_file_for_running(csv_path, csv_file_name):
    try:
        if mode == "live":
            df = download_csv_from_storage( csv_path, csv_file_name)
            # df.to_csv(f'/tmp/{xls_file_name}')
            df.to_csv(f'/tmp/{csv_file_name}')
        else:
            pass
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        logger.error(f'prepare_csv_file_for_running. Error: {e}, Line no.:{exc_tb.tb_lineno}')
        # send_line_error(f'{BOT_ID}-{dt.isoformat()} - prepare_csv_file_for_running.', "Error: {}, Line no.:{}".format(e,exc_tb.tb_lineno ),admin_Line_token,sub_account_name)

def prepare_excel_file_for_running(xls_path, xls_file_name):
    if mode == "live":
        from google.cloud import storage
        try:
            blob_name = f'{xls_path}/{xls_file_name}'
            storage_client = storage.Client()
            bucket = storage_client.bucket(BUCKET_NAME)
            blob = bucket.blob(blob_name)

            data_bytes = blob.download_as_bytes()

            df = pd.read_excel(data_bytes)
            df.to_excel(f'/tmp/{xls_file_name}')
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error(f'prepare_excel_file_for_running. Error: {e}, Line no.:{exc_tb.tb_lineno}')
            # send_line_error(f'{BOT_ID}-{dt.isoformat()} - prepare_excel_file_for_running.', "Error: {}, Line no.:{}".format(e,exc_tb.tb_lineno ),admin_Line_token,sub_account_name)
    else:
        pass

# #save file back to cloud storage from /tmp path
def backup_csv_to_storage(prefix, csv_file_name):
    upload_csv_to_storage(prefix, csv_file_name)

# #save file back to cloud storage from /tmp path
def backup_excel_to_storage(prefix, excel_file_name):
    upload_excel_to_storage(prefix, excel_file_name)