
import random
import time
import logging

from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)


author = 'Jan Dietrich'

doc = """
This app is to play the double auction game
"""

# Get an instance of a logger
logger = logging.getLogger(__name__)

class Constants(BaseConstants):
    name_in_url = 'double_auction'
    players_per_group = None
    num_rounds = 12

    quiz_radio_button = dict(
        choices=[[1, 'Yes'],
                 [2, 'No']],
        widget=widgets.RadioSelectHorizontal
    )

class Subsession(BaseSubsession):
    def creating_session(self):
        if self.round_number == 1:
            if len(self.get_players()) % self.session.config['market_size'] != 0:
                raise Exception('number of participant must be mulitple of market_size')


class Group(BaseGroup):
    pass

class Player(BasePlayer):
    money = models.IntegerField()
    cost = models.IntegerField()
    last_offer = models.IntegerField()
    trade_price = models.IntegerField()
    match_with = models.ForeignKey('Player', null=True, on_delete=models.CASCADE)
    match_with_player_id_in_group = models.IntegerField()
    instructions_da1 = models.IntegerField(
        verbose_name="You are a buyer. Your valuation for the good is 50 points. You submit a bid of 40 points and a seller accepts this bid. What are your earnings (in points)?",
    )

    instructions_da3 = models.IntegerField(
        verbose_name="You are a seller. Your production costs for the good are 20 points. You submit an ask of 25 points and a buyer accepts this ask. What are your earnings (in points)?",
    )
    instructions_da4 = models.IntegerField(
        verbose_name="You are a buyer. Your valuation for the good is 40 points. Is it possible to submit a bid of 60 points?",
        **Constants.quiz_radio_button
    )

    display_id = models.IntegerField()
    is_bot = models.BooleanField()

