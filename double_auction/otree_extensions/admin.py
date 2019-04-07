from django.http import HttpResponse
from django.views import View

import csv

class DoubleAuctionCsv(View):
    url_pattern = '^double_auction/$'
    url_name = 'double_auction'
    display_name = 'Double Auction Export'

    def get(self, request, *args, **kwargs):
        print("Muhahaha This view gets called")
        response = HttpResponse(content_type='text/csv')
        return response

data_export_views = [
    DoubleAuctionCsv
]
