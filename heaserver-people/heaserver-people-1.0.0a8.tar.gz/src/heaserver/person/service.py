"""
The HEA Person Microservice provides ...
"""

from heaserver.service import response
from heaserver.service.runner import init_cmd_line, routes, start, web
from heaserver.service.db import mongo, mongoservicelib
from heaserver.service.wstl import builder_factory, action
from heaobject.person import Person

MONGODB_PERSON_COLLECTION = 'people'

@routes.get('/ping')
async def ping(request: web.Request) -> web.Response:
    """
    For testing whether the service is up.

    :param request: the HTTP request.
    :return: Always returns status code 200.
    """
    return response.status_ok(None)


@routes.get('/people/{id}')
@action(name='heaserver-people-person-get-properties', rel='hea-properties')
@action(name='heaserver-people-person-open', rel='hea-opener', path='/people/{id}/opener')
@action(name='heaserver-people-person-duplicate', rel='hea-duplicator', path='/people/{id}/duplicator')
async def get_person(request: web.Request) -> web.Response:
    """
    Gets the person with the specified id.
    :param request: the HTTP request.
    :return: the requested person or Not Found.
    ---
    summary: A specific person.
    tags:
        - heaserver-people-get-person
    parameters:
        - $ref: '#/components/parameters/id'
    responses:
      '200':
        $ref: '#/components/responses/200'
      '404':
        $ref: '#/components/responses/404'
    """
    return await mongoservicelib.get(request, MONGODB_PERSON_COLLECTION)


@routes.get('/people/byname/{name}')
async def get_person_by_name(request: web.Request) -> web.Response:
    """
    Gets the person with the specified id.
    :param request: the HTTP request.
    :return: the requested person or Not Found.
    ---
    summary: A specific person, by name.
    tags:
        - heaserver-people-get-person-by-name
    parameters:
        - $ref: '#/components/parameters/name'
    responses:
      '200':
        $ref: '#/components/responses/200'
      '404':
        $ref: '#/components/responses/404'
    """
    return await mongoservicelib.get_by_name(request, MONGODB_PERSON_COLLECTION)


@routes.get('/people')
@routes.get('/people/')
@action(name='heaserver-people-person-get-properties', rel='hea-properties')
@action(name='heaserver-people-person-open', rel='hea-opener', path='/people/{id}/opener')
@action(name='heaserver-people-person-duplicate', rel='hea-duplicator', path='/people/{id}/duplicator')
async def get_all_persons(request: web.Request) -> web.Response:
    """
    Gets all persons.
    :param request: the HTTP request.
    :return: all persons.
    ---
    summary: All persons.
    tags:
        - heaserver-people-get-all-persons
    responses:
      '200':
        $ref: '#/components/responses/200'
    """
    return await mongoservicelib.get_all(request, MONGODB_PERSON_COLLECTION)


@routes.get('/people/{id}/duplicator')
@action(name='heaserver-people-person-duplicate-form')
async def get_person_duplicate_form(request: web.Request) -> web.Response:
    """
    Gets a form template for duplicating the requested person.

    :param request: the HTTP request. Required.
    :return: the requested form, or Not Found if the requested person was not found.
    """
    return await mongoservicelib.get(request, MONGODB_PERSON_COLLECTION)


@routes.post('/people/duplicator')
async def post_person_duplicator(request: web.Request) -> web.Response:
    """
    Posts the provided person for duplication.
    :param request: the HTTP request.
    :return: a Response object with a status of Created and the object's URI in the Location header.
    """
    return await mongoservicelib.post(request, MONGODB_PERSON_COLLECTION, Person)


