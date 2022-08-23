# mongo orm
# setup: 2 replica sets
# intialize table with primary and multiple secondary shards

# insert 10000 documents
# 1. verify all 10000 are split to shards
# 2. verify secondary shards are also updated for all 10000 documents

# update 100 documents
# 1. verify  updates are propagated to the secondary shards and are available for query

import unittest
import blaster
import gevent
import random
from blaster.mongo_orm import Model, Attribute, INDEX, SHARD_BY, initialize_mongo
from blaster.tools import get_random_id, get_str_id


class AModel(Model):
    _collection_name_ = "a"

    a = Attribute(int)
    b = Attribute(str)
    c = Attribute(str)
    d = Attribute(str)
    e = Attribute(str)
    f = Attribute(str)

    INDEX(
        (a, b),
        (b, c),
        (c, d),
        (c, d, e),
        (c, e)
    )
    SHARD_BY(primary=a, secondary=[b, c])


class BModel(Model):
    _collection_name_ = "b"

    a = Attribute(int)
    b = Attribute(str)
    c = Attribute(str)
    d = Attribute(str)
    e = Attribute(str)
    f = Attribute(str)

    INDEX(
        (a,),
        (b, c),
        (c, d),
        (c, d, e),
        (c, e)
    )
    SHARD_BY(primary=a, secondary=[b, c])

    def before_update(self):
        self.b = (self.b or "") + "0"


class CModel(Model):
    _collection_name_ = "c"

    _id = Attribute(str)
    a = Attribute(list)
    b = Attribute(dict)


initialize_mongo([{"host": "localhost:27017"}, {"host": "localhost:27019"}], "test_1")




class TestConcurrentThreadUpdates(unittest.TestCase):
    def make_table_changes(self, _by):
        item = AModel.get(a=0)
        item.b = (item.b or "") + _by
        item.f = (item.f or "") + _by
        # this should propagate b to secondary shard correctly
        item.commit()

        print(item.to_dict())
        for i in range(10):
            _i = random.randint(0, 9)
            item = AModel.get(a=_i)
            if(not item):
                item = AModel(a=_i).commit()
            item.b = (item.b or "") + _by
            item.c = (item.c or "") + _by
            item.d = (item.d or "") + _by
            item.e = (item.e or "") + _by
            item.f = (item.f or "") + _by
            item.commit()
            print(item.to_dict())

    def test_concurrent_thread_updates(self):
        AModel(a=0).commit()
        gevent.joinall([gevent.spawn(self.make_table_changes, str(i)) for i in range(10)])


class TestUpdates(unittest.TestCase):
    def test_update_with_change(self):
        b = BModel(a=0).commit()
        b = BModel.get(a=0)
        b.update({"$set": {"c": 100}})

        b = list(b.query({"a": 0}))[0]
        self.assertTrue(b.b == "00")
        self.assertTrue(b.c == "100")

    def test_list_insert(self):
        c = CModel(_id="3").commit()
        c.a.insert(0, 100)
        c.commit()
        self.assertTrue(c.a == [100])

        c_from_db = CModel.get("3", use_cache=False)
        self.assertTrue(c_from_db.a == [100])
        c.a.insert(1, 150)
        c.commit()

        c_from_db = CModel.get("3", use_cache=False)
        self.assertTrue(c_from_db.a == [100, 150])


# test remove multiple values from MongoList
# test remove multiple values from MongoDict
