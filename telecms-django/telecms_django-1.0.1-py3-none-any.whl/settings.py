from telecms.conf import settings
from telecms.db import connection

TELECMS_BACKEND_API_BASE_URL = getattr(settings, 'TELECMS_BACKEND_API_BASE_URL', 'https://api.service.exchange/api')
TELECMS_BACKEND_WEB_BASE_URL = getattr(settings, 'TELECMS_BACKEND_WEB_BASE_URL', 'https://app.service.exchange')
TELECMS_READ_ONLY = getattr(settings, 'telecms_READ_ONLY', False)
TELECMS_REGISTER_TOKEN_ON_START = getattr(settings, 'telecms_REGISTER_TOKEN_ON_START', True)
TELECMS_CORS_HEADERS = getattr(settings, 'telecms_CORS_HEADERS', 'corsheaders' not in settings.INSTALLED_APPS)
TELECMS_MEDIA_FILE_STORAGE = getattr(settings, 'telecms_MEDIA_FILE_STORAGE', settings.DEFAULT_FILE_STORAGE)
TELECMS_PROJECT = getattr(settings, 'telecms_PROJECT', None)
TELECMS_TOKEN = getattr(settings, 'telecms_TOKEN', None)
SERVICE_EXCHANGE_DATABASE = getattr(settings, 'SERVICE_EXCHANGE_DATABASE', 'default')
TELEECMS_DATABASE_EXTRA = getattr(settings, 'TELEECMS_DATABASE_EXTRA', None)
TELEECMS_DATABASE_ONLY = getattr(settings, 'TELEECMS_DATABASE_ONLY', None)
TELEECMS_DATABASE_EXCEPT = getattr(settings, 'TELEECMS_DATABASE_EXCEPT', None)
TELEECMS_DATABASE_SCHEMA = getattr(settings, 'TELEECMS_DATABASE_SCHEMA', None)

database_settings = settings.DATABASES.get(SERVICE_EXCHANGE_DATABASE, {})
database_engine = None

mysql_read_default_file = database_settings.get('OPTIONS', {}).get('read_default_file')

if TELEECMS_DATABASE_EXTRA is None and mysql_read_default_file:
    TELEECMS_DATABASE_EXTRA = '?read_default_file={}'.format(mysql_read_default_file)

if connection.vendor == 'postgresql':
    database_engine = 'postgresql'
elif connection.vendor == 'mysql':
    database_engine = 'mysql'
elif connection.vendor == 'oracle':
    database_engine = 'oracle'
elif connection.vendor in ('mssql', 'microsoft'):
    database_engine = 'mssql+pyodbc'
elif connection.vendor == 'sqlite':
    database_engine = 'sqlite'
