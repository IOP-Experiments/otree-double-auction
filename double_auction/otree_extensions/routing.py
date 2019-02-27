from .consumers import MarketConsumer
from otree.channels.routing import channel_routing
# from channels.routing import route_class


double_auction_routing = [route("websocket.connect",
                websocket_connect,  path=r'^/(?P<code>\w+)$'),
                route("websocket.receive",
                websocket_message,  path=r'^/(?P<code>\w+)$'),
                route("websocket.disconnect",
                websocket_disconnect,  path=r'^/(?P<code>\w+)$'), ]
channel_routing += [
    include(double_auction_routing, path=r"^/double-auction"),
]

