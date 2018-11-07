from channels.routing import route
from .consumers import ws_message, ws_connect, ws_disconnect
from otree.channels.routing import channel_routing
from channels.routing import include, route_class


double_auction_routing = [route("websocket.connect",
                ws_connect,  path=r'^/(?P<code>\w+)$'),
                route("websocket.receive",
                ws_message,  path=r'^/(?P<code>\w+)$'),
                route("websocket.disconnect",
                ws_disconnect,  path=r'^/(?P<code>\w+)$'), ]
channel_routing += [
    include(double_auction_routing, path=r"^/double-auction"),
]
