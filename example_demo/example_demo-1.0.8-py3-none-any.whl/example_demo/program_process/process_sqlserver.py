import copy


class SQLBase():
    def __init__(self, request_info: dict, file_download_info: list, **kwargs):
        self.request_info = request_info
        self.file_download_info = file_download_info
        self.option_args = kwargs
        pass

    def get_all_source(self):
        """Returns source for the program."""
        all_source = []
        sql_get = self.request_info.get("get_sql")
        for source in sql_get:
            _request_info = copy.deepcopy(self.request_info)
            _request_info["get_sql"] = source
            source_info = {"request_info": _request_info, "file_download_info": source}
            all_source.append({"info": source_info, "result": True})
        return all_source

    def download_source(self, source):
        """Returns source download result"""

        pass


class SQLParseBase():
    def __init__(self ,source: dict, **kwargs):
        '''
        source need {"info":{},"result":True or False}
        "info" is your prepare source ==> {"request_info":{}, "file_download_info":{}}
        '''
        self.source = source


    def parse_source(self):
        """

        parse download result or file or you can customize yourself

        """
        pass
