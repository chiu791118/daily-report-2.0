"""
Stock Data Collector Module
Fetches stock prices, technical indicators, and economic data.
"""
import yaml
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass, field
import pytz

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config.settings import (
    CONFIG_DIR,
    TIMEZONE,
    ALPHA_VANTAGE_API_KEY,
)


@dataclass
class StockData:
    """Represents stock data and analysis."""
    symbol: str
    name: str
    current_price: float
    previous_close: float
    change_percent: float
    volume: int
    avg_volume: int
    volume_ratio: float
    high_52w: float
    low_52w: float
    market_cap: float
    pe_ratio: Optional[float] = None
    notes: str = ""
    category: str = ""
    support_levels: list = field(default_factory=list)
    resistance_levels: list = field(default_factory=list)

    # Technical indicators
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    rsi_14: Optional[float] = None

    # Recent performance
    change_1w: Optional[float] = None
    change_1m: Optional[float] = None
    change_3m: Optional[float] = None

    @property
    def trend(self) -> str:
        """Determine trend based on moving averages."""
        if self.sma_20 and self.sma_50 and self.sma_200:
            if self.current_price > self.sma_20 > self.sma_50 > self.sma_200:
                return "Strong Uptrend"
            elif self.current_price > self.sma_50 > self.sma_200:
                return "Uptrend"
            elif self.current_price < self.sma_20 < self.sma_50 < self.sma_200:
                return "Strong Downtrend"
            elif self.current_price < self.sma_50 < self.sma_200:
                return "Downtrend"
        return "Neutral"

    @property
    def volume_signal(self) -> str:
        """Analyze volume compared to average."""
        if self.volume_ratio > 2.0:
            return "Very High Volume"
        elif self.volume_ratio > 1.5:
            return "High Volume"
        elif self.volume_ratio < 0.5:
            return "Low Volume"
        return "Normal Volume"


@dataclass
class MarketOverview:
    """Market indices overview."""
    sp500: Optional[StockData] = None
    nasdaq: Optional[StockData] = None
    dow: Optional[StockData] = None
    vix: Optional[float] = None
    vix_change: Optional[float] = None

    @property
    def market_sentiment(self) -> str:
        """Determine market sentiment based on VIX and index performance."""
        if self.vix:
            if self.vix > 30:
                return "High Fear"
            elif self.vix > 20:
                return "Elevated Caution"
            elif self.vix < 15:
                return "Low Volatility / Complacency"
        return "Neutral"


