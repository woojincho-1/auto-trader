import os
import requests
import time
import hmac
import hashlib
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
BASE_URL = os.getenv("BINANCE_API_BASE")

headers = {
    "X-MBX-APIKEY": API_KEY
}

def _sign(params):
    query_string = urlencode(params)
    signature = hmac.new(API_SECRET.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    return query_string + "&signature=" + signature

def get_price(symbol):
    return requests.get(f"{BASE_URL}/fapi/v1/ticker/bookTicker", params={"symbol": symbol}).json()

def get_balance():
    timestamp = int(time.time() * 1000)
    params = {"timestamp": timestamp}
    url = f"{BASE_URL}/fapi/v2/balance?" + _sign(params)
    return requests.get(url, headers=headers).json()

def set_leverage(symbol, leverage):
    timestamp = int(time.time() * 1000)
    params = {
        "symbol": symbol,
        "leverage": leverage,
        "timestamp": timestamp
    }
    url = f"{BASE_URL}/fapi/v1/leverage?" + _sign(params)
    return requests.post(url, headers=headers)

def get_position(symbol):
    timestamp = int(time.time() * 1000)
    params = {"timestamp": timestamp}
    url = f"{BASE_URL}/fapi/v2/positionRisk?" + _sign(params)
    positions = requests.get(url, headers=headers).json()
    return next((p for p in positions if p["symbol"] == symbol), None)

def place_order(symbol, side, qty, price):
    timestamp = int(time.time() * 1000)
    params = {
        "symbol": symbol,
        "side": side,
        "type": "LIMIT",
        "timeInForce": "GTX",
        "quantity": qty,
        "price": price,
        "timestamp": timestamp
    }
    url = f"{BASE_URL}/fapi/v1/order?" + _sign(params)
    return requests.post(url, headers=headers).json()
