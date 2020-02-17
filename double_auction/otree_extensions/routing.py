from django.conf.urls import url
from .consumers import DoubleAuctionWebSocketConsumer

websocket_routes = [
    url(r"^double-auction/(?P<code>\w+)$", DoubleAuctionWebSocketConsumer)
]
