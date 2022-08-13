from typing import List, Literal, Union

import toml
from pydantic import BaseModel, validator, root_validator

from think_dashboard_agent.exceptions import ConfigParseException


class BaseInstance(BaseModel):
    key: str
    name: str = None
    type: Literal['database', 'redis', 'elasticsearch', 'ssl']
    host: str
    port: int


class DatabaseInstance(BaseInstance):
    username: str
    password: str
    database: str
    port: int = 5432


class RedisInstance(BaseInstance):
    password: str = None
    db: int = 1


class ElasticSearchInstance(BaseInstance):
    username: str
    password: str

    @validator('host')
    def validate_host(cls, v):
        if not v.startswith('http'):
            v = 'https://{}'.format(v)
        return v


class SSLInstance(BaseInstance):
    port: int = 443

    @validator('host')
    def validate_host(cls, v):
        if v.startswith('http://'):
            v = v.replace('http://', '')
        elif v.startswith('https://'):
            v = v.replace('https://', '')
        return v


INSTANCE_TYPES = {
    'database': DatabaseInstance,
    'redis': RedisInstance,
    'elasticsearch': ElasticSearchInstance,
    'ssl': SSLInstance,
}
ALLOWED_TYPES = list(INSTANCE_TYPES.keys())


class Config(BaseModel):
    api_key: str
    dashboard_url: str
    server_name: str
    instances: List[BaseInstance]

    @root_validator(pre=True)
    def validate_instances(cls, values: dict):
        assert 'instance' in values, 'instance not found in config'
        _instances_config = values.pop('instance')
        instances = []
        _keys = set()
        for i in _instances_config:
            if 'type' not in i:
                raise ConfigParseException('Instance must have a type')

            _instance_type = INSTANCE_TYPES[i['type']]
            instance = _instance_type(**i)
            instances.append(instance)
            _keys.add(instance.key)

        if len(_keys) != len(instances):
            raise ConfigParseException('All instances must have a unique key')
        values['instances'] = instances
        return values

    @classmethod
    def from_file(cls, file_path: str) -> 'Config':
        with open(file_path, 'r') as f:
            return cls(**toml.load(f))


class InstanceCheckResult(BaseModel):
    status: int = 200
    data: Union[Union[Union[dict, list], str], None] = None
    error: str = None
