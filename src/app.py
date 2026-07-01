# -*- coding: utf-8 -*-
import streamlit as st
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime, timezone
import importlib
import news_sentinel
importlib.reload(news_sentinel)
from news_sentinel import NewsSentinel
from data_node import SovereignDataNode

sentinel = NewsSentinel()
# --- CONFIG & CONNECTION ---
st.set_page_config(page_title="Risk Desk", layout="wide", initial_sidebar_state="collapsed")
load_dotenv()

@st.cache_resource
def init_connection():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    return create_client(url, key)

supabase = init_connection()

# EXEC-07: Persistent Execution Environment
if 'metadata_loaded' not in st.session_state:
    try:
        meta_res = supabase.table("metadata").select("*").eq("id", 1).execute()
        if meta_res.data:
            meta = meta_res.data[0]
            st.session_state['capital_try_val'] = float(meta.get('capital_try') or 100000.0)
            st.session_state['capital_usd_val'] = float(meta.get('capital_usd') or 10000.0)
            st.session_state['risk_pct_val'] = float(meta.get('risk_pct') or 1.0)
        else:
            st.session_state['capital_try_val'] = 100000.0
            st.session_state['capital_usd_val'] = 10000.0
            st.session_state['risk_pct_val'] = 1.0
        st.session_state['metadata_loaded'] = True
    except:
        st.session_state['capital_try_val'] = 100000.0
        st.session_state['capital_usd_val'] = 10000.0
        st.session_state['risk_pct_val'] = 1.0

def update_metadata():
    try:
        supabase.table("metadata").upsert({
            "id": 1,
            "capital_try": st.session_state['capital_try_input'],
            "capital_usd": st.session_state['capital_usd_input'],
            "risk_pct": st.session_state['risk_pct_input']
        }).execute()
        st.session_state['capital_try_val'] = st.session_state['capital_try_input']
        st.session_state['capital_usd_val'] = st.session_state['capital_usd_input']
        st.session_state['risk_pct_val'] = st.session_state['risk_pct_input']
    except Exception as e:
        st.sidebar.error(f"Failed to sync parameters: {e}")

# --- SIDEBAR: RISK CONFIGURATION ---
with st.sidebar:
    st.markdown("##  Institutional Capital")
    st.markdown("Configure your wallet to dynamically calculate exact Kelly position sizes based on Stop Loss distances.")
    capital_try = st.number_input("BIST Portfolio Capital (₺)", min_value=1000, max_value=100000000, value=int(st.session_state['capital_try_val']), step=10000, key="capital_try_input", on_change=update_metadata)
    capital_usd = st.number_input("US Portfolio Capital ($)", min_value=100, max_value=10000000, value=int(st.session_state['capital_usd_val']), step=1000, key="capital_usd_input", on_change=update_metadata)
    risk_pct = st.slider("Risk Per Trade (%)", min_value=0.1, max_value=5.0, value=float(st.session_state['risk_pct_val']), step=0.1, key="risk_pct_input", on_change=update_metadata)
    
    st.session_state['capital_try'] = capital_try
    st.session_state['capital_usd'] = capital_usd
    st.session_state['risk_pct'] = risk_pct
    
    st.markdown("---")
    st.markdown(f"**BIST Risk Limit:** {capital_try * (risk_pct/100):.2f} ₺")
    st.markdown(f"**US Risk Limit:** ${capital_usd * (risk_pct/100):.2f}")

# Professional Global CSS
st.markdown("""
<style>
    html, body, [class*="css"]  {
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace !important;
        -webkit-font-smoothing: antialiased;
        color: #E2E8F0;
    }

    /* Hide default details triangle for exact centering */
    details > summary {
        list-style: none;
    }
    details > summary::-webkit-details-marker {
        display: none;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: #000000;
        padding: 6px;
        border-radius: 2px;
        /* flat */;
        -webkit-/* flat */;
        border: 1px solid #27272a;
    }
    .stTabs [data-baseweb="tab"] {
        height: 38px;
        border-radius: 2px;
        padding: 0 24px;
        color: #94A3B8;
        font-weight: 500;
        letter-spacing: 0.3px;
        font-size: 15px;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(255, 255, 255, 0.08) !important;
        color: #FFFFFF !important;
        box-shadow: none;
    }
    [data-testid="stSidebar"] {
        display: none !important;
    }
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    /* Dropdown / Expander UI */
    [data-testid="stExpander"] details {
        background: #000000 !important;
        border: 1px solid #27272a !important;
        border-radius: 2px !important;
        overflow: hidden;
    }
    [data-testid="stExpander"] summary {
        padding: 12px 16px !important;
        color: #F8FAFC !important;
        font-weight: 500 !important;
        background: rgba(255,255,255,0.02) !important;
        transition: background 0.2s;
    }
    [data-testid="stExpander"] summary:hover {
        background: #27272a !important;
    }
    [data-testid="stExpander"] {
        border: none !important;
        background: transparent !important;
    }
    
    /* Remove Native Top White Space */
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 2rem !important;
    }
    header[data-testid="stHeader"] {
        display: none !important;
    }
    /* SVGs */
    svg {
        display: inline-block;
        vertical-align: middle;
    }
</style>
""", unsafe_allow_html=True)



@st.cache_data(ttl=3600)
def fetch_dominant_sector():
    node = SovereignDataNode()
    return node.get_sector_rotation()

@st.cache_data(ttl=3600)
def fetch_usd_rate():
    try:
        import yfinance as yf
        df = yf.download("USDTRY=X", period="1d", progress=False)
        return float(df['Close'].iloc[-1])
    except:
        return 35.0

import sqlite3
import json
import time

class SQLiteUIBuffer:
    def __init__(self, client):
        self.client = client
        self.db_path = "ui_cache.db"
        self._init_db()
        
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute('''CREATE TABLE IF NOT EXISTS cache (
                        query_hash TEXT PRIMARY KEY,
                        data TEXT,
                        updated_at REAL
                    )''')
        conn.commit()
        conn.close()
        
    def fetch(self, query_hash, fetch_func, max_age=15):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT data, updated_at FROM cache WHERE query_hash=?", (query_hash,))
        row = c.fetchone()
        now = time.time()
        
        if row is None or (now - row[1]) > max_age:
            try:
                data = fetch_func()
                c.execute("INSERT OR REPLACE INTO cache (query_hash, data, updated_at) VALUES (?, ?, ?)",
                          (query_hash, json.dumps(data), now))
                conn.commit()
            except Exception as e:
                data = json.loads(row[0]) if row else None
        else:
            data = json.loads(row[0])
            
        conn.close()
        return data

@st.cache_resource
def get_db_buffer():
    return SQLiteUIBuffer(supabase)

db_buffer = get_db_buffer()

# --- DATA FETCHING ---
@st.cache_data(ttl=15)
def get_metadata():
    def _fetch():
        res = supabase.table("metadata").select("*").eq("id", 1).execute()
        return res.data[0] if res.data else None
    return db_buffer.fetch("metadata_id_1", _fetch)

@st.cache_data(ttl=15)
def get_limits(bucket=None):
    def _fetch():
        query = supabase.table("limits").select("*")
        if bucket:
            query = query.eq("bucket", bucket)
        res = query.execute()
        return res.data
    return db_buffer.fetch(f"limits_{bucket}", _fetch)

@st.cache_data(ttl=15)
def get_watchlist_full():
    def _fetch():
        res = supabase.table("watchlist").select("*").execute()
        return res.data
    return db_buffer.fetch("watchlist_full", _fetch)

@st.cache_data(ttl=60)
def get_bayesian_win_rates():
    from bayesian_self_auditor import BayesianSelfAuditor
    import db_manager
    auditor = BayesianSelfAuditor(db_manager.SovereignDatabase())
    return auditor.get_realized_edge()

@st.cache_data(ttl=60)
def get_live_portfolio_prices(tickers):
    if not tickers: return {}
    import yfinance as yf
    try:
        data = yf.download(tickers, period="5d", interval="15m", progress=False)
        prices = {}
        if not data.empty and 'Close' in data.columns:
            if len(tickers) == 1:
                try:
                    prices[tickers[0]] = float(data['Close'].dropna().iloc[-1])
                except:
                    pass
            else:
                for t in tickers:
                    try:
                        prices[t] = float(data['Close'][t].dropna().iloc[-1])
                    except:
                        pass
        return prices
    except:
        return {}

@st.cache_data(ttl=15)
def get_open_portfolio():
    def _fetch():
        res = supabase.table("portfolio").select("ticker").eq("status", "OPEN").execute()
        return [p['ticker'] for p in res.data] if res.data else []
    return db_buffer.fetch("portfolio_open_tickers", _fetch)

@st.cache_data(ttl=15)
def get_open_portfolio_full():
    def _fetch():
        res = supabase.table("portfolio").select("*").eq("status", "OPEN").execute()
        return res.data or []
    return db_buffer.fetch("portfolio_open_full", _fetch)

@st.cache_data(ttl=15)
def check_tilt_lockout():
    """ALPH-04: Psychological Tilt Lockout"""
    def _fetch():
        res = supabase.table("portfolio").select("*").eq("status", "CLOSED").order('exit_date', desc=True).limit(3).execute()
        return res.data
    history = db_buffer.fetch("portfolio_closed_3", _fetch)
    if history and len(history) == 3:
        all_losses = all(t.get('net_pnl', 0) < 0 for t in history)
        if all_losses:
            oldest_exit_str = history[2].get('exit_date')
            if oldest_exit_str:
                oldest_exit = datetime.fromisoformat(oldest_exit_str.replace('Z', '+00:00'))
                if (datetime.now(timezone.utc) - oldest_exit).total_seconds() < 86400:
                    return True
    return False

# --- SYSTEM HEALTH ---
meta = get_metadata()
if not meta:
    st.error("System Metadata not found. Run schema.sql and check worker.")
    st.stop()

last_success = datetime.fromisoformat(meta['last_success'].replace('Z', '+00:00'))
delta = datetime.now(timezone.utc) - last_success
usd_rate = fetch_usd_rate()

# SVG ICONS
ICON_ALERT = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>'
ICON_TARGET = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>'
ICON_SHIELD = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>'
ICON_TREND = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"></polyline><polyline points="16 7 22 7 22 13"></polyline></svg>'

