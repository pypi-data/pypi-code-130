import contextlib
import pickle
from builtins import property
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import timedelta
from types import ClassMethodDescriptorType, FunctionType, GetSetDescriptorType, MappingProxyType, MemberDescriptorType, \
    MethodDescriptorType, MethodType, MethodWrapperType, WrapperDescriptorType
from typing import Any, Dict, List, Optional, Set, Tuple

from pydantic.main import BaseModel as PydanticModel

from dropland.data.context import ContextData
from dropland.storages.relationship import Relationship


@dataclass
class FieldsCache:
    priv: Set[str] = field(default_factory=set)
    pub: Set[str] = field(default_factory=set)
    ser: Set[str] = field(default_factory=set)


class StorageBackend:
    @property
    def name(self) -> str:
        raise NotImplementedError


class StorageEngine:
    def __init__(self, backend: StorageBackend):
        self._backend = backend

    @property
    def backend(self):
        return self._backend

    @property
    def is_async(self):
        raise NotImplementedError

    def new_connection(self):
        raise NotImplementedError

    def start(self):
        pass

    def stop(self):
        pass

    async def async_start(self):
        pass

    async def async_stop(self):
        pass


class StorageModel:
    class Meta:
        private_fields: Set[str] = set()
        public_fields: Set[str] = set()
        serializable_fields: Set[str] = set()
        non_serializable_fields: Set[str] = set()
        _fields_cache: Dict[str, FieldsCache] = dict()
        relationships: Dict[str, Relationship] = dict()

    def get_id_value(self) -> Any:
        raise NotImplementedError

    @classmethod
    def get_engine(cls) -> StorageEngine:
        raise NotImplementedError

    @classmethod
    def has_cache(cls):
        return False

    @classmethod
    def _fields_cache_key(cls):
        return '.'.join([cls.__module__, cls.__qualname__])

    # noinspection PyProtectedMember
    @classmethod
    def _calculate_fields(cls):
        private_types = (
            type, FunctionType, MethodType, MappingProxyType,
            WrapperDescriptorType, MethodWrapperType, MethodDescriptorType,
            ClassMethodDescriptorType, GetSetDescriptorType, MemberDescriptorType
        )

        private_fields, public_fields, serializable_fields = set(), set(), set()
        relationship_keys = cls.Meta.relationships.keys()

        for field in dir(cls):
            value = getattr(cls, field)
            if isinstance(value, private_types) or field[0] == '_':
                private_fields.add(field)
            elif not isinstance(value, private_types):
                if not isinstance(value, property) and field not in relationship_keys:
                    serializable_fields.add(field)
                public_fields.add(field)

        private_fields.update(cls.Meta.private_fields)
        private_fields.difference_update(cls.Meta.public_fields)
        public_fields.update(cls.Meta.public_fields)
        public_fields.difference_update(cls.Meta.private_fields)
        serializable_fields.update(cls.Meta.serializable_fields)
        serializable_fields.difference_update(cls.Meta.non_serializable_fields)
        cls.Meta._fields_cache[cls._fields_cache_key()] = \
            FieldsCache(priv=private_fields, pub=public_fields, ser=serializable_fields)

    # noinspection PyProtectedMember
    @classmethod
    def drop_fields_cache(cls):
        key = cls._fields_cache_key()
        cls.Meta._fields_cache.pop(key, None)

    # noinspection PyProtectedMember
    @classmethod
    def get_serializable_fields(cls) -> Set[str]:
        key = cls._fields_cache_key()
        if key not in cls.Meta._fields_cache:
            cls._calculate_fields()
        return cls.Meta._fields_cache[key].ser

    # noinspection PyProtectedMember
    @classmethod
    def get_private_fields(cls) -> Set[str]:
        key = cls._fields_cache_key()
        if key not in cls.Meta._fields_cache:
            cls._calculate_fields()
        return cls.Meta._fields_cache[key].priv

    # noinspection PyProtectedMember
    @classmethod
    def get_public_fields(cls) -> Set[str]:
        key = cls._fields_cache_key()
        if key not in cls.Meta._fields_cache:
            cls._calculate_fields()
        return cls.Meta._fields_cache[key].pub

    @classmethod
    def get_fields(cls) -> Set[str]:
        return cls.get_public_fields()

    def get_values(
        self, only_fields: List[str] = None,
            exclude_fields: List[str] = None) -> Dict[str, Any]:
        public_fields = self.get_public_fields()
        only_fields = set(only_fields) if only_fields else set()
        exclude_fields = set(exclude_fields) if exclude_fields else set()

        return {
            name: getattr(self, name) for name in public_fields
            if hasattr(self, name) and (not only_fields or name in only_fields)
            and (not exclude_fields or name not in exclude_fields)
        }

    #
    # Local cache
    #

    @classmethod
    def _add_to_local_cache(cls, ctx: ContextData, instances: List['StorageModel']):
        if not hasattr(ctx, 'cache'):
            ctx.cache = defaultdict(lambda: defaultdict(dict))
        for instance in instances:
            ctx.cache[cls][instance.get_id_value()] = instance

    @classmethod
    def _get_from_local_cache(cls, ctx: ContextData, indices: List[Any]) -> List[Optional['StorageModel']]:
        if not hasattr(ctx, 'cache'):
            ctx.cache = defaultdict(lambda: defaultdict(dict))

        return [ctx.cache[cls].get(id_value) for id_value in indices]

    @classmethod
    def _drop_from_local_cache(cls, ctx: ContextData, indices: List[Any]) -> List[bool]:
        if not hasattr(ctx, 'cache'):
            ctx.cache = defaultdict(lambda: defaultdict(dict))

        return [ctx.cache[cls].pop(id_value, None) is None for id_value in indices]

    @classmethod
    def _has_in_local_cache(cls, ctx: ContextData, indices: List[Any]) -> List[bool]:
        if not hasattr(ctx, 'cache'):
            ctx.cache = defaultdict(lambda: defaultdict(dict))

        return [id_value in ctx.cache[cls] for id_value in indices]

    #
    # Retrieve operations
    #

    @classmethod
    async def get(cls, id_value: Any, **kwargs) -> Optional['StorageModel']:
        raise NotImplementedError

    async def save(self, *args, **kwargs) -> bool:
        raise NotImplementedError

    async def load(self, field_names: List[str] = None) -> bool:
        raise NotImplementedError

    @classmethod
    async def get_any(cls, indices: List[Any], **kwargs) -> List[Optional['StorageModel']]:
        raise NotImplementedError

    @classmethod
    async def save_all(cls, objects: List['StorageModel'], *args, **kwargs) -> bool:
        raise NotImplementedError

    #
    # Phases operations
    #

    def _assign(self, data: Dict[str, Any]) -> 'StorageModel':
        for k, v in data.items():
            setattr(self, k, v)
        return self

    @classmethod
    async def _construct(
        cls, _: ContextData, data: Dict[str, Any], instance: Optional['StorageModel'] = None,
            only_fields: Optional[Set[str]] = None, **kwargs) -> Optional['StorageModel']:
        if not isinstance(data, dict):
            return None

        field_data = dict() if only_fields else data
        if only_fields:
            for k, v in data.items():
                if only_fields is None or k in only_fields:
                    field_data[k] = v

        if instance:
            return instance._assign(field_data)
        else:
            if issubclass(cls, PydanticModel):
                return cls(**field_data)
            else:
                return cls()._assign(field_data)

    @classmethod
    async def _construct_list(
            cls, ctx: ContextData, objects: List[Dict[str, Any]], **kwargs) -> List['StorageModel']:
        return [await cls._construct(ctx, data, **kwargs) for data in objects if data is not None]

    @classmethod
    async def _register_instances(cls, ctx: ContextData, objects: List['StorageModel']):
        cls._add_to_local_cache(ctx, objects)

    @classmethod
    async def _unregister_indices(cls, ctx: ContextData, indices: List[Any]):
        cls._drop_from_local_cache(ctx, indices)

    @classmethod
    async def _build_rela(
        cls, ctx: ContextData, instance: 'StorageModel',
            load_fields: Optional[Set[str]] = None, **kwargs) -> Optional['StorageModel']:
        res = await cls._build_relationships(ctx, [instance], load_fields, **kwargs)
        return res[0]

    @classmethod
    async def _build_rela_list(
        cls, ctx: ContextData, objects: List['StorageModel'],
            load_fields: Optional[Set[str]] = None, **kwargs) -> List['StorageModel']:
        return await cls._build_relationships(ctx, objects, load_fields, **kwargs)

    @classmethod
    async def _build_relationships(
        cls, _: ContextData, objects: List['StorageModel'],
            load_fields: Optional[Set[str]] = None, **kwargs) -> List['StorageModel']:
        deps_ids: Dict[str, Dict[Any, Set[Any]]] = defaultdict(lambda: defaultdict(set))
        deps_values: Dict[str, Dict[Any, Any]] = defaultdict(dict)
        rela_map = cls.Meta.relationships.items()
        load_all = load_fields is None

        for instance in objects:
            if instance is None:
                continue

            for dep_key, relationship in rela_map:
                if not load_all and dep_key not in load_fields:
                    continue

                dep_key_value = relationship.get_key(instance)

                if relationship.single:
                    dep_key_value = [dep_key_value]

                deps_ids[dep_key][instance.get_id_value()].update(set(dep_key_value))

        for dep_key, relationship in rela_map:
            if not load_all and dep_key not in load_fields:
                continue

            dep_keys = set()
            for v in deps_ids[dep_key].values():
                dep_keys.update(v)
            model_class = relationship.get_model()
            dep_values = await model_class.get_any(list(dep_keys), **kwargs)

            for k, v in zip(dep_keys, dep_values):
                deps_values[dep_key][k] = v

        for instance in objects:
            if instance is None:
                continue

            for dep_key, relationship in rela_map:
                if not load_all and dep_key not in load_fields:
                    continue

                dep_key_values = list(deps_ids[dep_key][instance.get_id_value()])

                if relationship.single:
                    dep_key_value = dep_key_values[0] if len(dep_key_values) > 0 else dep_key_values
                    dep_value = deps_values[dep_key][dep_key_value]
                    setattr(instance, dep_key, dep_value)
                else:
                    dep_values = [deps_values[dep_key][k] for k in dep_key_values]
                    setattr(instance, dep_key, dep_values)

        return objects


