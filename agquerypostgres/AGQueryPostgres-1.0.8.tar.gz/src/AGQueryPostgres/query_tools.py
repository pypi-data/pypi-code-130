from .query_json_to_sql import AGJsonToSQL
from typing import Mapping


class AGQueryMapping:
    def __init__(self, json_obj: AGJsonToSQL, mapping: Mapping):
        self.json_obj = json_obj
        self.mapping = mapping

    def execute(self) -> AGJsonToSQL:
        where = {}
        where_rule = 'AND'
        for key, val in self.mapping.items():
            if key[0] == '_':
                if key == "_order_by":
                    self.json_obj.order_by.append(val)
                elif key == "_limit":
                    self.json_obj.limit = int(val)
                elif key == "_offset":
                    self.json_obj.offset = int(val)
                elif key == "_select":
                    self.json_obj.select = val.split(',')
                elif key == "_where_rule":
                    where_rule = val.upper()
            else:
                where[key] = val
        if len(where) > 0:
            if len(self.json_obj.where) > 0:
                if where_rule == 'OR':
                    self.json_obj.where.append(where)
                elif where_rule == 'INSTEAD':
                    self.json_obj.where[0] = where
                else:
                    self.json_obj.where[0] = {**self.json_obj.where[0], **where}

            else:
                self.json_obj.where.append(where)
        return self.json_obj
