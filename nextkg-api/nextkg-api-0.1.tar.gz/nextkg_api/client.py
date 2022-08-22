import json
from typing import List, Union, Tuple, Optional

from requests_toolbelt.sessions import BaseUrlSession

from nextkg_api.data_models import Entity, Neighbor


class NextKGClient:
    def __init__(self, host: str, kg_id: str):
        if '://' not in host:
            endpoint = f'http://{host}'
        else:
            endpoint = host
        if not endpoint.endswith('/'):
            endpoint += '/'
        self.endpoint = endpoint
        self.session = BaseUrlSession(endpoint)
        self.kg_id = kg_id

    def ping(self, raise_error=False) -> bool:
        try:
            resp = self.session.get('/health')
            resp.raise_for_status()
        except Exception:
            if raise_error:
                raise
            return False
        return True

    def link_entity(self, entity: Union[dict, Entity], strict: bool = False) -> List[Entity]:
        """
        实体链指

        :param entity:
        :param strict:
        :return:
        """
        if isinstance(entity, Entity):
            entity = json.loads(entity.json())
        resp = self.session.post(
            '/api/entities/link',
            json=dict(
                entity=entity,
                strict=strict,
            ),
            params=dict(
                kg_id=self.kg_id,
            )
        )
        resp.raise_for_status()
        data = resp.json()['data']
        return [Entity(**i) for i in data]

    def update_entity(self, entity_id: str, entity: Union[dict, Entity], refresh: bool = False) -> Entity:
        """
        覆盖式更新实体

        :param entity_id:
        :param entity:
        :param refresh:
        :return:
        """
        if isinstance(entity, Entity):
            entity = json.loads(entity.json())
        resp = self.session.put(
            f'/api/entities/{entity_id}',
            json=dict(
                entity=entity,
                refresh=refresh,
            ),
            params=dict(
                kg_id=self.kg_id,
                entity_id=entity_id,
            )
        )
        resp.raise_for_status()
        data = resp.json()['data']
        return Entity(**data)

    def partial_update_entity(self, entity_id: str, entity: Union[dict, Entity], refresh: bool = False) -> dict:
        """
        局部更新实体

        :param entity_id:
        :param entity:
        :param refresh:
        :return:
        """

        if isinstance(entity, Entity):
            entity = json.loads(entity.json())
        resp = self.session.post(
            f'/api/entities/{entity_id}/update',
            json=dict(
                entity=entity,
                refresh=refresh,
            ),
            params=dict(
                kg_id=self.kg_id,
                entity_id=entity_id,
            )
        )
        resp.raise_for_status()
        data = resp.json()
        return data

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """
        根据id获取实体

        :param entity_id:
        :return:
        """

        resp = self.session.get(
            f'/api/entities/{entity_id}',
            params=dict(
                kg_id=self.kg_id,
                entity_id=entity_id,
            )
        )
        if resp.status_code == 404:
            return
        resp.raise_for_status()
        data = resp.json()['data']
        return Entity(**data)

    def get_entity_by_origin_id(self, origin_id: str) -> Union[None, Entity, List[Entity]]:
        """
        根据origin id获取实体

        :param origin_id:
        :return:
        """

        body = {
            "query": {
                "match_phrase": {
                    "meta.origin_id": origin_id,
                }
            }
        }
        entities = self._search_by_dsl(body=body)
        if len(entities) == 0:
            return
        if len(entities) == 1:
            return entities[0]
        return entities

    def add_entity(self, entity: Union[dict, Entity], refresh: bool = False) -> Entity:
        """
        添加实体

        :param entity:
        :param refresh:
        :return:
        """

        if isinstance(entity, Entity):
            entity = json.loads(entity.json())
        resp = self.session.post(
            '/api/entities',
            json=dict(
                entity=entity,
                refresh=refresh,
            ),
            params=dict(
                kg_id=self.kg_id,
            )
        )
        resp.raise_for_status()
        data = resp.json()['data']
        return Entity(**data)

    def add_relation(self, start_entity_id: str, end_entity_id: str, relation_type: str):
        """
        添加关系

        :param start_entity_id:
        :param end_entity_id:
        :param relation_type:
        :return:
        """

        resp = self.session.post(
            '/api/relations',
            json=dict(
                start_entity_id=start_entity_id,
                end_entity_id=end_entity_id,
                relation_type=relation_type,
            ),
            params=dict(
                kg_id=self.kg_id,
            )
        )
        resp.raise_for_status()

    def get_neighbors(self, entity_id: str) -> Tuple[List[Neighbor], List[Neighbor]]:
        """
        获取邻居

        :param entity_id:
        :return:
        """

        resp = self.session.post(
            '/api/entities/find-neighbors',
            params=dict(
                kg_id=self.kg_id,
                entity_id=entity_id,
            )
        )
        resp.raise_for_status()
        data = resp.json()['data']
        children = [Neighbor(**i) for i in data['children']]
        parents = [Neighbor(**i) for i in data['parents']]
        return children, parents

    def _search_by_dsl(self, **params):
        resp = self.session.post(
            '/api/entities/search/by-dsl',
            params=dict(
                kg_id=self.kg_id,
            ),
            json=dict(
                params=params,
            )
        )
        resp.raise_for_status()
        data = resp.json()['data']
        return [Entity(**d) for d in data]

    def remove_entity(self, entity_id: str, refresh: bool = False):
        resp = self.session.delete(
            f'/api/entities/{entity_id}',
            params=dict(
                kg_id=self.kg_id,
                refresh=1 if refresh else 0,
            )
        )
        resp.raise_for_status()
