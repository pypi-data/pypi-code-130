"""Init file for Flair OAuth2 API"""


from flairaio import constants
from flairaio import exceptions
from flairaio import flair_client
from flairaio import model

from flairaio.constants import (ACCEPT, AUTH_URL, BASE_URL, CLIENT_ID,
                                CLIENT_SECRET, CONTENT_ENCODED, CONTENT_JSON,
                                CREATED, FORBIDDEN, GRANT_TYPE, HVACS_URL,
                                INVALID_CLIENT, PUCKS_URL, ROOMS_URL, SCOPES,
                                STRUCTURES_URL, THERMOSTATS_URL, TIMEOUT,
                                UNPROC_ENTITY, USERS_URL, VENTS_URL,
                                ZONES_URL,)
from flairaio.exceptions import (FlairAuthError, FlairError,)
from flairaio.flair_client import (FlairClient,)
from flairaio.model import (FlairData, HVACUnit, HVACUnits, Puck, Pucks, Room,
                            Rooms, Schedule, Structure, Structures, Thermostat,
                            Thermostats, User, Users, Vent, Vents, Zone,
                            Zones,)

__all__ = ['ACCEPT', 'AUTH_URL', 'BASE_URL', 'CLIENT_ID', 'CLIENT_SECRET',
           'CONTENT_ENCODED', 'CONTENT_JSON', 'CREATED', 'FORBIDDEN',
           'FlairAuthError', 'FlairClient', 'FlairData', 'FlairError',
           'GRANT_TYPE', 'HVACS_URL', 'HVACUnit', 'HVACUnits',
           'INVALID_CLIENT', 'PUCKS_URL', 'Puck', 'Pucks', 'ROOMS_URL', 'Room',
           'Rooms', 'SCOPES', 'STRUCTURES_URL', 'Schedule', 'Structure',
           'Structures', 'THERMOSTATS_URL', 'TIMEOUT', 'Thermostat',
           'Thermostats', 'UNPROC_ENTITY', 'USERS_URL', 'User', 'Users',
           'VENTS_URL', 'Vent', 'Vents', 'ZONES_URL', 'Zone', 'Zones',
           'constants', 'exceptions', 'flair_client', 'model']
