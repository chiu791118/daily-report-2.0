"""
Markdown Output Module
Generates markdown reports for market digest.
"""
from datetime import datetime
from pathlib import Path
import pytz

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config.settings import REPORTS_DIR, TIMEZONE

# Default tomorrow focus content (defined outside f-string for Python 3.9 compatibility)
DEFAULT_TOMORROW_FOCUS = """- 持續關注財報季動態
- 留意聯準會官員發言
- 觀察技術面支撐壓力位"""


class MarkdownReportGenerator:
    """Generates markdown reports."""

    def __init__(self):
        self.tz = pytz.timezone(TIMEZONE)

    def generate_pre_market_report(
        self,
        news_analysis: dict,
        market_overview: str,
        watchlist_summary: str,
        regulatory_updates: str = "",
        global_snapshot: str = "",
        categorized_news: dict = None,
        hashtags: list = None,
    ) -> str:
        """Generate pre-market (21:00 Taiwan time) report."""
        now = datetime.now(self.tz)
        date_str = now.strftime("%Y-%m-%d")
        weekday_map = {0: "週一", 1: "週二", 2: "週三", 3: "週四", 4: "週五", 5: "週六", 6: "週日"}
        weekday = weekday_map[now.weekday()]

        # Build global snapshot section (NEW - quick overview)
        snapshot_section = ""
        if global_snapshot:
            snapshot_section = f"""
## ⚡ 全球快覽

{global_snapshot}

---
"""

        # Build categorized news section (NEW - structured news breakdown)
        categorized_section = ""
        if categorized_news:
            macro_news = categorized_news.get('macro', '')
            tech_news = categorized_news.get('tech', '')
            industry_news = categorized_news.get('industry', '')

            categorized_section = f"""
### 🌍 宏觀與政策 (Macro & Policy)

{macro_news if macro_news else "今日無重大宏觀政策新聞。"}

### ⚡ 科技與地緣 (Tech & Geopolitics)

{tech_news if tech_news else "今日無重大科技地緣新聞。"}

### 🏢 巨頭與產業 (Market Movers)

{industry_news if industry_news else "今日無重大產業新聞。"}

---
"""

        # Build regulatory section if available
        regulatory_section = ""
        if regulatory_updates:
            regulatory_section = f"""
## 📋 監管與公告動態

{regulatory_updates}

---
"""

        # Build hashtag section (NEW - theme tags)
        hashtag_section = ""
        if hashtags:
            hashtag_str = " ".join([f"#{tag}" for tag in hashtags[:6]])
            hashtag_section = f"\n{hashtag_str}\n"

        report = f"""# 📈 每日市場摘要 - 開盤前報告
**🔥 全球財富早報 🔥**

**📅 {date_str} | {weekday}**
**⏰ 生成時間:** {now.strftime("%H:%M")} (台北時間)

---

{snapshot_section}## 🌍 市場概況

{market_overview}

---

## 📰 新聞摘要

**今日新聞數量:** {news_analysis.get('news_count', 0)} 則
**市場情緒:** {self._sentiment_emoji(news_analysis.get('sentiment', 'neutral'))} {news_analysis.get('sentiment', 'neutral').upper()}

{news_analysis.get('analysis', '無新聞分析')}

---

{categorized_section}{regulatory_section}## 📊 觀察清單

{watchlist_summary}

---
{hashtag_section}
*Daily Market Digest | {date_str}*
"""
        return report

    def generate_post_market_report(
        self,
        trading_date: str,
        market_review: str,
        watchlist_summary: str,
        after_hours_news: str = "",
        tomorrow_outlook: str = "",
        regulatory_updates: str = "",
    ) -> str:
        """Generate post-market (05:00 Taiwan time) report."""
        now = datetime.now(self.tz)

        # Build regulatory section if available
        regulatory_section = ""
        if regulatory_updates:
            regulatory_section = f"""
---

## 📋 監管與公告動態

{regulatory_updates}
"""

        report = f"""# 📉 每日市場摘要 - 收盤後報告

**美股交易日:** {trading_date}
**生成時間:** {now.strftime("%Y-%m-%d %H:%M")} (台北時間)
**報告類型:** 美股收盤後覆盤

---

## 📊 今日交易回顧

{market_review}

---

## 📈 觀察清單表現

{watchlist_summary}

---

## 📰 盤後重要消息

{after_hours_news if after_hours_news else "今日盤後無重大消息。"}
{regulatory_section}
---

## 🔮 明日展望

{tomorrow_outlook if tomorrow_outlook else "明日無特別需要關注的事件。"}

---

*Daily Market Digest | {trading_date}*
"""
        return report

    def save_report_to_date(self, content: str, report_type: str, date_str: str) -> Path:
        """Save report to a specific date folder."""
        # Create date directory
        date_dir = REPORTS_DIR / date_str
        date_dir.mkdir(parents=True, exist_ok=True)

        # Determine filename
        filename = f"{report_type}.md"
        filepath = date_dir / filename

        # Write file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"Report saved to: {filepath}")
        return filepath

    def _sentiment_emoji(self, sentiment: str) -> str:
        """Get emoji for sentiment."""
        emoji_map = {
            "bullish": "🟢",
            "bearish": "🔴",
            "neutral": "🟡",
            "unknown": "⚪",
        }
        return emoji_map.get(sentiment.lower(), "⚪")

    def save_report(self, content: str, report_type: str) -> Path:
        """Save report to file."""
        now = datetime.now(self.tz)
        date_str = now.strftime("%Y-%m-%d")

        # Create date directory
        date_dir = REPORTS_DIR / date_str
        date_dir.mkdir(parents=True, exist_ok=True)

        # Determine filename
        filename = f"{report_type}.md"
        filepath = date_dir / filename

        # Write file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"Report saved to: {filepath}")
        return filepath

    def generate_simple_report(
        self,
        title: str,
        sections: dict[str, str],
    ) -> str:
        """Generate a simple report with custom sections."""
        now = datetime.now(self.tz)

        lines = [
            f"# {title}",
            "",
            f"**生成時間:** {now.strftime('%Y-%m-%d %H:%M')} (台北時間)",
            "",
            "---",
            "",
        ]

        for section_title, content in sections.items():
            lines.extend([
                f"## {section_title}",
                "",
                content,
                "",
                "---",
                "",
            ])

        lines.append("*生成工具: Daily Market Digest*")

        return "\n".join(lines)

    def generate_saturday_report(
        self,
        week_market_summary: str,
        industry_analysis: str,
        watchlist_summary: str,
    ) -> str:
        """
        Generate Saturday industry cognition report (9am Taiwan time).

        This report follows the 8-section structure:
        0. This Week's Thesis
        1. Executive Brief
        2. Paradigm Shift Radar
        3. Industry Cognition Map Updates
        4. Technology Frontier
        5. Company Moves & Strategic Implications
        6. IP / Regulation / Talent Signals
        7. Key Metrics & Benchmarks
        8. Watchlist & Scenarios
        """
        now = datetime.now(self.tz)
        date_str = now.strftime("%Y-%m-%d")
        week_num = now.isocalendar()[1]

        report = f"""# 每週產業認知更新報告

**週次:** {now.year} W{week_num}
**日期:** {date_str}
**生成時間:** {now.strftime("%Y-%m-%d %H:%M")} (台北時間)

> 本報告為頂尖管理顧問與投資顧問設計，聚焦「認知更新」而非「資訊重述」。
> 明確區分【事實】【推論】【待驗證假說】。

---

## 📈 本週市場概覽

{week_market_summary}

---

{industry_analysis}

---

## 📊 觀察清單概覽

{watchlist_summary}

---

**免責聲明：** 本報告僅供研究參考，不構成投資建議。投資決策請諮詢專業顧問。

*Weekly Industry Cognition Report | {date_str}*
"""
        return report

    def generate_sunday_report(
        self,
        weekly_recap: str,
        weekly_outlook: str,
        watchlist_summary: str,
    ) -> str:
        """Generate Sunday weekly outlook report (6pm Taiwan time)."""
        now = datetime.now(self.tz)
        date_str = now.strftime("%Y-%m-%d")

        report = f"""# 🔮 週末展望報告 - 下週市場展望

**日期:** {date_str}
**生成時間:** {now.strftime("%Y-%m-%d %H:%M")} (台北時間)
**報告類型:** 週日下週展望

---

## 📅 本週市場總結

{weekly_recap}

---

## 🔭 下週展望與策略

{weekly_outlook}

---

## 📊 觀察清單狀態

{watchlist_summary}

---

*Daily Market Digest - 週末展望報告 | {date_str}*
"""
        return report

    def generate_pre_market_report_v2(
        self,
        layered_result,
        regulatory_updates: str = "",
        hashtags: list = None,
    ) -> str:
        """
        Generate pre-market report V2 with 6-layer structure.

        Structure:
        - Layer 0: Executive Snapshot (5 fixed blocks)
        - Layer 1: What Changed Today (Macro/Industry/Company)
        - Layer 2: Structural Interpretation (max 3 inferences + Quality Gate)
        - Layer 3: Asset Allocation Watchlist (🟢🟡🔴)
        - Layer 4: Equity Signals (4A Watchlist + 4B New Discoveries)
        - Layer 5: Decision Log (3 lines)
        - Market Data Appendix
        - News Summary (paragraph style)

        Args:
            layered_result: LayeredReportResult from PreMarketAnalyzer
            regulatory_updates: Formatted SEC/FDA updates
            hashtags: List of hashtag strings

        Returns:
            Complete markdown report
        """
        now = datetime.now(self.tz)
        date_str = now.strftime("%Y-%m-%d")
        weekday_map = {0: "週一", 1: "週二", 2: "週三", 3: "週四", 4: "週五", 5: "週六", 6: "週日"}
        weekday = weekday_map[now.weekday()]

        # Build regulatory section if available
        regulatory_section = ""
        if regulatory_updates:
            regulatory_section = f"""
---

## 📋 監管與公告動態

{regulatory_updates}
"""

        # Build hashtag section
        hashtag_section = ""
        if hashtags:
            hashtag_str = " ".join([f"#{tag}" for tag in hashtags[:8]])
            hashtag_section = f"\n{hashtag_str}\n"

        report = f"""# 📈 每日市場摘要 - 開盤前報告 V2
**🔥 全球財富早報 🔥**

**📅 {date_str} | {weekday}**
**⏰ 生成時間:** {now.strftime("%H:%M")} (台北時間)

---

{layered_result.layer_0}

---

{layered_result.layer_1}

---

{layered_result.layer_2}

---

{layered_result.layer_3}

---

{layered_result.layer_4}

---

{layered_result.layer_5}
{regulatory_section}
---

{layered_result.market_appendix}

---

## 📰 今日新聞摘要

{layered_result.news_summary}

---
{hashtag_section}
*Daily Market Digest V2 | {date_str}*
"""
        return report
    def generate_pre_market_report_v3(
        self,
        sections: dict,
        market_overview,
        economic_rows: list,
        earnings_rows: list,
        news_digest: list,
        regulatory_updates: str = "",
        economic_note: str = "",
        earnings_note: str = "",
    ) -> str:
        """Generate pre-market report V3 with a focused briefing structure."""
        tz_et = pytz.timezone("US/Eastern")
        now_tw = datetime.now(self.tz)
        now_et = now_tw.astimezone(tz_et)

        date_tw = now_tw.strftime("%Y-%m-%d")
        date_et = now_et.strftime("%Y-%m-%d")

        # Economic calendar section
        economic_section = self._format_economic_calendar(economic_rows, economic_note)

        # Earnings calendar section
        earnings_section = self._format_earnings_calendar(earnings_rows, earnings_note)

        # Market snapshot
        market_snapshot = self._format_market_snapshot(market_overview)

        # Sections from analyzer
        key_takeaways = self._format_numbered(sections.get("key_takeaways", []), 5)
        geo_events = self._format_bullets(sections.get("geo_events", []))
        market_state = self._format_bullets(sections.get("market_state", []))
        watchlist_focus = self._format_watchlist_table(sections.get("watchlist_focus", []))
        event_driven = self._format_event_driven_table(sections.get("event_driven", []))
        monitor_list = self._format_bullets(sections.get("monitor_list", []))

        # News digest
        news_digest_section = self._format_news_digest(news_digest)

        regulatory_section = ""
        if regulatory_updates:
            regulatory_section = f"""

---

## 📋 監管與公告動態

{regulatory_updates}
"""

        report = f"""# 📈 每日市場摘要 - 開盤前報告 V3

**📅 {date_et} (ET) / {date_tw} (台北)**
**⏰ 生成時間:** {now_et.strftime('%H:%M')} ET / {now_tw.strftime('%H:%M')} 台北

---

## A. 今日盤前 5 條關鍵結論

{key_takeaways}

---

## B. 今日經濟日程（ET / 台北）

{economic_section}

---

## C. 重要財報日程（ET / 台北）

{earnings_section}

---

## D. 國際與地區重點事件 → 對美股的潛在牽動

{geo_events}

---

## E. 市場狀態與短期風險圖

{market_snapshot}
{market_state}

---

## F. 今日必看（你的觀察清單）

{watchlist_focus}

---

## G. 事件驅動清單外公司

{event_driven}

---

## H. 開盤後監測清單

{monitor_list}

---

## 參考新聞（Top）

{news_digest_section}
{regulatory_section}

---
*Daily Market Digest V3 | {date_tw}*
"""
        return report

    def _format_economic_calendar(self, rows: list, note: str = "") -> str:
        if not rows:
            return note or "今日無重大經濟數據公布。"

        lines = [
            "| 時間(ET) | 時間(台北) | 國家 | 指標 | 重要性 | 預期 | 前值 |",
            "|---|---|---|---|---|---|---|",
        ]
        for row in rows[:15]:
            importance = row.get("importance")
            importance_str = "" if importance is None else ("★" * int(importance))
            lines.append(
                f"| {row.get('time_et','')} | {row.get('time_taipei','')} | {row.get('country','')} | "
                f"{row.get('event','')} | {importance_str} | {row.get('forecast','—') or '—'} | "
                f"{row.get('previous','—') or '—'} |"
            )
        return "
