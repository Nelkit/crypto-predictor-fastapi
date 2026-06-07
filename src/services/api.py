import requests
import requests_cache
import pandas as pd
import logging
from datetime import timedelta
from src.services.constants import BASE_API_URL, API_KEY

# Enable caching for 10 minutes
requests_cache.install_cache("coingecko_cache", expire_after=timedelta(minutes=0))

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class CoinGeckoApi:
    """Wrapper class for fetching cryptocurrency data from the CoinGecko API."""

    def __init__(self):
        self.session = requests.Session()
        self.base_url = BASE_API_URL

    def fetch_merged_daily_data( self, coin_id: str, vs_currency: str = "usd", days: int = 30, interval: str = "daily") -> pd.DataFrame:
        """
        Fetch daily market data for a specific coin using /market_chart.
        Derives OHLC and merges volume and market cap data.

        Returns:
            pd.DataFrame with columns ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'market_cap']
            or an empty DataFrame if the request fails.
        """
        endpoint = f"{self.base_url}/coins/{coin_id}/market_chart"
        headers = {"x-cg-demo-api-key": API_KEY} if API_KEY else {}
        params = {"vs_currency": vs_currency, "days": days, "interval": interval}

        try:
            response = self.session.get(endpoint, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()

            # Validate response structure
            required_keys = ["prices", "market_caps", "total_volumes"]
            if not all(k in data for k in required_keys):
                logger.warning(f"Incomplete data structure from API for {coin_id}.")
                return pd.DataFrame()

            # Parse CoinGecko data
            prices = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
            market_caps = pd.DataFrame(data["market_caps"], columns=["timestamp", "market_cap"])
            volumes = pd.DataFrame(data["total_volumes"], columns=["timestamp", "volume"])

            for df in (prices, market_caps, volumes):
                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

            # Derive OHLC
            prices["date"] = prices["timestamp"].dt.date
            ohlc = (
                prices.groupby("date")["price"]
                .agg(open="first", high="max", low="min", close="last")
                .reset_index()
            )
            ohlc["timestamp"] = pd.to_datetime(ohlc["date"])
            ohlc.drop(columns="date", inplace=True)


            df = (
                ohlc.merge(market_caps, on="timestamp", how="inner")
                .merge(volumes, on="timestamp", how="inner")
                .sort_values("timestamp")
                .reset_index(drop=True)
            )

            return df

        except requests.exceptions.Timeout:
            logger.error(f"⏰ Timeout while fetching data for {coin_id}")
            return pd.DataFrame()

        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                logger.warning(f"⚠️ Rate limit hit for {coin_id}. Using cached or fallback data.")
            else:
                logger.error(f"HTTP error fetching {coin_id}: {e}")
            return pd.DataFrame()

        except Exception as e:
            logger.error(f"Unexpected error fetching market data for {coin_id}: {e}")
            return pd.DataFrame()