class CacheModel(StorageModel):
    class Meta(StorageModel.Meta):
        cache_ttl_enable = True

    @classmethod
    def get_model_cache_key(cls) -> str:
        raise NotImplementedError

    @classmethod
    def get_cache_id(cls, id_value: Any) -> str:
        return str(id_value)

    @classmethod
    def get_cache_key(cls, id_value: Any) -> str:
        return f'{cls.get_model_cache_key()}:{cls.get_cache_id(id_value)}'

    def get_id_value(self) -> Any:
        raise NotImplementedError

    def get_serializable_values(self, only_fields: List[str] = None) -> Dict[str, Any]:
        serializable_fields = self.get_serializable_fields()
        only_fields = set(only_fields) if only_fields else set()

        return {
            name: getattr(self, name) for name in serializable_fields
            if hasattr(self, name) and (not only_fields or name in only_fields)
        }

    def serialize(self, only_fields: List[str] = None) -> bytes:
        return pickle.dumps(self.get_serializable_values(only_fields))

    @classmethod
    def deserialize(cls, data: bytes) -> Optional[Dict[str, Any]]:
        try:
            values = pickle.loads(data) if data else None
        except (pickle.UnpicklingError, ValueError, ModuleNotFoundError, MemoryError):
            return None

        return values

    @classmethod
    @contextlib.asynccontextmanager
    async def _async_connection_context(cls):
        raise NotImplementedError

    #
    # Retrieve operations
    #

    @classmethod
    async def get(cls, id_value: Any, **kwargs) -> Optional['CacheModel']:
        no_cache = kwargs.pop('no_cache', False)
        async with cls._async_connection_context() as ctx:
            if not no_cache:
                if instance := cls._get_from_local_cache(ctx, [id_value])[0]:
                    return instance
            exists, data = await cls._load_one(ctx, cls.get_cache_key(id_value), **kwargs)
            if exists:
                if instance := await cls._construct(ctx, data, **kwargs):
                    await cls._register_instances(ctx, [instance])
                    return await cls._build_rela(ctx, instance, **kwargs)
        return None

    @classmethod
    async def get_any(cls, indices: List[Any], **kwargs) -> List[Optional['CacheModel']]:
        no_cache = kwargs.pop('no_cache', False)
        async with cls._async_connection_context() as ctx:
            if not no_cache:
                objects = cls._get_from_local_cache(ctx, indices)
            else:
                objects = [None] * len(indices)
            non_cached_indices = [i for o, i in zip(objects, indices) if o is None]
            if non_cached_indices:
                data = await cls._load_many(ctx, non_cached_indices, **kwargs)
                if non_cached := await cls._construct_list(ctx, data, **kwargs):
                    await cls._register_instances(ctx, non_cached)
                    objects += await cls._build_rela_list(ctx, non_cached, **kwargs)

        objects = {obj.get_id_value(): obj for obj in objects if obj is not None}
        return [objects[id_value] if id_value in objects else None for id_value in indices]

    async def save(self, exp: Optional[timedelta] = None, **kwargs) -> bool:
        async with self._async_connection_context() as ctx:
            if not exp:
                await self._register_instances(ctx, [self])
            return await self._cache_one(ctx, self, exp=exp, **kwargs)

    async def load(self, field_names: List[str] = None) -> bool:
        field_names = set(field_names) if field_names else set()

        async with self._async_connection_context() as ctx:
            exists, data = await self._load_one(ctx, self.get_cache_key(self.get_id_value()))
            if exists:
                await type(self)._construct(ctx, data, self, field_names)
                await type(self)._build_rela(ctx, self, load_fields=field_names)
                return True
        return False

    @classmethod
    async def save_all(cls, objects: List['CacheModel'], exp: timedelta = None, **kwargs) -> bool:
        async with cls._async_connection_context() as ctx:
            if res := await cls._cache_many(ctx, objects, exp, **kwargs):
                if not exp:
                    await cls._register_instances(ctx, objects)
            return res

    async def drop(self) -> bool:
        async with self._async_connection_context() as ctx:
            id_value = self.get_id_value()
            await self._unregister_indices(ctx, [id_value])
            return await self._drop_one(ctx, self.get_cache_key(id_value))

    @classmethod
    async def drop_all(cls, indices: List[Any] = None) -> bool:
        async with cls._async_connection_context() as ctx:
            await cls._unregister_indices(ctx, indices)
            return await cls._drop_many(ctx, indices)

    @classmethod
    async def exists(cls, id_value: Any, no_cache: bool = False) -> bool:
        async with cls._async_connection_context() as ctx:
            if not no_cache and cls._has_in_local_cache(ctx, [id_value])[0]:
                return True
            return await cls._exists(ctx, cls.get_cache_key(id_value))

    @classmethod
    async def scan(cls, match: str, count: int = None, **kwargs) -> Tuple[str, Optional['CacheModel']]:
        async with cls._async_connection_context() as ctx:
            async for k, data in cls._scan(ctx, cls.get_model_cache_key(), match, count):
                if data is None:
                    yield k, None
                elif instance := await cls._construct(ctx, data, **kwargs):
                    await cls._register_instances(ctx, [instance])
                    yield k, await cls._build_rela(ctx, instance, **kwargs)
                else:
                    yield k, None

    @classmethod
    async def _cache_one(
        cls, ctx: ContextData, instance: Optional['CacheModel'] = None,
            id_value: Optional[Any] = None, data: Optional[Dict[str, Any]] = None,
            exp: Optional[timedelta] = None, **kwargs) -> bool:
        raise NotImplementedError

    @classmethod
    async def _cache_many(
            cls, ctx: ContextData, objects: List['CacheModel'], exp: timedelta = None, **kwargs) -> bool:
        raise NotImplementedError

    @classmethod
    async def _load_one(
            cls, ctx: ContextData, cache_key: str, **kwargs) -> Tuple[bool, Optional[Dict[str, Any]]]:
        raise NotImplementedError

    @classmethod
    async def _load_many(
            cls, ctx: ContextData, indices: List[Any], **kwargs) -> List[Optional[Dict[str, Any]]]:
        raise NotImplementedError

    @classmethod
    async def _drop_one(cls, ctx: ContextData, cache_key: str) -> bool:
        raise NotImplementedError

    @classmethod
    async def _drop_many(cls, ctx: ContextData, indices: List[Any] = None) -> bool:
        raise NotImplementedError

    @classmethod
    async def _exists(cls, ctx: ContextData, cache_key: str) -> bool:
        raise NotImplementedError

    @classmethod
    @contextlib.asynccontextmanager
    async def _scan(cls, ctx: ContextData, cache_key: str = None,
                    match: str = None, count: int = None) -> Tuple[str, Optional[Dict[str, Any]]]:
        raise NotImplementedError
