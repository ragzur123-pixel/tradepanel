import pandas as pd
import numpy as np

def calculate_rsi(series, period=14):
    """
    Wilder's Smoothing RSI implementation (matches TradingView/MT4).
    Uses SMMA (Smoothed Moving Average) instead of Simple Moving Average.
    """
    if len(series) < period:
        return pd.Series([50.0] * len(series), index=series.index)
    
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    # Wilder's Smoothing (SMMA): First value is SMA, subsequent are EMA-like
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    
    for i in range(period, len(series)):
        avg_gain.iloc[i] = (avg_gain.iloc[i-1] * (period - 1) + gain.iloc[i]) / period
        avg_loss.iloc[i] = (avg_loss.iloc[i-1] * (period - 1) + loss.iloc[i]) / period
        
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50.0)

def calculate_sma(series, period=20):
    """Pure Pandas implementation of SMA."""
    return series.rolling(window=period).mean()

def calculate_ema(series, period=20):
    """Pure Pandas implementation of EMA."""
    if len(series) == 0: return pd.Series([])
    return series.astype(float).ewm(span=period, adjust=False).mean()

def calculate_atr(df, period=14):
    """
    Wilder's ATR implementation. 
    Matches standard trading platform volatility measurements.
    """
    high = df['High']
    low = df['Low']
    close = df['Close']
    
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # Wilder's Smoothing for ATR
    atr = tr.rolling(window=period, min_periods=period).mean()
    for i in range(period, len(df)):
        atr.iloc[i] = (atr.iloc[i-1] * (period - 1) + tr.iloc[i]) / period
        
    return atr.fillna(tr.mean())

def calculate_adx(df, period=14):
    """
    Average Directional Index (ADX) implementation.
    Identifies trend strength (ADX > 20-25 indicates trending market).
    """
    df = df.copy()
    high = df['High']
    low = df['Low']
    close = df['Close']
    
    # 1. True Range
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # 2. Directional Movement
    up_move = high - high.shift()
    down_move = low.shift() - low
    
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0).flatten()
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0).flatten()
    
    # 3. Smoothed TR, +DM, -DM
    atr = calculate_atr(df, period)
    
    smooth_plus_dm = pd.Series(plus_dm, index=df.index).rolling(window=period).mean()
    smooth_minus_dm = pd.Series(minus_dm, index=df.index).rolling(window=period).mean()
    
    for i in range(period, len(df)):
        smooth_plus_dm.iloc[i] = (smooth_plus_dm.iloc[i-1] * (period - 1) + plus_dm[i]) / period
        smooth_minus_dm.iloc[i] = (smooth_minus_dm.iloc[i-1] * (period - 1) + minus_dm[i]) / period
        
    # 4. +DI and -DI
    plus_di = 100 * (smooth_plus_dm / atr)
    minus_di = 100 * (smooth_minus_dm / atr)
    
    # 5. DX and ADX
    dx = 100 * (abs(plus_di - minus_di) / (plus_di + minus_di))
    adx = dx.rolling(window=period).mean()
    
    for i in range(period * 2 - 1, len(df)):
        adx.iloc[i] = (adx.iloc[i-1] * (period - 1) + dx.iloc[i]) / period
        
    return adx.fillna(0.0)

def calculate_donchian(df, period=20):
    """Pure Pandas implementation of Donchian Channels."""
    upper = df['High'].rolling(window=period).max()
    lower = df['Low'].rolling(window=period).min()
    return lower, upper

def calculate_pivots(df):
    """Calculates Standard Pivot Points (P, R1, S1)."""
    if len(df) < 2:
        return None
    
    last_day = df.iloc[-2] # Assume daily or previous candle
    high = last_day['High']
    low = last_day['Low']
    close = last_day['Close']
    
    p = (high + low + close) / 3
    r1 = (2 * p) - low
    s1 = (2 * p) - high
    return {"P": p, "R1": r1, "S1": s1}

def calculate_zscore(series, window=20):
    """Calculates Rolling Z-Score of a series."""
    mean = series.rolling(window=window).mean()
    std = series.rolling(window=window).std()
    return (series - mean) / std

