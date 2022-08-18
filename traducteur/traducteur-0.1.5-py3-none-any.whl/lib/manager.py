from re import sub
from traducteur.lib.model import BaseModel, BaseSQLModel
from traducteur.lib.context import MongoContext, SQLite3Context
from bson import ObjectId

class BaseModelManager:
    def __init__(self, connection_string: str, database_name):
        self.connection_string = connection_string
        self.database_name = database_name

    def exists(self, col: str, id: str):
        pass

    def exists_where(self, col: str, query):
        pass

    def insert_one(self, item: BaseModel):
        pass

    def get_one(self, col: str, id: str):
        pass

    def get_many(self, col: str, query, limit: int):
        pass

    def update_one(self, update: BaseModel):
        pass

    def delete_one(self, query):
        pass




class SQLModelManager(BaseModelManager):
    def __init__(self, connection_string: str, database_name):
        super().__init__(connection_string, database_name)

    def __match_python_type_sql(self, type_name: str):
        match = {
            'string': 'TEXT',
            'integer': 'INT',
            'float': 'FLOAT(24)',
        }

        if match[type_name] == None:
            raise Exception('No SQL type found for ' + type_name)

        return match[type_name]

    def __check_table(self, name: str):
        query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{name}';"
        with SQLite3Context(self.connection_string, self.database_name) as db:
            cursor = db.execute(query)
            if cursor.fetchone()[0] == name:
                return True
            return False
        

    def create_table(self, schema: dict):
        if self.__check_table(schema['title']):
            print('Table already exists')
            return True

        cols = []
        for col, val in schema['properties'].items():
            sql_type = self.__match_python_type_sql(val['type'])
            req = f"\tNOT NULL" if col in schema['required'] else ""
            subquery = f"{col}\t{sql_type}{req}"
            cols.append(subquery)

        query = f"CREATE TABLE {schema['title']} ({', '.join(cols)});"
        self.query(query)

    # model actions
    def query(self, query: str):
        with SQLite3Context(self.connection_string, self.database_name) as db:
            return db.execute(query)

    def exists(self, col: str, id: str):
        with SQLite3Context(self.connection_string, self.database_name) as db:
            query = f"SELECT COUNT(id) FROM {col} WHERE id = ?;"
            cursor = db.execute(query, id)
            return len(cursor) >= 1

    def get_one(self, col: str, id: str):
        with SQLite3Context(self.connection_string, self.database_name) as db:
            query = f"SELECT * FROM {col} WHERE id = ?;"
            cursor = db.execute(query, id)
            return cursor.fetchone()

    def get_many(self, col: str, query, limit: int):
        with SQLite3Context(self.connection_string, self.database_name) as db:
            query = f"SELECT * FROM {col} WHERE {', '.join(query)} LIMIT {limit};"
            cursor = db.execute(query)
            return cursor.fetchall()

    def insert_one(self, item: BaseSQLModel):
        with SQLite3Context(self.connection_string, self.database_name) as db:
            query = f"INSERT INTO {item._col_name} ({item.sql_columns}) VALUES ({item.q_marks});"
            print(query)
            cursor = db.execute(query, item.column_values)
            return cursor.lastrowid

    def update_one(self, update: BaseSQLModel):
        with SQLite3Context(self.connection_string, self.database_name) as db:
            query = f"UPDATE {update._col_name} SET {update.sql_update} WHERE id = ?;"
            cursor = db.execute(query, update.id)
            return cursor.lastrowid

    def delete_one(self, item: BaseSQLModel):
        with SQLite3Context(self.connection_string, self.database_name) as db:
            query = f"DELETE FROM {item._col_name} WHERE id = ?;"
            cursor = db.execute(query, item.id)
            return True




class MongoModelManager(BaseModelManager):
    def __init__(self, connection_string: str, database_name):
        super().__init__(connection_string, database_name)

    def exists(self, col: str, id: str):
        with MongoContext(self.connection_string, self.database_name, col) as column:
            return column.count_documents({'_id': ObjectId(id)}) > 0

    def exists_where(self, col: str, query):
        with MongoContext(self.connection_string, self.database_name, col) as column:
            return column.count_documents(query) > 0

    def get_one(self, col: str, id: str):
        with MongoContext(self.connection_string, self.database_name, col) as column:
            query = {'_id': ObjectId(id)}
            return column.find_one(query)

    def get_all(self, col: str, limit: int = None):
        with MongoContext(self.connection_string, self.database_name, col) as column:
            return list(column.find().limit(limit) if limit != None else column.find())

    def get_many(self, col: str, query, limit: int):
        with MongoContext(self.connection_string, self.database_name, col) as column:
            return list(column.find(query).limit(limit))

    def insert_one(self, item: BaseModel):
        with MongoContext(self.connection_string, self.database_name, item._col_name) as column:
            result = column.insert_one(item.dict())
            item.id = result.inserted_id
            return item

    def update_one(self, update: BaseModel):
        with MongoContext(self.connection_string, self.database_name, update._col_name) as column:
            query = {'_id': ObjectId(update.id) }
            column.update_one(query, {"$set": update.dict()})
            return update

    def delete_one(self, item: BaseModel):
        with MongoContext(self.connection_string, self.database_name, item._col_name) as column:
            query = {'_id': ObjectId(item.id)}
            column.delete_one(query)
            return item