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
Luigi utilities
"""

from __future__ import unicode_literals, absolute_import

import os
import logging
import subprocess

from six.moves.xmlrpc_client import ProtocolError

from rattail.app import GenericHandler


log = logging.getLogger(__name__)


class LuigiHandler(GenericHandler):
    """
    Base class and default implementation for Luigi handler.
    """

    def get_supervisor_process_name(self, require=False, **kwargs):
        getter = self.config.require if require else self.config.get
        return getter('luigi', 'scheduler.supervisor_process_name')

    def restart_supervisor_process(self, name=None, **kwargs):
        if not name:
            name = self.get_supervisor_process_name()

        try:
            proxy = self.app.make_supervisorctl_proxy()
        except:
            log.warning("failed to make supervisorctl proxy", exc_info=True)

        else:
            # we have our proxy, so use that, then return
            try:
                info = proxy.supervisor.getProcessInfo(name)
                if info['state'] != 0:
                    proxy.supervisor.stopProcess(name)
                proxy.supervisor.startProcess(name)
            except ProtocolError as error:
                raise self.app.safe_supervisor_protocol_error(error)
            return

        # no proxy, but we can still try command line
        # TODO: should rename this setting at some point?
        cmd = self.config.get('luigi', 'scheduler.restart_command')
        if cmd:
            cmd = self.config.parse_list(cmd)
        elif name:
            cmd = ['supervisorctl', 'restart', name]

        log.debug("attempting luigi scheduler restart with command: %s", cmd)

        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as error:
            log.warning("failed to restart luigi scheduler; output was:")
            log.warning(error.output)
            raise

    def get_all_overnight_tasks(self, **kwargs):
        tasks = []
        keys = self.config.getlist('luigi', 'overnight_tasks',
                                   default=[])
        for key in keys:
            tasks.append({
                'key': key,
            })
        return tasks

    def restart_overnight_task(self, key, **kwargs):
        script = os.path.join(self.config.appdir(),
                              'restart-overnight-{}.sh'.format(key))
        subprocess.check_call(script)

    def purge_luigi_settings(self, session, **kwargs):
        model = self.model

        to_delete = session.query(model.Setting)\
                           .filter(model.Setting.name == 'luigi.overnight_tasks')\
                           .all()

        for setting in to_delete:
            self.app.delete_setting(session, setting.name)
