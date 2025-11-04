# Stocker - Quick Start Guide

## 🚀 Getting Started (30 seconds)

### Run the Interactive UI
```bash
# 1. Install dependencies (one time only)
pip install -r requirements.txt

# 2. Launch the interactive menu
python stocker.py
```

**That's it!** The menu system will guide you through everything. No commands to memorize!

---

## 📋 Main Menu Options

```
╔═══════════════════════════════════════════════════════════╗
║                    STOCKER v1.0                          ║
╚═══════════════════════════════════════════════════════════╝

1. 🚀 Quick Start Demo        - See system in action (no setup needed)
2. 🔍 Identify Stocks         - Find trading opportunities
3. 📊 Run Backtest            - Test strategy on historical data
4. 📈 Visualize Strategy      - Create charts (requires matplotlib)
5. 🤖 Live Trading (Dry Run) - Simulate trading (no money)
6. 💰 Live Trading (Paper)    - Trade with fake money (needs Alpaca)
7. ⚙️  Configuration          - View current settings
8. 📋 View Logs               - Check recent logs
9. 📊 Monitoring Report       - System health & metrics
0. ❌ Exit
```

---

## 🎯 Recommended Learning Path

### 👉 First-Time Users - Do This!

```bash
python stocker.py
```

Then follow this path:

**Step 1**: Select **1** (Quick Demo)
- No setup needed
- Automatic demonstration
- See the system in action
- Takes 30 seconds

**Step 2**: Select **3** (Backtest)
- Enter: `AAPL`
- Press Enter for defaults
- See historical performance
- Review win rate and trades

**Step 3**: Select **2** (Identify Stocks)
- Screens 14 popular stocks
- Find trading opportunities
- Compare signals

**Step 4**: Select **5** (Dry Run)
- Enter: `AAPL`
- Enter: `300` (check every 5 minutes)
- Watch real-time signals
- No money at risk
- Press Ctrl+C to stop

**Done!** You've learned the system. 🎉

### 📈 For Paper Trading (Optional)

**Step 5**: Setup Alpaca (one time)
- Go to https://alpaca.markets
- Sign up (free)
- Get API keys
- Add to `.env` file

**Step 6**: Select **6** (Paper Trading)
- Uses fake money
- Real order execution
- Build confidence

**Step 7**: Monitor with **7**, **8**, **9**
- Check configuration
- Review logs
- Track metrics

---

## 🎮 Usage

### Recommended: Interactive Menu (Easiest!)
```bash
python stocker.py
```
Then select from the menu:
- **1** for Quick Demo
- **3** for Backtest  
- **2** for Stock Screening
- **5** for Dry Run Trading
- **0** to Exit

### Alternative: Direct Script Execution (For Automation)
If you need command-line scripts for automation:
```bash
python quick_start.py              # Quick demo
python backtest.py AAPL            # Backtest a stock
python identify_stock.py           # Identify opportunities
python live_trade.py AAPL          # Dry run trading
```

**💡 Tip**: Use the menu for learning and manual operations. Use scripts for automation and scheduled tasks.

---

## ⚙️ Configuration (Optional)

### No Configuration Needed For:
- ✅ Quick Start Demo
- ✅ Backtesting
- ✅ Stock Identification
- ✅ Visualization
- ✅ Dry Run Trading

### Requires Setup:
- 💰 Paper Trading - Need Alpaca API keys

### Setup Alpaca (5 minutes)

1. Create `.env` file:
```bash
cp .env.example .env
```

2. Get Alpaca keys:
   - Go to https://alpaca.markets
   - Sign up for free
   - Get API keys from dashboard

3. Edit `.env`:
```bash
ALPACA_API_KEY=your_key_here
ALPACA_SECRET_KEY=your_secret_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets
```

---

## 📊 Sample Session (Copy & Paste!)

**Launch the UI:**
```bash
python stocker.py
```

**Then type these numbers when prompted:**
```
1    # Watch the quick demo
     # (Press Enter when done)

3    # Run a backtest
AAPL # Enter stock symbol
     # (Press Enter twice for defaults)
     # (Review results, press Enter)

2    # Identify stocks
y    # Confirm
     # (Wait ~1 minute, review, press Enter)

5    # Try dry run trading
AAPL # Enter symbol
300  # Check every 5 minutes
     # (Watch for a bit, press Ctrl+C to stop)
     # (Press Enter)

0    # Exit
```

**That's it!** You've:
- ✅ Seen a demo
- ✅ Run a backtest
- ✅ Found opportunities  
- ✅ Simulated trading

---

## 🆘 Troubleshooting

### "Module not found" errors?
```bash
pip install -r requirements.txt
```

### Can't backtest?
- Check internet connection (needs market data)
- Try a different stock symbol

### Alpaca connection fails?
- Check `.env` file has correct keys
- Verify account is active
- Use paper trading URL first

### Import errors?
```bash
# Activate virtual environment
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

---

## 🎓 Learning Tips

1. **Start with Menu System** - It's easier than remembering commands
2. **Run Demo First** - See what's possible
3. **Use Backtesting** - Test before trading
4. **Check Visualizations** - Understand signals visually
5. **Monitor Everything** - Use logs and metrics
6. **Never Skip Paper Trading** - Test with fake money first

---

## 📚 More Resources

- **README.md** - Complete documentation
- **SUMMARY.md** - Project overview
- **ENHANCEMENTS.md** - Advanced features
- **Tests** - Run `pytest tests/ -v`

---

## ⚠️ Important Reminders

- 📚 This is **educational software**
- 💰 Always test with **fake money first**
- 📊 Past performance ≠ future results
- 🛡️ Never risk more than you can afford to lose
- 🧪 Paper trade extensively before going live

---

## 🎉 You're Ready!

**Just run this ONE command:**
```bash
python stocker.py
```

Then follow the menu. It's that simple!

---

## 💡 Pro Tips

1. **Start with Option 1** - Always run the demo first
2. **Use the Menu** - It's easier than remembering commands
3. **Backtest Everything** - Test before trading
4. **Dry Run First** - Simulate before using money
5. **Check Option 7** - Review configuration anytime
6. **Monitor Option 9** - Track system health

## 🚀 Next Steps

After you're comfortable with the UI:
1. Read `README.md` for complete documentation
2. Check `CONSOLE_UI.md` for UI details
3. Review `ENHANCEMENTS.md` for advanced features
4. Run tests: `pytest tests/ -v`

## ⚡ Quick Reference

| Want to... | Menu Option |
|------------|-------------|
| See a demo | 1 |
| Find stocks to trade | 2 |
| Test a strategy | 3 |
| See pretty charts | 4 |
| Practice trading | 5 |
| Paper trade | 6 |
| Check settings | 7 |
| Debug issues | 8 |
| View metrics | 9 |

---

**Happy Trading!** 📈 (But remember: test thoroughly first! 🧪)

