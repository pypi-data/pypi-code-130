from functools import partial

from .core.exceptions import PloupyException
from .game import Game, Probe, Turret, Player, Factory


class Behaviour:
    def __init__(self, uid: str, game: Game) -> None:
        self._uid = uid
        self.config = game.config
        self.game = game
        self.map = game.map
        self.player = self.game.get_player(self._uid)
        if self.player is None:
            raise PloupyException("Can't find own player.")

        self._bind_callbacks()

    def _bind_callbacks(self):
        """"""
        self.player.on_income = self._wrap_callback(self.on_income)

        for player in self.game.players:
            player.on_factory_build = partial(
                self._wrap_callback(self.on_factory_build),
                player=player,
            )
            player.on_turret_build = partial(
                self._wrap_callback(self.on_turret_build),
                player=player,
            )
            player.on_probe_build = partial(
                self._wrap_callback(self.on_probe_build),
                player=player,
            )

    def _wrap_callback(self, cb):
        async def wrapper(*args, **kwargs):
            await cb(*args, **kwargs)

        return wrapper

    async def on_start(self) -> None:
        """
        Called on start of the game
        """

    async def on_income(self, new: int, old: int) -> None:
        """
        Called when the money is updated
        """

    async def on_factory_build(self, factory: Factory, player: Player) -> None:
        """ """

    async def on_turret_build(self, turret: Turret, player: Player) -> None:
        """ """

    async def on_probe_build(self, probe: Probe, player: Player) -> None:
        """ """