def calculate_beta(asset_returns, market_returns, window=60):
    """
    Calculates Beta (Systemic Risk) of an asset relative to the market.
    Beta = Cov(Asset, Market) / Var(Market)
    """
    combined = pd.concat([asset_returns, market_returns], axis=1).dropna()
    if len(combined) < window: return 1.0
    
    cov = combined.rolling(window=window).cov().iloc[-1, 1]
    var = combined.iloc[:, 1].rolling(window=window).var().iloc[-1]
    return cov / var if var > 0 else 1.0

def calculate_ou_params(series):
    """
    Fits Ornstein-Uhlenbeck (OU) process to a series.
    Returns: Lambda (Speed of Reversion), Half-Life (Days), Equilibrium Mean.
    """
    # spread_t = alpha + beta * spread_{t-1} + epsilon
    s_t = series.iloc[1:].values
    s_prev = series.iloc[:-1].values
    
    # Linear Regression
    from scipy import stats
    beta, alpha, r_val, p_val, std_err = stats.linregress(s_prev, s_t)
    
    # Lambda = -ln(beta) / dt (dt = 1/252 for daily, 1 for bar-count)
    lmbda = -np.log(beta) if beta > 0 else 0.0001
    half_life = np.log(2) / lmbda if lmbda > 0 else 999
    mu = alpha / (1 - beta)
    
    return {"lambda": round(lmbda, 5), "half_life": round(half_life, 2), "mu": round(mu, 5)}

def add_indicators(df):
    """Add mission-critical indicators to the dataframe without external TA libraries."""
    df = df.copy()
    df['RSI_14'] = calculate_rsi(df['Close'], 14)
    df['ATR_14'] = calculate_atr(df, 14)
    df['ADX_14'] = calculate_adx(df, 14)
    df['SMA_20'] = calculate_sma(df['Close'], 20)
    df['SMMA_20'] = calculate_smma(df['Close'], 20)
    df['EMA_20'] = calculate_ema(df['Close'], 20)
    df['DCL_20'], df['DCU_20'] = calculate_donchian(df, 20)
    
    cvd, cvd_gradient = calculate_cvd(df)
    df['CVD'] = cvd
    df['CVD_Gradient'] = cvd_gradient
    
    # Pivots are usually scalar for the current day
    pivots = calculate_pivots(df)
    if pivots:
        df['Pivot_P'] = pivots['P']
        df['Pivot_R1'] = pivots['R1']
        df['Pivot_S1'] = pivots['S1']
        
    return df

def calculate_adv(df, period=20):
    """Average Daily Volume (Susceptible to Block Trade Distortion)"""
    return df['Volume'].rolling(window=period).mean()

def calculate_mdv(df, period=20):
    """
    Median Daily Volume (MDV). 
    Replaces ADV to strip out massive institutional block trades 
    that give a false sense of retail liquidity on free data feeds.
    """
    return df['Volume'].rolling(window=period).median()

def round_to_tick(price, market='BIST'):
    """Ensures price is compliant with Borsa Istanbul tick sizes."""
    if market != 'BIST': return round(price, 2)
    if pd.isna(price) or price <= 0: return price
    
    if price < 20: tick = 0.01
    elif price < 50: tick = 0.02
    elif price < 100: tick = 0.05
    elif price < 250: tick = 0.10
    elif price < 500: tick = 0.25
    elif price < 1000: tick = 0.50
    elif price < 2500: tick = 1.00
    else: tick = 2.50
    
    return round(round(price / tick) * tick, 2)

# --- PHASE 1: ALPHA & MICROSTRUCTURE PIPELINE ---

def calculate_smma(series, period=20):
    """
    Wilder's Smoothing (SMMA). 
    Used for professional-grade RSI, ATR, and moving average stability.
    """
    if len(series) < period:
        return series.rolling(window=period).mean()
    smma = series.rolling(window=period, min_periods=period).mean()
    for i in range(period, len(series)):
        smma.iloc[i] = (smma.iloc[i-1] * (period - 1) + series.iloc[i]) / period
    return smma

def validate_ou_stationarity(series, max_half_life=15.0):
    """
    ALPHA-02: Index-Basis Error detection and Ornstein-Uhlenbeck (OU) process stationarity validation.
    """
    params = calculate_ou_params(series)
    params['is_stationary'] = params['lambda'] > 0 and params['half_life'] < max_half_life
    return params

