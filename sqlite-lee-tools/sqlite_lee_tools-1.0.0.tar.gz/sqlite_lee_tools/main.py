import sqlite3
from loguru import logger

class DataBasel:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = self.connect()
        self.c = self.conn.cursor()

    def connect(self):
        """
        connect the sqlite
        :return:
        """
        try:
            conn = sqlite3.connect(self.db_name)
            logger.info(f"连接数据库 {self.db_name} 成功")
            return conn
        except Exception as e:
            logger.error(e)

    def create_table(self, tb_name: str, table_struct: dict):
        """
        create database table
        :param tb_name: table name
        :param table_struct:
        demo_struct = {
            'name': 'text-',
            'age': 'int-',
            'address': 'char(50)',
            'salary': 'real'
        }
        :return: None
        """
        struct_command = ",\n".join([f"{item}    {table_struct[item].replace('-', '')}" if '-' not in table_struct[
            item] else f"{item}    {table_struct[item].replace('-', '')}    NOT NULL" for item in table_struct])
        sql_command = f"""CREATE TABLE {tb_name}
       (ID INT PRIMARY KEY     NOT NULL,
       {struct_command});
        """
        try:
            self.c.execute(sql_command)
            self.conn.commit()
            logger.info(f"创建数据表 {tb_name} 成功")
        except Exception as e:
            logger.error(e)

    def get_max_id_from_table(self, tb_name: str) -> int:
        sql_command = f"select max(id) from {tb_name}"
        try:
            cursor = self.c.execute(sql_command)
            for row in cursor:
                if row[0] is None:
                    return 0
                else:
                    return row[0]
        except Exception as e:
            logger.error(e)

    @staticmethod
    def double_list_to_dict(key_list: list, value_tuple: tuple):
        result_dict = {}
        for index in range(len(key_list)):
            result_dict[key_list[index]] = value_tuple[index]
        return result_dict

    def insert(self, tb_name: str, data: dict):
        """
        插入数据方法 暂时还没有解决id自增
        :param tb_name: table name
        :param data:
        example_data = {
            'id': 1,
            'name': 'apple',
            'age': 18,
            'address': 'Chengdu',
            'salary': 2
        }
        :return:
        """
        data['id'] = self.get_max_id_from_table(tb_name) + 1
        field_tuple = tuple([item for item in data])
        value_tuple = tuple([data[item] for item in data])
        sql_command = f"INSERT INTO {tb_name} {field_tuple} VALUES {value_tuple}"
        print(sql_command)
        try:
            self.c.execute(sql_command)
            self.conn.commit()
            logger.info("插入数据成功!")
        except Exception as e:
            logger.error(e)

    def select(self, tb_name: str, query_data=None):
        """
        检索功能， 虽然可以直接用select * from table name 但是还是优雅的写一下逻辑
        :param tb_name: table name
        :param query_data: query condition
        :return: some dict in list
        """
        result = []
        if query_data is None:
            self.c.execute(f'pragma table_info({tb_name})')
            cursor = self.c.fetchall()
            query_data = [x[1] for x in cursor]
        select_condition = ",".join(query_data)
        try:
            sql_command = f"SELECT {select_condition} FROM {tb_name}"
            cursor = self.c.execute(sql_command)
            for row in cursor:
                result.append(self.double_list_to_dict(query_data, row))
            logger.info("查询完毕")
            return result
        except Exception as e:
            logger.error(e)

    def update(self, tb_name: str, changes: str, query_condition: str):
        """
        改变数据
        :param tb_name: table name
        :param changes: 要修改的东西， 可以使用逗号分割
        :param query_condition: 过滤的条件
        :return: None
        """
        try:
            self.c.execute(f"UPDATE {tb_name} set {changes} where {query_condition}")
            self.conn.commit()
            logger.info(f"字段修改完毕!")
        except Exception as e:
            logger.error(e)

    def delete(self, tb_name: str, query_condition: str):
        try:
            self.c.execute(f"DELETE from {tb_name} where {query_condition};")
            self.conn.commit()
            logger.info(f"删除条件为 {query_condition} 数据成功")
        except Exception as e:
            logger.error(e)

    def close(self):
        """
        关闭连接 没什么好说的
        :return:
        """
        self.conn.close()
        logger.info("数据库链接关闭")
