"""
The HEA Server Activity Microservice provides ...
"""

from heaserver.service import response, appproperty
from heaserver.service.runner import init_cmd_line, routes, start, web
from heaserver.service.db import mongo, mongoservicelib
from heaserver.service.wstl import builder_factory, action
from heaobject.activity import Activity

MONGODB_ACTIVITY_COLLECTION = 'activity'


@routes.get('/activity/{id}')
@action('heaserver-activity-activity-get-properties', rel='hea-properties')
@action('heaserver-activity-activity-open', rel='hea-opener', path='/activity/{id}/opener')
@action('heaserver-activity-activity-duplicate', rel='hea-duplicator', path='/activity/{id}/duplicator')
async def get_activity(request: web.Request) -> web.Response:
    """
    Gets the activity with the specified id.
    :param request: the HTTP request.
    :return: the requested activity or Not Found.
    ---
    summary: A specific activity.
    tags:
        - heaserver-activity
    parameters:
        - $ref: '#/components/parameters/id'
    responses:
      '200':
        $ref: '#/components/responses/200'
      '404':
        $ref: '#/components/responses/404'
    """
    return await mongoservicelib.get(request, MONGODB_ACTIVITY_COLLECTION)


@routes.get('/activity/byname/{name}')
async def get_activity_by_name(request: web.Request) -> web.Response:
    """
    Gets the activity with the specified name.
    :param request: the HTTP request.
    :return: the requested activity or Not Found.
    ---
    summary: A specific activity, by name.
    tags:
        - heaserver-activity
    parameters:
        - $ref: '#/components/parameters/name'
    responses:
      '200':
        $ref: '#/components/responses/200'
      '404':
        $ref: '#/components/responses/404'
    """
    return await mongoservicelib.get_by_name(request, MONGODB_ACTIVITY_COLLECTION)


@routes.get('/activity')
@routes.get('/activity/')
@action('heaserver-activity-activity-get-properties', rel='hea-properties')
@action('heaserver-activity-activity-open', rel='hea-opener', path='/activity/{id}/opener')
@action('heaserver-activity-activity-duplicate', rel='hea-duplicator', path='/activity/{id}/duplicator')
async def get_all_activity(request: web.Request) -> web.Response:
    """
    Gets all activity.
    :param request: the HTTP request.
    :return: all activity.
    ---
    summary: All activities.
    tags:
        - heaserver-activity
    responses:
      '200':
        $ref: '#/components/responses/200'
    """
    return await mongoservicelib.get_all(request, MONGODB_ACTIVITY_COLLECTION)


@routes.get('/activity/{id}/duplicator')
@action(name='heaserver-activity-activity-duplicate-form')
async def get_activity_duplicate_form(request: web.Request) -> web.Response:
    """
    Gets a form template for duplicating the requested activity.

    :param request: the HTTP request. Required.
    :return: the requested form, or Not Found if the requested activity was not found.
    """
    return await mongoservicelib.get(request, MONGODB_ACTIVITY_COLLECTION)


@routes.post('/activity/duplicator')
async def post_activity_duplicator(request: web.Request) -> web.Response:
    """
    Posts the provided activity for duplication.
    :param request: the HTTP request.
    :return: a Response object with a status of Created and the object's URI in the Location header.
    """
    return await mongoservicelib.post(request, MONGODB_ACTIVITY_COLLECTION, Activity)