".join(lines)

    def _format_earnings_calendar(self, rows: list, note: str = "") -> str:
        if not rows:
            return note or "今日無重大財報公布。"

        lines = [
            "| 代碼 | 公司 | 時間(ET) | 時間(台北) | EPS 預期 | 營收預期 |",
            "|---|---|---|---|---|---|",
        ]
        for row in rows[:20]:
            lines.append(
                f"| {row.get('symbol','')} | {row.get('company','')} | {row.get('time_et','')} | "
                f"{row.get('time_taipei','')} | {row.get('eps_estimate','—') or '—'} | "
                f"{row.get('revenue_estimate','—') or '—'} |"
            )
        return "
".join(lines)

    def _format_market_snapshot(self, overview) -> str:
        lines = []
        if overview.sp500:
            lines.append(f"- S&P 500: {overview.sp500.current_price:,.2f} ({overview.sp500.change_percent:+.2f}%)")
        if overview.nasdaq:
            lines.append(f"- NASDAQ: {overview.nasdaq.current_price:,.2f} ({overview.nasdaq.change_percent:+.2f}%)")
        if overview.dow:
            lines.append(f"- Dow Jones: {overview.dow.current_price:,.2f} ({overview.dow.change_percent:+.2f}%)")
        if overview.vix is not None:
            lines.append(f"- VIX: {overview.vix:.2f} ({overview.vix_change:+.2f}%)")
        if overview.market_sentiment:
            lines.append(f"- 市場情緒: {overview.market_sentiment}")
        if not lines:
            return "- 市場數據不足
