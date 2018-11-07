from channels import Group
from ..models import Player
import json

def clear_bet(user_id):
    player = Player.objects.get(id=user_id)
    player.value = None
    player.save()
    return [json.dumps({
        "player_id": player.id,
        "type": "clear"
    })]
