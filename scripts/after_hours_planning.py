"""
After-Hours Trading Planning Module

Analyzes market data after-hours to plan potential trades for the next trading session.
This helps traders prepare for the market open by:
- Identifying stocks with strong signals
- Setting entry/exit points
- Planning risk management
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from data_fetcher import DataFetcher
from strategies import get_strategy, list_strategies, DEFAULT_STRATEGY
import json
import os


def analyze_for_tomorrow(symbols: List[str], strategy_name: str = DEFAULT_STRATEGY) -> Dict:
    """
    Analyze stocks for tomorrow's trading session.
    
    Args:
        symbols: List of stock tickers to analyze
        strategy_name: Strategy to use for analysis
        
    Returns:
        Dictionary with analysis results and trading plan
    """
    strategy = get_strategy(strategy_name)
    data_fetcher = DataFetcher(source='yfinance')
    
    trading_plan = {
        'generated_at': datetime.now().isoformat(),
        'strategy': strategy_name,
        'market_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
        'buy_candidates': [],
        'sell_candidates': [],
        'watch_list': [],
        'summary': {}
    }
    
    print(f"\n🌙 Analyzing {len(symbols)} stocks for tomorrow's session...")
    print(f"Strategy: {strategy_name.upper()}")
    print()
    
    for symbol in symbols:
        try:
            # Fetch recent data (30 days - good for indicators, works with data source)
            df = data_fetcher.fetch_data(symbol, period=30)
            
            # Analyze with strategy
            analyzed_df = strategy.analyze(df)
            latest = analyzed_df.iloc[-1]
            
            # Get current signal
            signal = int(latest['signal'])
            current_price = float(latest['close'])
            rsi = float(latest['rsi'])
            
            # Calculate recommended entry/exit levels
            stop_loss = current_price * 0.95  # 5% stop loss
            take_profit = current_price * 1.10  # 10% take profit
            
            stock_info = {
                'symbol': symbol,
                'current_price': round(current_price, 2),
                'rsi': round(rsi, 2),
                'fast_ma': round(float(latest['fast_ma']), 2),
                'slow_ma': round(float(latest['slow_ma']), 2),
                'signal_strength': 0,
                'stop_loss': round(stop_loss, 2),
                'take_profit': round(take_profit, 2),
            }
            
            # Categorize based on signal
            if signal == 1:
                # Buy signal
                signal_strength = calculate_signal_strength(latest, 'buy')
                stock_info['signal_strength'] = round(signal_strength, 2)
                stock_info['recommendation'] = 'BUY'
                stock_info['reason'] = get_buy_reason(latest)
                trading_plan['buy_candidates'].append(stock_info)
                print(f"✓ {symbol:<6} - BUY signal  (RSI: {rsi:.1f}, Price: ${current_price:.2f})")
                
            elif signal == -1:
                # Sell signal
                signal_strength = calculate_signal_strength(latest, 'sell')
                stock_info['signal_strength'] = round(signal_strength, 2)
                stock_info['recommendation'] = 'SELL'
                stock_info['reason'] = get_sell_reason(latest)
                trading_plan['sell_candidates'].append(stock_info)
                print(f"✓ {symbol:<6} - SELL signal (RSI: {rsi:.1f}, Price: ${current_price:.2f})")
                
            else:
                # Watch list - stocks close to signal thresholds
                if is_worth_watching(latest):
                    stock_info['recommendation'] = 'WATCH'
                    stock_info['reason'] = get_watch_reason(latest)
                    trading_plan['watch_list'].append(stock_info)
                    print(f"✓ {symbol:<6} - WATCH      (RSI: {rsi:.1f}, Price: ${current_price:.2f})")
                else:
                    print(f"○ {symbol:<6} - No signal")
                    
        except Exception as e:
            print(f"✗ {symbol:<6} - Error: {str(e)[:50]}")
            continue
    
    # Sort by signal strength
    trading_plan['buy_candidates'].sort(key=lambda x: x['signal_strength'], reverse=True)
    trading_plan['sell_candidates'].sort(key=lambda x: x['signal_strength'], reverse=True)
    
    # Generate summary
    trading_plan['summary'] = {
        'total_analyzed': len(symbols),
        'buy_signals': len(trading_plan['buy_candidates']),
        'sell_signals': len(trading_plan['sell_candidates']),
        'watch_list': len(trading_plan['watch_list']),
    }
    
    return trading_plan


def calculate_signal_strength(row: pd.Series, signal_type: str) -> float:
    """Calculate strength of a trading signal (0-100)"""
    if signal_type == 'buy':
        # Factors: RSI recovery, MA alignment, price momentum
        rsi_factor = min((50 - row['rsi']) / 20, 1.0) if row['rsi'] < 50 else 0.5
        ma_factor = (row['fast_ma'] - row['slow_ma']) / row['slow_ma'] * 10
        price_factor = (row['close'] - row['slow_ma']) / row['slow_ma'] * 5
        return max(0, min(100, (rsi_factor + ma_factor + price_factor) * 20))
    else:  # sell
        # Factors: RSI overbought, bearish MA alignment
        rsi_factor = (row['rsi'] - 50) / 30 if row['rsi'] > 50 else 0
        ma_factor = 1.0 if row['fast_ma'] < row['slow_ma'] else 0.5
        return max(0, min(100, (rsi_factor + ma_factor) * 40))


def get_buy_reason(row: pd.Series) -> str:
    """Generate human-readable reason for buy signal"""
    reasons = []
    
    if row['rsi'] < 35:
        reasons.append(f"RSI oversold ({row['rsi']:.1f})")
    if row['fast_ma'] > row['slow_ma']:
        reasons.append("Bullish MA crossover")
    if row['close'] > row['fast_ma']:
        reasons.append("Price above fast MA")
        
    return ", ".join(reasons) if reasons else "Multiple bullish indicators"


def get_sell_reason(row: pd.Series) -> str:
    """Generate human-readable reason for sell signal"""
    reasons = []
    
    if row['rsi'] > 70:
        reasons.append(f"RSI overbought ({row['rsi']:.1f})")
    if row['fast_ma'] < row['slow_ma']:
        reasons.append("Bearish MA crossover")
        
    return ", ".join(reasons) if reasons else "Multiple bearish indicators"


def get_watch_reason(row: pd.Series) -> str:
    """Generate reason for watch list"""
    if 35 < row['rsi'] < 45:
        return "RSI approaching oversold - potential buy setup"
    elif 60 < row['rsi'] < 70:
        return "RSI approaching overbought - potential sell setup"
    elif abs(row['fast_ma'] - row['slow_ma']) / row['slow_ma'] < 0.01:
        return "MAs converging - potential crossover soon"
    else:
        return "Monitor for signal development"


def is_worth_watching(row: pd.Series) -> bool:
    """Determine if stock should be on watch list"""
    # Add to watch list if:
    # 1. RSI approaching key levels
    # 2. MAs about to cross
    # 3. Other interesting setups
    
    rsi_interesting = (35 < row['rsi'] < 45) or (60 < row['rsi'] < 70)
    ma_converging = abs(row['fast_ma'] - row['slow_ma']) / row['slow_ma'] < 0.01
    
    return rsi_interesting or ma_converging


def save_trading_plan(plan: Dict, filename: Optional[str] = None) -> str:
    """Save trading plan to file"""
    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"trading_plan_{timestamp}.json"
    
    # Create plans directory if needed
    os.makedirs('trading_plans', exist_ok=True)
    filepath = os.path.join('trading_plans', filename)
    
    with open(filepath, 'w') as f:
        json.dump(plan, f, indent=2, default=str)
    
    return filepath


def print_trading_plan(plan: Dict):
    """Pretty print the trading plan"""
    print("\n" + "=" * 70)
    print("📋 TRADING PLAN FOR NEXT SESSION")
    print("=" * 70)
    print(f"Generated: {plan['generated_at']}")
    print(f"Market Date: {plan['market_date']}")
    print(f"Strategy: {plan['strategy'].upper()}")
    print()
    
    # Buy candidates
    if plan['buy_candidates']:
        print("=" * 70)
        print(f"🎯 BUY CANDIDATES ({len(plan['buy_candidates'])})")
        print("=" * 70)
        for stock in plan['buy_candidates'][:10]:  # Top 10
            print(f"\n{stock['symbol']:<6} ${stock['current_price']:>8.2f}  "
                  f"Strength: {stock['signal_strength']:>5.1f}/100")
            print(f"       RSI: {stock['rsi']:.1f}  |  "
                  f"Stop: ${stock['stop_loss']:.2f}  |  "
                  f"Target: ${stock['take_profit']:.2f}")
            print(f"       {stock['reason']}")
    
    # Sell candidates
    if plan['sell_candidates']:
        print("\n" + "=" * 70)
        print(f"📉 SELL CANDIDATES ({len(plan['sell_candidates'])})")
        print("=" * 70)
        for stock in plan['sell_candidates'][:10]:
            print(f"\n{stock['symbol']:<6} ${stock['current_price']:>8.2f}  "
                  f"Strength: {stock['signal_strength']:>5.1f}/100")
            print(f"       RSI: {stock['rsi']:.1f}")
            print(f"       {stock['reason']}")
    
    # Watch list
    if plan['watch_list']:
        print("\n" + "=" * 70)
        print(f"👁️  WATCH LIST ({len(plan['watch_list'])})")
        print("=" * 70)
        for stock in plan['watch_list'][:5]:
            print(f"  {stock['symbol']:<6} ${stock['current_price']:>8.2f}  "
                  f"RSI: {stock['rsi']:.1f}  -  {stock['reason']}")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total Analyzed:  {plan['summary']['total_analyzed']}")
    print(f"Buy Signals:     {plan['summary']['buy_signals']}")
    print(f"Sell Signals:    {plan['summary']['sell_signals']}")
    print(f"Watch List:      {plan['summary']['watch_list']}")
    print()


if __name__ == '__main__':
    import sys
    
    # Default stock universe
    symbols = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA',
        'TSLA', 'META', 'AMD', 'NFLX', 'INTC',
        'V', 'MA', 'JPM', 'DIS', 'PYPL',
        'ADBE', 'CRM', 'ORCL', 'CSCO', 'QCOM'
    ]
    
    strategy_name = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_STRATEGY
    
    print("=" * 70)
    print("🌙 AFTER-HOURS TRADING PLANNER")
    print("=" * 70)
    print()
    print("Preparing trading plan for tomorrow's session...")
    
    plan = analyze_for_tomorrow(symbols, strategy_name)
    print_trading_plan(plan)
    
    # Save plan
    filepath = save_trading_plan(plan)
    print(f"\n💾 Plan saved to: {filepath}")
    print()

