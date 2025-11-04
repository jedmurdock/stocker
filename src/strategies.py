"""
Multiple trading strategy profiles with different risk/reward characteristics.

Strategies:
- Conservative: Fewer trades, stricter conditions, lower risk
- Balanced: Moderate trade frequency, balanced signals (DEFAULT)
- Aggressive: More trades, looser conditions, higher risk
"""

import pandas as pd
from typing import Dict, Optional, Any
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
from config import Config


class StrategyProfile:
    """Base class for strategy profiles"""
    
    NAME = "Base"
    DESCRIPTION = "Base strategy"
    
    # Override these in subclasses
    RSI_OVERSOLD = 30
    RSI_OVERBOUGHT = 70
    FAST_MA_PERIOD = 10
    SLOW_MA_PERIOD = 50
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators"""
        if df.empty:
            raise ValueError("Cannot calculate indicators on empty DataFrame")
        
        required_cols = ['close', 'high', 'low']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        df = df.copy()
        
        # RSI
        rsi_indicator = RSIIndicator(close=df['close'], window=14)
        df['rsi'] = rsi_indicator.rsi()
        df['rsi_prev'] = df['rsi'].shift(1)
        
        # Moving Averages
        fast_ma = SMAIndicator(close=df['close'], window=self.FAST_MA_PERIOD)
        slow_ma = SMAIndicator(close=df['close'], window=self.SLOW_MA_PERIOD)
        
        df['fast_ma'] = fast_ma.sma_indicator()
        df['slow_ma'] = slow_ma.sma_indicator()
        df['fast_ma_prev'] = df['fast_ma'].shift(1)
        df['slow_ma_prev'] = df['slow_ma'].shift(1)
        
        return df
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate buy/sell signals - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement generate_signals")
    
    def analyze(self, df: pd.DataFrame) -> pd.DataFrame:
        """Complete analysis: calculate indicators and generate signals"""
        df = self.calculate_indicators(df)
        df = self.generate_signals(df)
        return df
    
    def get_current_signal(self, df: pd.DataFrame, 
                          position: Optional[Dict] = None) -> Dict[str, Any]:
        """Get current trading signal with position context"""
        if df.empty:
            return {'action': 'hold', 'reason': 'No data available'}
        
        required_cols = ['signal', 'close', 'rsi']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            return {'action': 'hold', 'reason': f'Missing columns: {missing_cols}'}
        
        latest = df.iloc[-1]
        current_signal = int(latest['signal'])
        
        # Check position-based exits
        if position:
            entry_price = position.get('entry_price')
            quantity = position.get('quantity', 0)
            current_price = latest['close']
            
            if quantity > 0 and entry_price:
                pnl_pct = (current_price - entry_price) / entry_price
                
                # Stop loss
                if pnl_pct <= -self.config.STOP_LOSS:
                    return {
                        'action': 'sell',
                        'reason': f'Stop loss triggered ({pnl_pct:.2%})',
                        'price': current_price
                    }
                
                # Take profit
                if pnl_pct >= self.config.TAKE_PROFIT:
                    return {
                        'action': 'sell',
                        'reason': f'Take profit triggered ({pnl_pct:.2%})',
                        'price': current_price
                    }
        
        # Return signal-based action
        if current_signal == 1:
            return {
                'action': 'buy',
                'reason': f'Buy signal (RSI: {latest["rsi"]:.1f})',
                'price': latest['close']
            }
        elif current_signal == -1:
            return {
                'action': 'sell',
                'reason': f'Sell signal (RSI: {latest["rsi"]:.1f})',
                'price': latest['close']
            }
        else:
            return {
                'action': 'hold',
                'reason': 'No clear signal',
                'price': latest['close']
            }


class ConservativeStrategy(StrategyProfile):
    """
    Conservative strategy: Fewer trades, stricter conditions.
    
    - Requires BOTH RSI recovery AND MA crossover to buy
    - Tighter RSI thresholds (25/75 instead of 30/70)
    - Longer MA periods for more stable signals
    - Best for: Risk-averse traders, volatile markets
    """
    
    NAME = "Conservative"
    DESCRIPTION = "Fewer trades, stricter conditions, lower risk"
    
    RSI_OVERSOLD = 25
    RSI_OVERBOUGHT = 75
    FAST_MA_PERIOD = 15
    SLOW_MA_PERIOD = 60
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Conservative signal generation - requires multiple confirmations"""
        df = df.copy()
        df['signal'] = 0
        
        # Buy: Requires BOTH RSI recovery AND MA crossover
        buy_condition = (
            (df['rsi'] > self.RSI_OVERSOLD) &  
            (df['rsi_prev'] <= self.RSI_OVERSOLD) &
            (df['fast_ma'] > df['slow_ma']) &
            (df['fast_ma_prev'] <= df['slow_ma_prev']) &
            (df['close'] > df['slow_ma'])
        )
        
        # Sell: Either overbought OR bearish crossover
        sell_condition = (
            (df['rsi'] > self.RSI_OVERBOUGHT) |
            ((df['fast_ma'] < df['slow_ma']) & (df['fast_ma_prev'] >= df['slow_ma_prev']))
        )
        
        df.loc[buy_condition, 'signal'] = 1
        df.loc[sell_condition, 'signal'] = -1
        
        return df


