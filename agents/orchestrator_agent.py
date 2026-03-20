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
        # Initialize the Agent Team
        self.curator = NewsCurator(config.USER_INTEREST, config.USER_INTEREST_BUSINESS, config.NEGATIVE_FILTER)
        self.prioritizer = Prioritizer()
        self.analyst = AnalystAgent()
        self.display_agent = DisplayAgent()

    def run_pipeline(self):
        print("\n" + "🚀" * 20)
        print("  AI NEWS PIPELINE STARTING  ")
        print("🚀" * 20 + "\n")

        all_curated_articles = []

        # Phase 1: Ingestion & Curator Agent (Semantic Filter)
        for name, url in config.RSS_FEEDS.items():
            status, raw_news = fetch_rss_feed(url)
            fetched = len(raw_news) if raw_news else 0
            if not raw_news:
                print(f"[FETCHING] {name}: 0 articles fetched")
                continue

            refined_batch = self.curator.filter_articles(raw_news, source_name=name)
            print(f"[FETCHING] {name}: {fetched} fetched → {len(refined_batch)} passed curation")
            all_curated_articles.extend(refined_batch)

        # Phase 2: Prioritizer Agent (Ranking)
        # We condense the volume to the Top 10 to save Local CPU/Gemini Quota
        top_10 = self.prioritizer.get_top_priority(all_curated_articles, limit=10)

        # TEMPORARY DEBUG — remove before final run
        print("\n[DEBUG] Top 10 articles selected for synthesis:")
        for i, art in enumerate(top_10, 1):
            print(f"  {i}. [{art['source']}] {art['title'][:60]} (score: {art['priority_score']})")
        

        if not top_10:
            print("\n[!] No relevant technical signals found in this cycle.")
            return

        # Phase 3: Analyst Agent (Narrative Synthesis)
        # This is the "heavy lifting" phase
        print(f"\n[ANALYSIS] Deep-processing {len(top_10)} priority articles...")
        final_reports = self.analyst.process_top_articles(top_10)

        # Phase 4: Display Agent (The Publisher)
        # The agent decides the visual theme and saves to /newsreports
        print("\n[DISPLAY] Generating agentic dashboard...")
        filename = self.display_agent.generate_html_report(final_reports)

        # Final Action: Open the report automatically
        self.auto_open_report(filename)

    def auto_open_report(self, filename):
        """Automatically launches the browser to view the results."""
        # We look for the file specifically in the newsreports folder
        report_path = os.path.abspath(os.path.join("newsreports", filename))
        if os.path.exists(report_path):
            print(f"✅ Pipeline Complete. Opening: {report_path}")
            webbrowser.open(f"file://{report_path}")
        else:
            print(f"⚠️ Report generated but could not find path: {report_path}")

if __name__ == "__main__":
    Orchestrator().run_pipeline()