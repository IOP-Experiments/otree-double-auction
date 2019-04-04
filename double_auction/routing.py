from channels.routing import route
from .consumers import websocket_connect, websocket_message, websocket_disconnect
from otree.channels.routing import channel_routing
from channels.routing import include, route_class

from otreeutils.admin_extensions.routing import channel_routing


double_auction_routing = [route("websocket.connect",
                websocket_connect,  path=r'^/(?P<code>\w+)$'),
                route("websocket.receive",
                websocket_message,  path=r'^/(?P<code>\w+)$'),
                route("websocket.disconnect",
                websocket_disconnect,  path=r'^/(?P<code>\w+)$'), ]
channel_routing += [
    include(double_auction_routing, path=r"^/double-auction"),
]
