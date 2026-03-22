import config
import os
import webbrowser
from utils.scraper import fetch_rss_feed
from agents.curator_agent import NewsCurator
from agents.prioritizer_agent import Prioritizer
from agents.analyst_agent import AnalystAgent
from agents.display_agent import DisplayAgent

class Orchestrator:
    def __init__(self):
        self.display_agent = DisplayAgent()

        # Only initialise heavy agents when not in dev mode
        if not config.DEV_MODE:
            self.curator     = NewsCurator(config.USER_INTEREST, config.USER_INTEREST_BUSINESS, config.NEGATIVE_FILTER)
            self.prioritizer = Prioritizer()
            self.analyst     = AnalystAgent()

    def run_pipeline(self):
        print("\n" + "🚀" * 20)
        print("  AI NEWS PIPELINE STARTING  ")
        print("🚀" * 20 + "\n")

        if config.DEV_MODE:
            self._run_dev()
        else:
            self._run_production()

    # ─────────────────────────────────────────────────────────────────────
    # DEV MODE — instant mock data, no fetching or API calls
    # ─────────────────────────────────────────────────────────────────────
    def _run_dev(self):
        print("⚡ DEV MODE ACTIVE — skipping fetch, embed, and Gemini calls\n")
        from utils.mock_data import get_mock_pipeline_data
        final_reports, pipeline_data = get_mock_pipeline_data()

        print("[DEV] Generating insights report...")
        insights_filename = self.display_agent.generate_insights_report(pipeline_data)

        print("[DEV] Generating main report...")
        filename = self.display_agent.generate_html_report(final_reports, insights_filename=insights_filename)

        print(f"\n✅ DEV pipeline complete in ~2s.")
        self.auto_open_report(filename)

    # ─────────────────────────────────────────────────────────────────────
    # PRODUCTION — full pipeline
    # ─────────────────────────────────────────────────────────────────────
    def _run_production(self):
        all_curated_articles = []
        feed_stats = {name: {'fetched': 0, 'curated': 0} for name in config.RSS_FEEDS.keys()}
        all_rejected_articles = []

        # Phase 1: Ingestion & Curator Agent (Semantic Filter)
        for name, url in config.RSS_FEEDS.items():
            status, raw_news = fetch_rss_feed(url)
            fetched = len(raw_news) if raw_news else 0
            feed_stats[name]['fetched'] = fetched

            if not raw_news:
                print(f"[FETCHING] {name}: 0 articles fetched")
                continue

            refined_batch = self.curator.filter_articles(raw_news, source_name=name)
            feed_stats[name]['curated'] = len(refined_batch)
            print(f"[FETCHING] {name}: {fetched} fetched → {len(refined_batch)} passed curation")
            all_curated_articles.extend(refined_batch)

            # Collect rejected articles for insights page
            curated_titles = {a['title'] for a in refined_batch}
            scored_batch   = self.curator.score_articles(raw_news, source_name=name)
            for a in scored_batch:
                if a['title'] not in curated_titles:
                    all_rejected_articles.append(a)

        # Phase 2: Prioritizer Agent (Ranking)
        top_10 = self.prioritizer.get_top_priority(all_curated_articles, limit=10)

        print("\n[DEBUG] Top 10 articles selected for synthesis:")
        for i, art in enumerate(top_10, 1):
            print(f"  {i}. [{art['source']}] {art['title'][:60]} (score: {art['priority_score']})")

        if not top_10:
            print("\n[!] No relevant technical signals found in this cycle.")
            return

        # Phase 3: Analyst Agent (Narrative Synthesis)
        print(f"\n[ANALYSIS] Deep-processing {len(top_10)} priority articles...")
        final_reports = self.analyst.process_top_articles(top_10)

        # Phase 4: Display Agent — insights page
        print("\n[DISPLAY] Generating insights report...")
        pipeline_data = {
            'feed_stats':    feed_stats,
            'all_curated':   all_curated_articles,
            'top_10':        top_10,
            'all_rejected':  all_rejected_articles,
            'final_reports': final_reports,
        }
        insights_filename = self.display_agent.generate_insights_report(pipeline_data)

        # Phase 5: Display Agent — main report
        print("\n[DISPLAY] Generating agentic dashboard...")
        filename = self.display_agent.generate_html_report(final_reports, insights_filename=insights_filename)

        self.auto_open_report(filename)

    def auto_open_report(self, filename):
        """Automatically launches the browser to view the results."""
        report_path = os.path.abspath(os.path.join("newsreports", filename))
        if os.path.exists(report_path):
            print(f"✅ Pipeline Complete. Opening: {report_path}")
            webbrowser.open(f"file://{report_path}")
        else:
            print(f"⚠️ Report generated but could not find path: {report_path}")

if __name__ == "__main__":
    Orchestrator().run_pipeline()