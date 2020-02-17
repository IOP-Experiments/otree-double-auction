from channels.generic.websocket import JsonWebsocketConsumer
from double_auction.models import Player, Group
from otree.models import Participant
from double_auction.helpers import handle_bid, get_player_from_code
from double_auction.controllers.bets import clear_bet
from double_auction.tasks import automated_bid
import otree.common
from asgiref.sync import async_to_sync

import time
import random
import datetime
import logging
logger = logging.getLogger(__name__)


class DoubleAuctionWebSocketConsumer(JsonWebsocketConsumer):

    def connect(self):
        """
        Perform things on connection start
        """
        code, player, group_channel = self.__get_infos()
        logger.info("Participant %s connected", code )
        logger.info('Channel name:%s' % group_channel)
        async_to_sync(self.channel_layer.group_add)(group_channel, self.channel_name)
        self.accept()

        if 'is_bot' in player.participant.vars and player.participant.vars['is_bot']:
            player.is_bot = False
            player.save()
            player.participant.vars["is_bot"] = False
            player.participant.save()
            self.send_to_group(group_channel, {
                "type": "action.status",
                "status": '',
                "player_id": player.id
            })
        logger.info("Player connected %s" % self.channel_name)

        messages = []
        for p in player.group.get_players():
            if 'is_bot' in p.participant.vars and p.participant.vars['is_bot']:
                bot_label = 'bot' if player.session.config['bot_enable'] else 'inactive'
                self.send_json({
                    "type": "action.status",
                    "status": bot_label,
                    "player_id": p.id
                })
            if p.last_offer is not None:


                if p.match_with is None:

                    message = {
                        "value": p.last_offer,
                        "type": "action.value." + p.participant.vars["role"],
                        "player_id": p.id,
                        "player_id_in_group": p.display_id
                    }
                    messages.append(message)

        for message in messages:
            self.send_json(message)

    def receive_json(self, content):
        """
        Called when a json message is received
        """
        code, player, group_channel = self.__get_infos()
        jsonmessage = content
        logger.info("Message received on socket. message:  %s", jsonmessage)
        logger.info(player.id)

        action_type = jsonmessage["type"]

        logger.info(action_type)

        if action_type == "message.clear":
            responses = clear_bet(player.id)
        elif action_type == "message.seller" or action_type == "message.buyer":
            bid_info = {
                'player': player,
                "value": jsonmessage["value"] if "value" in jsonmessage else None,
                "optionalPlayerId": jsonmessage["optionalPlayerId"] if "optionalPlayerId" in jsonmessage else None
            }
            responses = handle_bid(bid_info)
        self.send_to_group(group_channel, responses)

    def action_value_buyer(self, content):
        self.send_json(content)

    def action_value_seller(self, content):
        self.send_json(content)

    def action_match(self, content):
        self.send_json(content)

    def action_clear(self, content):
        self.send_json(content)

    def action_error(self, content):
        self.send_json(content)

    def action_status(self, content):
        self.send_json(content)

    def disconnect(self, close_code):
        """
        Perform things on connection close
        """
        code, player, group_channel = self.__get_infos()
        logger.info('player disconnected {}'.format( code ))
        async_to_sync(self.channel_layer.group_discard)(group_channel, self.channel_name)
        now = time.time()
        starttime = now if now > player.session.vars["starttime"] else player.session.vars["starttime"]
        endtime = player.session.vars["endtime"]
        remaining_seconds = endtime - starttime
        if 1 < remaining_seconds < 3:
            player.participant.vars['is_bot'] = True
            player.participant.save()
            if not player.last_offer:
                if player.participant.session.config['bot_enable']:
                    if otree.common.USE_REDIS:
                        logger.info("automated bid now: %s", player.participant.code)
                        automated_bid(code, player.round_number)
                    else:
                        logger.warning("you enabled bots but there will be no automated_bid if you don't enable redis (set REDIS_URL)")
            bot_label = 'bot' if player.session.config['bot_enable'] else 'inactive'
            self.send_to_group(group_channel, {
                "type": "action.status",
                "status": bot_label,
                "player_id": player.id
            })
        elif remaining_seconds >= 3:
            random_seconds = random.random() * ( endtime - 3 - starttime)
            random_timestamp = starttime + random_seconds
            random_time = datetime.datetime.fromtimestamp(random_timestamp)
            player.participant.vars['is_bot'] = True
            player.participant.save()
            player.is_bot = True
            player.save()
            if not player.last_offer:
                if player.participant.session.config['bot_enable']:
                    if otree.common.USE_REDIS:
                        logger.info("schedule automated bid: %s %s %s, now_or_starttime: %s", player.participant.code, random_seconds, random_time, starttime)
                        automated_bid.schedule(args=(code,player.round_number,), eta=random_time)
                    else:
                        logger.warning("you enabled bots but there will be no automated_bid if you don't enable redis (set REDIS_URL)")
            bot_label = 'bot' if player.session.config['bot_enable'] else 'inactive'
            self.send_to_group(group_channel, {
                "type": "action.status",
                "status": bot_label,
                "player_id": player.id
            })
        else:
            print("end of auction")

    def __get_infos(self):
        code = self.scope["url_route"]["kwargs"]["code"]
        participant = Participant.objects.get(code=code);
        player = Player.objects.filter(participant=participant, round_number=participant._round_number).first()
        group_channel = player.participant.session.code + str(player.group.id_in_subsession)
        return code, player, group_channel

    def send_to_group(self, group_channel, responses):
        responses = [responses] if not isinstance(responses, list) else responses
        for response in responses:
            async_to_sync(self.channel_layer.group_send)(group_channel, response)
