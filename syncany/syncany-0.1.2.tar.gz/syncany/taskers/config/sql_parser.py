# -*- coding: utf-8 -*-
# 2021/11/10
# create by: snower

from .parser import Parser


class SqlParser(Parser):
    def __init__(self, *args, **kwargs):
        super(SqlParser, self).__init__(*args, **kwargs)

        try:
            import sqlparse
            self.sqlparse = sqlparse
        except ImportError:
            raise ImportError("sqlparse>=0.3.1 is required")

    def parse_insert_info(self):
        pass

    def parse_select(self):
        pass

    def parse_from(self):
        pass

    def parse_where(self):
        pass

    def parse_limit(self):
        pass

    def parse(self):
        statements = self.sqlparse.parse(self.content)
        for token in statements[0]:
            if token.is_whitespace:
                continue
            if str(token) not in self.next_keywords:
                raise KeyError(str(token))

            if str(token) == "insert":
                self.parse_insert_info()
            if str(token) == "select":
                self.parse_insert_info()