import json

class MatchMessage:
    def __init__(self, buyer, seller, value):
        self.seller = seller
        self.buyer = buyer
        self.value = value
    def getMessage(self):
        return json.dumps({
            "type": "match",
            "buyer": self.buyer,
            "seller": self.seller,
            "value": self.value
        })

class FailBidMessage:
    def getMessage(self):
        return json.dumps({
            "type": "error",
            "error": "BadBid"
        })
