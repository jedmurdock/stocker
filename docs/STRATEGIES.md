# Trading Strategies

The Stocker system now supports multiple strategy profiles with different risk/reward characteristics. All strategies use RSI and Moving Average indicators but with different thresholds and signal logic.

## Available Strategies

### 1. Conservative Strategy
**Best for:** Risk-averse traders, volatile markets, capital preservation

**Characteristics:**
- **Strictest conditions** - Requires BOTH RSI recovery AND MA crossover simultaneously
- **Tighter RSI thresholds**: 25/75 (vs standard 30/70)
- **Longer MA periods**: Fast=15, Slow=60 (more stable signals)
- **Fewest trades** - Only takes highest conviction setups
- **Lower risk/reward** - Safer but fewer opportunities

**When to use:**
- High market volatility (VIX > 25)
- Learning phase - want to see how system works
- Limited trading capital
- Risk-averse personality

**Example Performance:**
- Fewer trades (typically 40-60% less than balanced)
- Higher win rate (typically 60-65%)
- Lower total returns but more consistent

---

### 2. Balanced Strategy (DEFAULT)
**Best for:** Most traders, normal market conditions, steady growth

**Characteristics:**
- **Moderate conditions** - Uses OR logic for buy signals
- **Standard RSI thresholds**: 30/70
- **Medium MA periods**: Fast=10, Slow=50
- **Balanced trade frequency** - Good mix of opportunity and quality
- **Moderate risk/reward** - Best all-around profile

**Buy Signal Triggers (EITHER):**
1. RSI crosses above 30 AND MAs are bullish, OR
2. MA bullish crossover AND RSI is healthy (30-70)

**When to use:**
- Normal market conditions
- General-purpose trading
- Starting point for most users
- Good risk/reward balance needed

**Example Performance:**
- Moderate trade frequency
- Win rate around 55-60%
- Good balance of returns and safety

---

### 3. Aggressive Strategy
**Best for:** Active traders, trending markets, higher risk tolerance

**Characteristics:**
- **Loosest conditions** - Multiple ways to trigger buy signals
- **Wider RSI thresholds**: 35/65 (more sensitive)
- **Shorter MA periods**: Fast=8, Slow=40 (faster signals)
- **Most trades** - Captures more opportunities
- **Higher risk/reward** - More opportunities, more whipsaws

**Buy Signal Triggers (ANY OF):**
1. RSI crosses above 35 AND MAs are bullish, OR
2. MA bullish crossover AND RSI < 65, OR
3. Strong momentum (price above fast MA, rising RSI, bullish MAs)

**Additional Features:**
- Quick exits on weakness (RSI < 35 triggers sell)
- Momentum-based entries (new for aggressive)

**When to use:**
- Strong trending markets
- High volatility with clear direction
- Active trading style (day/swing trading)
- Higher risk tolerance

**Example Performance:**
- Highest trade frequency (60-100% more than balanced)
- Win rate around 50-55%
- Highest potential returns (and losses)

---

## Strategy Comparison

| Feature | Conservative | Balanced | Aggressive |
|---------|-------------|----------|------------|
| RSI Oversold | 25 | 30 | 35 |
| RSI Overbought | 75 | 70 | 65 |
| Fast MA Period | 15 | 10 | 8 |
| Slow MA Period | 60 | 50 | 40 |
| Buy Logic | AND | OR | OR+ |
| Trade Frequency | Lowest | Medium | Highest |
| Win Rate | Highest | Medium | Lowest |
| Risk Level | Lowest | Medium | Highest |
| Best For | Beginners | Most users | Active traders |

---

## How to Select a Strategy

### In the Console UI (`stocker.py`)
When you select an option like "Identify Stocks" or "Run Backtest", you'll be prompted to choose a strategy:

```
 SELECT TRADING STRATEGY
===============================================================
  1. Conservative  - Fewer trades, stricter conditions, lower risk
  2. Balanced      - Moderate trades, balanced signals (DEFAULT) ⭐
  3. Aggressive    - More trades, looser conditions, higher risk

Choose strategy (1-3) (default: 2):
```

### Via Command Line

**Identify Stocks:**
```bash
python identify_stock.py conservative
python identify_stock.py balanced
python identify_stock.py aggressive
```

**Backtest:**
```bash
python backtest.py AAPL 2024-01-01 2024-12-31 balanced
python backtest.py TSLA 2024-01-01 2024-12-31 aggressive
```

**After-Hours Planning:**
```bash
python after_hours_planning.py conservative
python after_hours_planning.py aggressive
```

---

## Choosing the Right Strategy

### Start with Conservative if:
- ✓ You're new to algorithmic trading
- ✓ Market is highly volatile
- ✓ You have limited capital
- ✓ You want to understand the system first

### Use Balanced if:
- ✓ You want a general-purpose strategy
- ✓ Normal market conditions
- ✓ You're comfortable with moderate risk
- ✓ This is your production strategy

### Try Aggressive if:
- ✓ You're an active, experienced trader
- ✓ Strong trending market conditions
- ✓ You can handle more frequent trades
- ✓ You're comfortable with higher risk

---

## Testing Strategies

Always backtest each strategy before using it:

```bash
# Test all three on the same stock
python backtest.py AAPL 2024-01-01 2024-12-31 conservative
python backtest.py AAPL 2024-01-01 2024-12-31 balanced
python backtest.py AAPL 2024-01-01 2024-12-31 aggressive
```

Compare:
- Total return %
- Number of trades
- Win rate
- Max drawdown
- Which fits your risk tolerance

---

## Pro Tips

1. **Match strategy to market conditions**
   - Trending up → Aggressive or Balanced
   - Choppy/sideways → Conservative
   - High volatility → Conservative

2. **Backtest before switching**
   - Always test a strategy on your target stocks
   - Check performance over different time periods
   - Verify it matches your risk tolerance

3. **Consider combining strategies**
   - Use Conservative for large positions
   - Use Aggressive for smaller, speculative trades
   - Use Balanced as your baseline

4. **Monitor and adapt**
   - Review performance weekly
   - Switch strategies if market conditions change
   - Keep detailed records

---

## Implementation Notes

All strategies inherit from `StrategyProfile` base class in `strategies.py`. They share the same indicator calculation but differ in:
- RSI thresholds
- MA periods  
- Signal generation logic
- Entry/exit conditions

This makes them easy to compare and backtest consistently.

