from datetime import datetime
import os, uuid

from traducteur.lib.model import BaseSQLModel
from traducteur.lib.manager import SQLModelManager

class BaseSQLiteModel(BaseSQLModel):
    id: str = uuid.uuid4().hex

    @property
    def _manager(self):
        return self.__class__.__get_manager()

    @property
    def _col_name(self):
        return self.__class__.__name__

    class Config:
        arbitrary_types_allowed = True
        allow_population_by_field_name = True
    
    def save(self):
        if self.created_at == None:
            self.created_at = datetime.utcnow()
            self.updated_at = datetime.utcnow()
            return self._manager.insert_one(self)
        else:
            self.updated_at = datetime.utcnow()
            return self._manager.update_one(self)

    def delete(self):
        self.deleted_at = datetime.utcnow()
        return self._manager.delete_one(self)

    @classmethod
    def __get_manager(cls):
        con_str = os.environ['TRADUCTEUR_CONNECTION_STR']
        db_name = os.environ['TRADUCTEUR_DATABASE']
        return SQLModelManager(con_str, db_name)

    @classmethod
    def get(cls, id: str):
        manager = cls.__get_manager()
        result = manager.get_one(cls.__name__, id)
        return cls.from_dict(result)

    @classmethod
    def from_dict(cls, values: dict):
        return cls(**values)

    @classmethod
    def create_table(cls):
        schema = cls.schema()
        
        manager = cls.__get_manager()
        manager.create_table(schema)