# --- TOP NAVIGATION BAR ---
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; padding-top: 8px;">
            <h1 style="font-weight: 700; font-size: 32px; color: #F8FAFC; margin: 0; letter-spacing: -0.02em;">RISK DESK</h1>
            <p style="font-weight: 400; font-size: 15px; color: #8E8E93; margin: 4px 0 0 0;">Execution Terminal</p>
        </div>
    """, unsafe_allow_html=True)


with col2:
    status_color = "#00ff00" if delta.total_seconds() < 900 else "#ff4d4d"
    bg_color = "rgba(16, 185, 129, 0.15)" if delta.total_seconds() < 900 else "rgba(255, 77, 77, 0.15)"
    border_color = "rgba(16, 185, 129, 0.3)" if delta.total_seconds() < 900 else "rgba(255, 77, 77, 0.3)"
    
    st.markdown(f"""
        <div style="display: flex; justify-content: center; align-items: center; gap: 10px; padding: 12px 16px; background: {bg_color}; border-radius: 2px; border: 1px solid {border_color}; box-shadow: none; margin-bottom: 12px; margin-top: 12px;">
            <div style="width: 10px; height: 10px; border-radius: 50%; background-color: {status_color}; box-shadow: none;"></div>
            <span style="font-size: 13px; color: #F8FAFC; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase;">Engine Synced ({delta.total_seconds() // 60:.0f}m ago)</span>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("Manual Refresh", use_container_width=True):
        st.cache_data.clear()
        try:
            import threading
            import subprocess
            import time
            
            with st.spinner("Initializing Engine Sync..."):
                # Instantly update heartbeat so UI timer zeroes out
                supabase.table("metadata").update({"last_success": datetime.now(timezone.utc).isoformat()}).eq("id", 1).execute()
                
                # Spin up heavy backend engine in background thread so Streamlit doesn't freeze
                def run_worker():
                    subprocess.run(["python", "src/worker.py"])
                threading.Thread(target=run_worker, daemon=True).start()
                
                time.sleep(1.5) # Provide visual feedback that the button was pressed
                
            st.toast("Engine Sync started in background! Data will update automatically.", icon="🔄")
            time.sleep(0.5)
        except:
            pass
        st.rerun()

    st.markdown("<hr style='border-color: #27272a; margin: 16px 0;'>", unsafe_allow_html=True)
    st.markdown("<div style='color: #64748B; font-size: 11px; text-transform: uppercase; margin-bottom: 8px; font-weight: 600;'>INST-03: Pre-Market</div>", unsafe_allow_html=True)
    
    def generate_briefing():
        lines = []
        lines.append("# SOVEREIGN PRE-MARKET BRIEFING")
        lines.append(f"**Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d')}")
        lines.append(f"**Macro Regime:** {meta.get('bist_regime', 'UNKNOWN')} / US Regime: {meta.get('us_regime', 'UNKNOWN')}")
        lines.append("")
        
        all_limits = []
        for b in ["CORE", "SATELLITE", "GAMBLER"]:
            for l in get_limits(b):
                if "ACTION ZONE" in str(l.get('status', '')):
                    all_limits.append(l)
        
        all_limits.sort(key=lambda x: x.get('alpha_score', 0), reverse=True)
        top3 = all_limits[:3]
        
        lines.append("##  TOP 3 'A+' ASYMMETRIC SETUPS (Place GTC Limits)")
        if top3:
            for t in top3:
                lines.append(f"- **{t['ticker']}** ({t['bucket']}): Buy Limit @ {t['buy_limit']:.2f} | Target: {t['sell_target']:.2f} | Stop: {t['stop_loss']:.2f} | Alpha Score: {t.get('alpha_score', 0)}")
        else:
            lines.append("- No ACTION ZONE setups currently triggered. Keep powder dry.")
            
        lines.append("")
        lines.append("## <svg width='1em' height='1em' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z'></path><circle cx='12' cy='12' r='4'></circle></svg> ACTIVE OPERATIONS (Trailing Stops to Update)")
        try:
            open_pos = get_open_portfolio_full()
            if open_pos:
                for pos in open_pos:
                    lines.append(f"- **{pos.get('ticker')}**: Exit Target: {pos.get('exit_target')} | Hard Stop: {pos.get('stop_loss')}")
            else:
                lines.append("- No active exposure.")
        except:
            pass
            
        return "\n".join(lines)

    st.download_button("Download Morning Briefing", data=generate_briefing(), file_name=f"sovereign_briefing_{datetime.now(timezone.utc).strftime('%Y%m%d')}.md", mime="text/markdown", use_container_width=True)

now_utc = datetime.now(timezone.utc)
is_weekend = now_utc.weekday() >= 5
if delta.total_seconds() > 900 and not is_weekend: # 15 Minutes Max Latency during market days
    st.markdown(f"""
        <div style="background: rgba(239, 68, 68, 0.1); padding: 24px; border-radius: 2px; border: 1px solid rgba(239, 68, 68, 0.2); color: #FCA5A5; display: flex; align-items: center; gap: 16px; margin-bottom: 24px;">
            {ICON_ALERT}
            <div>
                <h3 style="margin: 0; font-weight: 500; color: #FECACA;">EXE-03 SILENT DEATH: Execution Lock Engaged</h3>
                <p style="margin: 4px 0 0 0; font-size: 15px;">worker.py has not successfully pushed limits in {delta.total_seconds() / 60:.1f} minutes. Trading on ghost limits guarantees slippage loss. UI is locked until the background node is revived.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

if meta.get('circuit_breaker') == 'TRIPPED':
    st.markdown(f"""
        <div style="background: rgba(239, 68, 68, 0.1); padding: 24px; border-radius: 2px; border: 1px solid rgba(239, 68, 68, 0.2); color: #FCA5A5; display: flex; align-items: center; gap: 16px; margin-bottom: 24px;">
            {ICON_ALERT}
            <div>
                <h3 style="margin: 0; font-weight: 500; color: #FECACA;">Circuit Breaker Engaged</h3>
                <p style="margin: 4px 0 0 0; font-size: 15px;">Extreme macro volatility detected. Trading is mathematically unsafe. Preserve capital.</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

def classify_ticker(ticker, market):
    try:
        import yfinance as yf
        info = yf.Ticker(ticker).info
        mcap = info.get('marketCap', 0)
        
        if market == "US":
            if mcap > 50_000_000_000: return "CORE"
            elif mcap > 2_000_000_000: return "SATELLITE"
            else: return "GAMBLER"
        else:
            if mcap > 100_000_000_000: return "CORE" 
            elif mcap > 15_000_000_000: return "SATELLITE"
            else: return "GAMBLER"
    except:
        return "SATELLITE"

with st.expander("TICKER MANAGEMENT", expanded=False):
    st.markdown("### Discovery / Screen")
    
    tab_manual, tab_radar = st.tabs(["Add Symbol", "Screener"])
    
    with tab_manual:
        st.markdown("Add a new security to the monitoring watchlist. The system will automatically classify its risk bucket.")
        col_t1, col_t2 = st.columns([3, 1])
        with col_t1:
            new_ticker = st.text_input("Ticker Symbol (e.g. AAPL, THYAO.IS)")
        with col_t2:
            st.write("") # Spacer
            st.write("")
            if st.button("Analyze & Add", use_container_width=True):
                if new_ticker:
                    new_ticker = new_ticker.strip().upper()
                    market = "BIST" if new_ticker.endswith(".IS") else "US"
                    
                    with st.spinner(f"Analyzing {new_ticker}..."):
                        bucket = classify_ticker(new_ticker, market)
                        try:
                            supabase.table("watchlist").insert({"ticker": new_ticker, "bucket": bucket, "market": market}).execute()
                            st.success(f"Assigned {new_ticker} to {bucket} bucket.")
                            st.cache_data.clear()
                            import threading
                            import subprocess
                            def run_worker_fast():
                                subprocess.run(["python", "src/worker.py"])
                            threading.Thread(target=run_worker_fast, daemon=True).start()
                        except Exception as e:
                            if "duplicate key" in str(e).lower():
                                st.warning(f"{new_ticker} is already in the watchlist.")
                            else:
                                st.error(f"Failed to inject: {e}")
                                
    with tab_radar:
        st.markdown("Screen predefined universe for structural uptrends with momentum pullbacks.")
        
        if "radar_results" not in st.session_state:
            st.session_state.radar_results = []
            
        if st.button("Run Screener", use_container_width=True):
            with st.spinner("Scanning S&P 500 and BIST 30 for high-probability setups..."):
                existing = [x['ticker'] for x in get_watchlist_full()]
                universe = [
                    "GARAN.IS", "SISE.IS", "FROTO.IS", "TTKOM.IS", "TOASO.IS", "PGSUS.IS", "SAHOL.IS", "YKBNK.IS", "ENKAI.IS", "ISCTR.IS",
                    "GOOG", "AMZN", "META", "AMD", "PLTR", "CRWD", "SNOW", "UBER", "SHOP", "NET"
                ]
                candidates = [t for t in universe if t not in existing]
                
                import yfinance as yf
                import pandas as pd
                results = []
                
                for t in candidates[:12]: # Scan up to 12 at a time for speed
                    try:
                        df = yf.download(t, period="1y", progress=False)
                        if len(df) < 200: continue
                        if isinstance(df.columns, pd.MultiIndex):
                            df.columns = df.columns.get_level_values(0)
                            
                        close_px = df['Close'].iloc[-1]
                        sma200 = df['Close'].rolling(window=200).mean().iloc[-1]
                        
                        if close_px > sma200:
                            delta = df['Close'].diff()
                            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                            rs = gain / loss
                            rsi = 100 - (100 / (1 + rs)).iloc[-1]
                            
                            if rsi < 55:
                                results.append({"ticker": t, "price": float(close_px), "rsi": float(rsi)})
                    except:
                        pass
                
                st.session_state.radar_results = sorted(results, key=lambda x: x['rsi'])[:3]
                
        if st.session_state.radar_results:
            st.success(f"Radar discovered {len(st.session_state.radar_results)} prime candidates!")
            for r in st.session_state.radar_results:
                col_r1, col_r2, col_r3 = st.columns([2, 2, 2])
                with col_r1:
                    st.markdown(f"**{r['ticker']}**")
                with col_r2:
                    st.markdown(f"RSI: {r['rsi']:.1f}")
                with col_r3:
                    if st.button(f"Add {r['ticker']}", key=f"inj_{r['ticker']}"):
                        mkt = "BIST" if r['ticker'].endswith(".IS") else "US"
                        bkt = classify_ticker(r['ticker'], mkt)
                        try:
                            supabase.table("watchlist").insert({"ticker": r['ticker'], "bucket": bkt, "market": mkt}).execute()
                            st.toast(f"Added {r['ticker']}!")
                            st.session_state.radar_results = [x for x in st.session_state.radar_results if x['ticker'] != r['ticker']]
                            st.cache_data.clear()
                            st.rerun()
                        except:
                            pass
        elif st.button("Clear Radar", key="clear_radar") if st.session_state.radar_results else False:
            st.session_state.radar_results = []
            st.rerun()

@st.cache_data(ttl=900)
def fetch_sparkline_data(ticker, period="1M"):
    try:
        import yfinance as yf
        t = yf.Ticker(ticker)
        if period == "1D":
            df = t.history(period="1d", interval="5m")
            fmt = "%H:%M"
        elif period == "1W":
            df = t.history(period="5d", interval="15m")
            fmt = "%b %d, %H:%M"
        elif period == "3M":
            df = t.history(period="3mo", interval="1d")
            fmt = "%b %d"
        else: # 1M
            df = t.history(period="1mo", interval="1h")
            fmt = "%b %d, %H:%M"
            
        if df.empty:
            return [], []
        return df.index.strftime(fmt).tolist(), df['Close'].dropna().tolist()
    except:
        return [], []

@st.cache_data(ttl=900)
def cached_fetch_news(ticker):
    try:
        data = sentinel.fetch_latest_news(ticker)
        return data if data else []
    except Exception as e:
        return []


# --- HELPER FUNCTIONS ---
def generate_svg_sparkline(dates, prices, color="#3B82F6"):
    if not prices or len(prices) < 2:
        return ""
    
    height = 70
    min_p, max_p = min(prices), max(prices)
    padding = (max_p - min_p) * 0.1
    if padding == 0: padding = max_p * 0.01
    
    min_p -= padding
    max_p += padding
    range_p = max_p - min_p
    
    points = []
    base_price = prices[0]
    
    for i, p in enumerate(prices):
        x = (i / (len(prices) - 1)) * 100
        y = height - ((p - min_p) / range_p) * height
        points.append(f"{x},{y}")
        
    polyline_points = " ".join(points)
    polygon_points = f"0,{height} {polyline_points} 100,{height}"
    
    svg = f'''<svg width="100%" height="{height}px" viewBox="0 0 100 {height}" preserveAspectRatio="none" style="display: block;"><defs><linearGradient id="grad_{color.replace('#','')}" x1="0%" y1="0%" x2="0%" y2="100%"><stop offset="0%" stop-color="{color}" stop-opacity="0.25"/><stop offset="100%" stop-color="{color}" stop-opacity="0.0"/></linearGradient></defs><polygon points="{polygon_points}" fill="url(#grad_{color.replace('#','')})" /><polyline points="{polyline_points}" fill="none" stroke="{color}" stroke-width="2" vector-effect="non-scaling-stroke" stroke-linecap="round" stroke-linejoin="round"/></svg>'''
    
    bars_html = []
    bar_width = 100 / len(prices)
    for i, (d, p) in enumerate(zip(dates, prices)):
        left_pct = (i / (len(prices) - 1)) * 100
        pct_change = ((p - base_price) / base_price) * 100
        sign = "+" if pct_change >= 0 else ""
        p_color = "#00ff00" if pct_change >= 0 else "#ff4d4d"
        
        tt_side = "left: 10px;" if left_pct < 50 else "right: 10px;"
        dot_y = height - ((p - min_p) / range_p) * height
        
        bars_html.append(f'''<div class="spark-bar" style="position: absolute; left: {i * bar_width}%; width: {bar_width}%; height: 100%; top: 0; z-index: 10;"><div class="spark-crosshair" style="position: absolute; left: 50%; top: 0; height: 100%; width: 1px; border-left: 1px dashed {color}; opacity: 0; pointer-events: none;"></div><div class="spark-dot" style="position: absolute; left: 50%; top: {dot_y}px; transform: translate(-50%, -50%); width: 8px; height: 8px; border-radius: 50%; background: {color}; border: 2px solid #0F172A; opacity: 0; pointer-events: none;"></div><div class="spark-tt" style="position: absolute; {tt_side} top: 0px; background: rgba(15, 23, 42, 0.95); border: 1px solid rgba(255,255,255,0.1); border-radius: 2px; padding: 8px 12px; opacity: 0; pointer-events: none; width: max-content; box-shadow: none; transition: opacity 0.1s; /* flat */;"><div style="font-size: 11px; color: #94A3B8; margin-bottom: 2px;">{d}</div><div style="display: flex; gap: 12px; align-items: baseline;"><span style="font-size: 14px; font-weight: 600; color: #F8FAFC;">{p:,.2f}₺</span><span style="font-size: 11px; font-weight: 600; color: {p_color};">{sign}{pct_change:.1f}%</span></div></div></div>''')
        
    wrapper = f'''<style>.spark-bar:hover .spark-crosshair {{ opacity: 0.6 !important; }} .spark-bar:hover .spark-dot {{ opacity: 1 !important; }} .spark-bar:hover .spark-tt {{ opacity: 1 !important; z-index: 50; }}</style><div style="position: relative; margin: 8px 0 16px 0; height: {height}px; width: 100%;">{svg}{"".join(bars_html)}</div>'''
    return wrapper

def parse_tr_float(val_str, default=0.0):
    try:
        val_str = str(val_str).strip()
        if not val_str: return default
        if "," in val_str:
            clean = val_str.replace(".", "").replace(",", ".")
            return float(clean)
        else:
            clean = val_str.replace(".", "")
            return float(clean)
    except Exception:
        return default

def tr_fmt(val):
    return f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def format_input_cb(key):
    val_str = st.session_state[key]
    if not str(val_str).strip():
        st.session_state[key] = "0"
        return
    val_float = parse_tr_float(val_str)
    fmt_val = tr_fmt(val_float)
    if fmt_val.endswith(",00"):
        fmt_val = fmt_val[:-3]
    st.session_state[key] = fmt_val

@st.fragment
def render_single_card(stock, realized_win_rates=None):
    status_text = stock.get('status') or 'NEUTRAL'
    status_text = status_text.replace("", "").replace("", "").replace("", "").replace("", "").replace("", "").replace("", "").replace("", "").strip()
    bg_color = "#09090b"
    border_color = "#27272a"
    accent_color = "#94A3B8"
    
    if "ACTION" in status_text: 
        accent_color = "#00ff00"
        border_color = "rgba(0, 255, 0, 0.3)"
    elif "APPROACHING" in status_text: 
        accent_color = "#ffb84d"
        border_color = "rgba(255, 184, 77, 0.3)"
    elif "REJECTED" in status_text: 
        accent_color = "#ff4d4d"
        border_color = "rgba(255, 77, 77, 0.3)"

    price = float(stock.get('current_price') or 0.0)
    buy_limit = float(stock.get('buy_limit') or 0.0)
    sell_target = float(stock.get('sell_target') or 0.0)
    stop_loss = float(stock.get('stop_loss') or 0.0)
    max_size = float(stock.get('max_pos_size') or 0.0)

    dist = 100
    if buy_limit > 0 and price > 0:
        dist = (price - buy_limit) / buy_limit * 100
            
    intelligence_data = cached_fetch_news(stock['ticker'])
    
    news_count = len(intelligence_data)
    
    news_html = '<details style="margin-top: 16px;">'
    news_html += f'<summary style="font-size: 13px; color: #F8FAFC; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px; outline: none; background: #000000; border: 1px solid #27272a; padding: 12px; border-radius: 2px;"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 22h14a2 2 0 0 0 2-2V7.5L14.5 2H6a2 2 0 0 0-2 2v4"/><polyline points="14 2 14 8 20 8"/><path d="M2 15h10"/><path d="M2 18h10"/><path d="M2 12h10"/></svg> Intelligence Feed ({news_count})</summary>'
    news_html += '<div style="margin-top: 12px; display: flex; flex-direction: column; gap: 8px;">'
    
    if news_count > 0:
        for item in intelligence_data[:5]:
            title = item.get('title', 'Market Update')
            if len(title) > 60:
                title = title[:57] + "..."
            link = item.get('link', '#')
            pub_date = item.get('pubDate', '')
            if pub_date:
                try:
                    dt = datetime.strptime(pub_date, "%Y-%m-%dT%H:%M:%SZ")
                    pub_date = dt.strftime("%H:%M")
                except:
                    pub_date = pub_date[:10]
                    
            sentiment = item.get('nlp_score', 0)
            sent_color = "#00ff00" if sentiment > 0 else "#ff4d4d" if sentiment < 0 else "#64748B"
            
            news_html += f"""
            <a href="{link}" target="_blank" style="text-decoration: none;">
                <div style="background: rgba(255,255,255,0.02); border: 1px solid #27272a; padding: 10px 12px; border-radius: 2px; transition: background 0.2s;">
                    <div style="font-size: 13px; color: #E2E8F0; margin-bottom: 6px; line-height: 1.4;">{title}</div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 11px; color: #64748B;">{pub_date}</span>
                        <span style="display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: {sent_color};"></span>
                    </div>
                </div>
            </a>
            """
    else:
        news_html += """
        <div style="background: rgba(255,255,255,0.01); border: 1px dashed #27272a; padding: 8px; border-radius: 2px; text-align: center;">
            <span style="font-size: 13px; color: #64748B;">No intelligence reports available.</span>
        </div>
        """
    news_html += "</div></details>"
    news_html = news_html.replace('\n', '')

    buy_usd = buy_limit / usd_rate
    target_usd = sell_target / usd_rate
    clean_ticker = stock['ticker'].replace(".IS", "")
    tv_symbol = f"BIST:{clean_ticker}" if stock['ticker'].endswith(".IS") else clean_ticker
    flag_emoji = "<span style='font-size: 11px; padding: 2px 6px; background: rgba(255,255,255,0.1); border-radius: 2px; margin-left: 6px;'>BIST</span>" if stock['ticker'].endswith(".IS") else "<span style='font-size: 11px; padding: 2px 6px; background: rgba(255,255,255,0.1); border-radius: 2px; margin-left: 6px;'>US</span>"

    period_key = f"per_{clean_ticker}"
    current_period = st.session_state.get(period_key)
    if not current_period:
        current_period = "1M"

    dates, prices = fetch_sparkline_data(stock['ticker'], current_period)
    chart_html = generate_svg_sparkline(dates, prices, color=accent_color)

    with st.container(border=True):
        st.markdown(f"<span class='card-marker-{clean_ticker}'></span>", unsafe_allow_html=True)
        st.markdown(f"""
        <style>
        div[data-testid="column"] div[data-testid="stVerticalBlockBorderWrapper"]:has(.card-marker-{clean_ticker}) {{
            height: 100% !important;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.card-marker-{clean_ticker}) {{
            background: {bg_color} !important;
            border: 1px solid {border_color} !important;
            border-radius: 2px !important;
            padding: 12px !important;
            height: 100% !important;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"]:has(.card-marker-{clean_ticker}) > div[data-testid="stVerticalBlock"] {{
            gap: 0 !important;
            height: 100% !important;
            display: flex !important;
            flex-direction: column !important;
        }}
        div.stMarkdown:has(.spacer-{clean_ticker}) {{
            flex-grow: 1 !important;
            min-height: 16px !important;
        }}
        </style>
        """.replace('\n', ''), unsafe_allow_html=True)

        st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
                <div>
                    <h2 style="margin:0; font-size: 15px; font-weight: 600; color: #F8FAFC; letter-spacing: -0.5px; display: flex; align-items: center; gap: 8px;">{stock['ticker']} {flag_emoji}</h2>
                </div>
                <div style="background: rgba(255,255,255,0.03); color: {accent_color}; padding: 4px 10px; border-radius: 2px; font-weight: 600; font-size: 13px; letter-spacing: 0.5px; border: 1px solid {border_color};">
                    {status_text}
                </div>
            </div>
            {chart_html}
        """.replace('\n', ''), unsafe_allow_html=True)
        
        st.segmented_control("Period", ["1D", "1W", "1M", "3M"], default=current_period, key=period_key, label_visibility="collapsed")
        
        lz_top = float(stock.get('liquidity_zone_top') or buy_limit)
        lz_bot = float(stock.get('liquidity_zone_bot') or buy_limit)
        
        cvd_val = float(stock.get('cvd_gradient') or 0.0)
        cvd_color = '#00ff00' if cvd_val > 0 else '#ff4d4d'
        cvd_sign = "+" if cvd_val > 0 else ""
        cvd_width = min(100.0, abs(cvd_val))
        cvd_w_pos = cvd_width if cvd_val > 0 else 0
        cvd_w_neg = cvd_width if cvd_val < 0 else 0
            
        prox_dot_pos = max(0.0, min(100.0, 80.0 - (dist * 1.6)))

        st.markdown(f"""
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; margin-top: 16px;">
                <div>
                    <div style="font-size: 13px; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; font-weight: 500;">Market Price</div>
                    <div style="font-size: 16px; font-weight: 400; color: #F8FAFC; letter-spacing: -0.5px;">{tr_fmt(price)}₺</div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 13px; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; font-weight: 500;">Liquidity Zone</div>
                    <div style="font-size: 18px; font-weight: 500; color: {accent_color}; letter-spacing: -0.5px;">{tr_fmt(lz_bot)} - {tr_fmt(lz_top)} ₺</div>
                    <div style="font-size: 11px; color: #64748B; margin-top: 4px; font-family: monospace;">HARD LIMIT: {tr_fmt(buy_limit)} ₺</div>
                </div>
            </div>
            
            <div style="margin-bottom: 24px;">
                <div style="display: flex; justify-content: space-between; font-size: 13px; color: #94A3B8; margin-bottom: 8px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">
                    <span>Proximity Delta</span>
                    <span style="color: #E2E8F0;">{dist:.1f}%</span>
                </div>
                <div style="height: 4px; background: #27272a; border-radius: 2px; position: relative; margin-top: 10px; margin-bottom: 6px;">
                    <div style="position: absolute; left: 0; top: 0; bottom: 0; width: {prox_dot_pos:.1f}%; background: {accent_color}; opacity: 0.5; border-radius: 2px;"></div>
                    <div style="position: absolute; left: 80%; top: -4px; bottom: -4px; width: 2px; background: {accent_color}; box-shadow: none; z-index: 1;"></div>
                    <div style="position: absolute; left: {prox_dot_pos:.1f}%; top: 50%; transform: translate(-50%, -50%); width: 10px; height: 10px; background: #FFFFFF; border-radius: 50%; box-shadow: none; z-index: 2; transition: left 0.3s ease;"></div>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 10px; color: #64748B; text-transform: uppercase;">
                    <span>Far</span>
                    <span style="padding-right: 18%;">Limit</span>
                </div>
            </div>
            
            <div style="margin-bottom: 24px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="color: #94A3B8; font-size: 13px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">CVD (Orderflow)</span>
                    <span style="color: {cvd_color};">{cvd_sign}{cvd_val:.1f}%</span>
                </div>
                <div style="display: flex; height: 6px; background: rgba(0,0,0,0.2); border-radius: 2px; position: relative;">
                    <div style="position: absolute; left: 50%; top: -2px; bottom: -2px; width: 2px; background: rgba(255,255,255,0.6); z-index: 10; transform: translateX(-50%); border-radius: 2px; box-shadow: none;"></div>
                    <div style="flex: 1; position: relative;">
                        <div style="position: absolute; right: 0; top: 0; bottom: 0; width: {cvd_w_neg:.1f}%; background: #ff4d4d; border-radius: 2px 0 0 3px; box-shadow: none;"></div>
                    </div>
                    <div style="flex: 1; position: relative;">
                        <div style="position: absolute; left: 0; top: 0; bottom: 0; width: {cvd_w_pos:.1f}%; background: #00ff00; border-radius: 0 3px 3px 0; box-shadow: none;"></div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    slippage_risk = float(stock.get('slippage_risk_pct') or 0.0)
    slippage_color = "#ff4d4d" if slippage_risk > 0.5 else ("#ffb84d" if slippage_risk > 0.2 else "#00ff00")
    
    market = "BIST" if stock.get('ticker', '').endswith('.IS') else "US"
    currency = "₺" if market == "BIST" else "$"
    
    capital = st.session_state.get('capital_try', 100000) if market == "BIST" else st.session_state.get('capital_usd', 10000)
    risk_p = st.session_state.get('risk_pct', 1.0)
    
    # ALPH-01: Kelly Multiplier for A+ Setups
    is_aplus = "A+" in status_text
    alpha_score = stock.get("alpha_score", 0)
    
    #  BAYESIAN KELLY SIZING (The Edge Integrator)
    if realized_win_rates is None: realized_win_rates = {}
    bucket = stock.get("bucket", "CORE")
    p = realized_win_rates.get(bucket, 0.45) # Realized Win Rate
    b = (sell_target - buy_limit) / (buy_limit - stop_loss) if (buy_limit - stop_loss) > 0 else 1.0 # Realized Reward/Risk
    q = 1 - p
    kelly_f = max(0.0, p - (q / b)) # Full Kelly Formula: W - (L/R)
    half_kelly = kelly_f / 2.0
    
    # Use user's risk input as an absolute maximum ceiling, but let Kelly shrink it during losing streaks.
    user_max_risk = risk_p / 100.0
    dynamic_risk_p = min(user_max_risk, half_kelly)
    
    if is_aplus:
        dynamic_risk_p = min(user_max_risk * 2.0, kelly_f)  # Double Kelly sizing ceiling for A+
        
    risk_amount = capital * dynamic_risk_p
    gap_penalty = stock.get("gap_penalty_multiplier", 1.0)
    risk_gap = (buy_limit - stop_loss) * gap_penalty
    
    if risk_gap > 0 and buy_limit > 0 and dynamic_risk_p > 0:
        kelly_shares = int(risk_amount / risk_gap)
        liquidity_cap_shares = int(max_size / buy_limit) if max_size > 0 else kelly_shares
        
        # OPR-02 & PRTF-03: Dual-Currency Settled Cash Sizer Constraint
        if market == 'US':
            settled_cash = stock.get('settled_cash_usd', capital)
        else:
            settled_cash = stock.get('settled_cash_try', capital)
            
        cash_cap_shares = int(settled_cash / buy_limit) if buy_limit > 0 else kelly_shares
        
        # SYNC-03: Liquidity Lock Kelly Cap (Max 15% Exposure per trade)
        max_exposure_cap = capital * 0.15
        hard_cap_shares = int(max_exposure_cap / buy_limit) if buy_limit > 0 else kelly_shares
        
        suggested_shares = min(kelly_shares, liquidity_cap_shares, cash_cap_shares, hard_cap_shares)
        exposure = suggested_shares * buy_limit
        is_cash_constrained = (suggested_shares == cash_cap_shares and cash_cap_shares < kelly_shares and cash_cap_shares < hard_cap_shares)
        is_hard_capped = (suggested_shares == hard_cap_shares and hard_cap_shares < kelly_shares)
    else:
        suggested_shares = 0
        exposure = 0
        is_cash_constrained = False
        is_hard_capped = False

    cvd_grad = float(stock.get("cvd_gradient") or 0.0)
    is_tick_sensitive = ("LIQUIDITY VACUUM" in status_text) or (abs(cvd_grad) > 3.0)

    st.markdown(f"""
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0px; background: #000000; border-radius: 2px; padding: 8px; border: 1px solid rgba(255,255,255,0.02);">
                <div style="border-right: 1px solid #27272a; padding-right: 16px;">
                    <div style="color: #64748B; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; font-weight: 500; display: flex; align-items: center;">
                        <span style="margin-right: 6px; color: #94A3B8;">{ICON_TARGET}</span> Target
                    </div>
                    <div style="color: #E2E8F0; font-weight: 500; font-size: 15px;">{tr_fmt(sell_target)}{currency}</div>
                </div>
                <div style="text-align: right; padding-left: 16px;">
                    <div style="color: #64748B; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; font-weight: 500; display: flex; align-items: center; justify-content: flex-end;">
                        <span style="margin-right: 6px; color: #94A3B8;">{ICON_SHIELD}</span> Stop Loss
                    </div>
                    <div style="color: #ff4d4d; font-weight: 500; font-size: 15px;">{tr_fmt(stop_loss)}{currency}</div>
                </div>
            </div>
            <div style="background: #000000; border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 2px; padding: 8px; margin-top: 16px; text-align: center;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div style="color: #94A3B8; font-size: 11px; text-transform: uppercase; font-weight: 600; letter-spacing: 1px;">Dynamic Kelly Size ({risk_p}% Risk)</div>
                    <div style="color: {'#00ff00' if alpha_score >= 90 else '#3B82F6'}; font-size: 11px; font-weight: 700; background: {'rgba(0, 255, 0, 0.1)' if alpha_score >= 90 else 'rgba(59, 130, 246, 0.1)'}; padding: 2px 8px; border-radius: 2px;">Alpha Score: {int(alpha_score)}</div>
                </div>
                <div style="color: #F8FAFC; font-size: 16px; font-weight: 500; font-family: 'Courier New', Courier, monospace;">{suggested_shares} UNITS</div>
                <div style="display: flex; justify-content: space-between; margin-top: 8px; padding-top: 8px; border-top: 1px solid #27272a;">
                    <div style="color: #64748B; font-size: 11px;">Capital Req: {tr_fmt(exposure)} {currency}</div>
                    <div style="color: {slippage_color}; font-size: 11px; font-weight: 600;" title="Estimated spread widening risk based on live volatility">Spread Cost: {slippage_risk:.2f}%</div>
                </div>
                {'<div style="color: #ffb84d; font-size: 11px; font-weight: 700; margin-top: 8px; text-transform: uppercase;"> Sizing penalized for overnight Gap Risk</div>' if gap_penalty > 1.05 else ''}
                { """<div style="color: #ff4d4d; font-size: 11px; font-weight: 700; margin-top: 8px; text-transform: uppercase;"><svg width='1em' height='1em' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z'></path><circle cx='12' cy='12' r='4'></circle></svg> Sizing constrained by Settled Cash</div>""" if is_cash_constrained else ""}
                { """<div style="color: #ff4d4d; font-size: 11px; font-weight: 700; margin-top: 8px; text-transform: uppercase;"><svg width='1em' height='1em' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z'></path><circle cx='12' cy='12' r='4'></circle></svg> SYNC-03: Kelly Sizer Hard-Capped at 15% (Liquidity Lock Defense)</div>""" if is_hard_capped else ""}
                {'<div style="color: #F87171; font-size: 11px; font-weight: 700; margin-top: 8px; text-transform: uppercase;"> TICK SENSITIVE: Execute immediately. Alpha decays in seconds.</div>' if is_tick_sensitive else ''}
            </div>
            {news_html}
        """.replace('\n', ''), unsafe_allow_html=True)
        
    stink_bid = stock.get("stink_bid", 0)
    st.markdown(f"""
        <div style="background: rgba(139, 92, 246, 0.1); border: 1px solid rgba(139, 92, 246, 0.2); border-radius: 2px; padding: 12px; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="color: #A78BFA; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;"> FLASH CRASH STINK BID</div>
                <div style="color: #64748B; font-size: 11px; margin-top: 2px;">Leave this GTC to absorb algorithmic dumps.</div>
            </div>
            <div style="color: #F8FAFC; font-weight: 600; font-family: monospace; font-size: 15px; background: rgba(139, 92, 246, 0.2); padding: 4px 10px; border-radius: 2px;">
                {tr_fmt(stink_bid)}{currency}
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    options_advice = stock.get("options_advice", "")
    if options_advice:
        st.markdown(f"""
            <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.2); border-radius: 2px; padding: 12px; margin-bottom: 16px; text-align: center;">
                <div style="color: #60A5FA; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px;">US MARKET OPTIONS RANKER</div>
                <div style="color: #F8FAFC; font-weight: 600; font-size: 13px;">{options_advice}</div>
            </div>
        """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1: st.code(tr_fmt(buy_limit), language="text")
    with c2: st.code(tr_fmt(sell_target), language="text")
    with c3: st.code(tr_fmt(stop_loss), language="text")
    
    st.markdown(f"<div class='spacer-{clean_ticker}'></div>", unsafe_allow_html=True)
    
    # DIS-02: Hard GTC Stop Mandate
    st.markdown("""
        <div style="background: rgba(255, 77, 77, 0.15); border: 1px solid rgba(255, 77, 77, 0.3); border-radius: 2px; padding: 12px; margin-bottom: 16px; text-align: center;">
            <div style="color: #ff4d4d; font-weight: 800; font-size: 13px; letter-spacing: 0.5px;"> PLACE GTC STOP LIMIT AT BROKER IMMEDIATELY</div>
            <div style="color: #FCA5A5; font-size: 11px; margin-top: 4px;">Mental stops are banned. The panel is not a stop-loss engine.</div>
        </div>
    """, unsafe_allow_html=True)

    # EXEC-06: Anti-Pyramiding Database Lock
    if "ALREADY LONG" in status_text:
        st.markdown("""
            <div style="background: #000000; border: 1px solid #27272a; border-radius: 2px; padding: 8px; margin-bottom: 16px; text-align: center;">
                <div style="color: #64748B; font-weight: 700; font-size: 13px; letter-spacing: 0.5px;"> ANTI-PYRAMIDING LOCK ACTIVE</div>
                <div style="color: #475569; font-size: 11px; margin-top: 4px;">Position is already OPEN. Averaging down is banned.</div>
            </div>
        """, unsafe_allow_html=True)
    elif "24H COOL-DOWN" in status_text:
        # DIS-04: The Revenge Trading Loop UI Lock
        st.markdown("""
            <div style="background: #000000; border: 1px solid #27272a; border-radius: 2px; padding: 8px; margin-bottom: 16px; text-align: center;">
                <div style="color: #ff4d4d; font-weight: 700; font-size: 13px; letter-spacing: 0.5px;"><svg width='1em' height='1em' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z'></path><circle cx='12' cy='12' r='4'></circle></svg> REVENGE TRADING LOCK ACTIVE</div>
                <div style="color: #FCA5A5; font-size: 11px; margin-top: 4px;">Recently stopped out. Re-entry banned for 24 hours.</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        # DIS-01: Slippage Audit (The "Perfect Fill" Fix)
        st.markdown("<div style='color: #94A3B8; font-size: 12px; margin-bottom: 4px; font-weight: 600;'>ACTUAL EXECUTION LOGGING:</div>", unsafe_allow_html=True)
        input_cols = st.columns(2)
        with input_cols[0]:
            actual_entry = st.number_input("Fill Price", value=float(buy_limit), step=0.01, key=f"act_price_{stock['ticker']}")
        with input_cols[1]:
            actual_qty = st.number_input("Qty Filled", value=max(1, int(suggested_shares)), min_value=1, step=1, key=f"act_qty_{stock['ticker']}")

        if st.button(f"LOG TRADE ({stock['ticker']})", key=f"log_{stock['ticker']}", use_container_width=True):
            try:
                supabase.table("portfolio").insert({
                    "ticker": stock['ticker'],
                    "bucket": stock.get('bucket', 'CORE'),
                    "entry_price": actual_entry,
                    "qty": actual_qty,
                    "status": "OPEN",
                    "exit_target": sell_target,
                    "stop_loss": stop_loss,
                    "entry_date": pd.Timestamp.now(timezone.utc).isoformat()
                }).execute()
                st.success("Trade Logged! Move to Active Operations tab.")
            except Exception as e:
                st.error(f"Failed to log trade: {e}")

    st.markdown(f"""
        <div style="margin-bottom: 24px; margin-top: 8px;">
            <a href="https://www.tradingview.com/chart/?symbol={tv_symbol}" target="_blank" style="display: flex; justify-content: center; align-items: center; gap: 8px; width: 100%; padding: 10px; background: transparent; color: #3B82F6; text-decoration: none; border-radius: 2px; font-size: 14px; font-weight: 500; border: 1px solid rgba(59, 130, 246, 0.2); transition: all 0.2s;">
                {ICON_TREND} Chart Analysis
            </a>
        </div>
    """, unsafe_allow_html=True)

def render_cards(limits_data, settled_cash_try, settled_cash_usd):
    if not limits_data:
        st.markdown("<p style='color:#64748B; text-align:center; padding: 60px 0; font-size: 15px;'>No assets registered in this tier.</p>", unsafe_allow_html=True)
        return

    realized_win_rates = get_bayesian_win_rates()
    cols = st.columns(3)
    for i, stock in enumerate(limits_data):
        with cols[i % 3]:
            # Inject dual settled cash into the stock object
            stock['settled_cash_try'] = settled_cash_try
            stock['settled_cash_usd'] = settled_cash_usd
            render_single_card(stock, realized_win_rates)

# --- PAGE RENDERING ---

with st.expander("PORTFOLIO ALLOCATION", expanded=False):
    # --- PART 1: REBALANCER ---
    st.markdown("""
        <div style="margin-bottom: 24px;">
            <h3 style="margin: 0; font-size: 18px; font-weight: 500; color: #F8FAFC;">Capital Allocation Matrix</h3>
            <p style="margin: 4px 0 0 0; font-size: 14px; color: #64748B;">Dynamic enforcement of the 70/30 structural safety doctrine and Global Vector Constraints.</p>
        </div>
    """, unsafe_allow_html=True)
    
    #  UI-02: Global Risk Rebalancer Variables
    # Fetch active exposure right now
    open_p = get_open_portfolio()
    active_bist = sum(1 for t in open_p if t.endswith('.IS'))
    active_us = len(open_p) - active_bist
    
    for k, v in [("cc_in", "70.000"), ("cs_in", "30.000"), ("cg_in", "0"), ("sc_in", "100.000")]:
        if k not in st.session_state: st.session_state[k] = v
        
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: 
        total_capital = st.session_state.get('capital_try', 100000.0)
        st.text_input("Total Capital (TRY)", value=f"{total_capital:,.2f}", disabled=True)
    with c2: 
        # PRTF-01 & PRTF-03: Dual-Currency Margin Manager
        open_positions_for_margin = get_open_portfolio_full()
        
        active_exposure_try = 0.0
        active_exposure_usd = 0.0
        for p in open_positions_for_margin:
            pos_val = (p.get('entry_price') or 0.0) * (p.get('qty') or 0.0)
            if p.get('ticker', '').endswith('.IS'):
                active_exposure_try += pos_val
            else:
                active_exposure_usd += pos_val
                
        available_capital_try = max(0.0, total_capital - active_exposure_try)
        total_capital_usd = st.session_state.get('capital_usd', 10000)
        available_capital_usd = max(0.0, total_capital_usd - active_exposure_usd)
        
        st.text_input(f"Settled Cash TRY (Auto: {available_capital_try:,.2f})", key="sc_in", on_change=format_input_cb, args=("sc_in",))
        settled_cash_try = parse_tr_float(st.session_state["sc_in"], available_capital_try)
    with c3: 
        st.text_input("Current Core", key="cc_in", on_change=format_input_cb, args=("cc_in",))
        current_tank = parse_tr_float(st.session_state["cc_in"], 70000.0)
    with c4: 
        st.text_input("Current Satellite", key="cs_in", on_change=format_input_cb, args=("cs_in",))
        current_sniper = parse_tr_float(st.session_state["cs_in"], 30000.0)
    with c5: 
        st.text_input("Current Arbitrage", key="cg_in", on_change=format_input_cb, args=("cg_in",))
        current_gambler = parse_tr_float(st.session_state["cg_in"], 0.0)

    st.markdown("<hr style='border: 0; height: 1px; background: #27272a; margin: 24px 0;'>", unsafe_allow_html=True)
    
    target_tank = total_capital * 0.70
    target_sniper = total_capital * 0.30
    drift_tank = current_tank - target_tank
    drift_sniper = current_sniper - target_sniper

    pct_tank = (current_tank / total_capital * 100) if total_capital > 0 else 0
    pct_sniper = (current_sniper / total_capital * 100) if total_capital > 0 else 0
    pct_gambler = (current_gambler / total_capital * 100) if total_capital > 0 else 0

    tank_status = "OPTIMAL" if abs(pct_tank - 70) <= 5 else ("OVERWEIGHT" if pct_tank > 70 else "UNDERWEIGHT")
    sniper_status = "OPTIMAL" if abs(pct_sniper - 30) <= 5 else ("OVERWEIGHT" if pct_sniper > 30 else "UNDERWEIGHT")
    gambler_status = "CRITICAL LIMIT" if pct_gambler > 5 else "OPTIMAL"

    tank_color = "#00ff00" if tank_status == "OPTIMAL" else "#ffb84d"
    sniper_color = "#00ff00" if sniper_status == "OPTIMAL" else "#ffb84d"
    gambler_color = "#ff4d4d" if gambler_status == "CRITICAL LIMIT" else "#3B82F6"

    st.markdown(f"""
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px;">
            <div style="background: #000000; border: 1px solid #27272a; border-radius: 2px; padding: 20px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                    <span style="color: #94A3B8; font-size: 13px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">Core Target (70%)</span>
                    <span style="color: {tank_color}; font-size: 11px; font-weight: 600; padding: 2px 8px; background: #27272a; border-radius: 2px; letter-spacing: 0.5px;">{tank_status}</span>
                </div>
                <div style="font-size: 18px; font-weight: 400; color: #F8FAFC; margin-bottom: 4px; letter-spacing: -0.5px;">{tr_fmt(current_tank)} ₺</div>
                <div style="font-size: 14px; color: #64748B; margin-bottom: 16px;">Target: {tr_fmt(target_tank)} ₺ &nbsp;•&nbsp; Drift: <span style="color: {tank_color};">{tr_fmt(drift_tank)} ₺</span></div>
                <div style="background: rgba(0,0,0,0.3); height: 6px; border-radius: 2px; overflow: hidden;">
                    <div style="background: {tank_color}; height: 100%; width: {min(100, pct_tank)}%; border-radius: 2px;"></div>
                </div>
                <div style="text-align: right; font-size: 13px; color: #94A3B8; margin-top: 8px; font-weight: 500;">Actual: {pct_tank:.1f}%</div>
            </div>
            <div style="background: #000000; border: 1px solid #27272a; border-radius: 2px; padding: 20px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                    <span style="color: #94A3B8; font-size: 13px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">Satellite Target (30%)</span>
                    <span style="color: {sniper_color}; font-size: 11px; font-weight: 600; padding: 2px 8px; background: #27272a; border-radius: 2px; letter-spacing: 0.5px;">{sniper_status}</span>
                </div>
                <div style="font-size: 18px; font-weight: 400; color: #F8FAFC; margin-bottom: 4px; letter-spacing: -0.5px;">{tr_fmt(current_sniper)} ₺</div>
                <div style="font-size: 14px; color: #64748B; margin-bottom: 16px;">Target: {tr_fmt(target_sniper)} ₺ &nbsp;•&nbsp; Drift: <span style="color: {sniper_color};">{tr_fmt(drift_sniper)} ₺</span></div>
                <div style="background: rgba(0,0,0,0.3); height: 6px; border-radius: 2px; overflow: hidden;">
                    <div style="background: {sniper_color}; height: 100%; width: {min(100, pct_sniper)}%; border-radius: 2px;"></div>
                </div>
                <div style="text-align: right; font-size: 13px; color: #94A3B8; margin-top: 8px; font-weight: 500;">Actual: {pct_sniper:.1f}%</div>
            </div>
            <div style="background: #000000; border: 1px solid #27272a; border-radius: 2px; padding: 20px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                    <span style="color: #94A3B8; font-size: 13px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;">Arbitrage Risk Cap (5%)</span>
                    <span style="color: {gambler_color}; font-size: 11px; font-weight: 600; padding: 2px 8px; background: #27272a; border-radius: 2px; letter-spacing: 0.5px;">{gambler_status}</span>
                </div>
                <div style="font-size: 18px; font-weight: 400; color: #F8FAFC; margin-bottom: 4px; letter-spacing: -0.5px;">{tr_fmt(current_gambler)} ₺</div>
                <div style="font-size: 14px; color: #64748B; margin-bottom: 16px;">Max Permitted: {tr_fmt(total_capital * 0.05)} ₺</div>
                <div style="background: rgba(0,0,0,0.3); height: 6px; border-radius: 2px; overflow: hidden;">
                    <div style="background: {gambler_color}; height: 100%; width: {min(100, pct_gambler * (100/5))}%; border-radius: 2px;"></div>
                </div>
                <div style="text-align: right; font-size: 13px; color: #94A3B8; margin-top: 8px; font-weight: 500;">Actual: {pct_gambler:.1f}%</div>
""", unsafe_allow_html=True)
    
    gambler_limits = get_limits("GAMBLER")
    gambler_action = any(s.get('status') in [' ACTION ZONE', ' APPROACHING'] for s in gambler_limits)
    
    if gambler_action:
        st.markdown(f"""
                <div style="margin-top: 16px; padding: 10px; background: rgba(0, 255, 0, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 2px; display: {'block' if pct_gambler <= 5 else 'none'};">
                    <div style="color: #00ff00; font-size: 11px; font-weight: 600; margin-bottom: 2px;">OU STATIONARITY ALERT</div>
                    <div style="color: #A7F3D0; font-size: 11px;">Stat-Arb Mean Reversion Extreme Flagged. Capacity available.</div>
                </div>
                <div style="margin-top: 16px; padding: 10px; background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 2px; display: {'block' if pct_gambler > 5 else 'none'};">
                    <div style="color: #ff4d4d; font-size: 11px; font-weight: 600; margin-bottom: 2px;">OU STATIONARITY LOCKOUT</div>
                    <div style="color: #FECACA; font-size: 11px;">Gambler cap exceeded. New Arbitrage entries suspended.</div>
                </div>
        """, unsafe_allow_html=True)
        
    st.markdown("""
            </div>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px;">
            <div style="background: #000000; border: 1px solid #27272a; border-radius: 2px; padding: 8px;">
                <div style="color: #94A3B8; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px;">Global Vector Limit: BIST (TRY)</div>
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div style="font-size: 15px; font-weight: 500; color: #F8FAFC;">{active_bist} / 3</div>
                    <div style="font-size: 12px; color: {'#ff4d4d' if active_bist >= 3 else '#00ff00'}; font-weight: 600; padding: 4px 8px; background: #27272a; border-radius: 2px;">
                        {'MAXED OUT' if active_bist >= 3 else 'CAPACITY OPEN'}
                    </div>
                </div>
            </div>
            <div style="background: #000000; border: 1px solid #27272a; border-radius: 2px; padding: 8px;">
                <div style="color: #94A3B8; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px;">Global Vector Limit: US (USD)</div>
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div style="font-size: 15px; font-weight: 500; color: #F8FAFC;">{active_us} / 3</div>
                    <div style="font-size: 12px; color: {'#ff4d4d' if active_us >= 3 else '#00ff00'}; font-weight: 600; padding: 4px 8px; background: #27272a; border-radius: 2px;">
                        {'MAXED OUT' if active_us >= 3 else 'CAPACITY OPEN'}
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # --- PART 2: MACRO RISK ---
    st.markdown("<hr style='border: 0; height: 1px; background: #27272a; margin: 32px 0;'>", unsafe_allow_html=True)
    
    st.markdown("""
        <div style="margin-bottom: 24px;">
            <h3 style="margin: 0; font-size: 18px; font-weight: 500; color: #F8FAFC;">Macro Risk Intelligence</h3>
            <p style="margin: 4px 0 0 0; font-size: 14px; color: #64748B;">Global trend sensors and tail-risk liquidity hedges.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.3); padding: 24px; border-radius: 2px; border: 1px solid #27272a; text-align: center;">
                <div style="color: #64748B; font-weight: 500; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px;">BIST Regime Tracker</div>
                <div style="font-size: 18px; font-weight: 400; color: #F8FAFC; margin-bottom: 12px;">{meta.get('bist_regime', 'N/A')}</div>
                <div style="color: #3B82F6; font-size: 13px; font-weight: 600; background: rgba(59, 130, 246, 0.1); padding: 4px 12px; border-radius: 2px; display: inline-block;">ADX Momentum: {meta.get('bist_adx', 0)}</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.3); padding: 24px; border-radius: 2px; border: 1px solid #27272a; text-align: center;">
                <div style="color: #64748B; font-weight: 500; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px;">US Global Regime</div>
                <div style="font-size: 18px; font-weight: 400; color: #F8FAFC; margin-bottom: 12px;">{meta.get('us_regime', 'N/A')}</div>
                <div style="color: #3B82F6; font-size: 13px; font-weight: 600; background: rgba(59, 130, 246, 0.1); padding: 4px 12px; border-radius: 2px; display: inline-block;">ADX Momentum: {meta.get('us_adx', 0)}</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        usd_color = "#ff4d4d" if meta.get('usd_try_trend') == 'UP' else "#00ff00"
        st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.3); padding: 24px; border-radius: 2px; border: 1px solid #27272a; text-align: center;">
                <div style="color: #64748B; font-weight: 500; font-size: 13px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px;">USD/TRY Capital Flow</div>
                <div style="font-size: 18px; font-weight: 400; color: {usd_color}; margin-bottom: 12px;">{meta.get('usd_try_trend')}</div>
                <div style="color: transparent; font-size: 13px; font-weight: 600; padding: 4px 12px;">-</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # EXEC-05: Tail-Risk CRO UI
    bist_r = meta.get('bist_regime', 'N/A')
    us_r = meta.get('us_regime', 'N/A')
    if "BEAR" in bist_r or "BEAR" in us_r:
        st.markdown("<h4 style='color: #ff4d4d; margin: 0 0 16px 0; font-weight: 600;'> CHIEF RISK OFFICER (CRO) DIRECTIVE</h4>", unsafe_allow_html=True)
        st.markdown("""
            <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(255, 77, 77, 0.3); border-radius: 2px; padding: 24px; display: flex; align-items: flex-start; gap: 20px; margin-bottom: 24px;">
                <div style="font-size: 40px;"><svg width='1em' height='1em' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z'></path><circle cx='12' cy='12' r='4'></circle></svg></div>
                <div style="flex: 1;">
                    <div style="color: #FCA5A5; font-size: 14px; font-weight: 600; letter-spacing: 1px; margin-bottom: 4px;">TAIL-RISK HEDGE REQUIRED</div>
                    <div style="color: #F8FAFC; font-size: 16px; margin-bottom: 12px; line-height: 1.5;">
                        A global Bear Regime has been detected. Standard long-only equity setups are extremely high-risk. To preserve capital and generate positive alpha during the crash, deploy the optimal hedge vehicles immediately.
                    </div>
                    <div style="display: flex; gap: 16px; margin-top: 16px;">
        """, unsafe_allow_html=True)
        
        try:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__)))
            from cro_risk import ChiefRiskOfficer
            cro_mod = ChiefRiskOfficer
        except Exception:
            class DummyCRO:
                @staticmethod
                def get_optimal_hedge(market="BIST"):
                    if market == "BIST": return {"hedge_ticker": "UZIPE.IS (XU030 Put Warrant)", "rationale": "BIST Bear Regime. Seeking delta-negative exposure."}
                    return {"hedge_ticker": "SQQQ", "rationale": "US Bear Regime. Seeking 3x Inverse Nasdaq exposure."}
            cro_mod = DummyCRO
            
        if "BEAR" in bist_r:
            hedge = cro_mod.get_optimal_hedge("BIST")
            st.markdown(f"""
                        <div style="background: rgba(15, 23, 42, 0.8); padding: 8px; border-radius: 2px; flex: 1; border-left: 4px solid #ff4d4d;">
                            <div style="color: #94A3B8; font-size: 12px; margin-bottom: 4px; text-transform: uppercase;">BIST Market Hedge</div>
                            <div style="color: #F8FAFC; font-size: 15px; font-weight: 700; margin-bottom: 8px; font-family: monospace;">{hedge['hedge_ticker']}</div>
                            <div style="color: #94A3B8; font-size: 13px;">{hedge['rationale']}</div>
                        </div>
            """, unsafe_allow_html=True)
            
        if "BEAR" in us_r:
            hedge = cro_mod.get_optimal_hedge("US")
            st.markdown(f"""
                        <div style="background: rgba(15, 23, 42, 0.8); padding: 8px; border-radius: 2px; flex: 1; border-left: 4px solid #ff4d4d;">
                            <div style="color: #94A3B8; font-size: 12px; margin-bottom: 4px; text-transform: uppercase;">US Market Hedge</div>
                            <div style="color: #F8FAFC; font-size: 15px; font-weight: 700; margin-bottom: 8px; font-family: monospace;">{hedge['hedge_ticker']}</div>
                            <div style="color: #94A3B8; font-size: 13px;">{hedge['rationale']}</div>
                        </div>
            """, unsafe_allow_html=True)
            
        st.markdown("""
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        dom_sec, dom_mom = fetch_dominant_sector()
        st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.3); padding: 32px; border-radius: 2px; border: 1px solid #27272a;">
                <h3 style="margin: 0 0 8px 0; font-weight: 500; font-size: 18px;">Sector Capital Concentration</h3>
                <p style="color: #64748B; font-size: 14px; margin: 0 0 24px 0;">Algorithmically identified dominant sector flow.</p>
                <div style="font-size: 28px; font-weight: 300; color: #F8FAFC; margin-bottom: 8px;">{dom_sec}</div>
                <div style="color: #00ff00; font-weight: 600; font-size: 15px;">+{dom_mom}% Trailing 14-Day Performance</div>
            </div>
        """, unsafe_allow_html=True)
        
    with c2:
        open_positions = get_open_portfolio()
        num_open = len(open_positions)
        st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.3); padding: 32px; border-radius: 2px; border: 1px solid #27272a;">
                <h3 style="margin: 0 0 8px 0; font-weight: 500; font-size: 18px;">VIOP Tail-Risk Status</h3>
                <p style="color: #64748B; font-size: 14px; margin: 0 0 24px 0;">Black-swan hedge analysis against overnight gap-downs.</p>
                <div style="font-size: 28px; font-weight: 300; color: #F8FAFC; margin-bottom: 8px;">{num_open} Naked Exposure Vectors</div>
            </div>
        """, unsafe_allow_html=True)
        if num_open > 0:
            st.warning("Tail-Risk detected: Naked exposure vectors active. Consider XU030 Put allocation.")
            
    if 'BEAR' in meta.get('bist_regime', ''):
        st.error(f"Macro Regime Status: {meta.get('bist_regime')}. Algorithmic sizing halved to prevent mean-reversion shredding.")
    elif 'BULL' in meta.get('bist_regime', '') and meta.get('usd_try_trend') == 'UP':
        st.warning(f"Macro Anomaly: BIST {meta.get('bist_regime')} coincides with Lira devaluation. Real alpha generation impaired.")
    elif 'CHAOS' in meta.get('bist_regime', ''):
        st.error("System Blackout. Parabolic Chaos detected. No trades will be executed.")

st.markdown("<hr style='border: 0; height: 1px; background: #27272a; margin: 24px 0;'>", unsafe_allow_html=True)

valid_dates = [s.get('last_updated') for tier in ["CORE", "SATELLITE", "GAMBLER"] for s in get_limits(tier) if s.get('last_updated')]
if valid_dates:
    oldest_date = datetime.fromisoformat(min(valid_dates).replace('Z', '+00:00'))
    if (datetime.now(timezone.utc) - oldest_date).days > 90:
        st.markdown(f"""
            <div style="background: rgba(245, 158, 11, 0.1); padding: 16px 20px; border-radius: 2px; border: 1px solid rgba(245, 158, 11, 0.2); color: #FCD34D; display: flex; align-items: center; gap: 12px; margin-bottom: 24px;">
                {ICON_ALERT}
                <span style="font-size: 15px; font-weight: 500;">Watchlist Rot: Stale assets detected in database (>90 days). Purge recommended.</span>
            </div>
        """, unsafe_allow_html=True)

st.markdown(f"""
    <div style="background: rgba(59, 130, 246, 0.1); padding: 16px 20px; border-radius: 2px; border: 1px solid rgba(59, 130, 246, 0.2); color: #93C5FD; display: flex; align-items: center; gap: 12px; margin-bottom: 24px;">
        {ICON_SHIELD}
        <span style="font-size: 15px; font-weight: 500;">Limit Drift Protocol: Ensure all manually placed Good-Til-Cancelled (GTC) orders on your broker are synced with today's dynamically recalculated targets. Cancel stale orders immediately.</span>
    </div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab_active, tab4 = st.tabs(["Core Allocation", "Satellite Operations", "High-Risk Arbitrage", "Active Operations", "Post-Trade Analytics"])

is_tilt_lockout = check_tilt_lockout()
tilt_html = """
    <div style="background: rgba(239, 68, 68, 0.1); border: 2px solid #ff4d4d; border-radius: 2px; padding: 40px; text-align: center; margin-top: 24px;">
        <div style="font-size: 48px; margin-bottom: 16px;"><svg width='1em' height='1em' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z'></path><circle cx='12' cy='12' r='4'></circle></svg></div>
        <h2 style="color: #ff4d4d; font-weight: 700; margin-bottom: 12px; letter-spacing: 2px;">TILT LOCKOUT ACTIVE</h2>
        <p style="color: #F8FAFC; font-size: 16px; max-width: 600px; margin: 0 auto; line-height: 1.6;">
            You have triggered 3 consecutive stop-losses within the last 24 hours. The AI has suspended all new setup visualizations to prevent emotional revenge trading. 
            <br><br><span style="color: #FCA5A5; font-weight: 600;">Close the terminal. Walk away. Capital preservation is priority one.</span>
        </p>
    </div>
"""

with tab1:
    if is_tilt_lockout:
        st.markdown(tilt_html, unsafe_allow_html=True)
    else:
        all_core = get_limits("CORE")
        all_core = sorted(all_core, key=lambda x: "REJECTED" in (x.get('status') or ""))
        render_cards(all_core, settled_cash_try, available_capital_usd)

with tab2:
    if is_tilt_lockout:
        st.markdown(tilt_html, unsafe_allow_html=True)
    else:
        all_sat = get_limits("SATELLITE")
        all_sat = sorted(all_sat, key=lambda x: "REJECTED" in (x.get('status') or ""))
        render_cards(all_sat, settled_cash_try, available_capital_usd)

with tab3:
    if is_tilt_lockout:
        st.markdown(tilt_html, unsafe_allow_html=True)
    else:
        all_gam = get_limits("GAMBLER")
        all_gam = sorted(all_gam, key=lambda x: "REJECTED" in (x.get('status') or ""))
        render_cards(all_gam, settled_cash_try, available_capital_usd)
                
        # INST-05: Pair-Trading Divergence Scanner
        st.markdown("<hr style='border-color: #27272a; margin: 32px 0;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: white; margin-bottom: 8px;'>INST-05: Statistical Arbitrage (Pairs Trading)</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #94A3B8; margin-bottom: 24px;'>Scanning historical correlations for extreme standard deviation divergences.</p>", unsafe_allow_html=True)
        
        if st.button("Run Divergence Scanner", key="run_arb_scan"):
            with st.spinner("Calculating Z-Scores for heavily correlated assets..."):
                try:
                    import yfinance as yf
                    import pandas as pd
                    pairs = [("AKBNK.IS", "YKBNK.IS"), ("KCHOL.IS", "SAHOL.IS"), ("FROTO.IS", "TOASO.IS"), ("TCELL.IS", "TTKOM.IS")]
                    
                    for p1, p2 in pairs:
                        data = yf.download([p1, p2], period="6mo", progress=False)['Close']
                        if not data.empty and p1 in data.columns and p2 in data.columns:
                            data = data.dropna()
                            ratio = data[p1] / data[p2]
                            
                            mean_ratio = ratio.mean()
                            std_ratio = ratio.std()
                            current_ratio = ratio.iloc[-1]
                            z_score = (current_ratio - mean_ratio) / std_ratio
                            
                            box_color = "#09090b"
                            border_color = "#27272a"
                            z_color = "#E2E8F0"
                            signal = " CORRELATED"
                            
                            if z_score > 2.0:
                                box_color = "rgba(0, 255, 0, 0.1)"
                                border_color = "rgba(16, 185, 129, 0.3)"
                                z_color = "#00ff00"
                                signal = f" PAIRS ARB: Short {p1} / Long {p2}"
                            elif z_score < -2.0:
                                box_color = "rgba(239, 68, 68, 0.1)"
                                border_color = "rgba(255, 77, 77, 0.3)"
                                z_color = "#ff4d4d"
                                signal = f" PAIRS ARB: Long {p1} / Short {p2}"
                                
                            st.markdown(f"""
                                <div style="background: {box_color}; border: 1px solid {border_color}; border-radius: 2px; padding: 8px; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center;">
                                    <div>
                                        <div style="color: #94A3B8; font-size: 13px; font-weight: 600; letter-spacing: 1px;">{p1} vs {p2}</div>
                                        <div style="font-size: 18px; font-weight: 700; color: #F8FAFC; margin-top: 4px;">{signal}</div>
                                    </div>
                                    <div style="text-align: right;">
                                        <div style="color: #64748B; font-size: 11px; text-transform: uppercase;">Z-Score Divergence</div>
                                        <div style="font-size: 18px; font-weight: 700; color: {z_color}; font-family: monospace;">{z_score:+.2f}σ</div>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Scanner failed: {e}")

with tab_active:
    st.markdown("<h3 style='color: white; margin-bottom: 24px;'>Live Active Operations (Open Vectors)</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8; margin-bottom: 32px;'>Monitor active positions. Automatically calculates Risk-Free Trailing Stops when price exceeds 1 ATR.</p>", unsafe_allow_html=True)
    
    open_positions = get_open_portfolio_full()
    
    if not open_positions:
        st.markdown("<p style='color:#64748B; text-align:center; padding: 60px 0; font-size: 15px;'>No active positions currently running.</p>", unsafe_allow_html=True)
    else:
        all_limits = {l['ticker']: l for l in get_limits()}
        
        # EXE-01: Independent Portfolio Pricing Engine
        missing_tickers = [p.get('ticker') for p in open_positions if p.get('ticker') not in all_limits]
        live_prices = get_live_portfolio_prices(missing_tickers) if missing_tickers else {}
        
        cols = st.columns(3)
        
        for i, pos in enumerate(open_positions):
            ticker = pos.get('ticker')
            entry_price = float(pos.get('entry_price') or 0.0)
            qty = pos.get('qty') or 0
            
            limit_data = all_limits.get(ticker, {})
            current_price = float(limit_data.get('current_price') or live_prices.get(ticker, entry_price))
            atr = float(limit_data.get('atr_14') or 0.0)
            target = float(pos.get('exit_target') or 0.0)
            sl = float(pos.get('stop_loss') or 0.0)
            
            # Risk-Free Logic: Entry + 1 ATR
            rf_target = entry_price + atr
            
            pnl_pct = ((current_price - entry_price) / entry_price * 100) if entry_price > 0 else 0
            pnl_color = "#00ff00" if pnl_pct > 0 else "#ff4d4d"
            pnl_sign = "+" if pnl_pct > 0 else ""
            
            # CAP-05: Time-Decay Dead Money Veto
            entry_date_str = pos.get('entry_date')
            is_stale = False
            if entry_date_str:
                try:
                    entry_dt = datetime.fromisoformat(entry_date_str.replace('Z', '+00:00'))
                    days_in_trade = (datetime.now(timezone.utc) - entry_dt).days
                    if days_in_trade >= 14 and current_price < rf_target:
                        is_stale = True
                except:
                    pass
            
            if current_price >= rf_target and entry_price > 0:
                rf_color = "#00ff00"
                rf_text = " MOVE STOP TO ENTRY (RISK-FREE). Consider 50% TP."
            elif current_price <= sl and sl > 0:
                rf_color = "#ff4d4d"
                rf_text = "<svg width='1em' height='1em' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z'></path><circle cx='12' cy='12' r='4'></circle></svg> STOP LOSS HIT. Close position immediately."
            elif is_stale:
                rf_color = "#64748B"
                rf_text = f" STALE (14+ Days). Dead Money Veto. Close position."
            else:
                rf_color = "#ffb84d"
                rf_text = f" HOLD. Need {rf_target:.2f} for Risk-Free trail."
                
            currency = "₺" if ticker.endswith('.IS') else "$"
            
            with cols[i % 3]:
                st.markdown(f"""
                    <div style="background: #09090b; border: 1px solid #27272a; border-radius: 2px; padding: 8px; margin-bottom: 16px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h4 style="color: #F8FAFC; margin: 0; font-size: 18px;">{ticker}</h4>
                            <div style="color: {pnl_color}; font-size: 16px; font-weight: 600;">{pnl_sign}{pnl_pct:.2f}%</div>
                        </div>
                        <div style="margin-top: 8px; color: #94A3B8; font-size: 12px;">{qty} UNITS</div>
                        <div style="display: flex; justify-content: space-between; margin-top: 12px; font-size: 14px;">
                            <span style="color: #94A3B8;">Entry: <span style="color: #E2E8F0;">{entry_price:.2f} {currency}</span></span>
                            <span style="color: #94A3B8;">Live: <span style="color: #E2E8F0;">{current_price:.2f} {currency}</span></span>
                        </div>
                        <div style="margin-top: 16px; padding: 12px; background: #000000; border-radius: 2px; border-left: 4px solid {rf_color};">
                            <span style="color: {rf_color}; font-weight: 600; font-size: 13px; letter-spacing: 0.5px;">{rf_text}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # EXE-02: Partial-Exit Analytics Integrity
                st.markdown("""<div style="margin-top: 16px; border-top: 1px solid #27272a; padding-top: 12px;">""", unsafe_allow_html=True)
                fill_cols = st.columns([1, 1])
                with fill_cols[0]:
                    actual_fill = st.number_input(f"Fill Price", value=current_price, step=0.01, key=f"fill_{pos['id']}")
                with fill_cols[1]:
                    safe_qty = max(1, int(qty))
                    close_qty = st.number_input(f"Shares to Close", value=safe_qty, min_value=1, max_value=safe_qty, step=1, key=f"cqty_{pos['id']}")
                
                # EXEC-08: OCO Naked Short Warning
                st.markdown("<p style='color: #ff4d4d; font-size: 12px; font-weight: 600; margin-bottom: 8px; text-align: center;'> BROKER SYNC REQUIRED: Manually cancel resting GTC Stop/Target orders at your broker after exit to prevent naked shorting.</p>", unsafe_allow_html=True)
                
                if st.button(f"Execute Exit ({ticker})", key=f"close_{pos['id']}", use_container_width=True):
                    try:
                        gross_pnl = (actual_fill - entry_price) * close_qty
                        # 0.3% round-trip friction (commission + slippage)
                        friction = (actual_fill * close_qty * 0.0015) + (entry_price * close_qty * 0.0015)
                        pnl_realized = gross_pnl - friction
                        
                        if close_qty >= qty:
                            supabase.table("portfolio").update({
                                "status": "CLOSED",
                                "exit_price": actual_fill,
                                "exit_date": datetime.now(timezone.utc).isoformat(),
                                "net_pnl": pnl_realized
                            }).eq("id", pos['id']).execute()
                        else:
                            supabase.table("portfolio").update({
                                "qty": qty - close_qty
                            }).eq("id", pos['id']).execute()
                            
                            supabase.table("portfolio").insert({
                                "ticker": ticker,
                                "entry_price": entry_price,
                                "entry_date": pos.get('entry_date'),
                                "qty": close_qty,
                                "stop_loss": sl,
                                "exit_target": target,
                                "status": "CLOSED",
                                "exit_price": actual_fill,
                                "exit_date": datetime.now(timezone.utc).isoformat(),
                                "net_pnl": pnl_realized
                            }).execute()
                        st.success(f"Exit Executed! Realized PnL: {pnl_realized:.2f}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to execute exit: {e}")
                st.markdown("</div>", unsafe_allow_html=True)

        # PROD-01 / SYNC-02: State Truth-Sync UI
        st.markdown("<hr style='border-color: #27272a; margin: 32px 0;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: white; margin-bottom: 8px;'>PROD-01 & SYNC-02: State Truth-Sync UI</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #94A3B8; margin-bottom: 24px;'>Reconcile your physical broker state with the AI database. Force-sync ghost positions, fix state detachments, and manually trail Stop/Target levels.</p>", unsafe_allow_html=True)
        
        sync_ticker = st.selectbox("Select Active Position to Modify", options=[p['ticker'] for p in open_positions], key="sync_ticker")
        
        if sync_ticker:
            target_pos = next(p for p in open_positions if p['ticker'] == sync_ticker)
            sync_cols = st.columns(5)
            with sync_cols[0]:
                new_qty = st.number_input("Real Broker Qty", value=int(target_pos.get('qty') or 0), step=1, key="sync_qty")
            with sync_cols[1]:
                new_entry = st.number_input("Real Cost Basis", value=float(target_pos.get('entry_price') or 0.0), step=0.01, key="sync_entry")
            with sync_cols[2]:
                new_sl = st.number_input("Trail Stop Loss", value=float(target_pos.get('stop_loss') or 0.0), step=0.01, key="sync_sl")
            with sync_cols[3]:
                new_tp = st.number_input("Edit Target", value=float(target_pos.get('exit_target') or 0.0), step=0.01, key="sync_tp")
            with sync_cols[4]:
                st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                if st.button("FORCE SYNC", use_container_width=True, key="sync_btn"):
                    with st.spinner(f"Synchronizing {sync_ticker} with database..."):
                        import time
                        time.sleep(0.5) 
                        try:
                            status = "CLOSED" if new_qty <= 0 else "OPEN"
                            supabase.table("portfolio").update({
                                "qty": new_qty,
                                "entry_price": new_entry,
                                "stop_loss": new_sl,
                                "exit_target": new_tp,
                                "status": status,
                                "exit_price": new_entry if status == "CLOSED" else None,
                                "exit_date": datetime.now(timezone.utc).isoformat() if status == "CLOSED" else None,
                                "net_pnl": 0.0 if status == "CLOSED" else None
                            }).eq("id", target_pos["id"]).execute()
                            st.toast(f"Synchronized {sync_ticker} successfully!", icon="✅")
                            time.sleep(0.5)
                        except Exception as e:
                            st.error(f"Sync failed: {e}")
                    st.rerun()

with tab4:
    st.markdown("<h3 style='color: white; margin-bottom: 24px;'>Bayesian Edge Analytics</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8; margin-bottom: 32px;'>This module mathematically tracks your realized manual execution win rates against the baseline AI expectancy. If your realized edge drops below the baseline, it indicates emotional tilt or poor execution discipline.</p>", unsafe_allow_html=True)
    
    from bayesian_self_auditor import BayesianSelfAuditor
    import db_manager
    auditor = BayesianSelfAuditor(db_manager.SovereignDatabase())
    realized_rates = auditor.get_realized_edge()
    base_rates = auditor.base_win_rates
    
    cols = st.columns(3)
    for i, (bucket, base_rate) in enumerate(base_rates.items()):
        real_rate = realized_rates.get(bucket, base_rate)
        diff = real_rate - base_rate
        color = "#00ff00" if diff >= 0 else "#ff4d4d"
        arrow = "▲" if diff >= 0 else "▼"
        
        with cols[i]:
            st.markdown(f"""
                <div style="background: #09090b; border: 1px solid #27272a; border-radius: 2px; padding: 24px; text-align: center;">
                    <div style="color: #94A3B8; font-size: 13px; font-weight: 600; letter-spacing: 1px; margin-bottom: 8px;">{bucket} BUCKET</div>
                    <div style="font-size: 36px; font-weight: 700; color: #FFFFFF; font-family: monospace;">{real_rate:.1%}</div>
                    <div style="color: {color}; font-size: 14px; font-weight: 500; margin-top: 8px;">
                        {arrow} {abs(diff):.1%} vs AI Baseline ({base_rate:.1%})
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
    st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 32px 0;'>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: white; margin-bottom: 16px;'>EXEC-03: Slippage Bleed Auditor</h4>", unsafe_allow_html=True)
    
    try:
        response = auditor.db.supabase.table("portfolio").select("*").eq("status", "CLOSED").order('exit_date', desc=True).limit(50).execute()
        history = response.data if response and response.data else []
        if history:
            total_theo = 0.0
            total_real = 0.0
            for t in history:
                ep = float(t.get('entry_price') or 0.0)
                xp = float(t.get('exit_price') or 0.0)
                tp = float(t.get('exit_target') or 0.0)
                sl = float(t.get('stop_loss') or 0.0)
                qty = float(t.get('qty') or 0.0)
                
                real_pnl = (xp - ep) * qty
                total_real += real_pnl
                
                theo_xp = tp if real_pnl > 0 else sl
                if theo_xp > 0 and ep > 0:
                    theo_pnl = (theo_xp - ep) * qty
                    total_theo += theo_pnl
                    
            bleed = total_theo - total_real
            b_color = "#ff4d4d" if bleed > 0 else "#00ff00"
            st.markdown(f"""
                <div style="background: #09090b; border: 1px solid #27272a; border-radius: 2px; padding: 24px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
                    <div>
                        <div style="color: #94A3B8; font-size: 13px; font-weight: 600; letter-spacing: 1px; margin-bottom: 8px;">TOTAL EXECUTION SLIPPAGE</div>
                        <div style="color: {b_color}; font-size: 32px; font-weight: 700; font-family: monospace;">{'-' if bleed > 0 else '+'}{abs(bleed):.2f} ₺</div>
                        <div style="color: #64748B; font-size: 13px; margin-top: 8px;">Measures value lost to bad spreads or delayed manual entries.</div>
                    </div>
                    <div style="text-align: right; font-size: 15px; color: #94A3B8;">
                        <div style="margin-bottom: 4px;">AI Theoretical PnL: <span style="color: #E2E8F0; font-weight: 600;">{total_theo:.2f} ₺</span></div>
                        <div>Your Realized PnL: <span style="color: #E2E8F0; font-weight: 600;">{total_real:.2f} ₺</span></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Failed to load slippage auditor: {e}")

    # INST-01: Real-Yield PnL Auditor
    st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 32px 0;'>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: white; margin-bottom: 16px;'>INST-01: Real-Yield PnL Auditor (USD-Pegged)</h4>", unsafe_allow_html=True)
    show_usd_yield = st.toggle("Convert BIST PnL to True USD Yield")
    if show_usd_yield:
        try:
            import yfinance as yf
            import pandas as pd
            
            usd_try_ticker = yf.Ticker("TRY=X")
            usd_df = usd_try_ticker.history(period="5y")['Close']
            
            if not usd_df.empty:
                usd_df.index = usd_df.index.tz_localize(None)
                
                total_nominal_try = 0.0
                total_real_usd = 0.0
                
                if 'history' not in locals():
                    response = auditor.db.supabase.table("portfolio").select("*").eq("status", "CLOSED").execute()
                    history = response.data if response and response.data else []
                    
                for t in history:
                    if t.get('ticker', '').endswith('.IS'):
                        ep = float(t.get('entry_price') or 0.0)
                        xp = float(t.get('exit_price') or 0.0)
                        qty = float(t.get('qty') or 0.0)
                        entry_date_str = t.get('entry_date') or t.get('created_at')
                        exit_date_str = t.get('exit_date')
                        
                        if entry_date_str and exit_date_str:
                            ed = pd.to_datetime(entry_date_str).tz_localize(None)
                            xd = pd.to_datetime(exit_date_str).tz_localize(None)
                            
                            try:
                                ed_idx = usd_df.index.get_indexer([ed], method='nearest')[0]
                                xd_idx = usd_df.index.get_indexer([xd], method='nearest')[0]
                                entry_usd_rate = float(usd_df.iloc[ed_idx])
                                exit_usd_rate = float(usd_df.iloc[xd_idx])
                                
                                nominal_pnl = (xp - ep) * qty
                                total_nominal_try += nominal_pnl
                                
                                entry_usd = (ep * qty) / entry_usd_rate
                                exit_usd = (xp * qty) / exit_usd_rate
                                real_usd_pnl = exit_usd - entry_usd
                                total_real_usd += real_usd_pnl
                            except:
                                pass
                                
                p_color = "#00ff00" if total_real_usd >= 0 else "#ff4d4d"
                st.markdown(f"""
                    <div style="background: #09090b; border: 1px solid #27272a; border-radius: 2px; padding: 24px; margin-bottom: 24px;">
                        <div style="color: #94A3B8; font-size: 13px; font-weight: 600; letter-spacing: 1px; margin-bottom: 8px;">TRUE PURCHASING POWER DELTA</div>
                        <div style="font-size: 32px; font-weight: 700; color: {p_color}; font-family: monospace;">{'+' if total_real_usd >=0 else ''}{total_real_usd:.2f} $</div>
                        <div style="color: #64748B; font-size: 13px; margin-top: 8px;">Nominal Yield (Illusion): {total_nominal_try:.2f} ₺</div>
                    </div>
                """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Failed to calculate Real Yield: {e}")

    st.markdown("<h4 style='color: white; margin-bottom: 16px;'>Trade Journal</h4>", unsafe_allow_html=True)
    
    try:
        response = auditor.db.supabase.table("portfolio").select("*").eq("status", "CLOSED").order('exit_date', desc=True).limit(10).execute()
        history = response.data if response and response.data else []
        if not history:
            st.markdown("<p style='color: #64748B; font-style: italic;'>No closed trades found in the journal.</p>", unsafe_allow_html=True)
        else:
            for trade in history:
                ticker = trade.get('ticker')
                bucket = trade.get('bucket')
                pnl = trade.get('pnl', 0)
                pnl_color = "#00ff00" if pnl > 0 else "#ff4d4d"
                pnl_sign = "+" if pnl > 0 else ""
                
                st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.02); padding: 12px 16px; border-radius: 2px; border-left: 3px solid {pnl_color}; margin-bottom: 8px;">
                        <div style="display: flex; align-items: center; gap: 16px;">
                            <span style="font-weight: 600; color: #F8FAFC; width: 80px;">{ticker}</span>
                            <span style="color: #94A3B8; font-size: 13px; background: #27272a; padding: 2px 8px; border-radius: 2px;">{bucket}</span>
                        </div>
                        <div style="font-family: monospace; font-weight: 600; color: {pnl_color}; font-size: 15px;">
                            {pnl_sign}{pnl:.2f}₺
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Failed to load journal: {e}")
