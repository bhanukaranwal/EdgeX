"""
strategy_utils.py
Helper functions for strategy signal processing & indicator calculations.
Includes:
    - Supertrend
    - ADX
    - Common option filters
"""

import pandas as pd
import numpy as np

def calc_atr(df, period=14):
    """Average True Range calculation."""
    df['H-L'] = df['high'] - df['low']
    df['H-PC'] = abs(df['high'] - df['close'].shift(1))
    df['L-PC'] = abs(df['low'] - df['close'].shift(1))
    df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
    df['ATR'] = df['TR'].rolling(window=period).mean()
    return df

def calc_supertrend(df, period=10, multiplier=3):
    """Supertrend indicator calculation."""
    df = calc_atr(df, period)
    hl2 = (df['high'] + df['low']) / 2
    df['basic_ub'] = hl2 + (multiplier * df['ATR'])
    df['basic_lb'] = hl2 - (multiplier * df['ATR'])
    df['final_ub'] = df['basic_ub']
    df['final_lb'] = df['basic_lb']
    for i in range(1, len(df)):
        if (df['close'][i-1] <= df['final_ub'][i-1]):
            df['final_ub'][i] = min(df['basic_ub'][i], df['final_ub'][i-1])
        else:
            df['final_ub'][i] = df['basic_ub'][i]
        if (df['close'][i-1] >= df['final_lb'][i-1]):
            df['final_lb'][i] = max(df['basic_lb'][i], df['final_lb'][i-1])
        else:
            df['final_lb'][i] = df['basic_lb'][i]
    df['supertrend'] = np.nan
    for i in range(len(df)):
        if (df['close'][i] <= df['final_ub'][i]):
            df['supertrend'][i] = df['final_ub'][i]
        else:
            df['supertrend'][i] = df['final_lb'][i]
    df['in_uptrend'] = df['close'] > df['supertrend']
    return df

def calc_adx(df, period=14):
    """ADX trend strength calculation."""
    plus_dm = df['high'].diff()
    minus_dm = df['low'].diff() * -1
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0
    tr = calc_atr(df, period)['ATR']
    plus_di = 100 * (plus_dm.rolling(window=period).sum() / tr)
    minus_di = 100 * (minus_dm.rolling(window=period).sum() / tr)
    dx = 100 * (abs(plus_di - minus_di) / (plus_di + minus_di))
    adx = dx.rolling(window=period).mean()
    df['ADX'] = adx
    return df
