
class MatchMessage:
    def __init__(self, buyer, seller, value):
        self.seller = seller
        self.buyer = buyer
        self.value = value
    def getMessage(self):
        return {
            "type": "action.match",
            "buyer": self.buyer,
            "seller": self.seller,
            "value": self.value
        }

class FailBidMessage:
    def getMessage(self):
        return {
            "type": "action.error",
            "error": "BadBid"
        }
