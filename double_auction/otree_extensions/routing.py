from channels.routing import route_class
from .consumers import DoubleAuctionWebSocketConsumer

channel_routing = [
    DoubleAuctionWebSocketConsumer.as_route(path=r"^/double-auction/(?P<code>\w+)$")
]
