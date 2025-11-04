# Stock Trading Bot

A Python-based algorithmic trading system for learning about AI, stocks, and automated trading. This project implements a conservative day trading strategy using RSI (Relative Strength Index) and Moving Average crossovers, with three distinct phases: stock identification, backtesting, and live trading.

## Features

- **Conservative Trading Strategy**: RSI + Moving Average crossover pattern
- **Stock Identification**: Analyze multiple stocks to find trading opportunities
- **Backtesting Framework**: Test strategies on historical data before risking real money
- **Paper Trading**: Test with simulated money before going live
- **Live Trading**: Connect to Alpaca API for real trading (paper or live)
- **Risk Management**: Built-in stop-loss and take-profit mechanisms

## Project Structure

```
stocker/
├── config.py              # Configuration management
├── data_fetcher.py        # Data fetching (yfinance/Alpaca)
├── strategy.py            # Trading strategy implementation
├── backtester.py          # Backtesting engine
├── broker.py              # Broker integration (Alpaca)
├── trader.py              # Main trading bot
├── identify_stock.py      # Stock identification script
├── backtest.py            # Backtesting script
├── live_trade.py          # Live trading script
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## Strategy Overview

The trading strategy combines two well-known technical indicators:

1. **RSI (Relative Strength Index)**: Identifies overbought (>70) and oversold (<30) conditions
2. **Moving Averages**: Fast MA (9 periods) and Slow MA (21 periods) for trend identification

### Buy Signals
- RSI crosses above oversold level (30)
- Fast MA crosses above Slow MA (bullish crossover)
- Price is above both moving averages

### Sell Signals
- RSI crosses above overbought level (70)
- Fast MA crosses below Slow MA (bearish crossover)
- Stop loss or take profit triggered

### Risk Management
- 2% risk per trade (configurable)
- 2% stop loss
- 4% take profit (2:1 risk/reward ratio)

## Installation

1. **Clone or create the project directory**:
```bash
cd stocker
```

2. **Create a virtual environment** (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**:
Create a `.env` file in the project root:
```bash
# Alpaca API Credentials (get from https://alpaca.markets)
ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET_KEY=your_secret_key_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets  # Paper trading URL

# Trading Configuration
MAX_POSITION_SIZE=1000
RISK_PER_TRADE=0.02
STOP_LOSS_PCT=0.02
TAKE_PROFIT_PCT=0.04
```

## Usage

### Phase 1: Identify Stocks

Analyze multiple stocks to find trading opportunities:

```bash
python identify_stock.py
```

This will analyze a list of popular stocks and display:
- Stocks with buy signals
- Signal strength scores
- Current RSI and moving average values
- Volume information

You can modify the `symbols` list in `identify_stock.py` to analyze different stocks.

### Phase 2: Backtesting (Dry Runs)

Test your strategy on historical data before risking real money:

```bash
# Basic backtest
python backtest.py AAPL

# Backtest with specific date range
python backtest.py AAPL 2024-01-01 2024-01-31
```

The backtest will show:
- Total return and percentage
- Number of trades executed
- Win rate
- Average return per trade
- Maximum drawdown
- Detailed trade history

Results are saved to `backtest_results/` directory.

**Example Output**:
```
BACKTEST RESULTS
============================================================
Initial Capital:     $10,000.00
Final Capital:       $10,450.00
Total Return:        $450.00
Total Return %:      4.50%
Number of Trades:    15
Win Rate:            60.00%
Average Return:      1.20%
Max Drawdown:        -2.30%
```

### Phase 3: Live Trading

⚠️ **IMPORTANT**: Always start with paper trading and dry-run mode!

#### Step 1: Dry Run (Simulation)
```bash
python live_trade.py AAPL
```

This will:
- Monitor the stock every 5 minutes
- Show signals and potential actions
- **NOT execute any trades** (simulation only)

#### Step 2: Paper Trading (Alpaca Paper Account)
1. Sign up for a free Alpaca account: https://alpaca.markets
2. Get your API keys from the Alpaca dashboard
3. Add them to your `.env` file
4. Run with dry_run=False (still uses paper trading account):

```bash
python live_trade.py AAPL --live
```

This will execute real orders in Alpaca's **paper trading** environment (simulated money).

#### Step 3: Live Trading (Real Money)
⚠️ **WARNING**: Only proceed after extensive testing!

1. Change `ALPACA_BASE_URL` to `https://api.alpaca.markets` in `.env`
2. Ensure you have real API keys for live trading
3. Start with small position sizes
4. Monitor closely

```bash
python live_trade.py AAPL --live
```

## Configuration

Edit `config.py` or use environment variables to customize:

