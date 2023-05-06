import websocket, json, pprint
import numpy as np
import talib as ta
from binance.client import Client
from binance.enums import *


BINANCE_API_KEY = "YOUR_BINANCE_API_KEY"
BINANCE_SECRET_KEY = "YOUR_BINANCE_SECRET_KEY"

client = Client(api_key=BINANCE_API_KEY, api_secret=BINANCE_SECRET_KEY)

MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

BB_PERIOD = 20
BB_STD_DEVIATION = 2

TRADE_SYMBOL = 'ETHUSDT'
TRADE_QUANTITY = 0.05
STOP_LOSS_PERCENT = 0.02 

in_position = False
last_bb_upperband = None
last_bb_lowerband = None
last_macd = None

closes = []
bb_upperbands = []
bb_lowerbands = []
macds = []
signal_lines = []


def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET, stop_price=None):
    try:
        print("sending order")
        if order_type == ORDER_TYPE_MARKET:
            order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        elif order_type == ORDER_TYPE_STOP_LOSS:
            order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity, stopPrice=stop_price)
        pprint.pprint(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False

    return True


def on_open(ws):
    print('connection opened')

def on_close(ws):
    print('connection closed')

def on_error(ws, error):
    print(f'error occured: {error}')

def on_message(ws, message):
    global closes, in_position, last_boll_upper, last_boll_middle, last_boll_lower, last_macd, last_signal

    json_message = json.loads(message)
    candle = json_message['k']
    is_candle_closed = candle['x']
    close = float(candle['c'])

    if is_candle_closed:
        closes.append(close)
        if len(closes) > BB_PERIOD:
            np_closes = np.array(closes)
            boll_upper, boll_middle, boll_lower = ta.BBANDS(np_closes, timeperiod=BB_PERIOD, nbdevup=BB_STD_DEVIATION, nbdevdn=BB_STD_DEVIATION, matype=ta.MA_Type.SMA)
            last_boll_upper = boll_upper[-1]
            last_boll_middle = boll_middle[-1]
            last_boll_lower = boll_lower[-1]

            macd, signal, _ = ta.MACD(np_closes, fastperiod=MACD_FAST, slowperiod=MACD_SLOW, signalperiod=MACD_SIGNAL)
            last_macd = macd[-1]
            last_signal = signal[-1]

            if close <= last_boll_lower and last_macd < last_signal and not in_position:
                print("BUY")
                order_success = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                if order_success:
                    in_position = True
                    stop_loss_price = round(close * (1 - STOP_LOSS_PERCENT), 2)
                    order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL, order_type=ORDER_TYPE_STOP_LOSS, stop_price=stop_loss_price)
            elif close >= last_boll_upper and last_macd > last_signal and in_position:
                print("SELL")
                order_success = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                if order_success:
                    in_position = False
            print(f"Current Price: {close:.2f}")
            print(f"Last Bollinger Bands Upper: {last_boll_upper:.2f}")
            print(f"Last Bollinger Bands Middle: {last_boll_middle:.2f}")
            print(f"Last Bollinger Bands Lower: {last_boll_lower:.2f}")
            print(f"Last MACD: {last_macd:.2f}")
            print(f"Last Signal: {last_signal:.2f}")
            print(f"In Position: {in_position}")

def start_strategy(currency):
    SOCKET = f"wss://stream.binance.com:9443/ws/{currency}@kline_1m"
    ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message, on_error=on_error)
    ws.run_forever()


start_strategy(TRADE_SYMBOL.lower())