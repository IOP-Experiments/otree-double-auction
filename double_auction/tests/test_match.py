from otree.api import Currency as c, currency_range, Submission
from .. import views
from .._builtin import Bot
from ..models import Constants

class PlayerBot(Bot):

    cases = ['match', 'no_match']

    def play_round(self):
        if self.player.participant_id % 3 == 1:
            if self.round_number == 1:
                yield(views.LotteryInstructions, {'instructions_lottery1': 0, 'instructions_lottery2': 100, 'instructions_lottery3': 100, })
            yield(views.LotteryGame, {'lottery_choice': 20})
            yield(views.LotteryResults)
        else:
            if self.round_number == 1:
                yield(views.Instructions, {'instructions_da1': 10, 'instructions_da2': 25, 'instructions_da3': 20, })
                yield(views.Role)
            yield Submission(views.Game, check_html=False)
            yield(views.Results)
