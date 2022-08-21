BASE_URL = "http://censius-logs-prod1.us-east-1.elasticbeanstalk.com/v1"
AMS_URL = "http://ams-prod.us-east-1.elasticbeanstalk.com"
EXPLAINATION_BASE_URL = "http://explainability-prod.us-east-1.elasticbeanstalk.com/explanations"
MONITORS_PROGRAMMATIC_BASE_URL = (
    "http://monitors-env.eba-ptkdpfrn.us-east-1.elasticbeanstalk.com/v1/programmatic"
)

# Models
REGISTER_MODEL_URL = lambda: f"{AMS_URL}/models/register"
REVISE_MODEL_URL = lambda: f"{AMS_URL}/models/revise"
PROCESS_MODEL_URL = lambda: f"{AMS_URL}/models/schema-updation"
REGISTER_NEW_MODEL_VERSION = lambda: f"{AMS_URL}/models/register_new_version"

# Logs
LOG_URL = lambda: f"{BASE_URL}/logs"
UPDATE_ACTUAL_URL = lambda prediction_id: f"{BASE_URL}/logs/{prediction_id}/updateActual"
BULK_LOG_DATATYPE_VALIDATION_URL = f"{BASE_URL}/logs/validate_bulk_datatype"
BULK_LOG_URL = f"{BASE_URL}/logs/bulk_logs"


# Dataset
REGISTER_DATASET_URL = lambda: f"{AMS_URL}/datasets/register"

# Project
REGISTER_PROJECT_URL = lambda: f"{AMS_URL}/projects/register-project"

# Explainations
EXPLAINATION_URL = lambda: f"{EXPLAINATION_BASE_URL}/insert_local"

# Monitors
GET_MODEL_HEALTH_URL = lambda: f"{MONITORS_PROGRAMMATIC_BASE_URL}/get_model_health"
