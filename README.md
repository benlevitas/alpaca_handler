# alpaca_handler

Wrapper for [Alpaca's Commision Free Trading API](https://github.com/alpacahq/alpaca-trade-api-python) 

### Installation

From cloned repository folder:

```
python setup.py install
```

### Prerequisites

An Alpaca account is required in order to retrieve API pair keys. 
Link to [sign up](https://app.alpaca.markets/signup)

### Sample code

First, enter your Alpaca key pair.

```
key = 'ENTER KEY HERE'
secret_key = 'ENTER SECRET KEY HERE'
```

Next, You can use the Data module to retrieve real-time market data.

```
from alpaca_handler.data import Data
data = Data(key, secret_key, symbols=['AAPL', 'GE'], time_frame='1D')
data.await_open()  # Wait for open market before retrieving data
bars = data.get_bars(limit=50, columns=['open']) # Retrieve The last 50 open day prices
```

Finally, use the Portfolio module to connect to your Alpaca portfolio.
Here you can Retrieve portfolio information or make trades.

```
from alpaca_handler.data import Portfolio
portfolio = Portfolio(key, secret_key, staging=True)  # Staging means you are using your paper account
portfolio.trade('AAPL', 10, 'buy')
```

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
