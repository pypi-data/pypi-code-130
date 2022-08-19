""" Python client for Flair OAuth2 API """
from __future__ import annotations

from typing import Any

import asyncio
from aiohttp import ClientResponse, ClientSession
from aiohttp.client_exceptions import ContentTypeError

from datetime import datetime, timedelta

from .constants import (ACCEPT, AUTH_URL, BASE_URL, CLIENT_ID,
                       CLIENT_SECRET, CONTENT_ENCODED, CONTENT_JSON,
                       CREATED, FORBIDDEN, GRANT_TYPE, HVACS_URL,
                       INVALID_CLIENT, PUCKS_URL, ROOMS_URL, SCOPES,
                       STRUCTURES_URL, THERMOSTATS_URL, TIMEOUT,
                       UNPROC_ENTITY, USERS_URL, VENTS_URL, ZONES_URL,)

from .exceptions import FlairError, FlairAuthError

from .model import (FlairData, HVACUnit, HVACUnits, Puck, Pucks, Room,
                   Rooms, Schedule, Structure, Structures, Thermostat,
                   Thermostats, User, Users, Vent, Vents, Zone, Zones,)


class FlairClient:
    """ Flair Client """

    def __init__(
            self, client_id: str, client_secret: str,
            session: ClientSession | None = None,
            timeout: int = TIMEOUT
    ) -> None:
        """
        client_id: OAuth 2.0 client_id provided by Flair
        client_secret: OAuth 2.0 client_secret provided by Flair
        session: aiohttp.ClientSession or None to create a new session
        """
        self.client_id: str = client_id
        self.client_secret: str = client_secret
        self._session = session if session else ClientSession()
        self.token: str | None = None
        self.token_expiration: datetime | None = None
        self.current_dt: datetime | None = None
        self.timeout: int = timeout


    async def get_token(self) -> None:
        """ Get OAuth2 token using client credentials """

        headers = {
            "content-type": CONTENT_ENCODED
        }

        data = {
            CLIENT_ID: self.client_id,
            CLIENT_SECRET: self.client_secret,
            "scope": SCOPES,
            "grant_type": GRANT_TYPE
        }

        response = await self._post(AUTH_URL, headers, data)
        self.token = response['access_token']
        self.token_expiration = datetime.now() + timedelta(seconds=response['expires_in'])


    async def check_token(self) -> None:
        """ Check to see if there is a valid token or if token is about to expire """

        self.current_dt = datetime.now()
        if (self.token or self.token_expiration) is None:
            await self.get_token()
        elif (self.token_expiration-self.current_dt).total_seconds() < 3600:
            await self.get_token()
        else:
            return None


    async def get_users(self) -> Users:
        """ Get all users information """

        fetched_users = await self._get(USERS_URL)
        users: dict[str, User] = {}
        if fetched_users['data']:
            for user in fetched_users['data']:
                users[user['id']] = User(
                    id=user['id'],
                    attributes=user['attributes'],
                    relationships=user['relationships'],
                )
        return Users(users=users)


    async def get_user(self, user_id: str) -> User:
        """ Get a single user """

        url = f'{USERS_URL}/{user_id}'
        user = await self._get(url)
        return User(
            id=user['data']['id'],
            attributes=user['data']['attributes'],
            relationships=user['data']['relationships'],
        )


    async def get_structures(self) -> Structures:
        """ Get all structures """

        fetched_structures = await self._get(STRUCTURES_URL)
        structures: dict[str, Structure] = {}
        if fetched_structures['data']:
            for structure in fetched_structures['data']:
                if structure['attributes'].get('setup-complete'):
                    structures[structure['id']] = Structure(
                        id=structure['id'],
                        attributes=structure['attributes'],
                        relationships=structure['relationships'],
                    )
        return Structures(structures=structures)


    async def get_structure(self, structure_id: str) -> Structure:
        """ Get a single structure """

        url = f'{STRUCTURES_URL}/{structure_id}'
        structure = await self._get(url)
        return Structure(
            id=structure['data']['id'],
            attributes=structure['data']['attributes'],
            relationships=structure['data']['relationships'],
        )


    async def get_rooms(self) -> Rooms:
        """ Get all rooms """

        fetched_rooms = await self._get(ROOMS_URL)
        rooms: dict[str, Room] = {}
        if fetched_rooms['data']:
            for room in fetched_rooms['data']:
                rooms[room['id']] = Room(
                        id=room['id'],
                        attributes=room['attributes'],
                        relationships=room['relationships'],
                    )
        return Rooms(rooms=rooms)


    async def get_room(self, room_id: str) -> Room:
        """ Get a single room """

        url = f'{ROOMS_URL}/{room_id}'
        room = await self._get(url)
        return Room(
            id=room['data']['id'],
            attributes=room['data']['attributes'],
            relationships=room['data']['relationships'],
        )


    async def get_pucks(self) -> Pucks:
        """ Get all pucks """

        fetched_pucks = await self._get(PUCKS_URL)
        pucks: dict[str, Puck] = {}
        if fetched_pucks['data']:
            for puck in fetched_pucks['data']:
                pucks[puck['id']] = Puck(
                        id=puck['id'],
                        attributes=puck['attributes'],
                        relationships=puck['relationships'],
                    )
        return Pucks(pucks=pucks)


    async def get_puck(self, puck_id: str) -> Puck:
        """ Get a single puck """

        url = f'{PUCKS_URL}/{puck_id}'
        puck = await self._get(url)
        return Puck(
            id=puck['data']['id'],
            attributes=puck['data']['attributes'],
            relationships=puck['data']['relationships'],
        )


    async def get_vents(self) -> Vents:
        """ Get all vents """

        fetched_vents = await self._get(VENTS_URL)
        vents: dict[str, Vent] = {}
        if fetched_vents['data']:
            for vent in fetched_vents['data']:
                vents[vent['id']] = Vent(
                        id=vent['id'],
                        attributes=vent['attributes'],
                        relationships=vent['relationships'],
                    )
        return Vents(vents=vents)


    async def get_vent(self, vent_id: str) -> Vent:
        """ Get a single vent """

        url = f'{VENTS_URL}/{vent_id}'
        vent = await self._get(url)
        return Vent(
            id=vent['data']['id'],
            attributes=vent['data']['attributes'],
            relationships=vent['data']['relationships'],
        )


    async def get_thermostats(self) -> Thermostats:
        """ Get all thermostats """

        fetched_thermostats = await self._get(THERMOSTATS_URL)
        thermostats: dict[str, Thermostat] = {}
        if fetched_thermostats['data']:
            for thermostat in fetched_thermostats['data']:
                thermostats[thermostat['id']] = Thermostat(
                        id=thermostat['id'],
                        attributes=thermostat['attributes'],
                        relationships=thermostat['relationships'],
                    )
        return Thermostats(thermostats=thermostats)


    async def get_thermostat(self, thermostat_id: str) -> Thermostat:
        """ Get a single Thermostat """

        url = f'{THERMOSTATS_URL}/{thermostat_id}'
        thermostat = await self._get(url)
        return Thermostat(
            id=thermostat['data']['id'],
            attributes=thermostat['data']['attributes'],
            relationships=thermostat['data']['relationships'],
        )


    async def get_hvac_units(self) -> HVACUnits:
        """ Get all HVAC units """

        fetched_hvacs = await self._get(HVACS_URL)
        hvacs: dict[str, HVACUnit] = {}
        if fetched_hvacs['data']:
            for hvac in fetched_hvacs['data']:
                if hvac['attributes'].get('model-id') is not None:
                    hvacs[hvac['id']] = HVACUnit(
                            id=hvac['id'],
                            attributes=hvac['attributes'],
                            relationships=hvac['relationships'],
                        )
        return HVACUnits(hvacs=hvacs)


    async def get_hvac_unit(self, hvac_id: str) -> HVACUnit:
        """ Get a single HVAC unit """

        url = f'{HVACS_URL}/{hvac_id}'
        hvac = await self._get(url)
        return HVACUnit(
            id=hvac['data']['id'],
            attributes=hvac['data']['attributes'],
            relationships=hvac['data']['relationships'],
        )


    async def get_zones(self) -> Zones:
        """ Get all zones """

        fetched_zones = await self._get(ZONES_URL)
        zones: dict[str, Zone] = {}
        if fetched_zones['data']:
            for zone in fetched_zones['data']:
                zones[zone['id']] = Zone(
                        id=zone['id'],
                        attributes=zone['attributes'],
                        relationships=zone['relationships'],
                    )
        return Zones(zones=zones)


    async def get_zone(self, zone_id: str) -> Zone:
        """ Get a single zone """

        url = f'{ZONES_URL}/{zone_id}'
        zone = await self._get(url)
        return Zone(
            id=zone['data']['id'],
            attributes=zone['data']['attributes'],
            relationships=zone['data']['relationships'],
        )


    async def get_flair_data(self) -> FlairData:
        """
        Return dataclass with rooms, vents, pucks, thermostats, HVAC units,
        zones, and schedules nested within their associated structure.
        """

        users_data: dict[str, User] = {}
        response = await self.get_users()
        if response.users:
            for user in response.users:
                users_data[response.users[user].id] = User(
                    id=response.users[user].id,
                    attributes=response.users[user].attributes,
                    relationships=response.users[user].relationships,
                )

        structures_data: dict[str, Structure] = {}
        rooms_data: dict[str, Room] = {}
        pucks_data: dict[str, Puck] = {}
        vents_data: dict[str, Vent] = {}
        thermostats_data: dict[str, Thermostat] = {}
        hvac_units_data: dict[str, HVACUnit] = {}
        zones_data: dict[str, Zone] = {}
        schedules_data: dict[str, Schedule] = {}

        response = await self.get_structures()
        if response.structures:
            for structure in response.structures:
                """ Fetch related items  """
                related_entities = await self.fetch_all_structure_relations(response.structures[structure])

                """ Related rooms """
                if related_entities[0]:
                    for room in related_entities[0]:
                        rooms_data[room['id']] = Room(
                            id=room['id'],
                            attributes=room['attributes'],
                            relationships=room['relationships'],
                        )

                """ Related pucks """
                if related_entities[1]:
                    for puck in related_entities[1]:
                        puck_object = Puck(
                            id=puck['id'],
                            attributes=puck['attributes'],
                            relationships=puck['relationships'],
                            current_reading=None
                        )
                        get_reading = await self.get_related(puck_object, 'current-reading')
                        attributes = get_reading['attributes']
                        setattr(puck_object, 'current_reading', attributes)
                        pucks_data[puck['id']] = puck_object

                """ Related vents """
                if related_entities[2]:
                    for vent in related_entities[2]:
                        vent_object = Vent(
                            id=vent['id'],
                            attributes=vent['attributes'],
                            relationships=vent['relationships'],
                            current_reading=None
                        )
                        get_reading = await self.get_related(vent_object, 'current-reading')
                        attributes = get_reading['attributes']
                        setattr(vent_object, 'current_reading', attributes)
                        vents_data[vent['id']] = vent_object

                """ Related thermostats """
                if related_entities[3]:
                    for thermostat in related_entities[3]:
                        thermostats_data[thermostat['id']] = Thermostat(
                            id=thermostat['id'],
                            attributes=thermostat['attributes'],
                            relationships=thermostat['relationships'],
                        )

                """ Related HVAC units """
                if related_entities[4]:
                    for hvac_unit in related_entities[4]:
                        hvac_units_data[hvac_unit['id']] = HVACUnit(
                            id=hvac_unit['id'],
                            attributes=hvac_unit['attributes'],
                            relationships=hvac_unit['relationships'],
                        )

                """ Related zones """
                if related_entities[5]:
                    for zone in related_entities[5]:
                        zones_data[zone['id']] = Zone(
                            id=zone['id'],
                            attributes=zone['attributes'],
                            relationships=zone['relationships'],
                        )

                """ Related schedules """
                if related_entities[6]:
                    for schedule in related_entities[6]:
                        schedules_data[schedule['id']] = Schedule(
                            id=schedule['id'],
                            attributes=schedule['attributes'],
                            relationships=schedule['relationships'],
                        )

                structures_data[response.structures[structure].id] = Structure(
                        id=response.structures[structure].id,
                        attributes=response.structures[structure].attributes,
                        relationships=response.structures[structure].relationships,
                        rooms=rooms_data,
                        pucks=pucks_data,
                        vents=vents_data,
                        thermostats=thermostats_data,
                        hvac_units=hvac_units_data,
                        zones=zones_data,
                        schedules=schedules_data,
                )
        return FlairData(users=users_data, structures=structures_data )


    async def get_related(self, object, type: str) -> list[int]:
        """ Get vents, rooms, pucks, etc. related to the object """

        link = object.relationships[type]['links']['related']
        response = await self._get(link)
        return response['data']


    async def fetch_all_structure_relations(self, object: Structure) -> list:
        """
        Parallel request are made to all related endpoints for a single structure.
        Returns a list containing rooms, pucks, vents, thermostats, HVAC units, and Zones
        related to said structure. This function is called by the get_flair_data function.
        """

        results = await asyncio.gather(*[
            self.get_related(object, 'rooms'),
            self.get_related(object, 'pucks'),
            self.get_related(object, 'vents'),
            self.get_related(object, 'thermostats'),
            self.get_related(object, 'hvac-units'),
            self.get_related(object, 'zones'),
            self.get_related(object, 'schedules')
            ],
        )
        return results


    async def create(self, resource_type: str, attributes: dict[str, Any], relationships: dict[str, Any]) -> dict[str, Any]:
        """ Create a new Flair room. Other scenarios currently untested. """

        await self.check_token()
        headers = {
            "content-type": 'application/json',
            "authorization": f'Bearer {self.token}'
        }

        request_data = {
            "data": {
                "type": resource_type,
                "attributes": attributes,
                "relationships": relationships
            }
        }
        request_url = f'/api/{resource_type}'
        return await self._post(request_url, headers, request_data)


    async def delete(self, resource_type: str, id: str) -> None:
        """ Delete a Flair room. Other scenarios currently untested. """

        request_url = f'/api/{resource_type}/{id}'
        return await self._delete(request_url)


    async def update(self, resource_type: str, id: str, attributes: dict[str, Any], relationships: dict[str, Any]) -> dict[str, Any]:
        """ Set structure mode, structure system mode, vent % open, select schedule, etc """

        request_data = {
            "data": {
                "type": resource_type,
                "attributes": attributes,
                "relationships": relationships
            }
        }
        request_url = f'/api/{resource_type}/{id}'
        return await self._patch(request_url, request_data)


    async def _create_get_header(self) -> dict[str, str]:
        """ Create header for all GET calls """

        headers = {
            "content-type": CONTENT_ENCODED,
            "accept": ACCEPT,
            "authorization": f'Bearer {self.token}'
        }
        return headers


    async def _create_json_header(self) -> dict[str, str]:
        """ Create json content-type header """

        headers = {
            "content-type": CONTENT_JSON,
            "authorization": f'Bearer {self.token}'
        }
        return headers


    async def _post(self, endpoint: str, headers: dict[str, Any], data: dict[str, Any]) -> dict[str, Any]:
        """ Make POST call to Flair servers """

        if headers['content-type'] == 'application/json':
            async with self._session.post(
                    url=f'{BASE_URL}{endpoint}', headers=headers,
                    json=data, timeout=self.timeout) as resp:
                return await self._response(resp)
        else:
            async with self._session.post(
                    url=f'{BASE_URL}{endpoint}', headers=headers,
                    data=data, timeout=self.timeout) as resp:
                return await self._response(resp)


    async def _get(self, endpoint: str, data: dict[str, Any] = {}) -> dict[str, Any]:
        """ Make GET call to Flair servers """

        await self.check_token()
        headers = await self._create_get_header()
        async with self._session.get(
                url=f'{BASE_URL}{endpoint}', headers=headers,
                data=data, timeout=self.timeout) as resp:
            return await self._response(resp)


    async def _delete(self, endpoint: str) -> None:
        """ Make DELETE call to Flair servers """

        await self.check_token()
        headers = await self._create_json_header()
        async with self._session.delete(
                url=f'{BASE_URL}{endpoint}', headers=headers,
                timeout=self.timeout) as resp:
            return await self._response(resp)


    async def _patch(self, endpoint: str, data: dict[str, Any]) -> dict[str, Any]:
        """ Make PATCH call to Flair servers """

        await self.check_token()
        headers = await self._create_json_header()
        async with self._session.patch(
                url=f'{BASE_URL}{endpoint}', headers=headers,
                json=data, timeout=self.timeout) as resp:
            return await self._response(resp)

    @staticmethod
    async def _response(resp: ClientResponse) -> dict[str, Any] | None:
        """ Check response for any errors & return original response if none """

        if resp.status == 204:
            return None
        elif resp.status == 504:
            raise FlairError(resp)
        else:
            try:
                response: dict[str, Any] = await resp.json()
                if resp.status != 200:
                    if resp.reason == CREATED:
                        return response
                    if resp.reason == FORBIDDEN:
                        raise FlairAuthError(f'{response["errors"][0]["detail"]}')
                    if resp.reason == UNPROC_ENTITY:
                        base = response['errors'][0]
                        raise FlairError(f'{base["title"]}: {base["detail"]}')
                    if 'error' in response:
                        if response['error'] == INVALID_CLIENT:
                            raise FlairAuthError('Invalid Client ID or Secret provided')
                else:
                    return response
            except ContentTypeError as cte:
                text = await resp.text()
                raise FlairError(f'Flair server response content-type is not json: {text}') from cte
            except Exception as e:
                raise FlairError(f'Flair API error: {e}') from e
