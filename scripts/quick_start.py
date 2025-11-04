"""
Quick start script to demonstrate the trading system.
Run this to see the system in action without needing API keys.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


from strategy import TradingStrategy
from data_fetcher import DataFetcher
from backtester import Backtester


def quick_demo():
    """Run a quick demonstration of the trading system"""
    
    print("=" * 60)
    print("STOCK TRADING BOT - QUICK START DEMO")
    print("=" * 60)
    print()
    
    # Step 1: Fetch data
    print("Step 1: Fetching market data...")
    data_fetcher = DataFetcher(source='yfinance')
    symbol = 'AAPL'
    
    try:
        df = data_fetcher.fetch_data(symbol, period=30)
        print(f"✓ Fetched {len(df)} data points for {symbol}")
        print(f"  Date range: {df.index[0]} to {df.index[-1]}")
        print(f"  Latest price: ${df['close'].iloc[-1]:.2f}")
        print()
    except Exception as e:
        print(f"✗ Error fetching data: {e}")
        return
    
    # Step 2: Analyze with strategy
    print("Step 2: Analyzing with trading strategy...")
    strategy = TradingStrategy()
    analyzed_df = strategy.analyze(df)
    
    latest = analyzed_df.iloc[-1]
    print(f"✓ Analysis complete")
    print(f"  Current RSI: {latest['rsi']:.2f}")
    print(f"  Fast MA: ${latest['fast_ma']:.2f}")
    print(f"  Slow MA: ${latest['slow_ma']:.2f}")
    print()
    
    # Step 3: Get current signal
    print("Step 3: Generating trading signal...")
    signal_info = strategy.get_current_signal(df)
    print(f"✓ Signal: {signal_info['signal'].upper()}")
    print(f"  Price: ${signal_info['price']:.2f}")
    print(f"  RSI: {signal_info['rsi']:.2f}")
    
    if signal_info['signal'] == 'buy':
        print(f"  Stop Loss: ${signal_info.get('stop_loss', 0):.2f}")
        print(f"  Take Profit: ${signal_info.get('take_profit', 0):.2f}")
    print()
    
    # Step 4: Quick backtest
    print("Step 4: Running quick backtest...")
    print("  (This may take a moment...)")
    
    try:
        backtester = Backtester(initial_capital=10000)
        results = backtester.run_backtest(symbol)
        
        print(f"✓ Backtest complete")
        print(f"  Initial Capital: ${results['initial_capital']:,.2f}")
        print(f"  Final Capital: ${results['final_capital']:,.2f}")
        print(f"  Total Return: {results['total_return_pct']:.2f}%")
        print(f"  Number of Trades: {results['num_trades']}")
        print(f"  Win Rate: {results['win_rate']:.2f}%")
        print()
    except Exception as e:
        print(f"✗ Backtest error: {e}")
        print()
    
    # Summary
    print("=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    print()
    print("🎉 Great! Now you're ready to explore more.")
    print()
    print("Next steps:")
    print("1. Launch the interactive menu:")
    print("   → python stocker.py")
    print()
    print("2. Then try these menu options:")
    print("   • Option 2 - Find trading opportunities")
    print("   • Option 3 - Run backtests on stocks")
    print("   • Option 4 - Visualize strategies")
    print("   • Option 5 - Practice with dry-run trading")
    print()
    print("💡 Tip: The menu is easier than remembering commands!")
    print()
    print("📚 See QUICKSTART.md for a 2-minute guided tour.")


if __name__ == '__main__':
    quick_demo()

