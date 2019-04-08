from channels import Group
from ..models import Player

def clear_bet(user_id):
    player = Player.objects.get(id=user_id)
    player.last_offer = None
    player.save()
    return [{
        "player_id": player.id,
        "type": "clear"
    }]
