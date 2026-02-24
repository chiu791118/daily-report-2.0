"""
Entity Matcher Module
Matches text against tracked entities (companies, people, institutions).
"""
import re
import yaml
from pathlib import Path
from typing import Tuple


class EntityMatcher:
    """Matches text against tracked entities from entities.yaml."""

    def __init__(self):
        self.config_path = Path(__file__).parent.parent / "config" / "entities.yaml"
        self._load_entities()

    def _load_entities(self):
        """Load and index entities for fast matching."""
        with open(self.config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # Build lookup dictionaries
        self.ticker_to_info = {}      # ticker -> {name, industry}
        self.entity_to_info = {}      # entity name -> {industry, ticker (if any)}
        self.alias_to_entity = {}     # alias -> entity name
        self.alias_to_ticker = {}     # alias -> ticker (for listed companies)
        self.industries = set()

        # Process entities by industry
        for industry, categories in data.get("entities", {}).items():
            self.industries.add(industry)

            # Listed companies
            for company in categories.get("listed", []):
                name = company["name"]
                ticker = company.get("ticker", "")
                aliases = company.get("aliases", [])

                if ticker:
                    self.ticker_to_info[ticker] = {
                        "name": name,
                        "industry": industry,
                    }
                    self.alias_to_ticker[name.lower()] = ticker
                    self.alias_to_ticker[ticker.lower()] = ticker

                self.entity_to_info[name] = {
                    "industry": industry,
                    "ticker": ticker,
                    "is_listed": True,
                }

                # Index aliases
                for alias in aliases:
                    self.alias_to_entity[alias.lower()] = name
                    if ticker:
                        self.alias_to_ticker[alias.lower()] = ticker

            # Unlisted companies
            for company in categories.get("unlisted", []):
                name = company["name"]
                aliases = company.get("aliases", [])

                self.entity_to_info[name] = {
                    "industry": industry,
                    "ticker": None,
                    "is_listed": False,
                }
                self.alias_to_entity[name.lower()] = name

                for alias in aliases:
                    self.alias_to_entity[alias.lower()] = name

        # Process key people
        for person in data.get("key_people", []):
            name = person["name"]
            entities = person.get("entities", [])
            aliases = person.get("aliases", [])

            self.alias_to_entity[name.lower()] = name
            for alias in aliases:
                self.alias_to_entity[alias.lower()] = name

            # Store person's related entities
            self.entity_to_info[name] = {
                "type": "person",
                "related_entities": entities,
            }

        # Process institutions
        for inst in data.get("institutions", []):
            name = inst["name"]
            aliases = inst.get("aliases", [])

            self.entity_to_info[name] = {
                "type": "institution",
            }
            self.alias_to_entity[name.lower()] = name
            for alias in aliases:
                self.alias_to_entity[alias.lower()] = name

        # Build regex patterns for efficient matching
        self._build_patterns()

    def _build_patterns(self):
        """Build regex patterns for matching."""
        # Sort by length (longer first) to avoid partial matches
        all_aliases = sorted(self.alias_to_entity.keys(), key=len, reverse=True)

        # Escape special regex characters and build pattern
        escaped = [re.escape(alias) for alias in all_aliases if len(alias) >= 2]

        # Build pattern with word boundaries where appropriate
        # For English words, use word boundaries; for Chinese, don't
        patterns = []
        for alias in escaped:
            # Check if contains Chinese characters
            if re.search(r'[\u4e00-\u9fff]', alias):
                patterns.append(alias)
            else:
                patterns.append(rf'\b{alias}\b')

        if patterns:
            self.entity_pattern = re.compile('|'.join(patterns), re.IGNORECASE)
        else:
            self.entity_pattern = None

        # Ticker pattern (uppercase 1-5 letters, may be preceded by $)
        ticker_list = sorted(self.ticker_to_info.keys(), key=len, reverse=True)
        if ticker_list:
            ticker_escaped = [re.escape(t) for t in ticker_list]
            self.ticker_pattern = re.compile(
                r'(?:^|[\s\$\(\|])(' + '|'.join(ticker_escaped) + r')(?:[\s\)\|\:\,\.]|$)',
                re.IGNORECASE
            )
        else:
            self.ticker_pattern = None

    def find_matches(self, text: str) -> Tuple[list, list, list]:
        """
        Find all matching entities in text.

        Returns:
            Tuple of (tickers, entities, industries)
            - tickers: list of matched stock tickers
            - entities: list of matched entity names (including unlisted)
            - industries: list of industries the entities belong to
        """
        tickers = set()
        entities = set()
        industries = set()

        if not text:
            return [], [], []

        text_lower = text.lower()

        # Match tickers directly
        if self.ticker_pattern:
            for match in self.ticker_pattern.finditer(text):
                ticker = match.group(1).upper()
                if ticker in self.ticker_to_info:
                    tickers.add(ticker)
                    info = self.ticker_to_info[ticker]
                    entities.add(info["name"])
                    industries.add(info["industry"])

        # Match entity aliases
        if self.entity_pattern:
            for match in self.entity_pattern.finditer(text_lower):
                matched_text = match.group(0).lower()
                if matched_text in self.alias_to_entity:
                    entity_name = self.alias_to_entity[matched_text]
                    entities.add(entity_name)

                    # Get ticker if exists
                    if matched_text in self.alias_to_ticker:
                        tickers.add(self.alias_to_ticker[matched_text])

                    # Get industry
                    if entity_name in self.entity_to_info:
                        info = self.entity_to_info[entity_name]
                        if "industry" in info:
                            industries.add(info["industry"])

        return list(tickers), list(entities), list(industries)

    def get_entity_info(self, entity_name: str) -> dict:
        """Get information about an entity."""
        return self.entity_to_info.get(entity_name, {})

    def get_ticker_info(self, ticker: str) -> dict:
        """Get information about a ticker."""
        return self.ticker_to_info.get(ticker.upper(), {})

    def get_all_tickers(self) -> list:
        """Get all tracked tickers."""
        return list(self.ticker_to_info.keys())

    def get_all_entities(self) -> list:
        """Get all tracked entity names."""
        return list(self.entity_to_info.keys())

    def get_entities_by_industry(self, industry: str) -> list:
        """Get all entities in a specific industry."""
        return [
            name for name, info in self.entity_to_info.items()
            if info.get("industry") == industry
        ]


def main():
    """Test the entity matcher."""
    matcher = EntityMatcher()

    test_texts = [
        "NVIDIA announced new H100 chips, while OpenAI released GPT-5",
        "台積電宣布與黃仁勳合作開發新製程",
        "Sam Altman discussed AI safety with Anthropic's Dario Amodei",
        "Tesla's Elon Musk announced Optimus robot updates",
        "Eli Lilly's Mounjaro and Novo Nordisk's Ozempic compete in obesity market",
        "Fed's Jerome Powell signals rate cuts, Jamie Dimon warns of risks",
    ]

    for text in test_texts:
        tickers, entities, industries = matcher.find_matches(text)
        print(f"\nText: {text[:60]}...")
        print(f"  Tickers: {tickers}")
        print(f"  Entities: {entities}")
        print(f"  Industries: {industries}")


if __name__ == "__main__":
    main()
