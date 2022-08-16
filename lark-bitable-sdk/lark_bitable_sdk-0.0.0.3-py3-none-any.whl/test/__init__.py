from lark import Auth
from lark import fetch_records

if __name__ == '__main__':
    Auth(app_id="app_id", app_secret="app_secret")
    print(fetch_records("app_token", "table_id", field_names='["field_name"]', page_size=3))



