#trade-bot
Here I prepared a script that generates a buy sell signal by using macd and bollinger band indicators together. 
By default It use Binance websocket and api. Please feel free to change any other exchange api.

First of All, You should run following comment to install necessary package:

```
pip3 install -r requirements.txt
```

Then you should change following fields with your own information:

```
BINANCE_API_KEY = "YOUR_BINANCE_API_KEY"
BINANCE_SECRET_KEY = "YOUR_BINANCE_SECRET_KEY"
```

Finally, on whichever currecy you want to run the strategy on, replace this field with that symbol. By default, eth is defined.

```
TRADE_SYMBOL = 'ETHUSDT'
```

Now You are ready run strategy. Happy Trading!!!

> **Important Notice:** Make sure you take your own risks while using this script. I cannot be held responsible for any loss.

