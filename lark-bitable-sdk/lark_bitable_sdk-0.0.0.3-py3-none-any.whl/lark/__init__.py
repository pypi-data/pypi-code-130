base_url = "https://open.feishu.cn/open-apis"
url_get_tenant_access_token = "/auth/v3/tenant_access_token/internal"
url_fetch_records = "/bitable/v1/apps/:app_token/tables/:table_id/records"
url_update_records = "/bitable/v1/apps/:app_token/tables/:table_id/records/batch_update"
url_create_records = "/bitable/v1/apps/:app_token/tables/:table_id/records/batch_create"
url_delete_records = "/bitable/v1/apps/:app_token/tables/:table_id/records/batch_delete"
url_record = "/bitable/v1/apps/:app_token/tables/:table_id/records/:record_id"

from lark.Auth import Auth
from lark.Records import add_record, update_record, delete_record, get_record, fetch_records, add_records, update_records, delete_records