def calculate_volume_delta(df):
    """
    Approximates Volume Delta (Order Flow) from OHLCV data.
    Measures the 'Intra-Candle' buying vs selling pressure.
    """
    range_val = (df['High'] - df['Low']).replace(0, 0.0001)
    buy_pressure = (df['Close'] - df['Low']) / range_val
    sell_pressure = (df['High'] - df['Close']) / range_val
    delta = df['Volume'] * (buy_pressure - sell_pressure)
    return delta

def calculate_cvd(df):
    """
    ALPHA-01: Cumulative Volume Delta (CVD) and Aggression Gradients.
    """
    delta = calculate_volume_delta(df)
    cvd = delta.cumsum()
    cvd_gradient = cvd.diff()
    return cvd, cvd_gradient

def calculate_swing_points(df, window=5):
    """Programmatically identify Swing Highs and Lows."""
    df = df.copy()
    df['is_high'] = df['High'] == df['High'].rolling(window=window*2+1, center=True).max()
    df['is_low'] = df['Low'] == df['Low'].rolling(window=window*2+1, center=True).min()
    
    df['swing_high'] = np.where(df['is_high'], df['High'], np.nan)
    df['swing_low'] = np.where(df['is_low'], df['Low'], np.nan)
    return df.drop(columns=['is_high', 'is_low'])

def detect_liquidity_sweeps(df, window=20):
    """ALPHA-03: Identifies Stop Runs (Liquidity Sweeps)."""
    df_swings = calculate_swing_points(df, window=5)
    highs = df_swings['swing_high'].dropna()
    lows = df_swings['swing_low'].dropna()
    
    if len(highs) < 2 or len(lows) < 2: return []
    
    latest = df.iloc[-1]
    sweeps = []
    
    prev_high = highs.iloc[-2]
    if latest['High'] > prev_high and latest['Close'] < prev_high:
        sweeps.append({"type": "BEARISH_LIQUIDITY_SWEEP", "level": prev_high})
        
    prev_low = lows.iloc[-2]
    if latest['Low'] < prev_low and latest['Close'] > prev_low:
        sweeps.append({"type": "BULLISH_LIQUIDITY_SWEEP", "level": prev_low})
        
    return sweeps

def detect_absorption(df, threshold_sigma=2.0):
    """ALPHA-03: Identifies 'Absorption' (High Effort, No Result)."""
    if len(df) < 20: return []
    
    delta = calculate_volume_delta(df)
    body_size = abs(df['Close'] - df['Open'])
    
    delta_mean = delta.abs().mean()
    delta_std = delta.abs().std()
    
    latest_delta = delta.iloc[-1]
    latest_body = body_size.iloc[-1]
    
    is_high_delta = abs(latest_delta) > (delta_mean + threshold_sigma * delta_std)
    is_small_body = latest_body < body_size.tail(20).median()
    
    results = []
    if is_high_delta and is_small_body:
        side = "BULLISH_ABSORPTION" if latest_delta > 0 else "BEARISH_ABSORPTION"
        results.append({"type": side, "level": df['Close'].iloc[-1]})
        
    return results

class ContrarianTrapHunter:
    """ALPHA-03: Identifies 'Retail Crowds' and 'Institutional Traps'."""
    def identify_trap_scenarios(self, df):
        if df is None or len(df) < 50: return []
        sweeps = detect_liquidity_sweeps(df)
        absorption = detect_absorption(df)
        traps = []
        
        bear_sweeps = [s for s in sweeps if s['type'] == "BEARISH_LIQUIDITY_SWEEP"]
        bull_abs = [a for a in absorption if a['type'] == "BULLISH_ABSORPTION"]
        if bear_sweeps and bull_abs: traps.append({"type": "TRAP_THE_BEARS"})
            
        bull_sweeps = [s for s in sweeps if s['type'] == "BULLISH_LIQUIDITY_SWEEP"]
        bear_abs = [a for a in absorption if a['type'] == "BEARISH_ABSORPTION"]
        if bull_sweeps and bear_abs: traps.append({"type": "TRAP_THE_BULLS"})
            
        return traps