- **RSI Parameters**: `RSI_PERIOD`, `RSI_OVERSOLD`, `RSI_OVERBOUGHT`
- **Moving Average**: `FAST_MA_PERIOD`, `SLOW_MA_PERIOD`
- **Risk Management**: `RISK_PER_TRADE`, `STOP_LOSS_PCT`, `TAKE_PROFIT_PCT`
- **Position Sizing**: `MAX_POSITION_SIZE`

## Understanding the Strategy

### Why RSI + Moving Averages?

This combination is popular because:
- **RSI** helps identify when a stock is oversold (potential buy) or overbought (potential sell)
- **Moving Averages** confirm the trend direction
- Together, they reduce false signals and improve win rate

### Conservative Approach

The strategy is conservative because:
- Requires multiple confirmations (RSI + MA crossover + price position)
- Uses stop losses to limit losses
- Implements position sizing based on risk
- 2:1 risk/reward ratio (risk $2 to make $4)

### Limitations

- Past performance doesn't guarantee future results
- Market conditions change
- Algorithmic trading has risks
- Always start with paper trading

## Learning Resources

This project helps you learn:

1. **Python**: Data manipulation, API integration, OOP
2. **Stock Market**: Technical analysis, indicators, trading strategies
3. **AI/ML Basics**: Algorithm development, backtesting, optimization
4. **Risk Management**: Position sizing, stop losses, portfolio management

## Next Steps / Improvements

Consider these enhancements:
- Add more technical indicators (MACD, Bollinger Bands)
- Implement machine learning for signal prediction
- Add portfolio management (multiple stocks)
- Create a web dashboard for monitoring
- Add email/SMS alerts for trades
- Optimize parameters using genetic algorithms
- Add order types (limit orders, trailing stops)

## Important Disclaimers

⚠️ **Trading Risk Warning**:
- Trading stocks involves substantial risk of loss
- Past performance does not guarantee future results
- This is educational software - use at your own risk
- Always test thoroughly before using real money
- Start with paper trading and small positions
- Never risk more than you can afford to lose

⚠️ **Legal Disclaimer**:
- This software is for educational purposes only
- Not financial advice
- The authors are not responsible for trading losses
- Ensure compliance with your local regulations

## Testing

The project includes a comprehensive test suite to ensure core behaviors work correctly.

### Running Tests

1. **Install test dependencies** (if not already installed):
   ```bash
   pip install -r requirements.txt
   ```

2. **Run all tests**:
   ```bash
   pytest tests/ -v
   ```
   
   Or use the test runner:
   ```bash
   python run_tests.py
   ```

3. **Run specific test files**:
   ```bash
   pytest tests/test_strategy.py -v
   pytest tests/test_backtester.py -v
   ```

4. **Run tests with coverage** (optional):
   ```bash
   pip install pytest-cov
   pytest tests/ --cov=. --cov-report=html
   ```

### Test Structure

- **`tests/test_config.py`** - Configuration loading and defaults
- **`tests/test_strategy.py`** - Trading strategy calculations and signals
- **`tests/test_data_fetcher.py`** - Data fetching functionality
- **`tests/test_backtester.py`** - Backtesting engine
- **`tests/test_integration.py`** - Integration tests (may be slower)

### What's Tested

✅ **Strategy Module**:
- RSI and Moving Average calculations
- Signal generation logic
- Buy/sell signal conditions
- Edge cases (empty data, minimal data)

✅ **Data Fetcher**:
- yfinance integration
- Alpaca integration (mocked)
- Error handling for invalid symbols
- Data format standardization

✅ **Backtester**:
- Trade simulation
- Portfolio value tracking
- Performance metrics calculation
- Win rate and return calculations

✅ **Integration**:
- End-to-end backtest flow
- Strategy consistency
- Config integration

### Writing Your Own Tests

Tests use `pytest` and follow standard Python testing patterns:

```python
def test_my_feature():
    """Test description"""
    # Arrange
    data = create_test_data()
    
    # Act
    result = my_function(data)
    
    # Assert
    assert result == expected_value
```

See existing tests in `tests/` for examples.

## Troubleshooting

### "No data found for symbol"
- Check if the symbol is valid
- Ensure you have internet connection
- Some symbols may not have 5-minute data available

### "Failed to connect to broker"
- Verify your Alpaca API keys in `.env`
- Check if you're using the correct base URL (paper vs live)
- Ensure your Alpaca account is active

### Import errors
- Make sure you've installed all dependencies: `pip install -r requirements.txt`
- Check that you're using the correct Python version (3.8+)

## License

This project is for educational purposes. Use at your own risk.

## Contributing

Feel free to fork, modify, and improve this project for your own learning!

---

**Happy Trading!** 📈 (But remember: paper trade first! 🧪)

