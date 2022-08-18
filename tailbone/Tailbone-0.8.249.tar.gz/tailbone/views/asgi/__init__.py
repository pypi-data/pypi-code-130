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
ASGI Views
"""

from __future__ import unicode_literals, absolute_import

import http.cookies

from beaker.cache import clsmap
from beaker.session import SessionObject, SignedCookie


class WebsocketView(object):

    def __init__(self, registry):
        self.registry = registry

    async def get_user_session(self, scope):
        settings = self.registry.settings
        beaker_key = settings['beaker.session.key']
        beaker_secret = settings['beaker.session.secret']
        beaker_type = settings['beaker.session.type']
        beaker_data_dir = settings['beaker.session.data_dir']
        beaker_lock_dir = settings['beaker.session.lock_dir']

        # get ahold of session identifier cookie
        headers = dict(scope['headers'])
        cookie = headers.get(b'cookie')
        if not cookie:
            return
        cookie = cookie.decode('utf_8')
        cookie = http.cookies.SimpleCookie(cookie)
        morsel = cookie[beaker_key]

        # simulate pyramid_beaker logic to get at the session
        cookieheader = morsel.output(header='')
        cookie = SignedCookie(beaker_secret, input=cookieheader)
        session_id = cookie[beaker_key].value
        request = {'cookie': cookieheader}
        session = SessionObject(
            request,
            id=session_id,
            key=beaker_key,
            namespace_class=clsmap[beaker_type],
            data_dir=beaker_data_dir,
            lock_dir=beaker_lock_dir)

        return session
