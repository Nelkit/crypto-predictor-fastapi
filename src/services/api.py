import requests
import requests_cache
from datetime import timedelta
import pandas as pd
from src.services.constants import BASE_API_URL

# === Enable caching for 10 minutes ===
requests_cache.install_cache("coingecko_cache", expire_after=timedelta(minutes=10))

class CoinGeckoApi:
    """Wrapper class for fetching cryptocurrency data from the CoinGecko API."""

    def __init__(self):
        self.session = requests.Session()
        self.base_url = BASE_API_URL

    def fetch_merged_daily_data(self, coin_id: str, vs_currency: str = "usd", days: int = 30, interval: str = "daily") -> pd.DataFrame | None:
        """
        Fetch daily market data for a specific coin using only the /market_chart endpoint.
        The method derives open, high, low, close from the price data, and merges them with
        volume and market cap from the same endpoint.

        Args:
            coin_id (str): CoinGecko ID (e.g., 'bitcoin', 'ethereum', 'solana', 'ripple')
            vs_currency (str): Currency to compare against (default: 'usd')
            days (int): Number of days of data to fetch
            interval (str): Data granularity ('daily', 'hourly', 'minutely')

        Returns:
            pd.DataFrame | None: DataFrame with columns
                ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'market_cap'],
                or None if request fails.
        """
        endpoint = f"{self.base_url}/coins/{coin_id}/market_chart"
        params = {"vs_currency": vs_currency, "days": days, "interval": interval}

        try:
            # === Request data (cached if within 10 minutes) ===
            response = self.session.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            # === Parse CoinGecko data ===
            prices = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
            market_caps = pd.DataFrame(data["market_caps"], columns=["timestamp", "market_cap"])
            volumes = pd.DataFrame(data["total_volumes"], columns=["timestamp", "volume"])

            # === Convert timestamps ===
            for df in (prices, market_caps, volumes):
                df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

            # === Derive OHLC ===
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

        except requests.exceptions.HTTPError as e:
            # Handle rate-limit or network errors
            if response.status_code == 429:
                print(f"⚠️ Rate limit hit for {coin_id}. Using cached or fallback data.")
            else:
                print(f"HTTP error while fetching {coin_id}: {e}")
            return None

        except Exception as e:
            print(f"Unexpected error fetching market data for {coin_id}: {e}")
            return None