@routes.post('/people')
@routes.post('/people/')
async def post_person(request: web.Request) -> web.Response:
    """
    Posts the provided person.
    :param request: the HTTP request.
    :return: a Response object with a status of Created and the object's URI in the Location header.
    ---
    summary: Person creation
    tags:
        - heaserver-people-post-person
    requestBody:
      description: A new person object.
      required: true
      content:
        application/vnd.collection+json:
          schema:
            type: object
          examples:
            example:
              summary: Person example
              value: {
                "template": {
                  "data": [{
                    "name": "created",
                    "value": null
                  },
                  {
                    "name": "derived_by",
                    "value": null
                  },
                  {
                    "name": "derived_from",
                    "value": []
                  },
                  {
                    "name": "description",
                    "value": null
                  },
                  {
                    "name": "display_name",
                    "value": "Reximus Texamus"
                  },
                  {
                    "name": "invites",
                    "value": []
                  },
                  {
                    "name": "modified",
                    "value": null
                  },
                  {
                    "name": "name",
                    "value": "reximus"
                  },
                  {
                    "name": "owner",
                    "value": "system|none"
                  },
                  {
                    "name": "shares",
                    "value": []
                  },
                  {
                    "name": "source",
                    "value": null
                  },
                  {
                    "name": "first_name",
                    "value": "Reximus"
                  },
                  {
                    "name": "last_name",
                    "value": "Texamus"
                  },
                  {
                    "name": "type",
                    "value": "heaobject.person.Person"
                  },
                  {
                    "name": "version",
                    "value": null
                  }
                  ]
                }
              }
        application/json:
          schema:
            type: object
          examples:
            example:
              summary: Person example
              value: {
                "created": null,
                "derived_by": null,
                "derived_from": [],
                "description": null,
                "display_name": "Reximus Texamus",
                "invited": [],
                "modified": null,
                "name": "reximus",
                "owner": "system|none",
                "shares": [],
                "source": null,
                "first_name": "Reximus",
                "last_name": "Texamus",
                "type": "heaobject.person.Person",
                "version": null,
              }
    responses:
      '201':
        $ref: '#/components/responses/201'
      '400':
        $ref: '#/components/responses/400'
      '404':
        $ref: '#/components/responses/404'
    """
    return await mongoservicelib.post(request, MONGODB_PERSON_COLLECTION, Person)


@routes.put('/people/{id}')
async def put_person(request: web.Request) -> web.Response:
    """
    Updates the person with the specified id.
    :param request: the HTTP request.
    :return: a Response object with a status of No Content or Not Found.
    ---
    summary: Person updates
    tags:
        - heaserver-people-put-person
    parameters:
        - $ref: '#/components/parameters/id'
    requestBody:
      description: An updated person object.
      required: true
      content:
        application/vnd.collection+json:
          schema:
            type: object
          examples:
            example:
              summary: Person example
              value: {
                "template": {
                  "data": [
                  {
                    "name": "id",
                    "value": "666f6f2d6261722d71757578"
                  },
                  {
                    "name": "created",
                    "value": null
                  },
                  {
                    "name": "derived_by",
                    "value": null
                  },
                  {
                    "name": "derived_from",
                    "value": []
                  },
                  {
                    "name": "description",
                    "value": "The great leader of /dev/full, Reximus Maximus"
                  },
                  {
                    "name": "display_name",
                    "value": "Reximus Maximus"
                  },
                  {
                    "name": "invites",
                    "value": []
                  },
                  {
                    "name": "modified",
                    "value": null
                  },
                  {
                    "name": "name",
                    "value": "reximus"
                  },
                  {
                    "name": "owner",
                    "value": "system|none"
                  },
                  {
                    "name": "shares",
                    "value": []
                  },
                  {
                    "name": "source",
                    "value": null
                  },
                  {
                    "name": "first_name",
                    "value": "Reximus"
                  },
                  {
                    "name": "last_name",
                    "value": "Maximus"
                  },
                  {
                    "name": "type",
                    "value": "heaobject.person.Person"
                  },
                  {
                    "name": "version",
                    "value": null
                  }
                  ]
                }
              }
        application/json:
          schema:
            type: object
          examples:
            example:
              summary: Person example
              value: {
                "id": "666f6f2d6261722d71757578",
                "created": null,
                "derived_by": null,
                "derived_from": [],
                "description": "The great leader of /dev/full, Reximus Maximus",
                "display_name": "Reximus Maximus",
                "invited": [],
                "modified": null,
                "name": "reximus",
                "owner": "system|none",
                "shares": [],
                "source": null,
                "first_name": "Reximus",
                "last_name": "Maximus",
                "type": "heaobject.person.Person",
                "version": null,
              }
    responses:
      '204':
        $ref: '#/components/responses/204'
      '400':
        $ref: '#/components/responses/400'
      '404':
        $ref: '#/components/responses/404'
    """
    return await mongoservicelib.put(request, MONGODB_PERSON_COLLECTION, Person)


@routes.delete('/people/{id}')
async def delete_person(request: web.Request) -> web.Response:
    """
    Deletes the person with the specified id.
    :param request: the HTTP request.
    :return: No Content or Not Found.
    ---
    summary: Person deletion
    tags:
        - heaserver-people-delete-person
    parameters:
        - $ref: '#/components/parameters/id'
    responses:
      '204':
        $ref: '#/components/responses/204'
      '404':
        $ref: '#/components/responses/404'
    """
    return await mongoservicelib.delete(request, MONGODB_PERSON_COLLECTION)


def main() -> None:
    config = init_cmd_line(description='A microservice designed to provide CRUD operations for the Person HEA object type',
                           default_port=8080)
    start(db=mongo.MongoManager, wstl_builder_factory=builder_factory(__package__), config=config)