class StockCollector:
    """Collects stock data and performs technical analysis."""

    def __init__(self):
        self.tz = pytz.timezone(TIMEZONE)
        self.watchlist = self._load_watchlist()

    def _load_watchlist(self) -> dict:
        """Load stock watchlist from YAML."""
        stocks_file = CONFIG_DIR / "stocks.yaml"
        with open(stocks_file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def get_market_overview(self) -> MarketOverview:
        """Get market indices overview."""
        overview = MarketOverview()

        # Fetch S&P 500
        try:
            sp500_data = self._get_stock_data("^GSPC", "S&P 500", "indices")
            overview.sp500 = sp500_data
        except Exception as e:
            print(f"Error fetching S&P 500: {e}")

        # Fetch NASDAQ
        try:
            nasdaq_data = self._get_stock_data("^IXIC", "NASDAQ", "indices")
            overview.nasdaq = nasdaq_data
        except Exception as e:
            print(f"Error fetching NASDAQ: {e}")

        # Fetch Dow
        try:
            dow_data = self._get_stock_data("^DJI", "Dow Jones", "indices")
            overview.dow = dow_data
        except Exception as e:
            print(f"Error fetching Dow: {e}")

        # Fetch VIX
        try:
            vix = yf.Ticker("^VIX")
            vix_info = vix.info
            overview.vix = vix_info.get("regularMarketPrice", 0)
            overview.vix_change = vix_info.get("regularMarketChangePercent", 0)
        except Exception as e:
            print(f"Error fetching VIX: {e}")

        return overview

    def collect_watchlist(self) -> list[StockData]:
        """Collect data for all stocks in watchlist."""
        all_stocks = []

        for category, stocks in self.watchlist.get("watchlist", {}).items():
            if category == "indices":
                continue  # Skip indices, handled separately

            for stock_info in stocks:
                try:
                    stock_data = self._get_stock_data(
                        symbol=stock_info["symbol"],
                        name=stock_info["name"],
                        category=category,
                        notes=stock_info.get("notes", ""),
                    )
                    # Add key levels if configured
                    key_levels = self.watchlist.get("key_levels", {}).get(
                        stock_info["symbol"], {}
                    )
                    stock_data.support_levels = key_levels.get("support", [])
                    stock_data.resistance_levels = key_levels.get("resistance", [])

                    all_stocks.append(stock_data)
                except Exception as e:
                    print(f"Error fetching {stock_info['symbol']}: {e}")

        return all_stocks

    def _get_stock_data(
        self,
        symbol: str,
        name: str,
        category: str,
        notes: str = "",
    ) -> StockData:
        """Get comprehensive data for a single stock."""
        ticker = yf.Ticker(symbol)
        info = ticker.info

        # Get historical data for technical analysis
        hist = ticker.history(period="1y")

        # Calculate moving averages
        sma_20 = hist["Close"].rolling(window=20).mean().iloc[-1] if len(hist) >= 20 else None
        sma_50 = hist["Close"].rolling(window=50).mean().iloc[-1] if len(hist) >= 50 else None
        sma_200 = hist["Close"].rolling(window=200).mean().iloc[-1] if len(hist) >= 200 else None

        # Calculate RSI
        rsi_14 = self._calculate_rsi(hist["Close"], 14)

        # Calculate performance periods
        current_price = info.get("regularMarketPrice", hist["Close"].iloc[-1])

        change_1w = None
        change_1m = None
        change_3m = None

        if len(hist) >= 5:
            change_1w = ((current_price / hist["Close"].iloc[-5]) - 1) * 100
        if len(hist) >= 21:
            change_1m = ((current_price / hist["Close"].iloc[-21]) - 1) * 100
        if len(hist) >= 63:
            change_3m = ((current_price / hist["Close"].iloc[-63]) - 1) * 100

        # Volume analysis
        volume = info.get("regularMarketVolume", 0)
        avg_volume = info.get("averageVolume", 1)
        volume_ratio = volume / avg_volume if avg_volume > 0 else 1

        return StockData(
            symbol=symbol,
            name=name,
            current_price=current_price,
            previous_close=info.get("regularMarketPreviousClose", 0),
            change_percent=info.get("regularMarketChangePercent", 0),
            volume=volume,
            avg_volume=avg_volume,
            volume_ratio=volume_ratio,
            high_52w=info.get("fiftyTwoWeekHigh", 0),
            low_52w=info.get("fiftyTwoWeekLow", 0),
            market_cap=info.get("marketCap", 0),
            pe_ratio=info.get("trailingPE"),
            notes=notes,
            category=category,
            sma_20=sma_20,
            sma_50=sma_50,
            sma_200=sma_200,
            rsi_14=rsi_14,
            change_1w=change_1w,
            change_1m=change_1m,
            change_3m=change_3m,
        )

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> Optional[float]:
        """Calculate RSI indicator."""
        if len(prices) < period + 1:
            return None

        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi.iloc[-1]

    def get_sector_performance(self) -> dict:
        """Get sector ETF performance."""
        sectors = self.watchlist.get("sectors", [])
        sector_data = {}

        for sector_symbol in sectors:
            try:
                ticker = yf.Ticker(sector_symbol)
                info = ticker.info
                sector_data[sector_symbol] = {
                    "name": info.get("shortName", sector_symbol),
                    "change_percent": info.get("regularMarketChangePercent", 0),
                    "price": info.get("regularMarketPrice", 0),
                }
            except Exception as e:
                print(f"Error fetching sector {sector_symbol}: {e}")

        return sector_data


def main():
    """Test the stock collector."""
    collector = StockCollector()

    # Get market overview
    print("\n=== Market Overview ===\n")
    overview = collector.get_market_overview()

    if overview.sp500:
        print(f"S&P 500: {overview.sp500.current_price:,.2f} ({overview.sp500.change_percent:+.2f}%)")
    if overview.nasdaq:
        print(f"NASDAQ: {overview.nasdaq.current_price:,.2f} ({overview.nasdaq.change_percent:+.2f}%)")
    if overview.dow:
        print(f"Dow Jones: {overview.dow.current_price:,.2f} ({overview.dow.change_percent:+.2f}%)")
    if overview.vix:
        print(f"VIX: {overview.vix:.2f} ({overview.vix_change:+.2f}%)")
    print(f"Market Sentiment: {overview.market_sentiment}")

    # Get watchlist
    print("\n=== Watchlist ===\n")
    stocks = collector.collect_watchlist()

    for stock in stocks:
        print(f"{stock.symbol} - {stock.name}")
        print(f"  Price: ${stock.current_price:,.2f} ({stock.change_percent:+.2f}%)")
        print(f"  Trend: {stock.trend} | RSI: {stock.rsi_14:.1f if stock.rsi_14 else 'N/A'}")
        print(f"  Volume: {stock.volume_signal}")
        print()


if __name__ == "__main__":
    main()
