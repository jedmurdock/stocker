"""
Data caching system for stock data.
Allows fetching data once and applying multiple strategies without repeated API calls.
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from data_fetcher import DataFetcher
import json
import os


class DataCache:
    """
    Cache for stock market data.
    Stores fetched data in memory and optionally persists to disk.
    """
    
    def __init__(self, cache_dir: str = ".cache"):
        """
        Initialize data cache.
        
        Args:
            cache_dir: Directory to store cache files
        """
        self.cache_dir = cache_dir
        self.memory_cache: Dict[str, pd.DataFrame] = {}
        self.cache_metadata: Dict[str, dict] = {}
        
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
    
    def fetch_and_cache(self, symbols: List[str], period: int = 30, 
                       source: str = 'yfinance') -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple symbols and cache them.
        
        Args:
            symbols: List of stock symbols
            period: Number of days to fetch
            source: Data source ('yfinance' or 'alpaca')
            
        Returns:
            Dictionary mapping symbols to DataFrames
        """
        data_fetcher = DataFetcher(source=source)
        results = {}
        
        print(f"Fetching data for {len(symbols)} symbols...")
        
        for symbol in symbols:
            try:
                # Check if we have valid cached data
                if self._is_cache_valid(symbol, period):
                    print(f"✓ {symbol:<6} (cached)")
                    results[symbol] = self.memory_cache[symbol]
                else:
                    # Fetch fresh data
                    df = data_fetcher.fetch_data(symbol, period=period)
                    
                    # Cache it
                    self.memory_cache[symbol] = df
                    self.cache_metadata[symbol] = {
                        'fetched_at': datetime.now().isoformat(),
                        'period': period,
                        'rows': len(df),
                        'start_date': str(df.index[0]) if not df.empty else None,
                        'end_date': str(df.index[-1]) if not df.empty else None
                    }
                    
                    results[symbol] = df
                    print(f"✓ {symbol:<6} (fetched {len(df)} rows)")
                    
            except Exception as e:
                print(f"✗ {symbol:<6} - Error: {str(e)[:50]}")
                continue
        
        return results
    
    def _is_cache_valid(self, symbol: str, period: int, 
                       max_age_minutes: int = 15) -> bool:
        """
        Check if cached data is still valid.
        
        Args:
            symbol: Stock symbol
            period: Required period
            max_age_minutes: Maximum age of cache in minutes
            
        Returns:
            True if cache is valid
        """
        if symbol not in self.memory_cache:
            return False
        
        if symbol not in self.cache_metadata:
            return False
        
        metadata = self.cache_metadata[symbol]
        
        # Check if period matches
        if metadata.get('period') != period:
            return False
        
        # Check age
        fetched_at = datetime.fromisoformat(metadata['fetched_at'])
        age = datetime.now() - fetched_at
        
        if age > timedelta(minutes=max_age_minutes):
            return False
        
        return True
    
    def get_cached_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        Get cached data for a symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            DataFrame if cached, None otherwise
        """
        return self.memory_cache.get(symbol)
    
    def get_cache_info(self) -> Dict:
        """
        Get information about cached data.
        
        Returns:
            Dictionary with cache statistics
        """
        return {
            'cached_symbols': list(self.memory_cache.keys()),
            'count': len(self.memory_cache),
            'metadata': self.cache_metadata.copy()
        }
    
    def clear_cache(self):
        """Clear all cached data"""
        self.memory_cache.clear()
        self.cache_metadata.clear()
    
    def save_to_disk(self, filename: Optional[str] = None):
        """
        Save cached data to disk.
        
        Args:
            filename: Optional filename, defaults to timestamp
        """
        if filename is None:
            filename = f"cache_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
        
        filepath = os.path.join(self.cache_dir, filename)
        
        # Save DataFrames as pickle
        import pickle
        with open(filepath, 'wb') as f:
            pickle.dump({
                'data': self.memory_cache,
                'metadata': self.cache_metadata
            }, f)
        
        print(f"Cache saved to: {filepath}")
        return filepath
    
    def load_from_disk(self, filename: str):
        """
        Load cached data from disk.
        
        Args:
            filename: Filename to load
        """
        filepath = os.path.join(self.cache_dir, filename)
        
        import pickle
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            self.memory_cache = data['data']
            self.cache_metadata = data['metadata']
        
        print(f"Cache loaded from: {filepath}")
        print(f"Loaded {len(self.memory_cache)} symbols")


def compare_strategies_on_cached_data(cache: DataCache, symbols: List[str],
                                     strategy_names: List[str] = None) -> pd.DataFrame:
    """
    Apply multiple strategies to cached data and compare results.
    
    Args:
        cache: DataCache with loaded data
        symbols: List of symbols to analyze
        strategy_names: List of strategy names to compare (default: all 3)
        
    Returns:
        DataFrame with comparison results
    """
    from strategies import get_strategy
    
    if strategy_names is None:
        strategy_names = ['conservative', 'balanced', 'aggressive']
    
    comparison_results = []
    
    print(f"\nComparing {len(strategy_names)} strategies on {len(symbols)} stocks...")
    print()
    
    for symbol in symbols:
        df = cache.get_cached_data(symbol)
        if df is None or df.empty:
            continue
        
        try:
            latest_price = df['close'].iloc[-1]
            latest_rsi = None
            
            # Analyze with each strategy
            row = {
                'symbol': symbol,
                'price': round(float(latest_price), 2)
            }
            
            for strategy_name in strategy_names:
                strategy = get_strategy(strategy_name)
                analyzed_df = strategy.analyze(df)
                latest = analyzed_df.iloc[-1]
                
                signal = int(latest['signal'])
                signal_text = 'buy' if signal == 1 else 'sell' if signal == -1 else 'hold'
                
                row[f'{strategy_name}_signal'] = signal_text
                row[f'{strategy_name}_rsi'] = round(float(latest['rsi']), 1)
                
                if latest_rsi is None:
                    latest_rsi = latest['rsi']
            
            row['rsi'] = round(float(latest_rsi), 1)
            comparison_results.append(row)
            
        except Exception as e:
            print(f"✗ {symbol} - Error: {e}")
            continue
    
    return pd.DataFrame(comparison_results)


def print_strategy_comparison(comparison_df: pd.DataFrame, strategy_names: List[str] = None):
    """
    Pretty print strategy comparison results.
    
    Args:
        comparison_df: DataFrame from compare_strategies_on_cached_data
        strategy_names: List of strategy names
    """
    if strategy_names is None:
        strategy_names = ['conservative', 'balanced', 'aggressive']
    
    print("\n" + "=" * 80)
    print("STRATEGY COMPARISON")
    print("=" * 80)
    print()
    
    # Show stocks where strategies disagree (most interesting!)
    print("🎯 STRATEGY DISAGREEMENTS (Most Interesting)")
    print("=" * 80)
    
    disagreements = []
    for _, row in comparison_df.iterrows():
        signals = [row[f'{s}_signal'] for s in strategy_names]
        if len(set(signals)) > 1:  # Not all the same
            disagreements.append(row)
    
    if disagreements:
        for row in disagreements[:15]:  # Top 15
            print(f"\n{row['symbol']:<6} ${row['price']:>8.2f}  RSI: {row['rsi']:>5.1f}")
            for strategy_name in strategy_names:
                signal = row[f'{strategy_name}_signal']
                icon = '🎯' if signal == 'buy' else '📉' if signal == 'sell' else '⏸️'
                print(f"  {strategy_name:12} {icon} {signal:4}")
    else:
        print("All strategies agree on all stocks")
    
    # Summary statistics
    print("\n" + "=" * 80)
    print("SUMMARY BY STRATEGY")
    print("=" * 80)
    
    for strategy_name in strategy_names:
        signal_col = f'{strategy_name}_signal'
        counts = comparison_df[signal_col].value_counts()
        
        buy_count = counts.get('buy', 0)
        sell_count = counts.get('sell', 0)
        hold_count = counts.get('hold', 0)
        
        print(f"\n{strategy_name.upper()}")
        print(f"  🎯 Buy signals:   {buy_count:3} ({buy_count/len(comparison_df)*100:.1f}%)")
        print(f"  📉 Sell signals:  {sell_count:3} ({sell_count/len(comparison_df)*100:.1f}%)")
        print(f"  ⏸️  Hold:          {hold_count:3} ({hold_count/len(comparison_df)*100:.1f}%)")
    
    # Show buy signals by strategy
    print("\n" + "=" * 80)
    print("BUY SIGNALS BY STRATEGY")
    print("=" * 80)
    
    for strategy_name in strategy_names:
        signal_col = f'{strategy_name}_signal'
        buys = comparison_df[comparison_df[signal_col] == 'buy']
        
        if not buys.empty:
            print(f"\n{strategy_name.upper()} ({len(buys)} buys):")
            for _, row in buys.head(10).iterrows():
                others = []
                for other_strategy in strategy_names:
                    if other_strategy != strategy_name:
                        signal = row[f'{other_strategy}_signal']
                        others.append(f"{other_strategy[0].upper()}:{signal}")
                
                other_text = " ".join(others)
                print(f"  {row['symbol']:<6} ${row['price']:>8.2f}  RSI: {row['rsi']:>5.1f}  ({other_text})")
    
    print()


if __name__ == '__main__':
    # Demo
    print("=" * 80)
    print("DATA CACHE DEMO")
    print("=" * 80)
    print()
    
    # Create cache and fetch data
    cache = DataCache()
    
    test_symbols = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'AMD', 'META']
    
    print("Step 1: Fetching data (will make API calls)")
    print("-" * 80)
    cache.fetch_and_cache(test_symbols, period=30)
    
    print("\n" + "=" * 80)
    print("Step 2: Comparing strategies (using cached data, NO API calls)")
    print("-" * 80)
    
    comparison = compare_strategies_on_cached_data(cache, test_symbols)
    print_strategy_comparison(comparison)
    
    print("\n" + "=" * 80)
    print("Step 3: Fetching again (should use cache)")
    print("-" * 80)
    cache.fetch_and_cache(test_symbols, period=30)
    
    print("\n✅ Demo complete!")

