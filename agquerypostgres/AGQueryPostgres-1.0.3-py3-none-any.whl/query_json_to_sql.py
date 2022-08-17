from AGCoder import Coder
from .query_where import AGQueryWhere


class AGJsonToSQL:
    # Input
    schema_name: str = None
    table_name: str = None
    alias_name: str = None
    id_name: str = None
    left_join: list = []
    inner_join: list = []

    up_relations: list = []
    down_relations: list = []
    select: list = []
    column_function: list = []
    window: list = []
    total: list = []
    rollup: bool = False

    where: list = []
    where_and: list = []
    where_string: str = ""
    order_by: list = []
    offset: int = 0
    limit: int = 0
    page: int = 0
    host: dict = {}

    object_name: str = None
    SQL: str = None
    inner_sql: str = None

    alias_list: list = []

    def __init__(self, schema_name: str = None, table_name: str = None):
        self.schema_name = schema_name
        self.table_name = table_name
        self.alias_name = ""
        self.id_name = ""
        self.object_name = ""
        self.where = []
        self.where_and = []
        self.where_string = ""
        self.order_by = []
        self.left_join = []
        self.inner_join = []
        self.up_relations = []
        self.down_relations = []
        self.select = []
        self.column_function = []
        self.window = []
        self.total = []
        self.rollup = False
        self.offset = 0
        self.limit = 0
        self.page = 0
        self.host = {}

        # Reset
        self.SQL = ""
        self.inner_sql = ""
        self.rows = []
        self.alias_list = []

    #
    # SELECT
    #
    def _get_column_name(self, column_name, alias_name):
        if "." in column_name:
            result = column_name
        else:
            result = alias_name + "." + column_name

        return result

    def _get_select(self, alias_name, select, total) -> Coder:
        c = Coder("sql")

        select_list = []
        if alias_name:
            for x, f in enumerate(select):
                # Insert HOST into SELECT columns
                url_name = ""
                if len(self.host.keys()) > 0:
                    url = self.host["url"]
                    for hf in self.host["select"]:
                        if f == hf:
                            url_name = "'" + url + "/'||"

                    column_name = self._get_column_name(f, alias_name)
                else:
                    # Date and time - try
                    result = self.extract_datetime(f, alias_name)
                    if result is not None:
                        column_name = result
                    else:
                        column_name = self._get_column_name(f, alias_name)

                if f == "*":
                    select_list.append("*")
                else:
                    select_list.append(url_name + column_name + " AS " + f.replace(".", "_"))

        if len(select_list) > 0:
            for f in select_list:
                c.a(0, f + ", ")

            c.strip_last(2)
        else:
            if len(total) == 0:
                c.a(0, "*")

        return c

    # EXTRACT FROM DATETIME
    def extract_datetime(self, column, alias_name=None) -> str:
        result = None
        if column.endswith("__year"):
            if alias_name is None:
                result = "EXTRACT(ISOYEAR FROM " + column[0:-6] + ")"
            else:
                result = "EXTRACT(ISOYEAR FROM " + alias_name + "." + column[0:-6] + ")"
        elif column.endswith("__month"):
            if alias_name is None:
                result = "EXTRACT(MONTH FROM " + column[0:-7] + ")"
            else:
                result = "EXTRACT(MONTH FROM " + alias_name + "." + column[0:-7] + ")"
        elif column.endswith("__day"):
            if alias_name is None:
                result = "EXTRACT(DAY FROM " + column[0:-5] + ")"
            else:
                result = "EXTRACT(DAY FROM " + alias_name + "." + column[0:-5] + ")"
        elif column.endswith("__hour"):
            if alias_name is None:
                result = "EXTRACT(HOUR FROM " + column[0:-6] + ")"
            else:
                result = "EXTRACT(HOUR FROM " + alias_name + "." + column[0:-6] + ")"
        elif column.endswith("__minute"):
            if alias_name is None:
                result = "EXTRACT(MINUTE FROM " + column[0:-8] + ")"
            else:
                result = "EXTRACT(MINUTE FROM " + alias_name + "." + column[0:-8] + ")"
        elif column.endswith("__second"):
            if alias_name is None:
                result = "EXTRACT(SECOND FROM " + column[0:-9] + ")"
            else:
                result = "EXTRACT(SECOND FROM " + alias_name + "." + column[0:-9] + ")"
        elif column.endswith("__week"):
            if alias_name is None:
                result = "EXTRACT(WEEK FROM " + column[0:-6] + ")"
            else:
                result = "EXTRACT(WEEK FROM " + alias_name + "." + column[0:-6] + ")"
        elif column.endswith("__weekday"):
            if alias_name is None:
                result = "EXTRACT(ISODOW FROM " + column[0:-9] + ")"
            else:
                result = "EXTRACT(ISODOW FROM " + alias_name + "." + column[0:-9] + ")"
        elif column.endswith("__yearday"):
            if alias_name is None:
                result = "EXTRACT(DOY FROM " + column[0:-9] + ")"
            else:
                result = "EXTRACT(DOY FROM " + alias_name + "." + column[0:-9] + ")"
        elif column.endswith("__quarter"):
            if alias_name is None:
                result = "EXTRACT(QUARTER FROM " + column[0:-9] + ")"
            else:
                result = "EXTRACT(QUARTER FROM " + alias_name + "." + column[0:-9] + ")"
        elif column.endswith("__date"):
            if alias_name is None:
                result = "TO_CHAR(" + column[0:-6] + ", 'yyyy-mm-dd')"
            else:
                result = "TO_CHAR(" + alias_name + "." + column[0:-6] + ", 'yyyy-mm-dd')"
        elif column.endswith("__time"):
            if alias_name is None:
                result = "TO_CHAR(" + column[0:-6] + ", 'hh24:mi:ss')"
            else:
                result = "TO_CHAR(" + alias_name + "." + column[0:-6] + ", 'hh24:mi:ss')"
        elif column.endswith("__datetime"):
            if alias_name is None:
                result = "TO_CHAR(" + column[0:-10] + ", 'yyyy-mm-dd hh24:mi:ss')"
            else:
                result = "TO_CHAR(" + alias_name + "." + column[0:-10] + ", 'yyyy-mm-dd hh24:mi:ss')"
        elif column.endswith("__time_x_sec"):
            if alias_name is None:
                result = "TO_CHAR(" + column[0:-12] + ", 'hh24:mi')"
            else:
                result = "TO_CHAR(" + alias_name + "." + column[0:-12] + ", 'hh24:mi')"
        elif column.endswith("__datetime_x_sec"):
            if alias_name is None:
                result = "TO_CHAR(" + column[0:-16] + ", 'yyyy-mm-dd hh24:mi')"
            else:
                result = "TO_CHAR(" + alias_name + "." + column[0:-16] + ", 'yyyy-mm-dd hh24:mi')"

        return result

    #
    # Column functions
    #
    def _get_column_function_parameters(self, t):
        if "alias" in t:
            if t["alias"] is None or t["alias"] == "":
                alias = ""
            else:
                alias = t["alias"]
        else:
            alias = "func_" + t["formula"][0:2]

        if "alias_name" in t:
            if t["alias_name"] is None or t["alias_name"] == "":
                alias = ""
            else:
                alias = t["alias_name"]

        if "formula" in t:
            if t["formula"] is None or t["formula"] == "":
                formula = ""
            else:
                formula = t["formula"]
        else:
            formula = ""

        if "order_by" in t:
            if t["order_by"] is None or t["order_by"] == "":
                order_by = ""
            else:
                order_by = t["order_by"].upper()
        else:
            order_by = ""

        return alias, formula, order_by

    def _get_column_function(self, select, column_function) -> Coder:
        c = Coder("sql")

        if len(column_function) > 0:
            c.c(0, "Column functions")

        for x, t in enumerate(column_function):
            column_function_string = ""
            alias, formula, order_by = self._get_column_function_parameters(t)

            if x == 0:
                if len(select) == 0:
                    column_function_string += formula + " AS " + alias + ", "
                else:
                    column_function_string += ", " + formula + " AS " + alias + ", "
            else:
                column_function_string += formula + " AS " + alias + ", "

            c.a(0, column_function_string)

        if c.lines > 0:
            c.strip_last(2)

        return c

    #
    # Window
    #
    def _get_window_parameters(self, t: dict, main_alias: str):
        if "action" in t:
            if t["action"] is None or t["action"] == "":
                action = "SUM"
            else:
                action = t["action"].upper()
        else:
            action = "SUM"

        if "column" in t:
            if t["column"] is None or t["column"] == "":
                column = ""
            else:
                column = t["column"]
        else:
            column = ""

        if "alias" in t:
            if t["alias"] is None or t["alias"] == "":
                alias = action.lower() + "_" + column.replace(".", "_")
            else:
                alias = t["alias"]
        else:
            alias = action.lower() + "_" + column.replace(".", "_")

        partition_by_string = ""
        if "partition_by" in t:
            partition_by = t["partition_by"]
            if len(partition_by) > 0:
                partition_by_string = "PARTITION BY "
                for f in partition_by:
                    if "." in f:
                        partition_by_string += f + ", "
                    else:
                        column_name = self._get_column_name(f, main_alias)
                        partition_by_string += column_name + ", "

                if len(partition_by_string) > 0:
                    partition_by_string = partition_by_string[0:-2]

        order_by_string = ""
        if "order_by" in t:
            order_by = t["order_by"]
            if len(order_by) > 0:
                order_by_string = "ORDER BY "
                for f in order_by:
                    if "." in f:
                        order_by_string += f + ", "
                    else:
                        column_name = self._get_column_name(f, main_alias)
                        order_by_string += column_name + ", "

                if len(order_by_string) > 0:
                    order_by_string = order_by_string[0:-2]

        return action, column, alias, partition_by_string, order_by_string

    def _get_window(self, select: list, window: list, main_alias: str) -> Coder:
        c = Coder("sql")

        if len(window) > 0:
            c.c(0, "Window")

            for x, t in enumerate(window):
                window_string = ""
                action, column, alias, partition_by_string, order_by_string = self._get_window_parameters(t, main_alias)
                over_string = (partition_by_string + " " + order_by_string).strip()
                action_string = action.upper() + "(" + column + ")"

                if x == 0:
                    if len(select) == 0:
                        window_string += action_string + " OVER (" + over_string + ")" + " AS " + alias + ", "
                    else:
                        window_string += ", " + action_string + " OVER (" + over_string + ")" + " AS " + alias + ", "
                else:
                    window_string += action_string + " OVER (" + over_string + ")" + " AS " + alias + ", "

                c.a(0, window_string)

        if c.lines > 0:
            c.strip_last(2)

        return c

    #
    # TOTAL AVG, MIN, MAX, SUM, COUNT functions
    #
    def _get_total_parameters(self, t):
        if "action" in t:
            if t["action"] is None or t["action"] == "":
                action = "SUM"
            else:
                action = t["action"].upper()
        else:
            action = "SUM"

        if "column" in t:
            if t["column"] is None or t["column"] == "":
                column = ""
            else:
                column = t["column"]
        else:
            column = ""

        if "alias" in t:
            if t["alias"] is None or t["alias"] == "":
                alias = action.lower() + "_" + column.replace(".", "_")
            else:
                alias = t["alias"]
        else:
            alias = action.lower() + "_" + column.replace(".", "_")

        if "having" in t:
            if t["having"] is None or t["having"] == "":
                having = ""
            else:
                having = t["having"]
        else:
            having = ""

        if "order_by" in t:
            if t["order_by"] is None or t["order_by"] == "":
                order_by = ""
            else:
                order_by = t["order_by"].upper()
        else:
            order_by = ""

        return action, column, alias, having, order_by

    def _get_total(self, select, total, table_alias) -> Coder:
        c = Coder("sql")

        total_fields_string = ""
        for x, t in enumerate(total):
            action, column, alias, having, order_by = self._get_total_parameters(t)

            column = self._get_column_name(column, table_alias)
            if x == 0:
                if len(select) == 0:
                    total_fields_string += action + "(" + column + ") AS " + alias + ", "
                else:
                    total_fields_string += ", " + action + "(" + column + ") AS " + alias + ", "
            else:
                total_fields_string += action + "(" + column + ") AS " + alias + ", "

        if len(total_fields_string) > 0:
            total_fields_string = total_fields_string[0:-2]
            c.c(0, "Total fields")
            c.a(0, total_fields_string)

        return c

    #
    # FROM
    #
    def _get_object_name(self, schema_name: str = None, table_name: str = None):
        if schema_name is not None:
            object_name = schema_name.lower() + "."
        else:
            object_name = self.schema_name.lower() + "."

        if table_name is not None:
            object_name += table_name.lower()
        else:
            object_name += self.table_name.lower()

        return object_name

    def _get_alias_name(self, main_name) -> str:
        # Alias suggestion
        name_array = main_name.split("_")
        alias_name = ""
        for an in name_array:
            alias_name += an[0:2]

        # Check if alias already in the list
        x = 1
        old_alias_name = alias_name
        while alias_name in self.alias_list:
            alias_name = old_alias_name + str(x)
            x += 1

        # Update list
        self.alias_list.append(alias_name)

        return alias_name

    #
    # JOIN
    #
    def _get_join_parameters(self, j):
        if "schema" in j:
            schema_name = j["schema"]
        else:
            if "schema_name" in j:
                schema_name = j["schema_name"]
            else:
                schema_name = self.schema_name

        if "table" in j:
            table_name = j["table"]
        else:
            if "table_name" in j:
                table_name = j["table_name"]
            else:
                table_name = self.table_name

        if "alias" in j:
            alias = j["alias"]
        else:
            if "alias_name" in j:
                alias = j["alias_name"]
            else:
                alias = self._get_alias_name(table_name)

        on = None
        if "relation" in j:
            relation = j["relation"]
        else:
            if "relation_name" in j:
                relation = j["relation_name"]
            else:
                if "on" in j:
                    on = j["on"]
                    relation = ""
                else:
                    relation = table_name

        return schema_name, table_name, alias, relation, on

    def _get_join(self, join_type, join_array, main_alias, id_name: str) -> Coder:
        c = Coder("sql")

        # Set default ID value
        if len(id_name) == 0:
            id_name = "id"

        if len(join_array) > 0:
            c.c(0, join_type.capitalize() + " joins")

        for j in join_array:
            schema_name, table_name, alias, relation, on = self._get_join_parameters(j)
            c.a(0, join_type.upper() + " JOIN " + schema_name + "." + table_name + " AS " + alias)
            if on is None:
                c.a(1, "ON " + alias + "." + id_name + " = " + main_alias + "." + relation)
            else:
                c.a(1, "ON " + on)

            # Inner join
            if "inner_join" in j:
                if len(j['inner_join']) > 0:
                    inner_join_coder = self._get_join("inner", j["inner_join"], alias, id_name)
                    c.b(0, inner_join_coder)

            # Left join
            if "left_join" in j:
                if len(j['left_join']) > 0:
                    left_join_coder = self._get_join("left", j["left_join"], alias, id_name)
                    c.b(0, left_join_coder)

        return c

    #
    # WHERE
    #
    def _get_where(self, lines, where, alias, prefix=True) -> Coder:
        c = Coder("sql")

        if len(where) > 0:
            if where is not None:
                w_list = AGQueryWhere(where, alias)

                if lines > 0:
                    c.a(0, "AND (")
                else:
                    if prefix:
                        c.a(0, "WHERE (")
                    else:
                        c.a(0, "AND (")

                c.b(1, w_list.c)

            c.a(0, ")")

        return c

    def _get_where_string(self, c_lines, where_string, prefix=True) -> Coder:
        c = Coder("sql")

        if len(where_string) > 0:
            where_statement = ""
            if self.where_string is not None:
                if prefix:
                    if c_lines > 0:
                        where_statement = "AND (" + where_string + ")"
                    else:
                        where_statement = "WHERE (" + where_string + ")"
                else:
                    where_statement = "AND (" + where_string + ")"

            c.a(0, where_statement)

        return c

    #
    # GROUP BY
    #
    def _get_group_by(self, alias, select, total) -> Coder:
        c = Coder("sql")

        if len(total) > 0:
            column_list = ""
            for f in select:
                result = self.extract_datetime(f)
                if result is not None:
                    column_name = result
                else:
                    column_name = self._get_column_name(f, alias)

                column_list += column_name + ", "

            if len(column_list) > 0:
                column_list = column_list[0:-2]
                if self.rollup:
                    c.a(0, "GROUP BY ROLLUP (" + column_list + ")")
                else:
                    c.a(0, "GROUP BY " + column_list)

        return c

    #
    # Having
    #
    def _get_having(self, main_alias, total) -> Coder:
        c = Coder("sql")

        having_string = ""
        for t in total:
            action, column, alias, having, total_order_by = self._get_total_parameters(t)

            if len(having) > 0:
                if len(having_string) == 0:
                    having_string = "HAVING "

                column_name = self._get_column_name(column, main_alias)
                having_string += action + "(" + column_name + ") " + having + ", "

        if len(having_string) > 0:
            having_string = having_string[0: -2]
            c.a(0, having_string)

        return c

    #
    # ORDER BY
    #
    def _get_order_by(self, order_by, main_alias, column_function, total) -> Coder:
        c = Coder("sql")

        order_by_string = ""

        # Column function
        for t in column_function:
            alias, formula, column_function_order_by = self._get_column_function_parameters(t)
            if column_function_order_by != "":
                if len(order_by_string) == 0:
                    order_by_string = "ORDER BY "

                order_by_string += formula + " " + column_function_order_by + ", "

        # Total
        for t in total:
            action, column, alias, having, total_order_by = self._get_total_parameters(t)
            if total_order_by != "":
                if len(order_by_string) == 0:
                    order_by_string = "ORDER BY "

                column_name = self._get_column_name(column, main_alias)
                order_by_string += action + "(" + column_name + ") " + total_order_by + ", "

        if len(order_by_string) > 0:
            order_by_string = order_by_string[0:-2]
            c.a(0, order_by_string)

        if len(order_by) > 0:
            if len(order_by_string) == 0:
                order_by_string = "ORDER BY "
            else:
                order_by_string = ", "

            for f in order_by:
                result = self.extract_datetime(f, main_alias)

                if result is None:
                    if "." in f:
                        order_by_string += f + ", "
                    else:
                        column_name = self._get_column_name(f, main_alias)
                        order_by_string += column_name + ", "
                else:
                    order_by_string += result + ", "

            if len(order_by_string) > 0:
                order_by_string = order_by_string[0:-2]
                c.a(0, order_by_string)

        return c

    def _get_limit(self, limit: int = 0) -> Coder:
        c = Coder("sql")

        if limit != 0:
            c.a(0, "LIMIT " + str(limit))

        return c

    def _get_offset(self, offset: int = 0, page: int = 0) -> Coder:
        c = Coder("sql")

        if offset != 0:
            c.a(0, "OFFSET " + str(offset))

        if page != 0:
            c.a(0, "OFFSET " + str(page * self.limit - 1))

        return c

    def _before_json(
            self,
            schema_name, table_name, alias_name, select, column_function, window, total,
            inner_join, left_join, id_name,
            up_relations, down_relations,
            where, where_and, where_string, order_by,
            limit, offset, page
        ):
        c = Coder("sql")

        if alias_name is None or alias_name == "":
            alias_name = self._get_alias_name(table_name)

        object_name = self._get_object_name(schema_name, table_name)

        main_from_string = "FROM " + object_name + " " + alias_name
        main_inner_join = self._get_join("inner", inner_join, alias_name, id_name)
        main_left_join = self._get_join("left", left_join, alias_name, id_name)

        main_select_block = self._get_select(alias_name, select, total)
        column_function_block = self._get_column_function(select, column_function)
        window_block = self._get_window(select, window, alias_name)
        total_fields_block = self._get_total(select, total, alias_name)

        if len(self.id_name) == 0:
            id_name = "id"

        # Up relations
        up_relation_coder = self._get_up_relations(up_relations, alias_name, id_name)

        # Down relations
        down_relation_coder = self._get_down_relations(down_relations, alias_name, id_name)

        # WHERE
        if len(where) > 0:
            where_block = self._get_where(0, where, alias_name)
        else:
            where_block = Coder("sql")

        # WHERE AND
        if len(where_and) > 0:
            where_and_block = self._get_where(where_block.lines, where_and, alias_name)
        else:
            where_and_block = Coder("sql")

        # WHERE STRING
        if len(where_string) > 0:
            lines = where_block.lines + where_and_block.lines
            where_string_block = self._get_where_string(lines, where_string)
        else:
            where_string_block = Coder("sql")

        # GROUP BY
        if len(self.total) > 0:
            group_by = self._get_group_by(alias_name, select, total)

            # HAVING
            having = self._get_having(alias_name, total)
        else:
            group_by = Coder("sql")
            having = Coder("sql")

        # ORDER BY
        order_by = self._get_order_by(order_by, alias_name, self.column_function, self.total)

        # LIMIT
        limit = self._get_limit(limit)

        # OFFSET
        offset = self._get_offset(offset, page)

        c.c(0, "Main table: " + schema_name + "." + table_name)
        c.a(0, "SELECT")
        c.b(1, main_select_block)
        c.b(1, up_relation_coder)
        c.b(1, down_relation_coder)
        c.b(1, column_function_block)
        c.b(1, window_block)
        c.b(1, total_fields_block)

        c.new_line()
        c.c(0, "Main table: " + schema_name + "." + table_name)
        c.a(0, main_from_string)
        c.b(0, main_inner_join)
        c.b(0, main_left_join)
        c.b(0, where_block)
        c.b(0, where_and_block)
        c.b(0, where_string_block)

        c.b(0, group_by)
        c.b(0, having)

        c.b(0, order_by)
        c.b(0, offset)
        c.b(0, limit)
        self.inner_sql = c.render()

        return c

    def _build_sql(self):
        c = Coder("sql")

        # Assemble SQL
        line = "SELECT ROW_TO_JSON(output) FROM ("
        c.a(0, line)
        c.new_line()

        before_json_block = self._before_json(
            schema_name=self.schema_name, table_name=self.table_name, alias_name=self.alias_name,
            select=self.select, column_function=self.column_function, window=self.window, total=self.total,
            inner_join=self.inner_join, left_join=self.left_join, id_name=self.id_name,
            up_relations=self.up_relations, down_relations=self.down_relations,
            where=self.where, where_and=self.where_and, where_string=self.where_string, order_by=self.order_by,
            limit=self.limit, offset=self.offset, page=self.page
        )
        c.b(1, before_json_block)

        line = ") AS output"
        c.a(0, line)

        self.SQL = c.render()

    def _get_up_relations(self, up_relations, alias_name, id_name) -> Coder:
        c = Coder("sql")

        for ur in up_relations:
            relation_schema_name = ur['schema_name']
            relation_table_name = ur['table_name']
            relation_object_name = self._get_object_name(relation_schema_name, relation_table_name)
            relation_alias_name = self._get_alias_name(relation_table_name)
            relation_select = ur['select']

            try:
                relation_relation = ur['relation']
            except LookupError as e:
                relation_relation = None

            c.new_line()
            c.c(0, "Up relation:" + relation_schema_name + "." + relation_table_name)

            line = ", (SELECT ROW_TO_JSON(" + relation_table_name + ")"
            c.a(0, line)

            if relation_relation:
                line = "AS " + relation_relation + " FROM"
                c.a(1, line)
            else:
                line = "AS " + relation_table_name + " FROM"
                c.a(1, line)

            select_block = self._get_select(relation_alias_name, relation_select, [])
            c.a(1, "(SELECT")
            c.b(2, select_block)

            if relation_relation:
                relation_id_name = relation_relation.replace("_id", "")
            else:
                relation_id_name = relation_table_name

            # Up relations
            if "up_relations" in ur:
                if len(ur['up_relations']) > 0:
                    up_relation_coder = self._get_up_relations(
                        ur['up_relations'], relation_alias_name, id_name
                    )
                    c.b(2, up_relation_coder)

            # Down relations
            if "down_relations" in ur:
                if len(ur['down_relations']) > 0:
                    down_relation_coder = self._get_down_relations(
                        ur['down_relations'], relation_alias_name, id_name
                    )
                    c.b(2, down_relation_coder)

            line = "FROM " + relation_object_name + " " + relation_alias_name
            c.a(1, line)

            line = "WHERE " + alias_name + "." + relation_id_name + " = " + relation_alias_name + "." + id_name
            c.a(1, line)

            # WHERE
            if "where" in ur:
                where_block = self._get_where(1, ur['where'], relation_alias_name, prefix=False)
                c.b(1, where_block)

            if "where_and" in ur:
                where_and_block = self._get_where(1, ur['where_and'], relation_alias_name, prefix=False)
                c.b(1, where_and_block)

            # WHERE STRING
            if "where_string" in ur:
                where_statement = self._get_where_string(1, ur['where_string'], prefix=False)
                c.b(1, where_statement)

            c.a(0, ") AS " + relation_table_name + ")")

        return c

    def _get_down_relations(self, down_relations, alias_name, id_name) -> Coder:
        c = Coder("sql")

        for dr in down_relations:
            relation_schema_name = dr['schema_name']
            relation_table_name = dr['table_name']
            relation_object_name = self._get_object_name(relation_schema_name, relation_table_name)
            relation_alias_name = self._get_alias_name(relation_table_name)

            #
            # Column function
            #
            if "column_function" in dr:
                column_function = dr["column_function"]
            else:
                column_function = []

            #
            # Window
            #
            if "window" in dr:
                window = dr["window"]
            else:
                window = []

            #
            # Window
            #
            if "window" in dr:
                window = dr["window"]
            else:
                window = []

            #
            # Total
            #
            if "total" in dr:
                total = dr["total"]
            else:
                total = []

            #
            # Select
            #
            if "select" in dr:
                relation_select = dr['select']
            else:
                if len(total) == 0:
                    relation_select = ["*"]
                else:
                    relation_select = []

            try:
                relation_relation = dr['relation']
            except LookupError as e:
                relation_relation = None

            c.new_line()
            c.c(0, "Down relation:" + relation_schema_name + "." + relation_table_name)
            line = ", (SELECT ARRAY_AGG(" + relation_table_name + ") "
            c.a(0, line)

            # From
            line = " AS " + relation_table_name + " FROM"
            c.a(0, line)

            # Alias/Relation
            if relation_relation:
                relation_id_name = relation_relation
            else:
                relation_id_name = self.table_name

            # Select
            select_block = self._get_select(relation_alias_name, relation_select, total)
            column_function_block = self._get_column_function(relation_select, column_function)
            window_block = self._get_window(relation_select, window, relation_alias_name)
            total_block = self._get_total(relation_select, total, relation_alias_name)

            c.a(1, "(SELECT")
            c.b(2, select_block)

            # Up relations
            if "up_relations" in dr:
                if len(dr['up_relations']) > 0:
                    up_relation_coder = self._get_up_relations(
                        dr['up_relations'], relation_alias_name, id_name
                    )
                    c.b(2, up_relation_coder)

            # Down relations
            if "down_relations" in dr:
                if len(dr['down_relations']) > 0:
                    down_relation_coder = self._get_down_relations(
                        dr['down_relations'], relation_alias_name, id_name
                    )
                    c.b(2, down_relation_coder)

            # Column functions
            c.b(2, column_function_block)

            # Window
            c.b(2, window_block)

            # Totals
            c.b(2, total_block)

            # From
            line = "FROM " + relation_object_name + " " + relation_alias_name
            c.a(1, line)

            # Joins
            if "inner_join" in dr:
                main_inner_join = self._get_join("inner", dr["inner_join"], relation_alias_name, id_name)
                c.b(1, main_inner_join)

            if "left_join" in dr:
                main_left_join = self._get_join("left", dr["left_join"], relation_alias_name, id_name)
                c.b(1, main_left_join)

            # Link down relation upwards in hierarchy
            line = "WHERE " + alias_name + "." + id_name + " = " + relation_alias_name + "." + relation_id_name
            c.a(1, line)

            # WHERE
            if "where" in dr:
                where_block = self._get_where(1, dr['where'], relation_alias_name, prefix=False)
                c.b(1, where_block)

            if "where_and" in dr:
                where_and_block = self._get_where(1, dr['where_and'], relation_alias_name, prefix=False)
                c.b(1, where_and_block)

            # WHERE STRING
            if "where_string" in dr:
                where_statement = self._get_where_string(1, dr['where_string'], prefix=False)
                c.b(1, where_statement)

            # GROUP BY
            if len(total) > 0:
                group_by = self._get_group_by(alias_name, relation_select, total)
                c.b(1, group_by)

                # HAVING
                having = self._get_having(alias_name, total)
                c.b(1, having)

            # ORDER BY
            if "order_by" in dr:
                order_by = self._get_order_by(dr['order_by'], relation_alias_name, column_function, total)
                c.b(1, order_by)

            # OFFSET
            if "offset" in dr or "page" in dr:
                if "page" in dr:
                    offset = self._get_offset(page=dr["page"])
                else:
                    offset = self._get_offset(offset=dr["offset"])

                c.b(1, offset)

            # LIMIT
            if "limit" in dr:
                limit = self._get_limit(dr["limit"])
                c.b(1, limit)

            # End
            c.a(0, ") AS " + relation_table_name + ")")

        return c

    #
    # Control functions
    #
    def validate(self):
        pass

    def print_sql(self):
        print(self.SQL)

    def parse_query(self, query: dict):
        if "schema" in query:
            self.schema_name = query["schema"]
        else:
            if "schema_name" in query:
                self.schema_name = query["schema_name"]
            else:
                self.schema_name = "public"

        if "table" in query:
            self.table_name = query["table"]
        else:
            if "table_name" in query:
                self.table_name = query["table_name"]

        if "id_name" in query:
            self.id_name = query["id_name"]
        else:
            self.id_name = "id"

        if "column_function" in query:
            self.column_function = query["column_function"]

        if "window" in query:
            self.window = query["window"]

        if "total" in query:
            self.total = query["total"]

        if "select" in query:
            self.select = query["select"]
        else:
            if len(self.total) == 0:
                self.select = ["*"]
            else:
                self.select = []

        if "alias" in query:
            self.alias_name = query["alias"]
        else:
            if "alias_name" in query:
                self.alias_name = query["alias_name"]
            else:
                self.alias_name = ""

        if "rollup" in query:
            self.rollup = query["rollup"]
        if "left_join" in query:
            self.left_join = query["left_join"]
        if "inner_join" in query:
            self.inner_join = query["inner_join"]
        if "up_relations" in query:
            self.up_relations = query["up_relations"]
        if "down_relations" in query:
            self.down_relations = query["down_relations"]

        if "where" in query:
            self.where = query["where"]
        if "where_and" in query:
            self.where_and = query["where_and"]
        if "where_string" in query:
            self.where_string = query["where_string"]

        if "order_by" in query:
            self.order_by = query["order_by"]
        if "offset" in query:
            self.offset = query["offset"]
        else:
            self.offset = 0

        if "limit" in query:
            self.limit = query["limit"]
        else:
            self.limit = 0
        if "page" in query:
            self.page = query["page"]
        else:
            self.page = 0

        if "host" in query:
            self.host = query["host"]

    def execute(self, query: dict = None) -> str:
        if query is not None:
            self.parse_query(query)

        self._build_sql()
        return self.SQL
