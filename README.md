# Stocker - Algorithmic Trading System

A Python-based algorithmic trading system featuring multiple strategies, backtesting, live trading simulation, and comprehensive analysis tools.

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the interactive console (recommended)
python scripts/stocker.py

# 3. Try the quick demo
python scripts/quick_start.py
```

See [QUICKSTART.md](QUICKSTART.md) for detailed getting started guide.

## 📁 Project Structure

```
stocker/
├── README.md                 # This file
├── QUICKSTART.md             # Getting started guide
├── requirements.txt          # Python dependencies
│
├── src/                      # Core modules
│   ├── config.py            # Configuration
│   ├── data_fetcher.py      # Market data fetching
│   ├── data_cache.py        # Data caching system
│   ├── strategy.py          # Base strategy
│   ├── strategies.py        # Multi-strategy system
│   ├── backtester.py        # Backtesting engine
│   ├── broker.py            # Broker integration (Alpaca)
│   ├── trader.py            # Live trading bot
│   ├── logger.py            # Structured logging
│   ├── monitoring.py        # Monitoring & metrics
│   └── validation.py        # Data validation
│
├── scripts/                  # User-facing scripts
│   ├── stocker.py           # Interactive console UI (START HERE)
│   ├── quick_start.py       # Quick demonstration
│   ├── identify_stock.py    # Stock screener
│   ├── backtest.py          # Backtesting tool
│   ├── after_hours_planning.py  # After-hours planner
│   ├── visualize.py         # Strategy visualization
│   └── live_trade.py        # Live trading
│
├── tests/                    # Test suite
├── docs/                     # Documentation
│   └── STRATEGIES.md        # Strategy guide
│
└── output/                   # Generated files
    ├── backtest_results/
    ├── trading_plans/
    └── logs/
```

## ✨ Features

### Three Trading Strategies
- **Conservative**: Fewer trades, stricter conditions, lower risk
- **Balanced**: Moderate trades, balanced signals (DEFAULT)
- **Aggressive**: More trades, looser conditions, higher risk

### Core Capabilities
- 📊 **Stock Screening**: Analyze 60+ stocks for trading opportunities
- 🔄 **Backtesting**: Test strategies on historical data (6 months default)
- 📈 **Visualization**: Chart strategies with buy/sell signals
- 🌙 **After-Hours Planning**: Generate trading plans for next session
- ⚖️ **Strategy Comparison**: Compare all strategies side-by-side
- 🤖 **Live Trading**: Paper trading and dry-run simulation
- 💾 **Data Caching**: Fetch once, analyze multiple times

## 🎯 Main Console UI

The easiest way to use the system:

```bash
python scripts/stocker.py
```

**Menu Options:**
1. Quick Start Demo
2. Identify Stocks (Stock Screener)
3. Run Backtest
4. Visualize Strategy
5. Live Trading (Dry Run)
6. Live Trading (Paper)
7. Configuration
8. View Logs
9. Monitoring Report
10. After-Hours Planning
11. Compare Strategies

## 📊 Usage Examples

### Stock Screening
```bash
python scripts/identify_stock.py
# Analyzes 60+ stocks and shows buy/sell/watch recommendations
```

### Backtesting
```bash
python scripts/backtest.py AAPL
# Tests strategy on AAPL over last 6 months
```

### Strategy Comparison
```bash
python scripts/stocker.py
# Choose Option 11 - Compare Strategies
# See which strategy works best for your stocks
```

### After-Hours Planning
```bash
python scripts/after_hours_planning.py aggressive
# Generates trading plan for tomorrow
```

## 🛠️ Configuration

Create `.env` file in project root:

```bash
# Data Source
DATA_SOURCE=yfinance

# Alpaca API (for live/paper trading)
ALPACA_API_KEY=your_key_here
ALPACA_SECRET_KEY=your_secret_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets  # Paper trading

# Strategy Parameters
FAST_MA_PERIOD=10
SLOW_MA_PERIOD=50
RSI_PERIOD=14
RSI_OVERSOLD=30
RSI_OVERBOUGHT=70
STOP_LOSS=0.05
TAKE_PROFIT=0.10
```

## 📈 Strategies Explained

### Conservative
- RSI: 25/75 thresholds
- MA: 15/60 periods
- Requires BOTH RSI recovery AND MA crossover
- **Best for**: Risk-averse traders, volatile markets

### Balanced (Default)
- RSI: 30/70 thresholds
- MA: 10/50 periods
- Uses OR logic for buy signals
- **Best for**: Most traders, general purpose

### Aggressive
- RSI: 35/65 thresholds
- MA: 8/40 periods
- Multiple entry conditions including momentum
- **Best for**: Active traders, trending markets

See [docs/STRATEGIES.md](docs/STRATEGIES.md) for detailed comparison.

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_strategy.py

# With verbose output
pytest -v
```

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 2 minutes
- **[docs/STRATEGIES.md](docs/STRATEGIES.md)** - Detailed strategy guide

## 🔧 Requirements

- Python 3.8+
- See `requirements.txt` for packages

## ⚠️ Disclaimer

This is educational software. **DO NOT use with real money without thorough testing.**

- Always start with paper trading
- Backtest extensively
- Understand the risks
- Never invest more than you can afford to lose

## 🤝 Contributing

This is a learning project. Feel free to:
- Report bugs
- Suggest improvements
- Add features
- Share feedback

## 📝 License

MIT License - See LICENSE file for details

## 🎓 Learning Resources

Built to learn about:
- Algorithmic trading
- Technical analysis (RSI, Moving Averages)
- Backtesting frameworks
- Trading psychology
- Risk management

---

**Happy Trading! 🚀** (With paper money first! 😉)
