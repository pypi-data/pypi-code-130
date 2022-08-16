import inspect
from typing import List

from lark import base_url, url_fetch_records, url_update_records, url_record, url_create_records, url_delete_records
from lark.Auth import Auth, AuthCheck
from utils.RestfulUtils import do_get, do_post, do_put, do_delete
from vo.lark.LarkBaseResponse import LarkBaseResponse
from vo.lark.LarkBitableRecordItem import LarkBitableRecordItem
from vo.lark.LarkBitableRecordsResponse import LarkBitableFetchRecordsResponse, LarkBitableGetRecordResponse, \
    LarkBitableGetRecordsResponse, LarkBitableDeleteRecordResponse, LarkBitableDeleteRecordsResponse


@AuthCheck
def fetch_records(app_token: str,
                  table_id: str,
                  view_id: str = None,
                  filter: str = None,
                  sort: List[str] = None,
                  field_names: str = None,
                  text_field_as_array: str = None,
                  page_token: str = None,
                  page_size: int = None,
                  user_id_type: str = None
                  ) -> LarkBaseResponse[LarkBitableFetchRecordsResponse]:
    frame = inspect.currentframe()
    args, _, _, values = inspect.getargvalues(frame)
    kwargs = {}
    for i in args:
        if values[i] is not None:
            kwargs[i] = values[i]
    return __fetch_records__(**kwargs)


@AuthCheck
def get_record(app_token: str, table_id: str, record_id: str) -> LarkBaseResponse[LarkBitableGetRecordResponse]:
    url = base_url + url_record.replace(":app_token", app_token).replace(":table_id", table_id).replace(":record_id",
                                                                                                        record_id)
    return LarkBaseResponse[LarkBitableGetRecordResponse](**do_get(url, header=Auth().get_headers()))


@AuthCheck
def add_record(app_token: str, table_id: str, record: dict) -> LarkBaseResponse[LarkBitableGetRecordResponse]:
    url = base_url + url_fetch_records.replace(":app_token", app_token).replace(":table_id", table_id)
    return LarkBaseResponse[LarkBitableGetRecordResponse](
        **do_post(url, body={"fields": record}, header=Auth().get_headers()))
    pass


@AuthCheck
def update_record(app_token: str, table_id: str, record: LarkBitableRecordItem) -> LarkBaseResponse[
    LarkBitableGetRecordResponse]:
    url = base_url + url_record.replace(":app_token", app_token).replace(":table_id", table_id).replace(":record_id",
                                                                                                        record.record_id)
    return LarkBaseResponse[LarkBitableGetRecordResponse](
        **do_put(url, body={"fields": record.fields}, header=Auth().get_headers()))


@AuthCheck
def delete_record(app_token: str, table_id: str, record_id: str) -> LarkBaseResponse[LarkBitableDeleteRecordResponse]:
    url = base_url + url_record.replace(":app_token", app_token).replace(":table_id", table_id).replace(":record_id",
                                                                                                        record_id)
    return LarkBaseResponse[LarkBitableDeleteRecordResponse](**do_delete(url, header=Auth().get_headers()))


@AuthCheck
def add_records(app_token: str, table_id: str, records: List[dict]) -> LarkBaseResponse[LarkBitableGetRecordsResponse]:
    url = base_url + url_create_records.replace(":app_token", app_token).replace(":table_id", table_id)
    return LarkBaseResponse[LarkBitableGetRecordsResponse](
        **do_post(url, body={"records": [{"fields": x} for x in records]}, header=Auth().get_headers()))


@AuthCheck
def update_records(app_token: str, table_id: str, records: List[LarkBitableRecordItem]) -> LarkBaseResponse[
    LarkBitableGetRecordsResponse]:
    url = base_url + url_update_records.replace(":app_token", app_token).replace(":table_id", table_id)
    return LarkBaseResponse[LarkBitableGetRecordsResponse](
        **do_post(url, body={"records": [x.dict() for x in records]}, header=Auth().get_headers()))


@AuthCheck
def delete_records(app_token: str, table_id: str, records: List[str]) -> LarkBaseResponse[
    LarkBitableDeleteRecordsResponse]:
    url = base_url + url_delete_records.replace(":app_token", app_token).replace(":table_id", table_id)
    return LarkBaseResponse[LarkBitableDeleteRecordsResponse](
        **do_post(url, body={"records": records}, header=Auth().get_headers()))


def __fetch_records__(app_token: str,
                      table_id: str,
                      **kwargs
                      ) -> LarkBaseResponse[LarkBitableFetchRecordsResponse]:
    url = base_url + url_fetch_records.replace(":app_token", app_token).replace(":table_id", table_id)
    return LarkBaseResponse[LarkBitableFetchRecordsResponse](**do_get(url, params=kwargs, header=Auth().get_headers()))


if __name__ == '__main__':
    # record = [{'简介': '我是新纪录','达人抖音号': 'testing'},{'简介': '我是新纪录2', '达人抖音号': 'testing2'}]
    # result = add_records("bascnt8rwQUvu85HoY81Tb0XpIf", "tbl02oxTA6WqjBO1", record)
    # records = ["recJTtRbow", "recf6vPwkT", "recsbzGZbf"]
    result = fetch_records("bascnt8rwQUvu85HoY81Tb0XpIf", "tbl02oxTA6WqjBO1", field_names='["简介"]', page_size=3)
    print(result)
