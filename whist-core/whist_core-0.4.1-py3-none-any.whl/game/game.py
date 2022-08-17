"""One Game of whist"""

from pydantic import BaseModel

from whist_core.game.errors import HandNotDoneError
from whist_core.game.hand import Hand
from whist_core.game.play_order import PlayOrder
from whist_core.game.player_at_table import PlayerAtTable
from whist_core.scoring.score_calculator import ScoreCalculator
from whist_core.scoring.score_card import ScoreCard
from whist_core.user.player import Player


class Game(BaseModel):
    """
    One Game of whist.
    """

    play_order: PlayOrder
    win_score: int = 3
    score_card: ScoreCard = ScoreCard()
    hands: list[Hand] = []

    # pylint: disable=too-few-public-methods
    class Config:
        """
        Enables to have non models as field types and sets the encoder for play order.
        """
        arbitrary_types_allowed = True

    def next_hand(self) -> Hand:
        """
        Checks if the current hand is done and if so will return the next hand. If not it will
        return the current hand.
        :rtype: Hand
        """
        if self.current_hand is None:
            hand = Hand.deal(self.play_order)
            self.hands.append(hand)
        elif not self.current_hand.done():
            raise HandNotDoneError()
        else:
            score = ScoreCalculator.calc_score(self.current_hand, self.play_order)
            self.score_card.add_score(score)
            self._next_play_order()
            hand = Hand.deal(self.play_order)
            self.hands.append(hand)
        return self.current_hand

    @property
    def current_hand(self):
        """
        Returns the current hand if there is one. Else None.
        """
        return self.hands[-1] if len(self.hands) > 0 else None

    @property
    def done(self):
        """
        Check if game is done.
        :return: True if done else false
        :rtype: bool
        """
        return self.win_score <= self.score_card.max

    def get_player(self, player: Player) -> PlayerAtTable:
        """
        Retrieves the PlayerAtTable for the player given.
        :param player: who needs it's counterpart at the table
        :return: the player at table
        """
        return self.play_order.get_player(player)

    def _next_play_order(self) -> None:
        """
        Creates the next order of player for next hand.
        """
        self.play_order = self.play_order.next_order()
