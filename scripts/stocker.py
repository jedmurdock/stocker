#!/usr/bin/env python3
"""
Stocker - Interactive Console UI for the Stock Trading System
Main entry point for all trading operations.
"""
import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from typing import Optional
from strategies import list_strategies, DEFAULT_STRATEGY

# ASCII art logo
LOGO = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     ███████╗████████╗ ██████╗  ██████╗██╗  ██╗███████╗██████╗
║     ██╔════╝╚══██╔══╝██╔═══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗
║     ███████╗   ██║   ██║   ██║██║     █████╔╝ █████╗  ██████╔╝
║     ╚════██║   ██║   ██║   ██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗
║     ███████║   ██║   ╚██████╔╝╚██████╗██║  ██╗███████╗██║  ██║
║     ╚══════╝   ╚═╝    ╚═════╝  ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
║                                                           ║
║            Algorithmic Trading System v1.0                ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""


class StockerUI:
    """Interactive console UI for the trading system"""
    
    def __init__(self):
        self.running = True
    
    def clear_screen(self):
        """Clear the console screen"""
        os.system('clear' if os.name != 'nt' else 'cls')
    
    def print_header(self):
        """Print the application header"""
        self.clear_screen()
        print(LOGO)
        print()
    
    def print_menu(self):
        """Print the main menu"""
        print("=" * 63)
        print("MAIN MENU")
        print("=" * 63)
        print()
        print("  1. 🚀 Quick Start Demo        - See the system in action")
        print("  2. 🔍 Identify Stocks         - Find trading opportunities")
        print("  3. 📊 Run Backtest            - Test strategy on history")
        print("  4. 📈 Visualize Strategy      - Create strategy charts")
        print("  5. 🤖 Live Trading (Dry Run) - Simulate trading")
        print("  6. 💰 Live Trading (Paper)    - Trade with fake money")
        print("  7. ⚙️  Configuration          - View/edit settings")
        print("  8. 📋 View Logs               - Check recent logs")
        print("  9. 📊 Monitoring Report       - System health & metrics")
        print("  10. 🌙 After-Hours Planning   - Plan tomorrow's trades")
        print("  11. ⚖️  Compare Strategies     - Test all strategies side-by-side")
        print()
        print("  0. ❌ Exit")
        print()
        print("=" * 63)
    
    def get_input(self, prompt: str, default: Optional[str] = None) -> str:
        """Get user input with optional default"""
        if default:
            prompt = f"{prompt} (default: {default})"
        
        value = input(f"{prompt}: ").strip()
        return value if value else (default if default else "")
    
    def select_strategy(self) -> str:
        """Let user select a strategy"""
        print("\n" + "=" * 63)
        print(" SELECT TRADING STRATEGY")
        print("=" * 63)
        
        strategies = list_strategies()
        strategy_names = list(strategies.keys())
        
        for i, (name, info) in enumerate(strategies.items(), 1):
            marker = " ⭐" if name == DEFAULT_STRATEGY else ""
            print(f"  {i}. {info['name']:12} - {info['description']}{marker}")
        
        print()
        choice = self.get_input(f"Choose strategy (1-{len(strategies)})", "2")
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(strategy_names):
                selected = strategy_names[idx]
                print(f"\n✅ Selected: {strategies[selected]['name']}")
                return selected
        except (ValueError, IndexError):
            pass
        
        print(f"\n⚠️  Invalid choice, using default: {DEFAULT_STRATEGY}")
        return DEFAULT_STRATEGY
    
    def pause(self):
        """Pause and wait for user to press enter"""
        print()
        input("Press Enter to continue...")
    
    def run_quick_start(self):
        """Run the quick start demo"""
        self.print_header()
        print("🚀 QUICK START DEMO")
        print("=" * 63)
        print()
        print("Running quick demo to showcase system features...")
        print()
        
        try:
            from quick_start import quick_demo
            quick_demo()
        except Exception as e:
            print(f"❌ Error: {e}")
        
        self.pause()
    
    def run_identify_stocks(self):
        """Run stock identification"""
        self.print_header()
        print("🔍 IDENTIFY TRADING OPPORTUNITIES")
        print("=" * 63)
        print()
        print("This will analyze popular stocks for trading signals.")
        print()
        
        # Select strategy
        strategy_name = self.select_strategy()
        
        print()
        try:
            # Import and run
            import pandas as pd
            from identify_stock import identify_potential_stocks
            
            # Expanded stock universe for better opportunity discovery
            symbols = [
                # Mega Cap Tech
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA',
                # Tech & Semiconductors
                'AMD', 'INTC', 'AVGO', 'QCOM', 'MU', 'AMAT', 'LRCX', 'KLAC',
                # Software & Cloud
                'ORCL', 'CRM', 'ADBE', 'NOW', 'PANW', 'SNOW', 'DDOG',
                # Streaming & Media
                'NFLX', 'DIS', 'SPOT', 'RBLX',
                # E-commerce & Payments
                'SHOP', 'SQ', 'PYPL', 'V', 'MA',
                # Auto & Energy
                'F', 'GM', 'RIVN', 'LCID', 'XLE', 'XOM', 'CVX',
                # Finance
                'JPM', 'BAC', 'GS', 'MS', 'C', 'WFC',
                # Healthcare & Biotech
                'JNJ', 'UNH', 'PFE', 'ABBV', 'TMO', 'DHR',
                # Consumer
                'WMT', 'TGT', 'COST', 'HD', 'LOW', 'NKE', 'SBUX',
                # ETFs for broader signals
                'SPY', 'QQQ', 'IWM', 'DIA', 'XLF', 'XLK', 'XLV'
            ]
            
            results = identify_potential_stocks(symbols, strategy_name=strategy_name)
            
            if not results.empty:
                print("\n" + "=" * 63)
                print("TOP TRADING OPPORTUNITIES")
                print("=" * 63)
                print(results[['symbol', 'signal', 'signal_strength', 'price', 'rsi']].head(10).to_string(index=False))
            else:
                print("\n❌ No opportunities found.")
        
        except Exception as e:
            print(f"❌ Error: {e}")
        
        self.pause()
    
    def run_backtest(self):
        """Run a backtest"""
        self.print_header()
        print("📊 RUN BACKTEST")
        print("=" * 63)
        print()
        
        symbol = self.get_input("Enter stock symbol (e.g., AAPL)", "AAPL").upper()
        capital = self.get_input("Initial capital", "10000")
        start_date = self.get_input("Start date (YYYY-MM-DD, or blank for default)", None)
        end_date = self.get_input("End date (YYYY-MM-DD, or blank for today)", None)
        
        # Select strategy
        strategy_name = self.select_strategy()
        
        print()
        print(f"Running backtest for {symbol}...")
        print()
        
        try:
            from backtest import run_backtest as run_backtest_func
            run_backtest_func(symbol, float(capital), start_date, end_date, strategy_name)
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        self.pause()
    
    def run_visualize(self):
        """Create strategy visualization"""
        self.print_header()
        print("📈 VISUALIZE STRATEGY")
        print("=" * 63)
        print()
        
        symbol = self.get_input("Enter stock symbol (e.g., AAPL)", "AAPL").upper()
        days = self.get_input("Number of days to analyze", "30")
        
        print()
        print(f"Creating visualization for {symbol}...")
        print()
        
        try:
            from visualize import visualize_strategy
            visualize_strategy(symbol, int(days))
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        self.pause()
    
    def run_dry_run_trading(self):
        """Run live trading in dry-run mode"""
        self.print_header()
        print("🤖 LIVE TRADING - DRY RUN (SIMULATION)")
        print("=" * 63)
        print()
        print("⚠️  This will SIMULATE trading without executing real orders.")
        print()
        
        symbol = self.get_input("Enter stock symbol (e.g., AAPL)", "AAPL").upper()
        interval = self.get_input("Check interval in seconds", "300")
        
        print()
        print(f"Starting dry-run trading for {symbol}...")
        print("Press Ctrl+C to stop")
        print()
        
        try:
            from live_trade import run_live_trading
            run_live_trading(symbol, dry_run=True, interval=int(interval))
        except KeyboardInterrupt:
            print("\n\n✋ Trading stopped by user.")
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        self.pause()
    
    def run_paper_trading(self):
        """Run live trading with paper account"""
        self.print_header()
        print("💰 LIVE TRADING - PAPER TRADING")
        print("=" * 63)
        print()
        print("⚠️  This will execute trades with PAPER MONEY (simulated).")
        print("⚠️  Requires Alpaca API credentials in .env file.")
        print()
        
        # Check for credentials
        from config import Config
        config = Config()
        if not config.ALPACA_API_KEY or not config.ALPACA_SECRET_KEY:
            print("❌ Error: Alpaca API credentials not configured!")
            print("Please set ALPACA_API_KEY and ALPACA_SECRET_KEY in .env file.")
            self.pause()
            return
        
        symbol = self.get_input("Enter stock symbol (e.g., AAPL)", "AAPL").upper()
        interval = self.get_input("Check interval in seconds", "300")
        
        print()
        confirm = self.get_input("Confirm paper trading? (yes/no)", "no").lower()
        if confirm != 'yes':
            print("❌ Cancelled.")
            self.pause()
            return
        
        print()
        print(f"Starting paper trading for {symbol}...")
        print("Press Ctrl+C to stop")
        print()
        
        try:
            from live_trade import run_live_trading
            run_live_trading(symbol, dry_run=False, interval=int(interval))
        except KeyboardInterrupt:
            print("\n\n✋ Trading stopped by user.")
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        self.pause()
    
    def show_configuration(self):
        """Display current configuration"""
        self.print_header()
        print("⚙️  CONFIGURATION")
        print("=" * 63)
        print()
        
        from config import Config
        config = Config()
        
        print("Trading Parameters:")
        print(f"  Max Position Size:    ${config.MAX_POSITION_SIZE:,.2f}")
        print(f"  Risk Per Trade:       {config.RISK_PER_TRADE * 100:.1f}%")
        print(f"  Stop Loss:            {config.STOP_LOSS_PCT * 100:.1f}%")
        print(f"  Take Profit:          {config.TAKE_PROFIT_PCT * 100:.1f}%")
        print()
        
        print("Strategy Parameters:")
        print(f"  RSI Period:           {config.RSI_PERIOD}")
        print(f"  RSI Oversold:         {config.RSI_OVERSOLD}")
        print(f"  RSI Overbought:       {config.RSI_OVERBOUGHT}")
        print(f"  Fast MA Period:       {config.FAST_MA_PERIOD}")
        print(f"  Slow MA Period:       {config.SLOW_MA_PERIOD}")
        print()
        
        print("Data Parameters:")
        print(f"  Timeframe:            {config.DATA_TIMEFRAME}")
        print(f"  Lookback Days:        {config.LOOKBACK_DAYS}")
        print()
        
        print("API Configuration:")
        api_configured = bool(config.ALPACA_API_KEY and config.ALPACA_SECRET_KEY)
        print(f"  Alpaca API:           {'✅ Configured' if api_configured else '❌ Not configured'}")
        print(f"  Base URL:             {config.ALPACA_BASE_URL}")
        print()
        
        print("To modify settings, edit your .env file or config.py")
        
        self.pause()
    
    def show_logs(self):
        """Show recent logs"""
        self.print_header()
        print("📋 RECENT LOGS")
        print("=" * 63)
        print()
        
        import glob
        from pathlib import Path
        
        log_files = list(Path('logs').glob('*.log')) if Path('logs').exists() else []
        
        if not log_files:
            print("No log files found.")
            print("Logs will be created when logging is enabled.")
            self.pause()
            return
        
        # Get most recent log file
        latest_log = max(log_files, key=lambda p: p.stat().st_mtime)
        
        print(f"Showing last 50 lines from: {latest_log.name}")
        print("=" * 63)
        print()
        
        try:
            with open(latest_log, 'r') as f:
                lines = f.readlines()
                for line in lines[-50:]:
                    print(line.rstrip())
        except Exception as e:
            print(f"❌ Error reading log: {e}")
        
        self.pause()
    
    def show_monitoring_report(self):
        """Display monitoring metrics"""
        self.print_header()
        print("📊 MONITORING REPORT")
        print("=" * 63)
        print()
        
        try:
            from monitoring import get_monitor
            monitor = get_monitor()
            summary = monitor.get_summary()
            
            print("System Health:")
            print(f"  Uptime:               {summary['uptime_seconds']:.0f} seconds")
            print()
            
            print("Errors:")
            print(f"  Total Errors:         {summary['errors']['total']}")
            print(f"  Error Rate:           {summary['errors']['rate_per_minute']:.2f}/min")
            if summary['errors']['by_category']:
                print(f"  By Category:          {summary['errors']['by_category']}")
            print()
            
            print("Warnings:")
            print(f"  Total Warnings:       {summary['warnings']['total']}")
            if summary['warnings']['by_category']:
                print(f"  By Category:          {summary['warnings']['by_category']}")
            print()
            
            print("Metrics:")
            if summary['metrics']:
                for key, value in list(summary['metrics'].items())[:10]:
                    print(f"  {key:<20}  {value}")
            else:
                print("  No metrics recorded yet")
            print()
            
            print("Performance:")
            if summary['timings']:
                for op, stats in summary['timings'].items():
                    print(f"  {op}:")
                    print(f"    Count:    {stats['count']}")
                    print(f"    Avg:      {stats['avg_ms']:.2f}ms")
                    print(f"    Min/Max:  {stats['min_ms']:.2f}ms / {stats['max_ms']:.2f}ms")
            else:
                print("  No timing data yet")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        self.pause()
    
    def run_after_hours_planning(self):
        """Run after-hours planning for tomorrow's trades"""
        self.print_header()
        print("🌙 AFTER-HOURS TRADING PLANNER")
        print("=" * 63)
        print()
        print("This will analyze stocks and prepare a trading plan for")
        print("tomorrow's session based on current signals.")
        print()
        
        # Select strategy
        strategy_name = self.select_strategy()
        
        print()
        
        # Stock universe to analyze
        symbols = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA',
            'TSLA', 'META', 'AMD', 'NFLX', 'INTC',
            'V', 'MA', 'JPM', 'DIS', 'PYPL',
            'ADBE', 'CRM', 'ORCL', 'CSCO', 'QCOM'
        ]
        
        try:
            from after_hours_planning import analyze_for_tomorrow, print_trading_plan, save_trading_plan
            
            plan = analyze_for_tomorrow(symbols, strategy_name)
            print_trading_plan(plan)
            
            # Save plan
            filepath = save_trading_plan(plan)
            print(f"\n💾 Plan saved to: {filepath}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        self.pause()
    
    def run_strategy_comparison(self):
        """Compare all strategies side-by-side"""
        self.print_header()
        print("⚖️  STRATEGY COMPARISON")
        print("=" * 63)
        print()
        print("This will fetch data ONCE and compare all 3 strategies")
        print("on the same stocks. See which strategy works best!")
        print()
        
        # Stock universe to analyze
        symbols = [
            # Popular stocks for comparison
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA',
            'META', 'AMD', 'INTC', 'NFLX', 'DIS',
            'PYPL', 'SQ', 'SHOP', 'V', 'MA',
            'JPM', 'BAC', 'WMT', 'TGT', 'COST',
            'SPY', 'QQQ', 'IWM'
        ]
        
        try:
            from data_cache import DataCache, compare_strategies_on_cached_data, print_strategy_comparison
            
            # Create cache and fetch data once
            cache = DataCache()
            print("Fetching data (this will take ~30 seconds)...")
            print()
            cache.fetch_and_cache(symbols, period=30)
            
            # Compare strategies
            print("\nAnalyzing with all strategies...")
            comparison = compare_strategies_on_cached_data(cache, symbols)
            
            # Display results
            print_strategy_comparison(comparison)
            
            # Save comparison
            timestamp = __import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"strategy_comparison_{timestamp}.csv"
            comparison.to_csv(filename, index=False)
            print(f"\n💾 Comparison saved to: {filename}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        self.pause()
    
    def run(self):
        """Main application loop"""
        while self.running:
            self.print_header()
            self.print_menu()
            
            choice = input("Select an option (0-11): ").strip()
            
            if choice == '1':
                self.run_quick_start()
            elif choice == '2':
                self.run_identify_stocks()
            elif choice == '3':
                self.run_backtest()
            elif choice == '4':
                self.run_visualize()
            elif choice == '5':
                self.run_dry_run_trading()
            elif choice == '6':
                self.run_paper_trading()
            elif choice == '7':
                self.show_configuration()
            elif choice == '8':
                self.show_logs()
            elif choice == '9':
                self.show_monitoring_report()
            elif choice == '10':
                self.run_after_hours_planning()
            elif choice == '11':
                self.run_strategy_comparison()
            elif choice == '0':
                self.print_header()
                print("👋 Thank you for using Stocker!")
                print()
                print("Remember: Always test thoroughly before trading with real money.")
                print()
                self.running = False
            else:
                print()
                print("❌ Invalid option. Please try again.")
                self.pause()


def main():
    """Main entry point"""
    try:
        ui = StockerUI()
        ui.run()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

