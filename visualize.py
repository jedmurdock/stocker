"""
Visualization script for backtest results and strategy signals.
Creates charts showing price action, indicators, and signals.
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import pandas as pd
from strategy import TradingStrategy
from data_fetcher import DataFetcher
from config import Config


def visualize_strategy(symbol: str, days: int = 30):
    """
    Create a visualization of the trading strategy on a stock.
    
    Args:
        symbol: Stock ticker
        days: Number of days of data to visualize
    """
    print(f"Creating visualization for {symbol}...")
    
    # Fetch data
    data_fetcher = DataFetcher(source='yfinance')
    df = data_fetcher.fetch_data(symbol, period=days)
    
    # Analyze
    strategy = TradingStrategy()
    analyzed_df = strategy.analyze(df)
    
    # Create figure with subplots
    fig, axes = plt.subplots(3, 1, figsize=(15, 12), sharex=True)
    fig.suptitle(f'{symbol} - Trading Strategy Analysis', fontsize=16, fontweight='bold')
    
    # Plot 1: Price and Moving Averages
    ax1 = axes[0]
    ax1.plot(analyzed_df.index, analyzed_df['close'], label='Price', linewidth=2, color='black')
    ax1.plot(analyzed_df.index, analyzed_df['fast_ma'], label=f'Fast MA ({Config().FAST_MA_PERIOD})', 
             linewidth=1.5, color='blue', alpha=0.7)
    ax1.plot(analyzed_df.index, analyzed_df['slow_ma'], label=f'Slow MA ({Config().SLOW_MA_PERIOD})', 
             linewidth=1.5, color='red', alpha=0.7)
    
    # Mark buy/sell signals
    buy_signals = analyzed_df[analyzed_df['signal'] == 1]
    sell_signals = analyzed_df[analyzed_df['signal'] == -1]
    
    ax1.scatter(buy_signals.index, buy_signals['close'], marker='^', color='green', 
               s=100, label='Buy Signal', zorder=5)
    ax1.scatter(sell_signals.index, sell_signals['close'], marker='v', color='red', 
               s=100, label='Sell Signal', zorder=5)
    
    ax1.set_ylabel('Price ($)', fontsize=12)
    ax1.set_title('Price Action with Moving Averages and Signals', fontsize=14)
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: RSI
    ax2 = axes[1]
    ax2.plot(analyzed_df.index, analyzed_df['rsi'], label='RSI', linewidth=2, color='purple')
    ax2.axhline(y=70, color='r', linestyle='--', alpha=0.7, label='Overbought (70)')
    ax2.axhline(y=50, color='gray', linestyle='--', alpha=0.5, label='Neutral (50)')
    ax2.axhline(y=30, color='g', linestyle='--', alpha=0.7, label='Oversold (30)')
    ax2.fill_between(analyzed_df.index, 30, 70, alpha=0.1, color='gray')
    
    ax2.set_ylabel('RSI', fontsize=12)
    ax2.set_title('Relative Strength Index (RSI)', fontsize=14)
    ax2.set_ylim(0, 100)
    ax2.legend(loc='best')
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Volume
    ax3 = axes[2]
    colors = ['red' if analyzed_df['close'].iloc[i] < analyzed_df['close'].iloc[i-1] 
              else 'green' for i in range(1, len(analyzed_df))]
    colors.insert(0, 'green')
    
    ax3.bar(analyzed_df.index, analyzed_df['volume'], color=colors, alpha=0.6)
    ax3.set_ylabel('Volume', fontsize=12)
    ax3.set_title('Trading Volume', fontsize=14)
    ax3.grid(True, alpha=0.3)
    
    # Format x-axis
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax3.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, days//10)))
    plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    
    # Save figure
    filename = f'{symbol}_strategy_analysis_{datetime.now().strftime("%Y%m%d")}.png'
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"Visualization saved to: {filename}")
    
    plt.show()


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python visualize.py <SYMBOL> [days]")
        print("Example: python visualize.py AAPL 30")
        sys.exit(1)
    
    symbol = sys.argv[1].upper()
    days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    
    visualize_strategy(symbol, days)

