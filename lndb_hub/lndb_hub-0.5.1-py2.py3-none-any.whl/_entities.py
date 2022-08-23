import uuid
from datetime import datetime
from pathlib import Path
from typing import Union

from cloudpathlib import CloudPath
from lamin_logger import logger
from lndb_setup import settings
from supabase import Client


class Entities:
    def __init__(self, hub: Client) -> None:
        self.hub = hub
        self.instance = Instance(self.hub)
        self.user_instance = UserInstance(self.hub)
        self.dtransform = Dtransform(self.hub)
        self.jupynb = Jupynb(self.hub)
        self.dobject = Dobject(self.hub)
        self.storage = Storage(self.hub)


class Entity:
    def __init__(self, hub: Client, table_name: str, primary_keys: list) -> None:
        self.hub = hub
        self.table_name = table_name
        self.primary_keys = primary_keys

    def exists(self, primary_keys_values: dict):
        statement = self.hub.table(self.table_name).select("*")
        for key in self.primary_keys:
            statement = statement.eq(key, primary_keys_values[key])
        data = statement.execute()
        if len(data.data) > 0:
            return True
        return False

    def delete(self, primary_keys_values: dict):
        statement = self.hub.table(self.table_name).delete()
        for key in self.primary_keys:
            statement = statement.eq(key, primary_keys_values[key])
        statement.execute()

    def insert(self, fields: dict):
        data = self.hub.table(self.table_name).insert(fields).execute()
        assert len(data.data) == 1
        return data.data[0]


class Instance:
    def __init__(self, hub: Client) -> None:
        self.hub = hub
        self.instance_entity = Entity(hub, "instance", ["id"])
        self.user_instance_entity = Entity(
            hub, "user_instance", ["user_id", "instance_id"]
        )

    def get_or_create(self):
        instance = self.get()
        if instance is None:
            instance = self.insert()
            logger.info("Pushing instance.")
        if not self.user_instance_entity.exists(
            {
                "instance_id": instance["id"],
                "user_id": self.hub.auth.session().user.id.hex,
            }
        ):
            self.user_instance_entity.insert(
                {
                    "instance_id": instance["id"],
                    "user_id": self.hub.auth.session().user.id.hex,
                }
            )
        return instance

    def get(self):
        data = (
            self.hub.table("instance")
            .select("*")
            .eq("name", settings.instance.name)
            .execute()
        )
        if len(data.data) > 0:
            return data.data[0]
        return None

    def delete(self):
        (
            self.hub.table("instance")
            .delete()
            .eq("name", settings.instance.name)
            .execute()
        )

    def insert(self):
        return self.instance_entity.insert(
            {
                "id": str(uuid.uuid4()),
                "name": settings.instance.name,
                "owner_id": self.hub.auth.session().user.id.hex,
                "storage_dir": str(settings.instance.storage_dir),
                "dbconfig": settings.instance._dbconfig,
                "cache_dir": str(settings.instance.cache_dir),
                "sqlite_file": str(settings.instance._sqlite_file),
                "sqlite_file_local": str(settings.instance._sqlite_file_local),
                "db": settings.instance.db,
            }
        )


class UserInstance:
    def __init__(self, hub: Client) -> None:
        self.hub = hub
        self.user_instance_entity = Entity(
            hub, "user_instance", ["user_id", "instance_id"]
        )

    def exists(self, instance_id: str):
        return self.user_instance_entity.exists(
            {"user_id": self.hub.auth.session().user.id.hex, "instance_id": instance_id}
        )

    def delete(self, instance_id: str):
        self.user_instance_entity.delete(
            {"user_id": self.hub.auth.session().user.id.hex, "instance_id": instance_id}
        )

    def insert(self, instance_id: str):
        return self.user_instance_entity.delete(
            {"user_id": self.hub.auth.session().user.id.hex, "instance_id": instance_id}
        )


class Jupynb:
    def __init__(self, hub: Client) -> None:
        self.hub = hub
        self.jupynb_entity = Entity(hub, "jupynb", ["id", "v", "instance_id"])

    def exists(self, id: str, v: str, instance_id: str):
        return self.jupynb_entity.exists({"id": id, "v": v, "instance_id": instance_id})

    def delete(self, id: str, v: str, instance_id: str):
        self.jupynb_entity.delete({"id": id, "v": v, "instance_id": instance_id})

    def insert(
        self,
        id: str,
        v: str,
        name: str,
        instance_id: str,
        time_created: datetime,
        time_updated: datetime,
    ):
        return self.jupynb_entity.insert(
            {
                "id": id,
                "v": v,
                "name": name,
                "instance_id": instance_id,
                "owner_id": self.hub.auth.session().user.id.hex,
                "time_created": time_created.strftime("%Y-%m-%d %H:%M:%S"),
                "time_updated": time_updated.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )


class Dobject:
    def __init__(self, hub: Client) -> None:
        self.hub = hub
        self.dobject_entity = Entity(hub, "dobject", ["id", "v", "instance_id"])

    def exists(self, id: str, v: str, instance_id: str):
        return self.dobject_entity.exists(
            {"id": id, "v": v, "instance_id": instance_id}
        )

    def delete(self, id: str, v: str, instance_id: str):
        self.dobject_entity.delete({"id": id, "v": v, "instance_id": instance_id})

    def insert(
        self,
        id: str,
        v: str,
        name: str,
        file_suffix: str,
        dtransform_id: str,
        storage_id: str,
        instance_id: str,
        time_created: datetime,
        time_updated: datetime,
    ):
        return self.dobject_entity.insert(
            {
                "id": id,
                "v": v,
                "name": name,
                "file_suffix": file_suffix,
                "dtransform_id": dtransform_id,
                "instance_id": instance_id,
                "storage_id": storage_id,
                "owner_id": self.hub.auth.session().user.id.hex,
                "time_created": time_created.strftime("%Y-%m-%d %H:%M:%S"),
                "time_updated": time_updated.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )


class Dtransform:
    def __init__(self, hub: Client) -> None:
        self.hub = hub
        self.dtransform_entity = Entity(hub, "dtransform", ["id", "instance_id"])

    def exists(self, id: str, instance_id: str):
        return self.dtransform_entity.exists({"id": id, "instance_id": instance_id})

    def delete(self, id: str, instance_id: str):
        self.dtransform_entity.delete({"id": id, "instance_id": instance_id})

    def insert(
        self,
        id: str,
        jupynb_id: str,
        jupynb_v: str,
        instance_id: str,
    ):
        return self.dtransform_entity.insert(
            {
                "id": id,
                "jupynb_id": jupynb_id,
                "jupynb_v": jupynb_v,
                "pipeline_run_id": None,
                "instance_id": instance_id,
                "owner_id": self.hub.auth.session().user.id.hex,
            }
        )


class Storage:
    def __init__(self, hub: Client) -> None:
        self.hub = hub
        self.dtransform_entity = Entity(hub, "storage", ["root"])

    def exists(self, root: Union[Path, CloudPath, str]):
        return self.dtransform_entity.exists(
            {
                "root": str(root),
            }
        )

    def delete(self, root: Union[Path, CloudPath, str]):
        self.dtransform_entity.delete(
            {
                "root": str(root),
            }
        )

    def insert(
        self,
        id: str,
        root: Union[Path, CloudPath, str],
        region: str,
        type: str,
    ):
        return self.dtransform_entity.insert(
            {
                "id": id,
                "root": str(root),
                "region": region,
                "type": type,
            }
        )
