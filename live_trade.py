"""
Script for live trading with real broker integration.
WARNING: This will execute real trades if dry_run=False.
Always test with dry_run=True first!
"""
import time
import sys
from trader import Trader
from config import Config


def run_live_trading(symbol: str, dry_run: bool = True, interval: int = 300):
    """
    Run live trading bot.
    
    Args:
        symbol: Stock ticker to trade
        dry_run: If True, only simulate trades (RECOMMENDED for testing)
        interval: Check interval in seconds (default 5 minutes)
    """
    print("=" * 60)
    print(f"LIVE TRADING BOT: {symbol}")
    print("=" * 60)
    print(f"Mode: {'DRY RUN (Simulation)' if dry_run else 'LIVE TRADING (Real Money)'}")
    print(f"Check Interval: {interval} seconds")
    print()
    
    if not dry_run:
        response = input("⚠️  WARNING: This will execute REAL TRADES with REAL MONEY!\n"
                        "Are you sure you want to continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Cancelled.")
            return
    
    trader = Trader(symbol, paper_trading=True)  # Always use paper trading initially
    
    print("Starting trading bot...")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            # Get status
            status = trader.get_status()
            
            print(f"\n[{status['current_signal']['timestamp']}]")
            print(f"Signal: {status['current_signal']['signal']}")
            print(f"Price: ${status['current_signal']['price']:.2f}")
            print(f"RSI: {status['current_signal']['rsi']:.2f}")
            
            # Check and execute
            result = trader.check_and_execute(dry_run=dry_run)
            
            print(f"Action: {result['action']}")
            print(f"Message: {result['message']}")
            
            # Show account info
            account = status['account']
            print(f"Buying Power: ${account['buying_power']:,.2f}")
            print(f"Portfolio Value: ${account['portfolio_value']:,.2f}")
            
            # Show positions
            if status['positions']:
                print("\nPositions:")
                for pos in status['positions']:
                    print(f"  {pos['symbol']}: {pos['qty']} shares @ ${pos['avg_entry_price']:.2f} "
                          f"(P&L: ${pos['unrealized_pl']:.2f})")
            
            print("\n" + "-" * 60)
            
            # Wait before next check
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n\nTrading bot stopped by user.")
    except Exception as e:
        print(f"\n\nError: {e}")
        raise


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python live_trade.py <SYMBOL> [--live]")
        print("Example: python live_trade.py AAPL")
        print("Example: python live_trade.py AAPL --live  # WARNING: Real trades!")
        sys.exit(1)
    
    symbol = sys.argv[1].upper()
    dry_run = '--live' not in sys.argv
    
    if not dry_run:
        print("⚠️  WARNING: --live flag detected. This will execute REAL trades!")
        print("⚠️  Make sure you have tested thoroughly with dry_run=True first!")
        print("⚠️  Consider using paper trading account first!")
        time.sleep(5)
    
    run_live_trading(symbol, dry_run=dry_run, interval=300)  # Check every 5 minutes

