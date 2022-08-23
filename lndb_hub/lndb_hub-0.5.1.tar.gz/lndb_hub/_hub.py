import lnschema_core as schema
import sqlmodel as sqm
from lamin_logger import logger
from lndb_setup import settings
from lndb_setup._hub import connect_hub
from supabase import Client

from ._entities import Entities
from ._schema import check_schema_version


def get_hub_with_authentication():
    hub = connect_hub()
    session = hub.auth.sign_in(
        email=settings.user.email, password=settings.user.password
    )
    hub.postgrest.auth(session.access_token)
    check_schema_version(hub)
    return hub


class hub:
    """Access the hub."""

    @classmethod
    def _load_entity(cls, entity):
        # we need to do this right now as we can't do a cyclic import
        # we first need to import all of lamindb (including load)
        # then lndb_hub is imported
        # once it's imported load can be imported here
        from lamindb.do._load import load

        return load.entity(entity)

    @classmethod
    def push_instance(cls):
        """Push instance with all dobjects."""
        hub = get_hub_with_authentication()
        dobject_df = cls._load_entity("dobject")
        for id, v in dobject_df.index:
            cls.push_dobject(id, v, hub)

    @classmethod
    def push_dobject(cls, id: str, v: str = "1", hub: Client = None):
        """Push a single dobject."""
        if hub is None:
            hub = get_hub_with_authentication()
        entities = Entities(hub)
        instance = entities.instance.get_or_create()
        with sqm.Session(settings.instance.db_engine()) as session:
            storage = session.exec(
                sqm.select(schema.storage).where(
                    schema.storage.root == str(settings.instance.storage_dir)
                )
            ).first()
            assert storage
            dobject = session.get(schema.dobject, (id, v))
            assert dobject
            dtransform = session.get(schema.dtransform, dobject.dtransform_id)
            assert dtransform
            jupynb = session.get(
                schema.jupynb, (dtransform.jupynb_id, dtransform.jupynb_v)
            )
            assert jupynb
        cls.__push_storage(entities, storage)
        cls.__push_jupynb(entities, jupynb, instance["id"])
        cls.__push_dtransform(entities, dtransform, instance["id"])
        cls.__push_dobject(entities, dobject, instance["id"])

    @classmethod
    def delete_instance(cls):
        """Delete the instance on the hub."""
        hub = get_hub_with_authentication()
        entities = Entities(hub)
        instance = entities.instance.get()
        dobject_df = cls._load_entity("dobject")
        jupynb_df = cls._load_entity("jupynb")
        dtransform_df = cls._load_entity("dtransform")
        storage_df = cls._load_entity("storage")
        for id, v in dobject_df.index:
            logger.info(f"Delete dobject ({id}, {v}).")
            entities.dobject.delete(id, v, instance["id"])
        for id in dtransform_df.index:
            logger.info(f"Delete dtransform ({id}).")
            entities.dtransform.delete(id, instance["id"])
        for id, v in jupynb_df.index:
            logger.info(f"Delete jupynb ({id}, {v}).")
            entities.jupynb.delete(id, v, instance["id"])
        for root in storage_df["root"].values:
            logger.info(f"Delete storage ({root}).")
            entities.storage.delete(root)
        entities.user_instance.delete(instance["id"])
        entities.instance.delete()

    @classmethod
    def __push_storage(self, entities: Entities, storage: schema.storage):
        if not entities.storage.exists(storage.root):
            logger.info(f"Push storage ({storage.root}).")
            entities.storage.insert(
                storage.id,
                storage.root,
                storage.region,
                storage.type,
            )
        else:
            logger.warning(
                f"storage ({storage.root}) already exists and is not pushed."
            )

    @classmethod
    def __push_dtransform(
        self, entities: Entities, dtransform: schema.dtransform, instance_id: str
    ):
        if not entities.dtransform.exists(dtransform.id, instance_id):
            logger.info(f"Push dtransform ({dtransform.id}).")
            entities.dtransform.insert(
                dtransform.id, dtransform.jupynb_id, dtransform.jupynb_v, instance_id
            )
        else:
            logger.warning(
                f"dtransform ({dtransform.id}) already exists and is not pushed."
            )

    @classmethod
    def __push_jupynb(
        self, entities: Entities, jupynb: schema.jupynb, instance_id: str
    ):
        if not entities.jupynb.exists(jupynb.id, jupynb.v, instance_id):
            logger.info(f"Push jupynb ({jupynb.id}, {jupynb.v}).")
            entities.jupynb.insert(
                jupynb.id,
                jupynb.v,
                jupynb.name,
                instance_id,
                jupynb.time_created,
                jupynb.time_updated,
            )
        else:
            logger.warning(
                f"jupynb ({jupynb.id}, {jupynb.v}) already exists and is not pushed."
            )

    @classmethod
    def __push_dobject(
        self, entities: Entities, dobject: schema.dobject, instance_id: str
    ):
        if not entities.dobject.exists(dobject.id, dobject.v, instance_id):
            logger.info(f"Push dobject ({dobject.id}, {dobject.v}).")
            entities.dobject.insert(
                dobject.id,
                dobject.v,
                dobject.name,
                dobject.file_suffix,
                dobject.dtransform_id,
                dobject.storage_id,
                instance_id,
                dobject.time_created,
                dobject.time_updated,
            )
        else:
            logger.warning(
                f"dobject ({dobject.id}, {dobject.v}) already exists and is not pushed."
            )
