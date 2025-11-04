"""
Script for running backtests on historical data.
This is the dry-run phase to test and refine the algorithm.
"""
import json
from datetime import datetime
from backtester import Backtester
from config import Config


def run_backtest(symbol: str, initial_capital: float = 10000, 
                start_date: str = None, end_date: str = None):
    """
    Run a backtest and display results.
    
    Args:
        symbol: Stock ticker to backtest
        initial_capital: Starting capital
        start_date: Start date (YYYY-MM-DD), optional
        end_date: End date (YYYY-MM-DD), optional
    """
    print("=" * 60)
    print(f"BACKTESTING: {symbol}")
    print("=" * 60)
    print(f"Initial Capital: ${initial_capital:,.2f}")
    print(f"Start Date: {start_date or 'Default (30 days)'}")
    print(f"End Date: {end_date or 'Today'}")
    print()
    
    backtester = Backtester(initial_capital=initial_capital)
    
    try:
        results = backtester.run_backtest(symbol, start_date, end_date)
        
        # Display results
        print("=" * 60)
        print("BACKTEST RESULTS")
        print("=" * 60)
        print(f"Initial Capital:     ${results['initial_capital']:,.2f}")
        print(f"Final Capital:       ${results['final_capital']:,.2f}")
        print(f"Total Return:        ${results['total_return']:,.2f}")
        print(f"Total Return %:      {results['total_return_pct']:.2f}%")
        print(f"Number of Trades:    {results['num_trades']}")
        print(f"Win Rate:            {results['win_rate']:.2f}%")
        print(f"Average Return:      {results['avg_return']:.2f}%")
        print(f"Max Drawdown:        {results['max_drawdown']:.2f}%")
        print()
        
        if results['num_trades'] > 0:
            print("=" * 60)
            print("RECENT TRADES")
            print("=" * 60)
            trades = results['trades'][-10:]  # Show last 10 trades
            for i, trade in enumerate(trades, 1):
                print(f"\nTrade {i}:")
                print(f"  Entry:  {trade['entry_time']} @ ${trade['entry_price']:.2f}")
                print(f"  Exit:   {trade['exit_time']} @ ${trade['exit_price']:.2f}")
                print(f"  Shares: {trade['shares']}")
                print(f"  P&L:    ${trade['pnl']:.2f} ({trade['return_pct']:.2f}%)")
                print(f"  Reason: {trade['exit_reason']}")
        
        # Save results to file
        output_file = f"backtest_results/{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        import os
        os.makedirs('backtest_results', exist_ok=True)
        with open(output_file, 'w') as f:
            # Convert datetime objects to strings for JSON serialization
            results_copy = results.copy()
            results_copy['trades'] = [
                {k: str(v) if isinstance(v, datetime) else v 
                 for k, v in trade.items()} 
                for trade in results_copy['trades']
            ]
            json.dump(results_copy, f, indent=2, default=str)
        
        print(f"\nResults saved to: {output_file}")
        
    except Exception as e:
        print(f"Error during backtest: {e}")
        raise


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python backtest.py <SYMBOL> [start_date] [end_date]")
        print("Example: python backtest.py AAPL 2024-01-01 2024-01-31")
        sys.exit(1)
    
    symbol = sys.argv[1].upper()
    start_date = sys.argv[2] if len(sys.argv) > 2 else None
    end_date = sys.argv[3] if len(sys.argv) > 3 else None
    
    run_backtest(symbol, initial_capital=10000, start_date=start_date, end_date=end_date)

