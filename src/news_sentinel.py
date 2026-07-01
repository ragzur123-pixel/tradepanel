import yfinance as yf
import pandas as pd
from datetime import datetime, timezone, timedelta
import logging

logger = logging.getLogger(__name__)

class NewsSentinel:
    def __init__(self):
        pass

    def check_corporate_actions(self, ticker):
        """
        Checks for recent or upcoming stock splits and dividends using yfinance.
        If a split or dividend is detected within the last 5 days or today, 
        it invalidates the technical math and flags as HIGH RISK.
        """
        try:
            yf_ticker = ticker

            stock = yf.Ticker(yf_ticker)
            actions = stock.actions
            
            if actions is None or actions.empty:
                return {"status": "SAFE", "message": "No recent corporate actions detected."}

            # Filter for actions in the last 7 days
            recent_threshold = pd.Timestamp.now(timezone.utc) - pd.DateOffset(days=7)
            
            # Ensure the actions index is timezone-aware for comparison
            if actions.index.tz is None:
                actions.index = actions.index.tz_localize('UTC')
            
            recent_actions = actions[actions.index >= recent_threshold]

            if not recent_actions.empty:
                action_types = []
                if 'Dividends' in recent_actions.columns and recent_actions['Dividends'].sum() > 0:
                    action_types.append("Dividend")
                if 'Stock Splits' in recent_actions.columns and recent_actions['Stock Splits'].sum() > 0:
                    action_types.append("Stock Split")
                
                if action_types:
                    action_str = " and ".join(action_types)
                    return {
                        "status": "HIGH_RISK", 
                        "message": f" KAP ALERT: Recent {action_str} detected. Technical math may be invalid."
                    }

            return {"status": "SAFE", "message": "No recent corporate actions detected."}

        except Exception as e:
            logger.error(f"Failed to fetch corporate actions for {ticker}: {e}")
            return {"status": "UNKNOWN", "message": "Failed to fetch KAP/Actions data."}

    def fetch_latest_news(self, ticker):
        """
        Fetches the latest news headlines from Yahoo Finance.
        """
        #  HARVEST-04: Institutional Sentiment NLP Lexicon
        BULLISH_WORDS = ['surge', 'jump', 'soar', 'beat', 'growth', 'upgrade', 'buy', 'record', 'high', 'profit', 'dividend', 'agreement', 'partner', 'launch']
        BEARISH_WORDS = ['plunge', 'drop', 'fall', 'miss', 'decline', 'downgrade', 'sell', 'low', 'loss', 'lawsuit', 'investigation', 'delay', 'cut', 'debt']
        
        def _score_headline(text):
            text = text.lower()
            bull_score = sum(1 for word in BULLISH_WORDS if word in text)
            bear_score = sum(1 for word in BEARISH_WORDS if word in text)
            
            if bull_score > bear_score: return 1.0    # Bullish
            if bear_score > bull_score: return -1.0   # Bearish
            return 0.0                                # Neutral

        try:
            yf_ticker = ticker
                
            stock = yf.Ticker(yf_ticker)
            news = stock.news
            
            if not news:
                return []
                
            headlines = []
            for item in news[:3]: # Get top 3
                if 'content' in item:
                    content = item['content']
                    title = content.get('title', 'Unknown Title')
                    publisher = content.get('provider', {}).get('displayName', 'Unknown')
                    link = content.get('clickThroughUrl', {}).get('url', '#')
                    
                    pub_date_str = content.get('pubDate')
                    if pub_date_str:
                        # e.g., '2025-11-08T07:06:49Z'
                        pub_time = pd.to_datetime(pub_date_str).to_pydatetime()
                        if pub_time.tzinfo is None:
                            pub_time = pub_time.replace(tzinfo=timezone.utc)
                    else:
                        pub_time = datetime.now(timezone.utc)
                else:
                    # Fallback to old format
                    title = item.get('title', 'Unknown Title')
                    publisher = item.get('publisher', 'Unknown')
                    link = item.get('link', '#')
                    pub_time = datetime.fromtimestamp(item.get('providerPublishTime', 0), tz=timezone.utc)
                
                hours_old = (datetime.now(timezone.utc) - pub_time).total_seconds() / 3600
                nlp_score = _score_headline(title)
                
                headlines.append({
                    "title": title,
                    "publisher": publisher,
                    "hours_old": max(0.0, round(hours_old, 1)),
                    "nlp_score": nlp_score,
                    "link": link
                })
                
            return headlines
            
        except Exception as e:
            logger.error(f"Failed to fetch news for {ticker}: {e}")
            return []

    def check_macro_blackout(self):
        """
        EXEC-04: Simulates an Economic Calendar by checking SPY top news for 
        high-impact macro keywords (CPI, FOMC, Powell, Inflation). 
        If highly prevalent, triggers a Macro Blackout.
        """
        try:
            spy = yf.Ticker("SPY")
            news = spy.news
            if not news:
                return False
                
            mentions = 0
            for item in news[:10]:
                content = item.get('content', item)
                title = content.get('title', '').upper()
                summary = content.get('summary', '').upper()
                text = title + " " + summary
                if any(k in text for k in ['CPI', 'FOMC', 'POWELL', 'RATE DECISION', 'INFLATION', 'NFP']):
                    mentions += 1
            
            if mentions >= 2: # High concentration of macro news
                return True
        except Exception as e:
            logger.error(f"Failed to check macro blackout: {e}")
        return False

if __name__ == "__main__":
    sentinel = NewsSentinel()
    print("Testing THYAO.IS Corporate Actions...")
    print(sentinel.check_corporate_actions("THYAO.IS"))
    
    print("\nTesting THYAO.IS Latest News...")
    news = sentinel.fetch_latest_news("THYAO.IS")
    for n in news:
        print(f"- {n['title']} ({n['hours_old']} hours ago)")