"
        return "
".join(lines) + "
"

    def _format_numbered(self, items: list, expected: int) -> str:
        if not items:
            return "無資料"
        lines = []
        for i, item in enumerate(items[:expected], 1):
            lines.append(f"{i}. {item}")
        return "
".join(lines)

    def _format_bullets(self, items: list) -> str:
        if not items:
            return "無資料"
        return "
".join([f"- {i}" for i in items])

    def _format_watchlist_table(self, items: list) -> str:
        if not items:
            return "今日無需特別關注的觀察清單標的。"
        lines = [
            "| 代碼 | 觸發原因 | 今日觀察點 |",
            "|---|---|---|",
        ]
        for item in items[:8]:
            lines.append(
                f"| {item.get('symbol','')} | {item.get('why','')} | {item.get('watch','')} |"
            )
        return "
".join(lines)

    def _format_event_driven_table(self, items: list) -> str:
        if not items:
            return "今日無清單外事件驅動標的。"
        lines = [
            "| 代碼 | 事件 | 潛在影響 |",
            "|---|---|---|",
        ]
        for item in items[:8]:
            lines.append(
                f"| {item.get('symbol','')} | {item.get('why','')} | {item.get('impact','')} |"
            )
        return "
".join(lines)

    def _format_news_digest(self, news_items: list) -> str:
        if not news_items:
            return "無新聞資料。"
        lines = []
        for item in news_items[:12]:
            time_part = ""
            if item.get("time_et") and item.get("time_taipei"):
                time_part = f" ({item.get('time_et')} ET / {item.get('time_taipei')} 台北)"
            lines.append(f"- [{item.get('source','')}] {item.get('title','')}{time_part}")
        return "
".join(lines)



def main():
    """Test the markdown generator."""
    generator = MarkdownReportGenerator()

    # Test simple report
    report = generator.generate_simple_report(
        title="測試報告",
        sections={
            "📰 新聞摘要": "今日市場波動較大...",
            "📊 市場數據": "S&P 500: 5,000.00 (+0.5%)",
            "📝 備註": "這是測試內容",
        },
    )

    print(report)

    # Save test report
    filepath = generator.save_report(report, "test-report")
    print(f"\nSaved to: {filepath}")


if __name__ == "__main__":
    main()
