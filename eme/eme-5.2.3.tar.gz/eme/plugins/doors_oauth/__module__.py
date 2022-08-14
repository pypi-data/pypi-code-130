import os

from eme.data_access import get_repo
from eme.website import WebsiteBlueprint
from eme.entities import load_settings

from .controllers.UsersController import UsersController
from .groups.UsersGroup import UsersGroup
from .services import auth


class DoorsOauthEmeModule:
    _EME_PLUGIN = True

    def __init__(self, conf, UserEntCls, UserRepo = None):
        self.ent = UserEntCls
        self.repo = get_repo(UserEntCls) if UserRepo is None else UserRepo
        self.conf = conf

        self.blueprint = None

    def init_webapp(self, webapp, webconf):
        auth.init(webapp, self.conf['auth'], self.ent, self.repo)

        self.blueprint = WebsiteBlueprint('doors', {'website': {'type': 'custom'}}, webapp.script_path, module_route="/users")
        self.blueprint.load_controllers({
            'Users': UsersController(webapp, self.ent)
        }, webconf)

    def init_cliapp(self, app, conf):
        #    app.commands.update(load_handlers(app, 'Command', path=os.path.join(module_path, 'commands')))
        pass

    def init_wsapp(self, wsapp, wsconf):
        auth.init_ws(wsapp, self.conf, self.repo)

        wsapp.load_groups({
            "Users": UsersGroup(wsapp)
        }, conf=self.conf)

    def init_dal(self):
        pass

    def init_migration(self):
        pass