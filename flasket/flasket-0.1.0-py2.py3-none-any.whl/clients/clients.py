from attr import attrs

from ..clients import g_clients
from ..mixins import AppMixin

# TODO: Rename ClientFactory
@attrs(kw_only=True)
class Clients(AppMixin):
    def __attrs_post_init__(self: object) -> None:
        # Use the flask config, not the Application config
        if "CLIENTS" not in self.app.app.config:
            self.app.app.config["CLIENTS"] = {}

    def __getattr__(self, name):
        return self._load_client(name)

    def _load_client(self, name):
        # Return client if we have one
        cfg = self.app.app.config["CLIENTS"]
        # assert False, self.app.app.config
        retval = cfg.get(name)
        if retval:
            return retval

        self.app.logger.info(f"Creating client '{name}'...")
        fn = g_clients.get(name)
        if fn is None:
            self.app.logger.error(f"Client '{name}' is not registered.")
            raise TypeError(f"Client '{name}' does not exist")

        try:
            retval = fn(app=self.app)
        except Exception as err:
            self.app.logger.error(f"Client '{name}' could not be loaded.")
            raise err from err

        cfg[name] = retval
        return retval


## TODO