class BalancedStrategy(StrategyProfile):
    """
    Balanced strategy: Moderate trade frequency (DEFAULT).
    
    - Uses OR logic for buy signals
    - Standard RSI thresholds (30/70)
    - Medium MA periods
    - Best for: Most traders, normal market conditions
    """
    
    NAME = "Balanced"
    DESCRIPTION = "Moderate trades, balanced signals (DEFAULT)"
    
    RSI_OVERSOLD = 30
    RSI_OVERBOUGHT = 70
    FAST_MA_PERIOD = 10
    SLOW_MA_PERIOD = 50
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Balanced signal generation - OR logic for opportunities"""
        df = df.copy()
        df['signal'] = 0
        
        # Condition 1: RSI recovery with bullish MAs
        rsi_recovery = (
            (df['rsi'] > self.RSI_OVERSOLD) &
            (df['rsi_prev'] <= self.RSI_OVERSOLD) &
            (df['fast_ma'] > df['slow_ma'])
        )
        
        # Condition 2: MA crossover with healthy RSI
        ma_crossover = (
            (df['fast_ma'] > df['slow_ma']) &
            (df['fast_ma_prev'] <= df['slow_ma_prev']) &
            (df['rsi'] < self.RSI_OVERBOUGHT) &
            (df['rsi'] > self.RSI_OVERSOLD)
        )
        
        # Buy if EITHER condition is true
        buy_condition = (rsi_recovery | ma_crossover) & (df['close'] > df['slow_ma'])
        
        # Sell conditions
        sell_condition = (
            (df['rsi'] > self.RSI_OVERBOUGHT) |
            ((df['fast_ma'] < df['slow_ma']) & (df['fast_ma_prev'] >= df['slow_ma_prev']))
        )
        
        df.loc[buy_condition, 'signal'] = 1
        df.loc[sell_condition, 'signal'] = -1
        
        return df


class AggressiveStrategy(StrategyProfile):
    """
    Aggressive strategy: More trades, looser conditions.
    
    - Wider RSI thresholds (35/65)
    - Shorter MA periods for faster signals
    - Additional momentum-based buy signals
    - Best for: Active traders, trending markets
    """
    
    NAME = "Aggressive"
    DESCRIPTION = "More trades, looser conditions, higher risk"
    
    RSI_OVERSOLD = 35
    RSI_OVERBOUGHT = 65
    FAST_MA_PERIOD = 8
    SLOW_MA_PERIOD = 40
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aggressive signal generation - multiple buy opportunities"""
        df = df.copy()
        df['signal'] = 0
        
        # Condition 1: RSI recovery
        rsi_recovery = (
            (df['rsi'] > self.RSI_OVERSOLD) &
            (df['rsi_prev'] <= self.RSI_OVERSOLD) &
            (df['fast_ma'] > df['slow_ma'])
        )
        
        # Condition 2: MA crossover
        ma_crossover = (
            (df['fast_ma'] > df['slow_ma']) &
            (df['fast_ma_prev'] <= df['slow_ma_prev']) &
            (df['rsi'] < self.RSI_OVERBOUGHT)
        )
        
        # Condition 3: Strong momentum (NEW for aggressive)
        strong_momentum = (
            (df['fast_ma'] > df['slow_ma']) &
            (df['close'] > df['fast_ma']) &
            (df['rsi'] > 40) & (df['rsi'] < self.RSI_OVERBOUGHT) &
            (df['rsi'] > df['rsi_prev'])  # RSI increasing
        )
        
        # Buy if ANY condition is true
        buy_condition = (rsi_recovery | ma_crossover | strong_momentum) & (df['close'] > df['slow_ma'])
        
        # Sell conditions
        sell_condition = (
            (df['rsi'] > self.RSI_OVERBOUGHT) |
            ((df['fast_ma'] < df['slow_ma']) & (df['fast_ma_prev'] >= df['slow_ma_prev'])) |
            (df['rsi'] < self.RSI_OVERSOLD)  # Quick exit on weakness
        )
        
        df.loc[buy_condition, 'signal'] = 1
        df.loc[sell_condition, 'signal'] = -1
        
        return df


# Strategy registry for easy access
STRATEGIES = {
    'conservative': ConservativeStrategy,
    'balanced': BalancedStrategy,
    'aggressive': AggressiveStrategy,
}

DEFAULT_STRATEGY = 'balanced'


def get_strategy(name: str = DEFAULT_STRATEGY, config: Optional[Config] = None) -> StrategyProfile:
    """
    Get a strategy by name.
    
    Args:
        name: Strategy name ('conservative', 'balanced', or 'aggressive')
        config: Optional Config instance
        
    Returns:
        Strategy instance
        
    Raises:
        ValueError: If strategy name is not recognized
    """
    name = name.lower()
    if name not in STRATEGIES:
        raise ValueError(f"Unknown strategy: {name}. Choose from: {list(STRATEGIES.keys())}")
    
    return STRATEGIES[name](config)


def list_strategies() -> Dict[str, Dict[str, str]]:
    """
    List all available strategies with descriptions.
    
    Returns:
        Dictionary mapping strategy names to their info
    """
    return {
        name: {
            'name': strategy.NAME,
            'description': strategy.DESCRIPTION,
        }
        for name, strategy in STRATEGIES.items()
    }

