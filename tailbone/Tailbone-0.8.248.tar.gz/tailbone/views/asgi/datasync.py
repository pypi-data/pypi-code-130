# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2022 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
DataSync Views
"""

from __future__ import unicode_literals, absolute_import

import asyncio
import json

from tailbone.views.asgi import WebsocketView


class DatasyncWS(WebsocketView):

    async def status(self, scope, receive, send):
        rattail_config = self.registry['rattail_config']
        app = rattail_config.get_app()
        model = app.model
        auth_handler = app.get_auth_handler()
        datasync_handler = app.get_datasync_handler()

        authorized = False
        user_session = await self.get_user_session(scope)
        if user_session:
            user_uuid = user_session.get('auth.userid')
            session = app.make_session()

            user = None
            if user_uuid:
                user = session.query(model.User).get(user_uuid)

            # figure out if user is authorized for this websocket
            permission = 'datasync.status'
            authorized = auth_handler.has_permission(session, user, permission)
            session.close()

        # wait for client to connect
        message = await receive()
        assert message['type'] == 'websocket.connect'

        # allow or deny access, per authorization
        if authorized:
            await send({'type': 'websocket.accept'})
        else: # forbidden
            await send({'type': 'websocket.close'})
            return

        # this tracks when client disconnects
        state = {'disconnected': False}

        async def wait_for_disconnect():
            message = await receive()
            if message['type'] == 'websocket.disconnect':
                state['disconnected'] = True

        # watch for client disconnect, while we do other things
        asyncio.create_task(wait_for_disconnect())

        # do the rest forever, until client disconnects
        while not state['disconnected']:

            # give client latest supervisor process info
            info = datasync_handler.get_supervisor_process_info()
            await send({'type': 'websocket.send',
                        'subtype': 'datasync.supervisor_process_info',
                        'text': json.dumps(info)})

            # pause for 1 second
            await asyncio.sleep(1)

    @classmethod
    def defaults(cls, config):
        cls._defaults(config)

    @classmethod
    def _defaults(cls, config):

        # status
        config.add_tailbone_websocket('datasync.status',
                                      cls, attr='status')


def defaults(config, **kwargs):
    base = globals()

    DatasyncWS = kwargs.get('DatasyncWS', base['DatasyncWS'])
    DatasyncWS.defaults(config)


def includeme(config):
    defaults(config)
