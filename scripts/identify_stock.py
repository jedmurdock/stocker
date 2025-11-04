"""
Script for identifying potential stocks to trade.
Analyzes multiple stocks to find ones with good trading signals.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


import pandas as pd
from strategies import get_strategy, DEFAULT_STRATEGY
from data_fetcher import DataFetcher
from config import Config


def identify_potential_stocks(symbols: list, min_volume: int = 1000000, 
                             strategy_name: str = 'balanced') -> pd.DataFrame:
    """
    Analyze multiple stocks and identify potential trading opportunities.
    
    Args:
        symbols: List of stock tickers to analyze
        min_volume: Minimum daily volume threshold
        strategy_name: Strategy to use (conservative, balanced, aggressive)
        
    Returns:
        DataFrame with analysis results sorted by signal strength
    """
    strategy = get_strategy(strategy_name)
    data_fetcher = DataFetcher(source='yfinance')
    results = []
    
    print(f"Analyzing {len(symbols)} stocks...")
    
    for symbol in symbols:
        try:
            # Fetch data
            df = data_fetcher.fetch_data(symbol, period=30)
            
            # Check volume (but still include in results even if low)
            avg_volume = df['volume'].tail(20).mean()
            low_volume = avg_volume < min_volume
            
            # Analyze
            analyzed_df = strategy.analyze(df)
            latest = analyzed_df.iloc[-1]
            
            # Calculate signal strength (for all stocks, not just buy signals)
            signal_strength = 0
            
            if latest['signal'] == 1:
                # Buy signal strength based on RSI and MA alignment
                rsi_score = max(0, (50 - latest['rsi']) / 20) if latest['rsi'] < 50 else 0.3
                ma_score = (latest['fast_ma'] - latest['slow_ma']) / latest['slow_ma']
                signal_strength = max(0, min(100, (rsi_score + ma_score * 100)))
            elif latest['signal'] == -1:
                # Sell signal strength
                rsi_score = (latest['rsi'] - 50) / 30 if latest['rsi'] > 50 else 0
                signal_strength = max(0, min(100, rsi_score * 80))
            else:
                # For hold, calculate "potential" score
                # How close is it to generating a signal?
                rsi_proximity = 0
                if 35 < latest['rsi'] < 45:  # Near oversold
                    rsi_proximity = (45 - latest['rsi']) / 10 * 50
                elif 60 < latest['rsi'] < 70:  # Near overbought
                    rsi_proximity = (latest['rsi'] - 60) / 10 * 50
                
                ma_proximity = 0
                if latest['fast_ma'] > 0 and latest['slow_ma'] > 0:
                    ma_diff_pct = abs((latest['fast_ma'] - latest['slow_ma']) / latest['slow_ma']) * 100
                    if ma_diff_pct < 2:  # MAs within 2% of each other
                        ma_proximity = (2 - ma_diff_pct) / 2 * 50
                
                signal_strength = max(rsi_proximity, ma_proximity)
            
            # Determine status
            status = 'buy' if latest['signal'] == 1 else 'sell' if latest['signal'] == -1 else 'hold'
            
            # Add watch indicator for stocks close to signals
            watch_indicator = ''
            if status == 'hold' and signal_strength > 30:
                watch_indicator = ' 👁️'
            
            results.append({
                'symbol': symbol,
                'signal': status + watch_indicator,
                'signal_value': latest['signal'],
                'signal_strength': round(signal_strength, 1),
                'price': round(latest['close'], 2),
                'rsi': round(latest['rsi'], 1),
                'fast_ma': round(latest['fast_ma'], 2),
                'slow_ma': round(latest['slow_ma'], 2),
                'volume': int(avg_volume),
                'ma_crossover': latest['fast_ma'] > latest['slow_ma'],
                'low_volume': low_volume
            })
            
            print(f"✓ Analyzed {symbol}")
            
        except Exception as e:
            print(f"✗ Failed to analyze {symbol}: {e}")
            continue
    
    # Create DataFrame and sort by signal strength
    results_df = pd.DataFrame(results)
    if not results_df.empty:
        # Sort: buy signals first (by strength), then sell, then hold
        results_df = results_df.sort_values(
            by=['signal_value', 'signal_strength'], 
            ascending=[False, False]
        )
    
    return results_df


if __name__ == '__main__':
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
    
    print("=" * 60)
    print("STOCK IDENTIFICATION - Finding Trading Opportunities")
    print("=" * 60)
    
    results = identify_potential_stocks(symbols)
    
    if not results.empty:
        print("\n" + "=" * 60)
        print("TOP TRADING OPPORTUNITIES")
        print("=" * 60)
        
        # Show all results with formatting
        display_cols = ['symbol', 'signal', 'signal_strength', 'price', 'rsi']
        print(results[display_cols].to_string(index=False))
        
        # Highlight buy signals
        buy_signals = results[results['signal'].str.contains('buy', na=False)]
        if not buy_signals.empty:
            print("\n" + "=" * 60)
            print(f"🎯 BUY SIGNALS DETECTED ({len(buy_signals)} stocks)")
            print("=" * 60)
            for _, stock in buy_signals.head(10).iterrows():
                print(f"  {stock['symbol']:<6} ${stock['price']:>8.2f}  "
                      f"RSI: {stock['rsi']:>5.1f}  "
                      f"Strength: {stock['signal_strength']:>5.1f}")
        
        # Highlight watch list (high potential holds)
        watch_list = results[results['signal'].str.contains('👁️', na=False)]
        if not watch_list.empty:
            print("\n" + "=" * 60)
            print(f"👁️  WATCH LIST ({len(watch_list)} stocks)")
            print("=" * 60)
            print("These stocks are close to generating signals:")
            for _, stock in watch_list.head(10).iterrows():
                reason = ""
                if 35 < stock['rsi'] < 45:
                    reason = "RSI approaching oversold"
                elif 60 < stock['rsi'] < 70:
                    reason = "RSI approaching overbought"
                else:
                    reason = "MAs converging"
                print(f"  {stock['symbol']:<6} ${stock['price']:>8.2f}  "
                      f"RSI: {stock['rsi']:>5.1f}  -  {reason}")
        
        # Show summary
        buy_count = len(results[results['signal'].str.contains('buy', na=False)])
        sell_count = len(results[results['signal'].str.contains('sell', na=False)])
        watch_count = len(results[results['signal'].str.contains('👁️', na=False)])
        hold_count = len(results[results['signal'].str.contains('hold', na=False)]) - watch_count
        
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Total analyzed:  {len(results)}")
        print(f"  🎯 Buy signals:   {buy_count}")
        print(f"  📉 Sell signals:  {sell_count}")
        print(f"  👁️  Watch list:    {watch_count}")
        print(f"  ⏸️  Hold:          {hold_count}")
    else:
        print("\n❌ No trading opportunities found in the analyzed stocks.")

