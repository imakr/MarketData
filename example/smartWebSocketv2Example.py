"""
    Created on Monday Feb 2 2022

    @author: Nishant Jain

    :copyright: (c) 2022 by Angel One Limited
"""

from SmartApi.smartWebSocketV2 import SmartWebSocketV2

AUTH_TOKEN = 'Bearer eyJhbGci.....'
API_KEY = 'YOUR_API_KEY'
CLIENT_CODE = 'YOUR_CLIENT_CODE'
FEED_TOKEN = 'YOUR_FEED_TOKEN'

correlation_id = "arun_123_qwerty"
action = 1
mode = 3

token_list = [{"exchangeType": 5, "tokens": ["247456"]}]

sws = SmartWebSocketV2(AUTH_TOKEN, API_KEY, CLIENT_CODE, FEED_TOKEN)


def on_data(wsapp, message):
    print("Ticks: {}".format(message))


def on_open(wsapp):
    print("on open")
    sws.subscribe(correlation_id, mode, token_list)


def on_error(wsapp, error):
    print(error)


def on_close(wsapp):
    print("Close")


# Assign the callbacks.
sws.on_open = on_open
sws.on_data = on_data
sws.on_error = on_error
sws.on_close = on_close

sws.connect()


