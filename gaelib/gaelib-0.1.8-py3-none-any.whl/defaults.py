"""
    This module contains all defaults available for when
    the application importing the lib doesnt set values
"""
DASHBOARD_URL_PREFIX = 'admindashboard'
DASHBOARD_ASSETS_PREFIX = 'https://storage.googleapis.com/gaelib-assets/assets'
POST_LOGIN_PAGE = 'users'
SIDEBAR_TEMPLATE = 'dashboard/operations_sidebar'
PARAMETER_LOGGING = 'true'
SESSION_SECRET = 'lib_key'
# TODO: Move this to a more generic bucket name
DEFAULT_PROFILE_IMAGE = 'https://storage.googleapis.com/crypticcup-images/default_profile.jpg'

# Twilio Auth Settings
VERIFICATION_SID = ''
ACCOUNT_SID = ''
AUTH_TOKEN = ''
TOKEN_LENGTH = 12

# Firebase Notifications Settings
AUTH0_JKWS_DOMAIN = ''
APNS_KEY_ID = ''
APNS_TEAM_ID = ''
APNS_AUTH_KEY_PATH = ''
IOS_BUNDLE_ID = ''

# Task Queues
TASK_QUEUE_STAGING = {
    'queue_name': 'notifications-rev2',
    'location': 'us-central1'}
TASK_QUEUE_PROD = {
    'queue_name': 'TBD',
    'location': 'TBD'}

# Notification Task Constants
MAX_NOTIFICATION_TASK_RETRIES = 5