"""Rubber of whist"""
from pydantic import BaseModel

from whist_core.game.errors import GameNotStartedError, GameNotDoneError
from whist_core.game.game import Game
from whist_core.game.play_order import PlayOrder
from whist_core.scoring.team import Team
from whist_core.session.matcher import RandomMatcher
from whist_core.session.userlist import UserList


class Rubber(BaseModel):
    """
    Implementation of a rubber.
    """
    max_games: int = 3
    games: list[Game] = []
    teams: list[Team]

    # pylint: disable=too-few-public-methods
    class Config:
        """
        Configuration class for base model to allow fields which are not pydantic models.
        """
        arbitrary_types_allowed = True

    @property
    def games_played(self) -> int:
        """
        Amounts of games played already.
        :rtype: int
        """
        return len(self.games)

    @property
    def done(self) -> bool:
        """
        Checks if the rubber is done.
        :return: True if done else False
        :rtype: bool
        """
        return self.games_played == self.max_games

    def current_game(self) -> Game:
        """
        Returns the current game.
        """
        if len(self.games) == 0:
            raise GameNotStartedError()
        return self.games[-1]

    def next_game(self) -> Game:
        """
        Creates a new game if the previous is done.
        :rtype: Game
        """
        if len(self.games) == 0 or self.games[-1].done:
            self.games.append(Game(play_order=PlayOrder.from_team_list(self.teams)))
        elif not self.games[-1].done:
            raise GameNotDoneError()

        return self.current_game()

    @classmethod
    def create_random(cls, users: UserList, num_teams: int, team_size: int) -> 'Rubber':
        """
        Creates a rubber with a random distribution of players in teams.
        :param users: all players and stati at the table
        :param num_teams: the amount of teams
        :param team_size: the size of each team
        :return: the rubber object
        """
        teams = RandomMatcher.distribute(num_teams, team_size, users)
        rubber = Rubber(teams=teams)
        return rubber
