import random
import time
import datetime
from math import floor, ceil
import logging

from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants
from itertools import zip_longest

import otree.common_internal
from .tasks import automated_bid

# Get an instance of a logger
logger = logging.getLogger(__name__)

class Instructions(Page):
    timeout_seconds = 720
    form_model = 'player'
    form_fields = ["instructions_da1",  "instructions_da3", "instructions_da4"]
    def is_displayed(self):
        return self.subsession.round_number==1
    def instructions_da1_error_message(self, value):
        if value != 10:
            return "Value is not correct"
    def instructions_da3_error_message(self, value):
        if value != 5:
            return "Value is not correct"
    def instructions_da4_error_message(self, value):
            if value != 2:
                return "Answer is not correct"

    def vars_for_template(self):
        num_players = len(self.subsession.get_players())
        market_size = self.session.config['market_size']
        num_markets = ceil(num_players / market_size)

        picture_path_number = str(num_players) if num_players <= 20 else "over_20"
        picture_path = "instructions/num_players_" + picture_path_number + ".png"

        label_buyer = "buyer" if num_players == 2 else "buyers"
        label_seller = "seller" if num_players == 2 else "sellers"

        return {
            'daPlayers': num_players / 2,
            'num_of_rounds': Constants.num_rounds - self.session.config["num_of_test_rounds"],
            'market_time': self.session.config["time_per_round"],
            'freeze_time': self.session.config["delay_before_market_opens"],
            'picture': picture_path,
            'label_buyer': label_buyer,
            'label_seller': label_seller
        }
    def before_next_page(self):
        if self.timeout_happened:
            self.player.participant.vars['instructions_failed'] = True


class PostInstructions(Page):
    timeout_seconds = 120
    def is_displayed(self):
        return self.subsession.round_number == 1 and 'instructions_failed' in self.player.participant.vars

class WhatNextDA(Page):
    timeout_seconds = 90
    def is_displayed(self):
        return self.subsession.round_number==1
    def vars_for_template(self):
        return {
            'payoff_per_point': c(1).to_real_world_currency(self.session),
            'num_of_rounds': Constants.num_rounds - self.session.config["num_of_test_rounds"]
        }

class Role(Page):
    timeout_seconds = 15
    def is_displayed(self):
        return self.subsession.round_number == 1
    def before_next_page(self):
        if self.timeout_happened:
            self.player.participant.vars["is_bot"] = True
        else:
            self.player.participant.vars["is_bot"] = False

class AfterTestrounds(Page):
    timeout_seconds = 20
    def is_displayed(self):
        return self.subsession.round_number == self.session.config["num_of_test_rounds"]
    def before_next_page(self):
        if self.timeout_happened:
            self.player.participant.vars["is_bot"] = True
        else:
            self.player.participant.vars["is_bot"] = False
    def vars_for_template(self):
        return {
            'num_of_rounds': Constants.num_rounds - self.session.config["num_of_test_rounds"]
        }

class InitialWait(WaitPage):
    template_name = 'double_auction/InitialWait.html'

class WaitAfterRole(WaitPage):
    template_name = 'double_auction/WaitAfterRole.html'

    def after_all_players_arrive(self):
        """ after all players arrived """

        da_players = self.group.get_players()

        # setup valuation table
        money_max_value = self.session.config['valuation_max']
        money_min_value = self.session.config['valuation_min']
        money_steps = self.session.config['valuation_increments']
        num_of_values = floor( (money_max_value - money_min_value) / money_steps) + 1

        buyer_valuation = [ money_min_value + m * money_steps for m in range(num_of_values) ]

        logger.info("Buyer Valuation %s" % buyer_valuation)

        cost_max_value = self.session.config['production_costs_max']
        cost_min_value = self.session.config['production_costs_min']
        cost_steps = self.session.config['production_costs_increments']
        num_of_values = floor( (cost_max_value - cost_min_value) / cost_steps) + 1

        seller_valuation = [ cost_min_value + m * cost_steps for m in range(num_of_values) ]
        logger.info("Seller Valuation %s" % seller_valuation)

        # setup display ids
        num_of_da_players_per_role = int(ceil(len(da_players)/2))
        seller_ids = [ i+1 for i in range(num_of_da_players_per_role) ]
        buyer_ids = [ i+1 for i in range(num_of_da_players_per_role) ]
        random.shuffle(seller_ids)
        random.shuffle(buyer_ids)

        # Set timer for players
        starttime = time.time() + self.session.config['delay_before_market_opens']
        endtime = starttime + self.session.config['time_per_round']
        self.session.vars["starttime"] = starttime
        self.session.vars["endtime"] = endtime

        for index, player in enumerate(da_players):
            # create bots for missing players
            if 'is_bot' in player.participant.vars and player.participant.vars['is_bot']:
                if player.participant.session.config['bot_enable']:
                    if otree.common_internal.USE_REDIS:
                        random_seconds = random.random() * ( endtime - 3 - starttime)
                        random_timestamp = starttime + random_seconds
                        random_time = datetime.datetime.fromtimestamp(random_timestamp)
                        logger.info("schedule automated bid: %s %s %s, starttime: %s", player.participant.code, random_seconds, random_time, datetime.datetime.fromtimestamp(starttime) )
                        automated_bid.schedule(args=(player.participant.code, player.round_number,), eta=random_time, convert_utc=True)
                    else:
                        logger.warning("you enabled bots but there will be no automated_bid if you don't enable redis (set REDIS_URL)")

            if player.participant.vars["role"]=="buyer":
                if not buyer_valuation:
                    buyer_valuation = [ money_min_value + m * money_steps for m in range(num_of_values) ]

                random_index = random.randint(0, len(buyer_valuation) - 1)

                player.money = buyer_valuation[random_index]
                buyer_valuation.pop(random_index)
                player.display_id = buyer_ids.pop()

            else:
                if len(seller_valuation)==0:
                    seller_valuation = [ cost_min_value + m * cost_steps for m in range(num_of_values) ]

                random_index = random.randint(0, len(seller_valuation) - 1 )

                player.cost = seller_valuation[random_index]
                seller_valuation.pop(random_index)

                player.display_id = seller_ids.pop()

