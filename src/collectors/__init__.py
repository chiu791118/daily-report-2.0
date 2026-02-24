"""Data collectors for Daily Market Digest."""
from .news import NewsCollector, NewsItem
from .youtube import YouTubeCollector, YouTubeVideo
from .stocks import StockCollector, StockData, MarketOverview
from .economic_calendar import EconomicCalendarCollector, EconomicEvent
from .earnings import EarningsCalendarCollector, EarningsEvent
from .universe import UniverseCollector

# New collectors for weekend reports
from .base import IntelItem, SourceType, SignalStrength, SignalType, BaseCollector
from .entity_matcher import EntityMatcher
from .sec_edgar import SECEdgarCollector
from .arxiv import ArxivCollector
from .clinical_trials import ClinicalTrialsCollector
from .fda import FDACollector
from .intel_aggregator import IntelAggregator

__all__ = [
    # Original collectors
    "NewsCollector",
    "NewsItem",
    "YouTubeCollector",
    "YouTubeVideo",
    "StockCollector",
    "StockData",
    "MarketOverview",
    "EconomicCalendarCollector",
    "EconomicEvent",
    "EarningsCalendarCollector",
    "EarningsEvent",
    "UniverseCollector",
    # Base classes
    "IntelItem",
    "SourceType",
    "SignalStrength",
    "SignalType",
    "BaseCollector",
    "EntityMatcher",
    # New collectors
    "SECEdgarCollector",
    "ArxivCollector",
    "ClinicalTrialsCollector",
    "FDACollector",
    "IntelAggregator",
]
