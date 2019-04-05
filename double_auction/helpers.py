from .models import Player, Transaction
from otree.models import Participant
from channels import Group
import json
import logging

from .messages import MatchMessage, FailBidMessage

logger = logging.getLogger(__name__)

def update_value(player, value, is_bot):
    new_bid = Transaction.objects.create(
        user = player,
        value = value,
        bot=is_bot
    )
    player.last_offer = value
    player.save()
    return json.dumps({
        "player_id": player.id,
        "player_id_in_group": player.display_id,
        "value": value,
        "type": player.participant.vars["role"]
    })

def handle_bid(bid_info, is_bot=False):
    player = bid_info["player"]
    new_value = bid_info["value"]
    player_role = player.participant.vars["role"]
    other_role = "buyer" if player_role == "seller" else "seller"
    optional_player_id = bid_info["optionalPlayerId"]
    messages = []

    if player.match_with is None and new_value is not None:

        players = player.get_others_in_group()
        other_role_players = [p for p in players if p.participant.vars["role"] == other_role]

        other_player = find_match_and_get_other_player(new_value, player_role, optional_player_id, other_role_players)

        if other_player is not None:
            if new_value != other_player.last_offer:
                new_value = other_player.last_offer

            update_message = update_value(player, new_value, is_bot)
            messages.append(update_message)
            match_message = handle_match(player, new_value, other_player, player.id)
            messages.append(match_message)
        else:
            update_message = update_value(player, new_value, is_bot)
            messages.append(update_message)

        logger.info(messages)
        return messages


def get_player_from_code(code):
    participant = Participant.objects.get(code=code);
    return Player.objects.filter(participant=participant, round_number=participant._round_number).first()

def filter_other_players(other_role_players):
    return [ p for p in other_role_players if p.last_offer and p.match_with is None]

def check_match_with(other_player, new_value):
    return other_player.last_offer == new_value and other_player.match_with is None

def handle_match(player, value, other_player, player_id):
    """ When a match happens, this functions handles it """

    buyer = player if player.participant.vars["role"] == "buyer" else other_player
    seller = player if player.participant.vars["role"] == "seller" else other_player

    buyer_id = int(player_id) if player.participant.vars["role"] == "buyer" else other_player.id
    seller_id = int(player_id) if player.participant.vars["role"] == "seller" else other_player.id

    logger.info("seller %s and buyer %s match", seller_id, buyer_id)
    logger.info("player %s and other_player %s match", player.last_offer, other_player.last_offer)

    # update models
    buyer.match_with = seller
    buyer.match_with_display_id = seller.display_id
    seller.match_with = buyer
    seller.match_with_display_id  = buyer.display_id
    buyer.payoff = buyer.money - buyer.last_offer
    seller.payoff = seller.last_offer - seller.cost
    other_player.save()
    player.save()

    match = MatchMessage(buyer_id, seller_id, player.last_offer)
    return match.getMessage()

def get_other_player(other_player_id, other_role_players):
    logger.info("optionalPlayerId set")
    return next(other_player for other_player in other_role_players if other_player.id == other_player_id)

def get_better_bids(players, player_role, new_value):
    """ Check if there are better bids from other users """
    for p in players:
        if p.last_offer:
            if player_role == "seller" and p.last_offer < new_value and not p.match_with or player_role == "buyer" and p.last_offer > new_value and not p.match_with:
                yield p


def find_matching_player(player_role, new_value, other_role_players):
    filtered_other_players = filter_other_players(other_role_players)
    for other_player in filtered_other_players:
        if player_role == "seller" and new_value <= other_player.last_offer or player_role == "buyer" and new_value >= other_player.last_offer:
            logger.info("match!")
            return other_player
    return None

def find_match_and_get_other_player(new_value, player_role, optional_player_id, other_role_players):
    if optional_player_id:
        other_player_id = optional_player_id
        other_player = get_other_player(other_player_id, other_role_players)

        if check_match_with(other_player, new_value):
            return other_player

    else:
        return find_matching_player(player_role, new_value, other_role_players)