class FirstWait(WaitPage):
    template_name = 'double_auction/FirstWait.html'
    group_by_arrival_time = True

    def is_displayed(self):
        """ is displayed """
        return self.subsession.round_number == 1

    def get_players_for_group(self, waiting_players):
        num_of_da_players_per_group = self.session.config['market_size']
        num_of_active_groups = len(self.subsession.get_group_matrix())-1
        num_players = len(self.subsession.get_players())
        market_size = self.session.config['market_size']
        number_markets = ceil(num_players / market_size)
        if num_of_active_groups < number_markets and len(waiting_players) >= num_of_da_players_per_group:
            logger.info('creating double auction group')
            da_players = waiting_players[:num_of_da_players_per_group]
            for i, p in enumerate(da_players):
                p.participant.vars['game'] = 'double_auction'
                p.participant.vars["chosen_round"] = random.randint(self.session.config['num_of_test_rounds'] + 1, Constants.num_rounds)
                if (i % 2 == 0):
                    p.participant.vars["role"]="buyer"
                else:
                    p.participant.vars["role"]="seller"
            return da_players
        elif num_of_active_groups >= number_markets:
            player = waiting_players[0]
            return waiting_players


class Results(Page):
    """ Result Page """
    def get_timeout_seconds(self):
        return self.participant.vars['endtime'] - time.time()

    def is_displayed(self):
        return self.player.participant.vars['game'] == 'double_auction'
    def vars_for_template(self):
        transactions = []
        for p in self.player.group.get_players():
            if p.last_offer is not None:
                if p.participant.vars["role"] == "buyer" and p.match_with is not None:
                    message = {
                        "type": "transactions",
                        "buyer": p.id,
                        "buyer_id_in_group": p.display_id,
                        "seller": p.match_with.id,
                        "seller_id_in_group": p.match_with.display_id,
                        "value": p.last_offer
                    }
                    transactions.append(message)
        return {
            'transactions': transactions,
            'round_number': self.subsession.round_number - self.session.config["num_of_test_rounds"],
            'num_of_rounds': Constants.num_rounds - self.session.config["num_of_test_rounds"]
        }
    def before_next_page(self):
        if self.timeout_happened:
            self.player.participant.vars["is_bot"] = True
        else:
            self.player.participant.vars["is_bot"] = False


class Game(Page):

    def get_timeout_seconds(self):
        return self.session.vars["endtime"] - time.time()

    def is_displayed(self):
        return self.player.participant.vars['game'] == 'double_auction'

    def vars_for_template(self):
        players = self.group.get_players()

        seller= [ {'id': p.id, 'id_in_group': p.display_id, 'role': p.participant.vars["role"], 'status': '' } for p in players if p.participant.vars["role"] == "seller" ]
        buyer= [ {'id': p.id, 'id_in_group': p.display_id, 'role': p.participant.vars["role"], 'status': '' } for p in players if p.participant.vars["role"] == "buyer" ]
        participant_table = [ list(i) for i in  zip_longest( buyer, seller) ]

        return {
            'minValue': self.player.cost if self.participant.vars["role"]=="seller" else self.session.config["production_costs_min"],
            'maxValue': self.player.money if self.participant.vars["role"]=="buyer" else self.session.config["valuation_max"],
            'lock': True if self.player.match_with else False,
            'participants': participant_table,
            'seconds_to_start': self.session.vars["starttime"] - time.time(),
            'round_number': self.subsession.round_number - self.session.config["num_of_test_rounds"],
            'num_of_rounds': Constants.num_rounds - self.session.config["num_of_test_rounds"]
        }

    def before_next_page(self):
        # set timeout to small amount if is_bot
        if 'is_bot' in self.participant.vars and self.participant.vars['is_bot']:
            self.participant.vars['endtime'] = time.time()
        else:
            self.participant.vars['endtime'] = time.time() + 15




class EndResults(Page):
    timeout_seconds = 20
    def is_displayed(self):
        return self.subsession.round_number == Constants.num_rounds and self.player.participant.vars['game'] == 'double_auction'

    def vars_for_template(self):
        rounds_payoff = [
            {
                'round_number': i + 1 if i < self.session.config['num_of_test_rounds'] else i + 1 - self.session.config['num_of_test_rounds'],
                'test_round': True if i < self.session.config['num_of_test_rounds'] else False,
                'valuation': player.cost if self.player.participant.vars["role"]=="seller" else player.money,
                'trading_price': player.last_offer if player.match_with else "-",
                'payoff': player.payoff
            } for i, player in enumerate(self.player.in_all_rounds())
        ]
        self.player.participant.vars["da_payoffs"]=rounds_payoff
        return {
            'rounds_payoff': rounds_payoff
        }
    def before_next_page(self):
        payoff_player = self.player.in_all_rounds()[self.participant.vars['chosen_round']-1]
        self.player.participant.payoff = payoff_player.payoff



page_sequence = [
    FirstWait,
    Instructions,
    PostInstructions,
    WhatNextDA,
    InitialWait,
    Role,
    WaitAfterRole,
    Game,
    Results,
    AfterTestrounds,
    EndResults
]
