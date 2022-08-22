from __future__ import annotations
from sqlalchemy import create_engine
#from IPython.display import display
import pandas as pd
import numpy as np
import difflib

# develop insert mode (only_print, print_and_ask_confirm, ask_confirm, nothing)
# think show table to insert or statement? hum..


def scoped_environment(func):
    """
    If the function has the kwarg env will be run in the env of the kwarg, no matters
    in which env the class is working, will change the env and put again the original when
    finish the execution.
    """

    def wrapper_scope(*args, **kwargs):
        is_env_argument = ('env' in kwargs)
        self_arg = args[0]
        if is_env_argument:
            input_env = kwargs['env']
            """
            if input_env in ['prod|preprod','preprod|prod','both']:
                print('calling both environments')
                self_arg.change_environment('prod')
                func(*args, **kwargs)
                self_arg.change_environment('preprod')
                #kwargs['env'] = 'preprod' also good strategy
                func(*args, **kwargs)
                outputs = None
            elif input_env: #..
            """
            if input_env:  # env = something
                print('calling scoped environment')
                print()
                current_env = self_arg.env
                self_arg.change_environment(input_env)
                outputs = func(*args, **kwargs)
                if current_env != self_arg.env:
                    # print("going back to original environment")
                    self_arg.change_environment(current_env)
            else:  # env=None
                outputs = func(*args, **kwargs)
        else:  # no env arg in function
            outputs = func(*args, **kwargs)
        return outputs

    return wrapper_scope


def print_or_execute(func):
    """
    Only print as a decorator, consider using it more.., or not
    """
    def wrapper_print(*args, **kwargs):
        is_only_print_argument = ('only_print' in kwargs)
        self_arg = args[0]
        sql_str = func(*args, **kwargs)
        if is_only_print_argument:
            only_print = kwargs['only_print']
            self_arg.print_or_execute_sql_str(sql_str, only_print=only_print, ask_usr=False)
        else:
            self_arg.print_or_execute_sql_str(sql_str, only_print=False, ask_usr=False)
    return wrapper_print


def correct_table_name(func):
    """
    Correct table name, (should be the first argument)
    """
    def wrapper_name(*args, **kwargs):
        self_arg = args[0]
        if args[1] != "INFORMATION_SCHEMA.TABLES":
            arg_list = list(args)
            arg_list[1] = self_arg.check_table_name_in_db(args[1])
            args = tuple(arg_list)
        return func(*args, **kwargs)
    return wrapper_name


