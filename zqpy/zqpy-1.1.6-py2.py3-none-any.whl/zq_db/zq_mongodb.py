
# https://www.runoob.com/python3/python-mongodb.html
import pymongo

class zq_mongodb_class():
    def __init__(self, host='43.128.88.114', port=27072, uri=None):
        '''
        初始化：下面比选一个   不要用_id进行操作，那个是游标的，查改不到东西
        :param host:ip '43.128.88.114'
        :param port:端口 27072

        :param uri:自定义拼装地址
        '''
        if uri:
            self.myclient = pymongo.MongoClient(uri)
        else:
            self.myclient = pymongo.MongoClient(host=host, port=port)

    def mongodb_has_db(self, db_name):
        '''
        是否存在数据库
        '''
        return db_name in self.myclient.list_database_names()

    def mongodb_has_table(self, db_name, table_name):
        '''
        是否存在表
        '''
        return table_name in self.mongodb_get_db(db_name).list_collection_names()

    def mongodb_get_db(self, db_name):
        '''
        获取db数据库
        '''
        return self.myclient[db_name]

    def mongodb_get_table(self, db_name, table_name):
        '''
        获取 db 里的 表
        '''
        return self.mongodb_get_db(db_name)[table_name]
    
    def mongodb_insert(self, db_name, table_name, data:dict):
        '''
        插入单条记录
        :param data: {'_id':固定id[不填默认最后],'字段名1':'值1', '字段名2':'值3'}
        :return 类型: inserted_id插入id
        '''
        return self.mongodb_get_table(db_name, table_name).insert_one(data)
    
    def mongodb_inserts(self, db_name, table_name, data:dict):
        '''
        插入多条记录
        :param data: [{'_id':固定id[不填默认最后], '字段名1':'值1', '字段名2':'值3'},{'_id':固定id[不填默认最后], '字段名1':'值1', '字段名2':'值3'}]
        :return 类型: inserted_ids插入id列表
        '''
        self.mongodb_get_table(db_name, table_name).insert_many(data)
    
    def mongodb_find_one(self, db_name, table_name, data:dict, result_data:dict=None):
        '''
        查询一条数据
        '''
        return self.mongodb_get_table(db_name, table_name).find_one(data, projection=(result_data if result_data else {}))

    def mongodb_find(self, db_name, table_name, data:dict, result_data:dict=None, limit:int=0):
        '''
        查询自定义数据, 返回游标
        :param data: 
        1. None 所有数据
        2. {'name': 'RUNOOB' } 根据指定条件查询
        3. {'name': {'$gt': 'H'}} 高级搜索，读取name字段中第一个字母ASCII值大于 'H' 的数据，大于的修饰符条件为 {'$gt': 'H'}
        4. {'name': {'$regex': '^R'}} 使用正则表达式搜索，用于读取 name 字段中第一个字母为 'R' 的数据，正则表达式修饰符条件为 {'$regex': '^R'}  正则刘开头的内容{'$in': ['/^liu/']}
        5. { $or: [ { quantity: { $lt: 20 } }, { price: 10 } ] }  或者
        :param result_data: 
        1. None 所有数据
        2. {'字段': 值, '字段': 值}  查询所有数据,返回指定字段 要返回的 1 不返回的 0 除了_id，不能在一个对象中同时指定 0 和 1
        :param limit: 返回的最大条数
        '''
        return self.mongodb_get_table(db_name, table_name).find(data if data else {}, result_data).limit(limit)

    def mongodb_find_to_list(self, db_name, table_name, data:dict, result_data:dict=None, limit:int=0):
        '''
        查询自定义数据，返回列表
        '''
        db_all = self.mongodb_find(db_name, table_name, data, result_data, limit)
        db_all_list = []
        for db_item in db_all:
            db_all_list.append(db_item)
        return db_all_list
    
    def mongodb_find_exits(self, db_name, table_name, data:dict):
        '''
        查询是否存在于数据库，find查到的是具体数据，用的游标
        '''
        all_data = self.mongodb_find(db_name, table_name, data, limit=1)
        for item in all_data:
            return True
        return False

    def mongodb_find_sort(self, db_name, table_name, data:dict, result_data:dict, limit:int, sort:list):
        '''
        查询数据并排序
        :param sort: 排序条件 (字段/字段列表,  1 升序  -1降序)
        '''
        return self.mongodb_find(db_name, table_name, data, result_data, limit).sort(sort[0], sort[1])

    def mongodb_update_one(self, db_name, table_name, query:dict, data:dict):
        '''
        更新一条数据
        :param query: {'name':{'$regex':'^F'}} 查询条件
        :param data: {'name':{'$regex':'^F'}} 替换为数据
        :return 类型: 描述
        '''
        return self.mongodb_get_table(db_name, table_name).update_one(query, data)

    def mongodb_update(self, db_name, table_name, query:dict, data:dict):
        '''
        更新多条记录
        :param query: {'name':{'$regex':'^F'}} 查询条件
        :param data: {'$set':{'name':{'$regex':'^F'}}} 替换为数据
        :return 类型: 描述
        '''
        return self.mongodb_get_table(db_name, table_name).update_many(query, data)

    def mongodb_delete_one(self, db_name, table_name, query:dict):
        '''
        删除一条数据
        :param query: {'name':{'$regex':'^F'}} 查询条件
        :return 类型: 描述
        '''
        return self.mongodb_get_table(db_name, table_name).delete_one(query)

    def mongodb_delete(self, db_name, table_name, query:dict={}):
        '''
        删除多条记录
        :param query: {'name':{'$regex':'^F'}} 查询条件, 空 表示删除全部
        :return 类型: 描述
        '''
        return self.mongodb_get_table(db_name, table_name).delete_many(query)

    def mongodb_delete_table(self, db_name, table_name):
        '''
        删除表
        '''
        return self.mongodb_get_table(db_name, table_name).drop()
    
    def mongodb_table_num(self, db_name, table_name):
        '''
        获取表数据条数
        '''
        return self.mongodb_find(db_name, table_name, None, limit=1).count()

    def mongodb_update_or_insert(self, db_name, table_name, find_data, update_data, update_symbol='$set'):
        '''
        更新或者插入数据
        '''
        if self.mongodb_find_exits(db_name, table_name, find_data):
            self.mongodb_update(db_name, table_name, find_data,  {update_symbol:update_data})
        else:
            self.mongodb_insert(db_name, table_name, update_data)

if __name__ == '__main__':
    zq_mongodb = zq_mongodb_class()
    x = zq_mongodb.mongodb_find_one('ET1', 'DBLoginInfo', {'PlayerId':'393538333331393938333037343138313539'}, None)
    y = zq_mongodb.mongodb_find_one('ET1', 'Chat', {})
    for x in zq_mongodb.mongodb_find('ET1', 'Chat', {}, None, limit=2):
        print(x)
    for x in zq_mongodb.mongodb_find_to_list('ET1', 'Chat', {}, None, limit=2):
        print(x)
    