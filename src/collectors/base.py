"""
Base classes and data structures for collectors.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class SourceType(Enum):
    """資料來源類型"""
    NEWS = "news"
    SEC_FILING = "sec_filing"
    RESEARCH_PAPER = "research_paper"
    CLINICAL_TRIAL = "clinical_trial"
    REGULATORY = "regulatory"


class SignalStrength(Enum):
    """信號強度（供 AI 分類用）"""
    HIGH = "high"           # 會改變認知地圖
    MEDIUM = "medium"       # 確認既有趨勢
    LOW = "low"             # 噪音或無法判斷
    UNCLASSIFIED = "unclassified"


class SignalType(Enum):
    """信號類型（對應 Prompt #2 分類）"""
    FACT = "fact"                   # 直接事實 (observable facts)
    ACTION = "action"               # 行為訊號 (actions / decisions)
    CONSTRAINT = "constraint"       # 約束或激勵線索 (constraints / incentives)
    NOISE = "noise"                 # 噪音或重複資訊


@dataclass
class IntelItem:
    """
    統一情報資料結構

    設計原則：
    1. 共同欄位放基類，專屬資料放 metadata
    2. 支援上市公司（ticker）和非上市公司（entity）
    3. 預留 AI 分類欄位
    """
    # === 基本資訊 ===
    title: str
    source: str                     # "WSJ", "SEC", "arXiv", "FDA"
    source_type: SourceType
    url: str
    published: datetime

    # === 內容 ===
    summary: str = ""
    full_text: str = ""             # 可選，部分來源可取得全文

    # === 分類標籤 ===
    category: str = ""              # "8-K", "cs.AI", "Phase 3", "Approval"
    industries: list = field(default_factory=list)      # ["AI", "半導體"]

    # === 關聯實體（支援非上市公司）===
    related_tickers: list = field(default_factory=list)     # ["NVDA", "MSFT"]
    related_entities: list = field(default_factory=list)    # ["OpenAI", "Anthropic"]

    # === AI 分析欄位（後續填入）===
    signal_strength: SignalStrength = SignalStrength.UNCLASSIFIED
    signal_type: SignalType = SignalType.FACT
    why_it_matters: str = ""        # AI 生成的「所以呢」

    # === 來源專屬資料 ===
    metadata: dict = field(default_factory=dict)
    """
    metadata 範例：

    SEC:
    {
        "form_type": "8-K",
        "cik": "0001318605",
        "company_name": "Tesla Inc",
        "filing_date": "2024-01-15",
        "items": ["Item 2.02", "Item 9.01"]
    }

    arXiv:
    {
        "arxiv_id": "2401.12345",
        "authors": ["Author 1", "Author 2"],
        "categories": ["cs.AI", "cs.LG"],
        "pdf_url": "https://arxiv.org/pdf/2401.12345",
        "affiliations": ["Google DeepMind", "Stanford"]
    }

    ClinicalTrials:
    {
        "nct_id": "NCT12345678",
        "phase": "Phase 3",
        "status": "RECRUITING",
        "sponsor": "Eli Lilly",
        "conditions": ["Obesity", "Type 2 Diabetes"],
        "interventions": ["Tirzepatide"]
    }

    FDA:
    {
        "application_number": "NDA 215866",
        "approval_type": "New Drug Application",
        "active_ingredient": "semaglutide",
        "brand_name": "Wegovy",
        "sponsor": "Novo Nordisk"
    }
    """

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "title": self.title,
            "source": self.source,
            "source_type": self.source_type.value,
            "url": self.url,
            "published": self.published.isoformat(),
            "summary": self.summary,
            "full_text": self.full_text,
            "category": self.category,
            "industries": self.industries,
            "related_tickers": self.related_tickers,
            "related_entities": self.related_entities,
            "signal_strength": self.signal_strength.value,
            "signal_type": self.signal_type.value,
            "why_it_matters": self.why_it_matters,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "IntelItem":
        """Create from dictionary."""
        return cls(
            title=data["title"],
            source=data["source"],
            source_type=SourceType(data["source_type"]),
            url=data["url"],
            published=datetime.fromisoformat(data["published"]),
            summary=data.get("summary", ""),
            full_text=data.get("full_text", ""),
            category=data.get("category", ""),
            industries=data.get("industries", []),
            related_tickers=data.get("related_tickers", []),
            related_entities=data.get("related_entities", []),
            signal_strength=SignalStrength(data.get("signal_strength", "unclassified")),
            signal_type=SignalType(data.get("signal_type", "fact")),
            why_it_matters=data.get("why_it_matters", ""),
            metadata=data.get("metadata", {}),
        )


class BaseCollector:
    """Base class for all collectors."""

    def __init__(self):
        self.entity_matcher = None  # Will be initialized when needed

    def _load_entity_matcher(self):
        """Lazy load entity matcher."""
        if self.entity_matcher is None:
            from src.collectors.entity_matcher import EntityMatcher
            self.entity_matcher = EntityMatcher()
        return self.entity_matcher

    def tag_entities(self, item: IntelItem) -> IntelItem:
        """Tag an IntelItem with related tickers and entities."""
        matcher = self._load_entity_matcher()
        text = f"{item.title} {item.summary}"

        tickers, entities, industries = matcher.find_matches(text)

        item.related_tickers = list(set(item.related_tickers + tickers))
        item.related_entities = list(set(item.related_entities + entities))
        item.industries = list(set(item.industries + industries))

        return item