@routes.post('/activity')
@routes.post('/activity/')
async def post_activity(request: web.Request) -> web.Response:
    """
    Posts the provided activity.
    :param request: the HTTP request.
    :return: a Response object with a status of Created and the object's URI in the Location header.
    ---
    summary: Activity creation
    tags:
        - heaserver-activity
    requestBody:
      description: A new activity object.
      required: true
      content:
        application/vnd.collection+json:
          schema:
            type: object
          examples:
            example:
              summary: User activity example
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
                    "value": "Joe"
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
                    "value": "joe"
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
                    "name": "status",
                    "value": "IN_PROGRESS"
                  },
                  {
                    "name": "arn",
                    "value": "a:1323445"
                  },
                  {
                    "name": "user_id",
                    "value": "user-b"
                  },
                  {
                    "name": "version",
                    "value": null
                  },
                  {
                    "name": "type",
                    "value": "heaobject.activity.UserActivity"
                  }]
                }
              }
        application/json:
          schema:
            type: object
          examples:
            example:
              summary: User activity example
              value: {
                "created": null,
                "derived_by": null,
                "derived_from": [],
                "description": null,
                "display_name": "Joe",
                "invites": [],
                "modified": null,
                "name": "joe",
                "owner": "system|none",
                "shares": [],
                "status": "IN_PROGRESS",
                "arn": 'a:1323445',
                "user_id": 'user-b',
                "type": "heaobject.activity.UserActivity",
                "version": null
              }
    responses:
      '201':
        $ref: '#/components/responses/201'
      '400':
        $ref: '#/components/responses/400'
      '404':
        $ref: '#/components/responses/404'
    """
    return await mongoservicelib.post(request, MONGODB_ACTIVITY_COLLECTION, Activity)


@routes.put('/activity/{id}')
async def put_activity(request: web.Request) -> web.Response:
    """
    Updates the activity with the specified id.
    :param request: the HTTP request.
    :return: a Response object with a status of No Content or Not Found.
    ---
    summary: Activity updates
    tags:
        - heaserver-activity
    parameters:
        - $ref: '#/components/parameters/id'
    requestBody:
      description: An updated activity object.
      required: true
      content:
        application/vnd.collection+json:
          schema:
            type: object
          examples:
            example:
              summary: User activity example
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
                    "value": "Reximus Max"
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
                    "name": "status",
                    "value": "COMPLETE"
                  },
                  {
                    "name": "arn",
                    "value": "a:1323444"
                  },
                  {
                    "name": "user_id",
                    "value": "user-b"
                  },
                  {
                    "name": "version",
                    "value": null
                  },
                  {
                    "name": "id",
                    "value": "666f6f2d6261722d71757578"
                  },
                  {
                    "name": "type",
                    "value": "heaobject.activity.UserActivity"
                  }]
                }
              }
        application/json:
          schema:
            type: object
          examples:
            example:
              summary: User activity example
              value: {
                "id": "666f6f2d6261722d71757578",
                "created": null,
                "derived_by": null,
                "derived_from": [],
                "description": null,
                "display_name": "Reximus Max",
                "invites": [],
                "modified": null,
                "name": "reximus",
                "owner": "system|none",
                "shares": [],
                "status": "COMPLETE",
                "arn": 'a:1323444',
                "user_id": 'user-b',
                "type": "heaobject.activity.UserActivity",
                "version": null
              }
    responses:
      '204':
        $ref: '#/components/responses/204'
      '400':
        $ref: '#/components/responses/400'
      '404':
        $ref: '#/components/responses/404'
    """
    return await mongoservicelib.put(request, MONGODB_ACTIVITY_COLLECTION, Activity)


@routes.delete('/activity/{id}')
async def delete_activity(request: web.Request) -> web.Response:
    """
    Deletes the activity with the specified id.
    :param request: the HTTP request.
    :return: No Content or Not Found.
    ---
    summary: Activity deletion
    tags:
        - heaserver-activity
    parameters:
        - $ref: '#/components/parameters/id'
    responses:
      '204':
        $ref: '#/components/responses/204'
      '404':
        $ref: '#/components/responses/404'
    """
    return await mongoservicelib.delete(request, MONGODB_ACTIVITY_COLLECTION)


def main() -> None:
    config = init_cmd_line(description='A service for tracking activity in hea',
                           default_port=8080)
    start(db=mongo.MongoManager, wstl_builder_factory=builder_factory(__package__), config=config)
