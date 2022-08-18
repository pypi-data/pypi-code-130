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
Views for Luigi
"""

from __future__ import unicode_literals, absolute_import

import json

from rattail.util import simple_error

from tailbone.views import MasterView


class LuigiJobView(MasterView):
    """
    Simple views for Luigi jobs.
    """
    normalized_model_name = 'luigijobs'
    model_key = 'jobname'
    model_title = "Luigi Job"
    route_prefix = 'luigi'
    url_prefix = '/luigi'

    viewable = False
    creatable = False
    editable = False
    deletable = False
    configurable = True

    def __init__(self, request, context=None):
        super(LuigiJobView, self).__init__(request, context=context)
        app = self.get_rattail_app()
        self.luigi_handler = app.get_luigi_handler()

    def index(self):
        luigi_url = self.rattail_config.get('luigi', 'url')
        history_url = '{}/history'.format(luigi_url.rstrip('/')) if luigi_url else None
        return self.render_to_response('index', {
            'use_buefy': self.get_use_buefy(),
            'index_url': None,
            'luigi_url': luigi_url,
            'luigi_history_url': history_url,
            'overnight_tasks': self.luigi_handler.get_all_overnight_tasks(),
        })

    def launch(self):
        key = self.request.POST['job']
        assert key
        self.luigi_handler.restart_overnight_task(key)
        self.request.session.flash("Scheduled overnight task for immediate launch: {}".format(key))
        return self.redirect(self.get_index_url())

    def restart_scheduler(self):
        try:
            self.luigi_handler.restart_supervisor_process()
            self.request.session.flash("Luigi scheduler has been restarted.")

        except Exception as error:
            self.request.session.flash(simple_error(error), 'error')

        return self.redirect(self.request.get_referrer(
            default=self.get_index_url()))

    def configure_get_simple_settings(self):
        return [

            # luigi proper
            {'section': 'luigi',
             'option': 'url'},
            {'section': 'luigi',
             'option': 'scheduler.supervisor_process_name'},
            {'section': 'luigi',
             'option': 'scheduler.restart_command'},

        ]

    def configure_get_context(self, **kwargs):
        context = super(LuigiJobView, self).configure_get_context(**kwargs)
        context['overnight_tasks'] = self.luigi_handler.get_all_overnight_tasks()
        return context

    def configure_gather_settings(self, data):
        settings = super(LuigiJobView, self).configure_gather_settings(data)

        keys = []
        for task in json.loads(data['overnight_tasks']):
            keys.append(task['key'])

        if keys:
            settings.append({'name': 'luigi.overnight_tasks',
                             'value': ', '.join(keys)})

        return settings

    def configure_remove_settings(self):
        super(LuigiJobView, self).configure_remove_settings()
        self.luigi_handler.purge_luigi_settings(self.Session())

    @classmethod
    def defaults(cls, config):
        cls._defaults(config)
        cls._luigi_defaults(config)

    @classmethod
    def _luigi_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        permission_prefix = cls.get_permission_prefix()
        url_prefix = cls.get_url_prefix()
        model_title_plural = cls.get_model_title_plural()

        # launch job
        config.add_tailbone_permission(permission_prefix,
                                       '{}.launch'.format(permission_prefix),
                                       label="Launch any Luigi job")
        config.add_route('{}.launch'.format(route_prefix),
                         '{}/launch'.format(url_prefix),
                         request_method='POST')
        config.add_view(cls, attr='launch',
                        route_name='{}.launch'.format(route_prefix),
                        permission='{}.launch'.format(permission_prefix))

        # restart luigid scheduler
        config.add_tailbone_permission(permission_prefix,
                                       '{}.restart_scheduler'.format(permission_prefix),
                                       label="Restart the Luigi Scheduler daemon")
        config.add_route('{}.restart_scheduler'.format(route_prefix),
                         '{}/restart-scheduler'.format(url_prefix),
                         request_method='POST')
        config.add_view(cls, attr='restart_scheduler',
                        route_name='{}.restart_scheduler'.format(route_prefix),
                        permission='{}.restart_scheduler'.format(permission_prefix))


def defaults(config, **kwargs):
    base = globals()

    LuigiJobView = kwargs.get('LuigiJobView', base['LuigiJobView'])
    LuigiJobView.defaults(config)


def includeme(config):
    defaults(config)
