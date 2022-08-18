from typing import List
import pyAesCrypt
import os
import json
import datetime

from clustery import t
from clustery import exceptions

true = True
false = False

class Table:
    def __init__(self, name:str, keys:dict):
        self.name = name
        self.keys = keys

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()

class Database:
    def __init__(db, path:str):
        db.path:str = path

        db.name:str = ""
        db.enc_key:str = "CLUSTERY-KEY-JUST-FOR-NICE-STUFF-IDC-IF-YOU-SEE-THIS-SINCE-IT-IS-NOT-A-SECURITY-FLAW-OH-AND-CHECK-OUT-THIS-VIDEO-https://www.youtube.com/watch?v=iik25wqIuFo"
        db.use_ids:bool = False
        
        db.tables:List[Table] = []

        q = open(path, "r").read()

        execs = q[q.find("+--+") + len("+--+"):q.rfind("+--+")]
        evals = q.replace(execs, "").replace("+--+", "")

        exec(execs)
        eval(evals)

        db.ids_keys = {}

        for table in db.tables:
            db.ids_keys[table.name] = t.int

        if db.use_ids == True:
            db.ids_table = f"{db.name}-IDS"
            db.set_table(db.ids_table, db.ids_keys)

    def set_table(db, name:str, keys:dict) -> Table:
        t:Table = Table(name, keys)
        db.tables.append(t)
        return t

    def get_table(db, table:str) -> Table:
        r:Table = None

        for t in db.tables:
            if t.name == table:
                r = t
                break

        return r

    def clear_table(db, table:str) -> dict:
        data = db.load_data()

        if table in data:
            data[table] = []

        db.save_data(data)
        return data

    def set_item(db, table:str, keys:dict) -> dict:
        tab:Table = db.get_table(table)

        for key in tab.keys:
            if key not in keys:
                raise exceptions.KeyMissing(f"Item is missing key '{key}'")

            dont_check = False

            if type(keys[key]) == list and type(tab.keys[key]) == List:
                dont_check = True

            if dont_check and tab.keys[key] != type(keys[key]):
                raise exceptions.InvalidKeyType(f"Key type '{tab.keys[key].__name__}' does not match '{type(keys[key]).__name__}'")

        data = db.load_data()

        if db.use_ids == True:
            if not db.ids_table in data:
                data[db.ids_table] = []
                data[db.ids_table].append(db.ids_keys)

                for key in data[db.ids_table][0]:
                    data[db.ids_table][0][key] = 0
            else:
                data[db.ids_table][0][table] += 1

        if not table in data:
            data[table] = []

        if db.use_ids == True: keys["id"] = data[db.ids_table][0][table]
        data[table].append(keys)

        db.save_data(data)

        return keys

    def set_itemv(db, table:str, *args, **kwargs) -> dict:
        return db.set_item(table, kwargs)

    def get_item(db, table:str, key:str, value) -> dict:
        data = db.load_data()

        if not table in data:
            data[table] = []

        result = None

        for item in data[table]:
            if item[key] == value:
                result = item

        db.save_data(data)

        return result

    def get_itemv(db, table:str, *args, **kwargs) -> dict:
        data = db.load_data()

        if not table in data:
            data[table] = []

        result = None

        for item in data[table]:
            for key in kwargs:
                result = item
                if item[key] != kwargs[key]:
                    result = None

        db.save_data(data)

        return result

    def delete_item(db, table:str, key:str, value) -> dict:
        item = db.get_item(table, key, value)

        data = db.load_data()

        data[table].remove(item)

        db.save_data(data)

        return data[table]

    def delete_itemv(db, table:str, *args, **kwargs) -> dict:
        item = db.get_itemv(table, *args, **kwargs)

        data = db.load_data()

        data[table].remove(item)

        db.save_data(data)

        return data[table]

    def update_item(db, table:str, key:str, value, new_key:str, new_value) -> dict:
        item = db.get_item(table, key, value)
        
        data = db.load_data()

        for count, i in enumerate(data[table]):
            if i == item:
                data[table][count][new_key] = new_value

        item[new_key] = new_value
        db.save_data(data)

        return item

    def update_itemv(db, table:str, item:dict, *args, **kwargs):        
        data = db.load_data()

        for count, i in enumerate(data[table]):
            if i == item:
                for key in kwargs:
                    item[key] = kwargs[key]
                    data[table][count] = item

        db.save_data(data)

        return item

    def item_count(db, table:str) -> int:
        data = db.load_data()
        db.save_data(data)

        return len(data[table])

    def load_data(db) -> dict:
        if not os.path.exists(".clustery"):
            os.mkdir(".clustery")

        data_path = f".clustery/{db.name}.clud.temp"

        data = {}

        if os.path.exists(f".clustery/{db.name}.clud"):
            pyAesCrypt.decryptFile(f".clustery/{db.name}.clud", data_path, db.enc_key)
            data = json.loads(open(data_path, "r").read())

        return data

    def save_data(db, data:dict):
        data_path = f".clustery/{db.name}.clud.temp"

        with open(data_path, "w+") as file:
            json.dump(data, file, default=str, cls=JSONEncoder)

        pyAesCrypt.encryptFile(data_path, f".clustery/{db.name}.clud", db.enc_key)
        os.remove(data_path)

    def query(db, q:str):
        return eval(q)