class SQLManager:
    
    def __init__(self, env_connection_dict: dict, env: str, verbose=True):
        """
        Takes a engine dict and the name of the engine to use

        Args:
            env_connection_dict: dict, dictionary of engine strings.
            env: str, engine to used from the env_connection_dict.
            verbose: bool, use verbose print statements.

        Example use:

            connection_dict = {'test_env': 'connection string from engine',
                               'prod_env': 'mssql+pyodbc://ur@prod.com/url2?driver=ODBC+Driver+17+for+SQL+Server'
                               }
            env = 'test_env'

            instance = SQLManager(connection_dict,env)

        """
        self.engine = None
        self.env = None
        self.verbose = verbose
        self.env_connection_dict = env_connection_dict
        self.change_environment(env)
        if self.env != 'meta':
            all_tables = self.sql_get_all_table_info()
            self.all_tables = all_tables.TABLE_SCHEMA + "." + all_tables.TABLE_NAME
            self.all_table_names = all_tables.TABLE_NAME

    def change_environment(self, env: str):
        """
        Changes the environment of the sql manager, make sure you are in the correct vpn.

        Args:
            env: str, The selected environments from the env_connection_dict
        """
        if self.env == env:
            self.vprint(f"Already at env {env}")
        elif env in self.env_connection_dict.keys():
            self.env = env
            connection_str = self.env_connection_dict[env]
            if env == 'meta':
                self.engine = self.env_connection_dict[env]
            else:
                self.engine = create_engine(connection_str)
        else:
            print(f"Environment chosen: {env} is invalid")
            raise Exception(f'Environment should be in {self.env_connection_dict.keys()}')
        self.vprint(f"Set {self.env} environment")

    # TABLE properties/ operations -------------------------------------------------------------------

    def get_column_names(self, table_name: str):
        """
        Get column names of a table
        """
        table_schema = self.select_all(f"INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}'")
        return list(table_schema.COLUMN_NAME)

    @scoped_environment
    def extract_changes_from_db_by_key(self, table_name: str, to_update: pd.DataFrame, key: str, drop_keys=None, env=None):
        """
        Given a table an a table name look for differences in the db by id
        drop_keys to ignore some keys in the compare, useful for entry date etc

        Also takes out whatever is not in the db
        """
        print('--looking for differences')
        db_table = self.select_all(table_name, key, to_update[key])
        to_insert = to_update[~to_update.ID.isin(db_table[key])].copy()
        to_update = to_update[to_update.ID.isin(db_table[key])].copy()

        if drop_keys:
            to_update.drop(drop_keys, axis=1, errors='ignore', inplace=True)
            db_table.drop(drop_keys, axis=1, errors='ignore', inplace=True)

        db_table = db_table.sort_values(by=[key]).reset_index(drop='True')
        to_update = to_update.sort_values(by=[key]).reset_index(drop='True')

        try:
            compared = db_table.compare(to_update)
            to_update = to_update.loc[compared.index]

            changed_keys = list(set([i[0] for i in compared.keys()]))
            if to_update.empty:
                print("--No differences found")
            else:
                print("--to_update, to_insert, changed_keys returned")
            return to_update, to_insert, changed_keys  # maybe two functions?
        except (Exception,):  # we could in fact drop them natively, would be easier
            print("Compare failed, look for differences in keys or rows")
            print(table_name)
            print(f"Look at: {set(to_update.keys()) - set(db_table.keys())}, or, "
                  f"{set(db_table.keys()) - set(to_update.keys())}")

    @scoped_environment
    def exclude_present_key(self, table_name: str, to_insert: pd.DataFrame, key='ID', **kargs):
        """
        Excludes rows that are already in the db by key, no copy made...
        """
        if key in to_insert.keys():
            present_keys = set(self.query(f"SELECT {key} FROM {table_name}")[key])
            to_insert = to_insert[~to_insert[key].isin(present_keys)]
        else:
            print(f"--No {key} in table")
        return to_insert

    @scoped_environment
    def exclude_present_ids(self, table_name: str, to_insert: pd.DataFrame, **kargs):
        """
        Excludes rows that are already in the db by ID, no copy made...
        """
        return self.exclude_present_key(table_name, to_insert, key='ID')

    def get_count(self, name):
        """
        Counts rows in a sql table,
        """
        try:
            sql_str = f"SELECT COUNT(*) Count FROM {name}"
            count = int(self.query(sql_str).Count.iloc[0])
        except (Exception,):
            count = None
        return count

    # SELECT Insert Update Delete --------------------------------------------------------------------

    @staticmethod
    def in_list(str_list):
        """
        sugar syntax for in queries
        """
        str_list = list(str_list)
        if len(str_list) > 1:
            return f"IN ({str(list(str_list))[1:-1]})"
        else:
            return f"= '{str_list[0]}'"

    def f_where(self, where='', _in=None, rel='AND'):
        """Parses the where to sql syntax"""
        string = ''
        if isinstance(where, pd.Series) or where:  # consider change to pd.series
            string = ' WHERE '
            if not pd.Series(_in, dtype=object).empty:
                where_list = np.atleast_1d(np.array(where, dtype=object))
                if len(where_list) > 1:
                    _in = pd.Series(_in, dtype=object)
                    _in = [pd.Series(el, dtype=object) for el in np.atleast_1d(_in)]
                else:
                    _in = [pd.Series(el, dtype=object) for el in np.atleast_2d(_in)]
                any_empty = any(i.empty for i in _in)
                if any_empty:
                    string += ' 0=1 --empty condition'
                else:
                    string += f" {rel} ".join([f"{i} {self.in_list(j.values)}" for i, j in zip(where_list, _in)])
            else:
                if isinstance(_in, type(None)):
                    string += where
                else:
                    string += ' 0=1 --empty condition'
        return string

    def where(self, conditions, values, rel='AND'):
        """Surely deprecated by fwhere"""
        string = 'WHERE '
        conditions, values = np.atleast_1d(conditions), np.atleast_1d(values)
        if len(conditions) != len(values):
            string += self.in_list(values)
        else:
            string += f' {rel} '.join([condition + self.in_list(value) for condition, value in zip(conditions, values)])
        return string

    @scoped_environment
    # @correct_table_name
    def select_all(self, table_name: str, where='', _in=None, only_print=False, **kargs):
        """
        Reads a pandas dataframe from a SELECT * FROM query, enhanced syntax, can be called
        now is a bit less flexible but a ton more scalable, think in other possibilities..
        """
        return self.print_or_read_sql_str(f"SELECT * FROM {table_name}" + self.f_where(where, _in, rel='AND'),
                                          only_print=only_print)

    @scoped_environment
    def select(self, columns, table_name: str, where='', _in=None, only_print=False, **kargs):
        """ Select statement like select_all but allows to choose columns to select"""
        return self.print_or_read_sql_str(f"SELECT {columns} FROM {table_name}" + self.f_where(where, _in),
                                          only_print=only_print)  # {', '.join(columns)}

    @scoped_environment
    @correct_table_name
    def delete(self, table_name: str, where='', _in=None, only_print=False, **kargs):
        """ Delete statement from python to db """
        return self.print_or_execute_sql_str(f"DELETE {table_name}" + self.f_where(where, _in), only_print=only_print)

    def basic_insert(self, table_name: str, to_insert: pd.DataFrame, ask_usr=True, _display=True):
        """
        Insert data into table asking confirmation, before: add_basic_table,
        in fact i could insert it via sql and deprecate this...but maybe gives date problems
        """
        if self.required_confirmation(to_insert, table_name, ask_usr=ask_usr, _display=_display):
            to_insert.to_sql(table_name, self.engine, if_exists='append', index=False)

    @scoped_environment
    def insert(self, table_name: str, to_insert: pd.DataFrame, drop_keys: list = None, ask_usr=True,
               only_print: bool = False, _display=True, **kargs):  # can be a pandas method
        """
        Goes to the selected environment insert a table and return to the original one.
        """

        if isinstance(to_insert, pd.DataFrame):
            table_name = self.check_table_name_in_db(table_name)
            to_insert = to_insert.copy()

            # you may want to update excluded ones
            # to_update, changed_keys =
            # self.extract_differences_from_db_by_key(to_update, table_name,key, drop_keys=drop_keys)
            to_insert = self.exclude_present_ids(table_name, to_insert)

            if not to_insert.empty:
                if drop_keys:
                    to_insert.drop(drop_keys, axis=1, errors='ignore', inplace=True)
                schema, table_name = self.get_table_name_and_schema(table_name)

                if only_print:
                    self.sql_insert_statement_from_dataframe(table_name, to_insert)
                else:
                    self.basic_insert(table_name, to_insert, ask_usr=ask_usr, _display=_display)
            else:
                print(f"--Nothing to insert at {table_name}")
        else:
            print(f"--to_insert at {table_name} should be a dataframe")

    def deprecated_update_table_from_id(self, table_name: str, to_update: pd.DataFrame,
                                        drop_list: list = None, **kargs):
        """
        DEPRECATED: use update_by_id. will be removed in next version.
        """
        to_update = to_update.copy()
        print(f"Update in {table_name}, rows to update:")
        if self.required_confirmation(to_update):
            ids_to_update = list(to_update.ID)  # test empty is better
            if drop_list:
                print(f"dropping {drop_list} if exist")
                to_update.drop(drop_list, axis=1, errors='ignore', inplace=True)
            if len(ids_to_update) == 0:
                print("nothing to update, or no ID")
            else:
                schema, table_name = self.get_table_name_and_schema(table_name)
                self.delete_by_id(ids_to_update, table_name, ask_usr=False)
                to_update.to_sql(table_name, self.engine, if_exists='append', index=False, schema=schema)
                print("table updated")

    @scoped_environment
    def update_by_key(self, table_name: str, to_update: pd.DataFrame, reference_key: str = 'ID', insert=False,
                      keys_to_update=None, drop_keys=None, ask_usr: bool = True, only_print: bool = False, **kargs):
        """
        This method should overwrite the upper one eventually or at least think about it, needs to support more than
        one row drop_keys
        """
        table_name = self.check_table_name_in_db(table_name)
        to_update = to_update.copy()

        if keys_to_update:
            # drop all except what you want to keep
            keys_to_update = keys_to_update + [reference_key]
            drop_keys = list(set(to_update.keys()) - set(keys_to_update))
            to_update = to_update[keys_to_update]

        to_update, to_insert, changed_keys = self.extract_changes_from_db_by_key(table_name, to_update, reference_key,
                                                                                 drop_keys=drop_keys)
        keys_to_update = changed_keys
        for i, row in to_update.iterrows():
            txt_updates = self.sql_replace(" ".join([f"{key} = '{row[key]}'," for key in keys_to_update])[:-1])
            sql_str = f"UPDATE {table_name} SET {txt_updates} WHERE {reference_key} = '{row[reference_key]}'"
            self.print_or_execute_sql_str(sql_str, ask_usr=ask_usr, only_print=only_print)
        print()
        if insert and not to_insert.empty:
            self.insert(to_insert, table_name=table_name, drop_keys=drop_keys, only_print=only_print, _display=True)

    def update_by_id(self, table_name: str, to_update: pd.DataFrame, insert: bool = True, keys_to_update=None,
                     drop_keys=None, ask_usr: bool = True, only_print: bool = False, env=None):
        """
        This method checks in the db what have you changed looking the ids and then makes an update where
        the compare returns that you changed something.
        """
        self.update_by_key(table_name=table_name, to_update=to_update, reference_key='ID', insert=insert,
                           keys_to_update=keys_to_update, drop_keys=drop_keys, ask_usr=ask_usr,
                           only_print=only_print, env=env)

    @scoped_environment
    @print_or_execute
    def delete_by_key_old(self, table_name: str, list_to_delete, key='ID', ask_usr: bool = True, **kargs):
        """
        Almost deprecated use delete, but it holds a ofk decorator.
        Todo: add ask_usr
        """
        table_name = self.check_table_name_in_db(table_name)
        if isinstance(list_to_delete, str):
            list_to_delete = [list_to_delete]
        return f"DELETE {table_name} WHERE {key} {self.in_list(list_to_delete)}"

    @scoped_environment
    def delete_by_key(self,  table_name: str, ids_to_delete, key, only_print=False, ask_usr: bool = True, **kargs):
        """
        Delete statement given an key, accepts env, only_print as kargs
        """
        self.delete(table_name, key, ids_to_delete, only_print=only_print)

    @scoped_environment
    def delete_by_id(self,  table_name: str, ids_to_delete, only_print=False, ask_usr: bool = True, **kargs):
        """
        Delete statement given an ID list, accepts env, only_print as kargs
        """
        self.delete(table_name, "ID", ids_to_delete, only_print=only_print)

    def sql_insert_statement_from_dataframe(self, target_name: str, to_insert: pd.DataFrame):
        """
        make the insert print from a pd table
        """
        print(f"INSERT INTO {target_name} ({', '.join(to_insert.columns)})")
        print('VALUES')
        df_len = len(to_insert) - 1
        for i, (index, row) in enumerate(to_insert.iterrows()):
            string = self.sql_replace(str(tuple(row.values)))
            last_it = (i != df_len)
            print(string + ',' * last_it)
        print()

    def one_by_one_sql_insert_statement_from_dataframe(self, to_insert: pd.DataFrame, target_name: str):
        """
        make the insert print from a pd table, Deprecated
        """
        for index, row in to_insert.iterrows():
            values = self.sql_replace(str(tuple(row.values)))
            print('INSERT INTO ' + target_name + ' (' + str(', '.join(to_insert.columns)) + ') VALUES ' + values)

    @scoped_environment
    def print_or_execute_sql_str(self, sql_str: str, ask_usr: bool = True, only_print: bool = True, **kargs):
        """
        Given a sql statement, prints it or execute it
        """
        if only_print:
            print(sql_str)
        elif self.required_confirmation(sql_str, ask_usr=ask_usr):
            self.execute_sql_str(sql_str)

    @scoped_environment
    def print_or_read_sql_str(self, sql_str: str, only_print: bool = False, **kargs):
        """
        Given a sql statement, prints it or execute it
        """
        if only_print:
            print(sql_str)
        else:
            return pd.read_sql_query(sql_str, self.engine)

    @scoped_environment
    def execute_sql_str(self, sql_str: str, only_print: bool = False, **kargs):
        """
        Just execute a sql string
        """
        sql_str = self.sql_replace(sql_str)  # .replace("'None'",'NULL') # before?
        if only_print:
            print(sql_str)
        else:
            with self.engine.connect() as conn:
                conn.execute(sql_str)

    @scoped_environment
    def execute_sql_exec(self, sql_str: str, **kargs):
        """
        Just execute a sql string
        """
        sql_str = self.sql_replace(sql_str)
        with self.engine.begin() as conn:
            conn.execute(sql_str)

    @scoped_environment
    def query(self, sql_str: str, only_print: bool = False, **kargs):
        """queries sql string from database"""
        return self.print_or_read_sql_str(sql_str)

    # Utilities --------------------------------------------------------------------

    @staticmethod
    def required_confirmation(table=None, table_name='', ask_usr=True, _display=True):
        """
        Ask for a text confirmation when required
        """
        if ask_usr:
            print("--Select/Insert/update: " + table_name)
            if _display:
                print(table)
		#display(table)
            confirmation = input("Are you sure you want to perform this operation?")
            if confirmation in ["yes", 'y', 'YES', 'Yes']:
                print("Operation accepted")
                return True
            else:
                print("Operation cancelled by user")
                return False
        else:
            return True

    @staticmethod
    def get_table_name_and_schema(table: str):
        """given a name returns table and schema"""
        if "." in table:
            schema, table_name = table.split(".")
        else:
            schema, table_name = None, table
        return schema, table_name

    @staticmethod
    def sql_replace(sql_str: str):
        """
        Corrects some differences between df and sql syntax
        need to support #datetime
        """
        mapping = [(" False ", "'False'"), (" True ", "'True'"),
                   ("'NULL'", "NULL"), ("None", "NULL"),
                   (" nan ", "NULL"), ("'nan'", "NULL"),
                   ("\'", "'")]
        for r in mapping:
            sql_str = sql_str.replace(*r)
        return sql_str

    # All database functionalities  --------------------------------------------------------

    def sql_get_all_table_info(self, count_rows: bool = False):
        """
        Gets information about all sql tables in a db
        """
        tables = self.select_all("INFORMATION_SCHEMA.TABLES", "TABLE_TYPE", 'BASE TABLE')
        tables["Complete_Name"] = tables.TABLE_SCHEMA + '.' + tables.TABLE_NAME
        if count_rows:
            tables["rows"] = tables["Complete_Name"].apply(self.get_count)
        return tables

    @scoped_environment
    def check_table_name_in_db(self, table_name: str, env=None):
        """
        Checks if the table_name is in the db, this may be better as a decorator
        """
        table_names_in_db = set(self.all_table_names) | set(self.all_tables)

        if table_name not in table_names_in_db:  # .lower() maybe convenient
            dif = difflib.get_close_matches(table_name, table_names_in_db)
            corrected_name = dif[0]
            confirmation = input(f"{table_name} is not in the db, do you mean: {corrected_name}")
            if confirmation in ["yes", 'y', 'Y', 'YES', 'Yes']:
                table_name = corrected_name
            else:
                print("WARNING: Incorrect statement may be generated")
        return table_name

    def vprint(self, to_print):
        if self.verbose:
            print(to_print)


if __name__ == "__main__":
    # import here your own connection string dictionary
    # from src.core.connection_dict import DefaultConnections
    #connect = DefaultConnections()
    #sql = SQLManager(connect.connection_string_dict, 'preprod')
    print(sql)


