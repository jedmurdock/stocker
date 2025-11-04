"""
Script for identifying potential stocks to trade.
Analyzes multiple stocks to find ones with good trading signals.
"""
import pandas as pd
from strategy import TradingStrategy
from data_fetcher import DataFetcher
from config import Config


def identify_potential_stocks(symbols: list, min_volume: int = 1000000) -> pd.DataFrame:
    """
    Analyze multiple stocks and identify potential trading opportunities.
    
    Args:
        symbols: List of stock tickers to analyze
        min_volume: Minimum daily volume threshold
        
    Returns:
        DataFrame with analysis results sorted by signal strength
    """
    strategy = TradingStrategy()
    data_fetcher = DataFetcher(source='yfinance')
    results = []
    
    print(f"Analyzing {len(symbols)} stocks...")
    
    for symbol in symbols:
        try:
            # Fetch data
            df = data_fetcher.fetch_data(symbol, period=30)
            
            # Check volume
            avg_volume = df['volume'].tail(20).mean()
            if avg_volume < min_volume:
                continue
            
            # Analyze
            analyzed_df = strategy.analyze(df)
            latest = analyzed_df.iloc[-1]
            
            # Calculate signal strength
            signal_strength = 0
            if latest['signal'] == 1:
                # Buy signal strength based on RSI and MA alignment
                rsi_score = max(0, (latest['rsi'] - 30) / 40)  # Normalize RSI above oversold
                ma_score = (latest['fast_ma'] - latest['slow_ma']) / latest['slow_ma']
                signal_strength = (rsi_score + ma_score * 10) / 2
            
            results.append({
                'symbol': symbol,
                'signal': 'buy' if latest['signal'] == 1 else 'sell' if latest['signal'] == -1 else 'hold',
                'signal_value': latest['signal'],
                'signal_strength': signal_strength,
                'price': latest['close'],
                'rsi': latest['rsi'],
                'fast_ma': latest['fast_ma'],
                'slow_ma': latest['slow_ma'],
                'volume': avg_volume,
                'ma_crossover': latest['fast_ma'] > latest['slow_ma']
            })
            
            print(f"✓ Analyzed {symbol}")
            
        except Exception as e:
            print(f"✗ Failed to analyze {symbol}: {e}")
            continue
    
    # Create DataFrame and sort by signal strength
    results_df = pd.DataFrame(results)
    if not results_df.empty:
        results_df = results_df.sort_values('signal_strength', ascending=False)
    
    return results_df


if __name__ == '__main__':
    # Example: Analyze popular tech stocks
    symbols = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'AMD',
        'INTC', 'NFLX', 'SPY', 'QQQ', 'IWM', 'DIA'
    ]
    
    print("=" * 60)
    print("STOCK IDENTIFICATION - Finding Trading Opportunities")
    print("=" * 60)
    
    results = identify_potential_stocks(symbols)
    
    if not results.empty:
        print("\n" + "=" * 60)
        print("TOP TRADING OPPORTUNITIES")
        print("=" * 60)
        print(results[['symbol', 'signal', 'signal_strength', 'price', 'rsi', 'volume']].to_string(index=False))
        
        # Show buy signals
        buy_signals = results[results['signal'] == 'buy']
        if not buy_signals.empty:
            print("\n" + "=" * 60)
            print("BUY SIGNALS DETECTED")
            print("=" * 60)
            print(buy_signals[['symbol', 'signal_strength', 'price', 'rsi']].to_string(index=False))
    else:
        print("\nNo trading opportunities found in the analyzed stocks.")

