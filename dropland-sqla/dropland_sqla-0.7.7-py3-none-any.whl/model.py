import itertools
from typing import Any, Dict, List, Optional, Set

from sqlalchemy import Column, delete, insert, inspect, select, update, func, distinct
from sqlalchemy.engine import Row
from sqlalchemy.exc import NoInspectionAvailable
from sqlalchemy.orm import DeclarativeMeta as ModelType, attributes, registry
from sqlalchemy.orm.instrumentation import instance_state
from sqlalchemy.orm.util import identity_key

from dropland.data.context import ContextData
from dropland.storages.sql import SqlModel as SqlModelMeta, SqlModelBase, SqlStorageType


class SqlModel(ModelType, SqlModelMeta):
    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            column_name_map = inspect(cls).c
        except NoInspectionAvailable:
            pass
        else:
            cls._column_name_map = dict(zip([column.name for column in column_name_map], column_name_map.keys()))

    def __new__(mcs, class_name, parents, attributes):
        if 'registry' not in attributes:
            attributes['registry'] = registry()

        return super().__new__(mcs, class_name, parents, attributes)


class SqlaModel(SqlModelBase, metaclass=SqlModel):
    __abstract__ = True
    __metaclass__ = SqlModel
    _column_name_map = dict()

    # noinspection PyProtectedMember
    @classmethod
    def query_for_select(cls, **kwargs):
        query = select(cls)

        rela_map = cls.Meta.relationships.items()
        one_to_many_relationships = []

        if cls.get_engine().db_type == SqlStorageType.POSTGRES:
            for dep_key, relationship in rela_map:
                if relationship.single:
                    continue

                model_class = relationship.get_model()
                join_model_class = relationship.get_join_model()

                if model_class != join_model_class:
                    fkc = join_model_class._get_fk_columns(model_class)
                else:
                    fkc = model_class._get_id_columns()

                for pk in fkc:
                    if relationship.join_model:
                        subq = func.array_remove(func.array_agg(distinct(pk)), None)
                    else:
                        subq = func.array_remove(func.array_agg(pk), None)

                    query = query.column(subq)

                one_to_many_relationships.append((join_model_class, relationship))

        if one_to_many_relationships:
            query = query.group_by(*cls._get_id_columns())
            for model_class, relationship in one_to_many_relationships:
                query = query.outerjoin(model_class, onclause=relationship.get_on_clause(cls))

        if 'sql_load_options' in kwargs:
            for option in kwargs['sql_load_options']:
                query = query.options(option)

        return query

    @classmethod
    def query_for_update(cls, **kwargs):
        query = update(cls)

        if 'sql_load_options' in kwargs:
            for option in kwargs['sql_load_options']:
                query = query.options(option)

        return query

    @classmethod
    def query_for_delete(cls, **kwargs):
        query = delete(cls)

        if 'sql_load_options' in kwargs:
            for option in kwargs['sql_load_options']:
                query = query.options(option)

        return query

    @classmethod
    def _get_field_by_column(cls, c: Column) -> str:
        return cls._column_name_map.get(c.name)

    @classmethod
    async def _get_from_orm_cache(cls, ctx: ContextData, indices: List[Any]) -> List[Optional['SqlaModel']]:
        sqla_cache_indices = [identity_key(cls, id_value) for id_value in indices]

        def _get(session):
            return [session.identity_map.get(ident) for ident in sqla_cache_indices]

        return await ctx.sql.connection.run_sync(_get) if sqla_cache_indices else []

    # noinspection PyProtectedMember
    @classmethod
    async def _attach_to_session(cls, ctx: ContextData, objects: List['SqlaModel']):
        states = list()

        for instance in objects:
            if instance is None:
                continue
            state = attributes.instance_state(instance)
            if state.session_id or state.key:
                continue
            state.session_id = ctx.sql.connection.sync_session.hash_key
            states.append(state)

        # noinspection PyProtectedMember
        def _set(session):
            session._register_persistent(states)

        await ctx.sql.connection.run_sync(_set)

    #
    # Phases operations
    #

    def _assign(self, data: Dict[str, Any]) -> 'SqlaModel':
        for k, v in data.items():
            try:
                attributes.set_committed_value(self, k, v)
            except KeyError as e:
                setattr(self, k, v)
        return self

    # noinspection PyProtectedMember
    @classmethod
    async def _construct(
        cls, ctx: ContextData, data: Dict[str, Any], instance: Optional['SqlaModel'] = None,
            only_fields: Optional[Set[str]] = None, **kwargs) -> Optional['SqlaModel']:
        column_names = [c.name for c in cls.get_columns()]
        rela_map = cls.Meta.relationships.items()
        one_to_many_models: Dict[str, int] = dict()

        if cls.get_engine().db_type == SqlStorageType.POSTGRES:
            for dep_key, relationship in rela_map:
                if relationship.single or not isinstance(relationship.key, str):
                    continue

                model_class = relationship.get_model()
                join_model_class = relationship.get_join_model()

                if model_class != join_model_class:
                    fkc = join_model_class._get_fk_columns(model_class)
                else:
                    fkc = model_class._get_id_columns()

                one_to_many_models[relationship.key] = len(fkc)

        elif isinstance(data, (tuple, Row)):
            data = data[0]

        if isinstance(data, dict):
            class_data = {c: data[c] for c in column_names if c in data}
            if instance := await super()._construct(ctx, class_data, instance, only_fields, **kwargs):
                for k, count in one_to_many_models.items():
                    setattr(instance, k, data.get(k, []))

        elif isinstance(data, (tuple, Row)):
            if isinstance(data[0], cls):
                instance = data[0]
                data_counter = 1
            else:
                class_data = {k: v for k, v in zip(column_names, data[0:len(column_names)])}
                data_counter = len(column_names)
                instance = await super()._construct(ctx, class_data, instance, only_fields, **kwargs)

            for k, count in one_to_many_models.items():
                if count == 1:
                    setattr(instance, k, data[data_counter])
                elif count > 1:
                    last_values = [None] * count
                    tuples = [data[data_counter + i] for i in range(count)]
                    for tuple_ in itertools.zip_longest(*tuples, fillvalue=None):
                        for i, v in enumerate(tuple_):
                            if v is None and last_values[i] is not None:
                                tuples[i].append(last_values[i])
                            else:
                                last_values[i] = v
                    setattr(instance, k, list(zip(*tuples)))
                data_counter += count
        else:
            instance = data

        return instance

    @classmethod
    async def _register_instances(cls, ctx: ContextData, objects: List['SqlaModel']):
        await super()._register_instances(ctx, objects)
        await cls._attach_to_session(ctx, objects)

    #
    # Perform operations
    #

    @classmethod
    async def perform_get(cls, ctx: ContextData, query, **kwargs) -> Optional['SqlaModel']:
        query = query.execution_options(timeout=ctx.sql.timeout_secs)
        if data := (await ctx.sql.connection.execute(query)).first():
            return await cls._construct(ctx, data, **kwargs)
        return None

    @classmethod
    async def perform_list(cls, ctx: ContextData, query, **kwargs) -> List['SqlaModel']:
        query = query.execution_options(timeout=ctx.sql.timeout_secs)
        data = (await ctx.sql.connection.execute(query)).all()
        return await cls._construct_list(ctx, data, **kwargs)

    @classmethod
    async def perform_any(cls, ctx: ContextData, query, **kwargs) -> List[Optional['SqlaModel']]:
        query = query.execution_options(timeout=ctx.sql.timeout_secs)
        data = (await ctx.sql.connection.execute(query)).all()
        return await cls._construct_list(ctx, data, **kwargs)

    @classmethod
    async def perform_count(cls, ctx: ContextData, query, **kwargs) -> int:
        query = query.execution_options(timeout=ctx.sql.timeout_secs)
        return await ctx.sql.connection.scalar(query)

    @classmethod
    async def perform_exists(cls, ctx: ContextData, query, **kwargs) -> bool:
        query = query.execution_options(timeout=ctx.sql.timeout_secs)
        return bool(await ctx.sql.connection.scalar(query))

    @classmethod
    async def perform_exists_by(cls, ctx: ContextData, query, **kwargs) -> bool:
        query = query.execution_options(timeout=ctx.sql.timeout_secs)
        return bool(await ctx.sql.connection.scalar(query))

    @classmethod
    async def perform_create(cls, ctx: ContextData, data: Dict[str, Any]) -> Optional['SqlaModel']:
        db_query = insert(cls, values=data).execution_options(timeout=ctx.sql.timeout_secs)
        cursor = await ctx.sql.connection.execute(db_query)
        assert cursor.rowcount == 1
        new_id = tuple(cursor.inserted_primary_key)
        db_query = cls._get_helper(new_id).execution_options(timeout=ctx.sql.timeout_secs)
        data = (await ctx.sql.connection.execute(db_query)).first()
        return await cls._construct(ctx, data)

    @classmethod
    async def perform_update(
            cls, ctx: ContextData, data: Dict[str, Any], id_value: Any) -> Optional[Dict[str, Any]]:
        if ctx.sql.engine.db_type == SqlStorageType.POSTGRES:
            db_query = cls._get_helper(id_value, query=update(cls, values=data)) \
                .returning(*[getattr(cls, key) for key in cls._column_name_map.values()],) \
                .execution_options(timeout=ctx.sql.timeout_secs, synchronize_session=False)
            row = (await ctx.sql.connection.execute(db_query)).first()

        else:
            db_query = cls._get_helper(id_value, query=update(cls, values=data)) \
                .execution_options(timeout=ctx.sql.timeout_secs, synchronize_session=False)
            cursor = await ctx.sql.connection.execute(db_query)
            if cursor.rowcount != 1:
                return None

            if not isinstance(id_value, (list, tuple, dict)):
                id_value = [id_value]

            new_id = []

            for i, c in enumerate(cls._get_id_columns()):
                field = cls._get_field_by_column(c)
                if field in data:
                    new_id.append(data[field])
                else:
                    new_id.append(id_value[i])

            if len(new_id) == 1:
                new_id = new_id[0]

            # noinspection PyUnresolvedReferences
            db_query = cls._get_helper(new_id, query=select(cls.__table__)).execution_options(timeout=ctx.sql.timeout_secs)
            row = (await ctx.sql.connection.execute(db_query)).first()

        return dict(zip(cls._column_name_map.values(), (*row,))) if row is not None else dict()

    @classmethod
    async def perform_update_by(cls, ctx: ContextData, data: Dict[str, Any], query) -> int:
        db_query = query.values(data).execution_options(timeout=ctx.sql.timeout_secs)
        cursor = await ctx.sql.connection.execute(db_query)
        return cursor.rowcount

    @classmethod
    async def perform_delete(cls, ctx: ContextData, id_value: Any) -> bool:
        db_query = cls._get_helper(id_value, query=delete(cls)).execution_options(timeout=ctx.sql.timeout_secs)
        cursor = await ctx.sql.connection.execute(db_query)
        await cls._unregister_indices(ctx, [id_value])
        return 1 == cursor.rowcount

    @classmethod
    async def perform_delete_by(cls, ctx: ContextData, query) -> int:
        db_query = query.execution_options(timeout=ctx.sql.timeout_secs)
        cursor = await ctx.sql.connection.execute(db_query)
        return cursor.rowcount

    async def perform_save(
        self, ctx: ContextData, data: Dict[str, Any], updated_fields: Set[str], **kwargs) \
            -> Optional[Dict[str, Any]]:
        iss = instance_state(self)

        if iss.transient:
            ctx.sql.connection.add(self)
            await ctx.sql.connection.flush(objects=[self])
            return self.get_values()

        else:
            data = {
                k: v for k, v in self.prepare_for_update(data).items()
                if not updated_fields or k in updated_fields
            }
            return await self.perform_update(ctx, data, iss.identity)

    async def perform_load(self, ctx: ContextData, query, field_names: List[str] = None) -> bool:
        query = query.execution_options(timeout=ctx.sql.timeout_secs)

        if row := (await ctx.sql.connection.execute(query)).first():
            await type(self)._construct(ctx, row, self, set(field_names) if field_names else None)
            return True
        return False

    @classmethod
    async def perform_save_all(cls, ctx: ContextData, objects: List['SqlaModel'], **kwargs) -> bool:
        def save_all_impl(session):
            session.bulk_save_objects(objects)

        for obj in objects:
            ctx.sql.connection.add(obj)

        await ctx.sql.connection.run_sync(save_all_impl)
        await ctx.sql.connection.flush(objects=objects)
        return True
