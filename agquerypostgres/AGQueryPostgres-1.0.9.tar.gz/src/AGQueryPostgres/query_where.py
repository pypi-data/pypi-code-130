from AGCoder import Coder
from uuid import UUID
import datetime


class AGQueryWhere:
    # Input
    where: list = []

    # Variable
    c = Coder("sql")

    def __init__(self, where, main_alias: str = ""):
        self.c.clear_all()
        self.where = where

        if len(self.where) > 0:
            for or_block in self.where:
                and_sql = Coder("sql")
                for and_block in or_block.keys():
                    and_block = and_block.lower()

                    value = or_block[and_block]

                    if type(value) is str:
                        if and_block.endswith("__startswith"):
                            value = "'" + str(value) + "%'"
                        elif and_block.endswith("__istartswith"):
                            value = "'" + str(value) + "%'"
                        elif and_block.endswith("__endswith"):
                            value = "'%" + str(value) + "'"
                        elif and_block.endswith("__iendswith"):
                            value = "'%" + str(value) + "'"
                        elif and_block.endswith("__contains"):
                            value = "'%" + str(value) + "%'"
                        elif and_block.endswith("__icontains"):
                            value = "'%" + str(value) + "%'"
                        else:
                            if value.startswith("="):
                                value = value[1:]

                                if and_block.lower().endswith("__year"):
                                    value = self._get_extract(value[0:-6], "year")
                                elif and_block.lower().endswith("__month"):
                                    value = self._get_extract(value[0:-7], "month")
                                elif and_block.lower().endswith("__day"):
                                    value = self._get_extract(value[0:-5], "day")
                                elif and_block.lower().endswith("__hour"):
                                    value = self._get_extract(value[0:-6], "hour")
                                elif and_block.lower().endswith("__minute"):
                                    value = self._get_extract(value[0:-8], "minute")
                                elif and_block.lower().endswith("__second"):
                                    value = self._get_extract(value[0:-8], "second")
                                elif and_block.lower().endswith("__week"):
                                    value = self._get_extract(value[0:-6], "week")
                                elif and_block.lower().endswith("__weekday"):
                                    value = self._get_extract(value[0:-9], "weekday")
                                elif and_block.lower().endswith("__yearday"):
                                    value = self._get_extract(value[0:-9], "yearday")
                                elif and_block.lower().endswith("__quarter"):
                                    value = self._get_extract(value[0:-9], "quarter")
                            else:
                                value = "'" + str(value) + "'"
                    elif type(value) is UUID:
                        value = "'" + str(value) + "'"
                    elif type(value) is datetime.datetime:
                        value = "'" + value.strftime('%Y-%m-%d %H:%M:%S') + "'"
                    else:
                        value = str(value)

                    # Greater/Smaller than
                    if and_block.endswith("__gt"):
                        column_name = self._get_column_name(and_block[0:-4], main_alias)
                        and_sql.a(0, column_name + " > " + value)
                    elif and_block.endswith("__gte"):
                        column_name = self._get_column_name(and_block[0:-5], main_alias)
                        and_sql.a(0, column_name + " >= " + value)
                    elif and_block.endswith("__lt"):
                        column_name = self._get_column_name(and_block[0:-4], main_alias)
                        and_sql.a(0, column_name + " < " + value)
                    elif and_block.endswith("__lte"):
                        column_name = self._get_column_name(and_block[0:-5], main_alias)
                        and_sql.a(0, column_name + " <= " + value)

                    # Exact strings
                    elif and_block.endswith("__exact"):
                        column_name = self._get_column_name(and_block[0:-7], main_alias)
                        and_sql.a(0, column_name + " = " + value)
                    elif and_block.endswith("__iexact"):
                        column_name = self._get_column_name(and_block[0:-8], main_alias)
                        and_sql.a(0, "LOWER(" + column_name + ") = LOWER(" + value + ")")

                    # Starts with
                    elif and_block.endswith("__startswith"):
                        column_name = self._get_column_name(and_block[0:-12], main_alias)
                        and_sql.a(0, column_name + " LIKE " + value)
                    elif and_block.endswith("__istartswith"):
                        column_name = self._get_column_name(and_block[0:-13], main_alias)
                        and_sql.a(0, column_name + " ILIKE " + value)

                    # Ends with
                    elif and_block.endswith("__endswith"):
                        column_name = self._get_column_name(and_block[0:-10], main_alias)
                        and_sql.a(0, column_name + " LIKE " + value)
                    elif and_block.endswith("__iendswith"):
                        column_name = self._get_column_name(and_block[0:-11], main_alias)
                        and_sql.a(0, column_name + " ILIKE " + value)

                    # Contains
                    elif and_block.endswith("__contains"):
                        column_name = self._get_column_name(and_block[0:-10], main_alias)
                        and_sql.a(0, column_name + " LIKE " + value)
                    elif and_block.endswith("__icontains"):
                        column_name = self._get_column_name(and_block[0:-11], main_alias)
                        and_sql.a(0, column_name + " ILIKE " + value)

                    # In SELECT
                    elif and_block.endswith("__in_select"):
                        column_name = self._get_column_name(and_block[0:-11], main_alias)
                        select_block = self._get_in_select_parameters(or_block[and_block])
                        and_sql.a(0, column_name + " IN ")
                        and_sql.b(0, select_block)
                    elif and_block.endswith("__notin_select"):
                        column_name = self._get_column_name(and_block[0:-14], main_alias)
                        select_block = self._get_in_select_parameters(or_block[and_block])
                        and_sql.a(0, column_name + " NOT IN ")
                        and_sql.b(0, select_block)

                    # In
                    elif and_block.endswith("__in"):
                        column_name = self._get_column_name(and_block[0:-4], main_alias)
                        in_string = self._get_in_string(or_block[and_block])
                        and_sql.a(0, column_name + " IN " + in_string)
                    elif and_block.endswith("__notin"):
                        column_name = self._get_column_name(and_block[0:-7], main_alias)
                        in_string = self._get_in_string(or_block[and_block])
                        and_sql.a(0, column_name + " NOT IN " + in_string)

                    #
                    # Datetime facilities
                    #
                    elif and_block.endswith("__year"):
                        column_name = self._get_column_name(and_block[0:-6], main_alias)
                        and_sql.a(0, self._get_extract(column_name, "year") + " = " + value)
                    elif and_block.endswith("__month"):
                        column_name = self._get_column_name(and_block[0:-7], main_alias)
                        and_sql.a(0, self._get_extract(column_name, "month") + " = " + value)
                    elif and_block.endswith("__day"):
                        column_name = self._get_column_name(and_block[0:-5], main_alias)
                        and_sql.a(0, self._get_extract(column_name, "day") + " = " + value)
                    elif and_block.endswith("__hour"):
                        column_name = self._get_column_name(and_block[0:-6], main_alias)
                        and_sql.a(0, self._get_extract(column_name, "hour") + " = " + value)
                    elif and_block.endswith("__minute"):
                        column_name = self._get_column_name(and_block[0:-8], main_alias)
                        and_sql.a(0, self._get_extract(column_name, "minute") + " = " + value)
                    elif and_block.endswith("__second"):
                        column_name = self._get_column_name(and_block[0:-8], main_alias)
                        and_sql.a(0, self._get_extract(column_name, "second") + " = " + value)
                    elif and_block.endswith("__week"):
                        column_name = self._get_column_name(and_block[0:-6], main_alias)
                        and_sql.a(0, self._get_extract(column_name, "week") + " = " + value)
                    elif and_block.endswith("__weekday"):
                        column_name = self._get_column_name(and_block[0:-9], main_alias)
                        and_sql.a(0, self._get_extract(column_name, "weekday") + " = " + value)
                    elif and_block.endswith("__yearday"):
                        column_name = self._get_column_name(and_block[0:-9], main_alias)
                        and_sql.a(0, self._get_extract(column_name, "yearday") + " = " + value)
                    elif and_block.endswith("__quarter"):
                        column_name = self._get_column_name(and_block[0:-9], main_alias)
                        and_sql.a(0, self._get_extract(column_name, "quarter") + " = " + value)
                    elif and_block.endswith("__date"):
                        column_name = self._get_column_name(and_block[0:-6], main_alias)
                        and_sql.a(0, "TO_CHAR(" + column_name + ", 'yyyy-mm-dd') = " + value)
                    elif and_block.endswith("__time"):
                        column_name = self._get_column_name(and_block[0:-6], main_alias)
                        and_sql.a(0, "TO_CHAR(" + column_name + ", 'hh24:mi:ss') = " + value)
                    elif and_block.endswith("__datetime"):
                        column_name = self._get_column_name(and_block[0:-10], main_alias)
                        and_sql.a(0, "TO_CHAR(" + column_name + ", 'yyyy-mm-dd hh24:mi:ss') = " + value)
                    elif and_block.endswith("__time_x_sec"):
                        column_name = self._get_column_name(and_block[0:-12], main_alias)
                        and_sql.a(0, "TO_CHAR(" + column_name + ", 'hh24:mi') = " + value)
                    elif and_block.endswith("__datetime_x_sec"):
                        column_name = self._get_column_name(and_block[0:-16], main_alias)
                        and_sql.a(0, "TO_CHAR(" + column_name + ", 'yyyy-mm-dd hh24:mi') = " + value)

                    # Is null
                    elif and_block.endswith("__isnull"):
                        column_name = self._get_column_name(and_block[0:-8], main_alias)
                        if or_block[and_block].lower() in ["true", "yes", "1", "t", "y"]:
                            and_sql.a(0, column_name + " IS NULL")
                        else:
                            and_sql.a(0, column_name + " IS NOT NULL")
                    else:
                        column_name = self._get_column_name(and_block, main_alias)
                        and_sql.a(0, column_name + " = " + value)

                    and_sql.a(0, "AND")

                if and_sql.lines > 0:
                    and_sql.code = and_sql.code[0:-1]
                    if len(self.where) > 1:
                        self.c.a(0, "(")
                        self.c.b(1, and_sql)
                    else:
                        self.c.b(0, and_sql)

                    if len(self.where) > 1:
                        self.c.a(0, ") OR")

            if self.c.lines > 0:
                if len(self.where) > 1:
                    self.c.strip_last(2)

    def _get_column_name(self, column_name, alias_name):
        if "." in column_name:
            result = column_name
        else:
            if len(alias_name) > 0:
                result = alias_name + "." + column_name
            else:
                result = column_name

        return result

    def _get_extract(self, column, endswith):
        result = ""
        if endswith == "year":
            result = "EXTRACT(ISOYEAR FROM " + column + ")"
        elif endswith == "month":
            result = "EXTRACT(ISOYEAR FROM " + column + ")"
        elif endswith == "day":
            result = "EXTRACT(DAY FROM " + column + ")"
        elif endswith == "hour":
            result = "EXTRACT(HOUR FROM " + column + ")"
        elif endswith == "minute":
            result = "EXTRACT(MINUTE FROM " + column + ")"
        elif endswith == "second":
            result = "EXTRACT(SECOND FROM " + column + ")"
        elif endswith == "week":
            result = "EXTRACT(WEEK FROM " + column + ")"
        elif endswith == "weekday":
            result = "EXTRACT(ISODOW FROM " + column + ")"
        elif endswith == "yearday":
            result = "EXTRACT(DOY FROM " + column + ")"
        elif endswith == "quarter":
            result = "EXTRACT(QUARTER FROM " + column + ")"

        return result

    def _get_in_string(self, in_string_array) -> str:
        in_string = "("
        for e in in_string_array:
            if type(e) is str:
                e = "'" + e + "',"
            else:
                e = str(e) + ","

            in_string += e

        in_string = in_string[0:-1] + ")"
        return in_string

    def _get_in_select_parameters(self, t):
        c = Coder("sql")

        if "schema_name" in t:
            if t["schema_name"] is None or t["schema_name"] == "":
                schema_name = ""
            else:
                schema_name = t["schema_name"]
        else:
            schema_name = ""

        if "table_name" in t:
            if t["table_name"] is None or t["table_name"] == "":
                table_name = ""
            else:
                table_name = t["table_name"]
        else:
            table_name = ""

        if "id_name" in t:
            if t["id_name"] is None or t["id_name"] == "":
                id_name = ""
            else:
                id_name = t["id_name"]
        else:
            id_name = ""

        if "where_string" in t:
            if t["where_string"] is None or t["where_string"] == "":
                where_string = ""
            else:
                where_string = t["where_string"]
        else:
            where_string = ""

        c.add(0, "(")
        c.add(1, "SELECT DISTINCT " + id_name)
        c.add(1, "FROM " + schema_name + "." + table_name)
        if len(where_string) > 0:
            c.a(1, "WHERE " + where_string)
        c.add(0, ")")

        return c
