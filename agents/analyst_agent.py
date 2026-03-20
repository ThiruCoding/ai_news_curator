import trafilatura
from utils.llm_client import get_llm_summary

class AnalystAgent:
    def __init__(self):
        # The agent relies on the llm_client for processing
        pass

    def process_top_articles(self, articles):
        """
        Coordinates the extraction and synthesis for the top 10 articles.
        Returns a list of dictionaries with the finalized narrative summaries.
        """
        final_reports = []

        print(f"\n[ANALYST] Initializing deep-scan for {len(articles)} priority articles.")

        for art in articles:
            print(f"  -> Synthesizing: {art['title'][:50]}...")
            
            # 1. High-Precision Extraction
            # We fetch the full page content to give the LLM maximum context
            downloaded = trafilatura.fetch_url(art['link'])
            full_text = trafilatura.extract(downloaded, include_comments=False)
            
            # Fallback logic: if the page is blocked, use the RSS snippet
            context_material = full_text if (full_text and len(full_text) > 400) else art.get('summary', '')

            # 2. Synthesis Phase
            # We use the prompt structure we discussed for 5-10 line paragraphs
            narrative = self._generate_narrative(context_material)
            
            # 3. Data Packaging
            # We maintain the metadata so the Display Agent has everything it needs
            final_reports.append({
                'title': art['title'],
                'source': art['source'],
                'link': art['link'],
                'summary': narrative,
                'priority_score': art['priority_score']
            })

        return final_reports

    def _generate_narrative(self, text):
        """
        Internal method to construct the grounded prompt.
        """
        prompt = f"""
        You are an AI Industry Analyst. 
        TASK: Write a cohesive narrative summary of the provided news article.
        
        OUTPUT FORMAT: 
        - A single, well-structured paragraph.
        - Maximum 5 lines.
        
        STRICT GROUNDING RULES:
        1. NO HALLUCINATION: Only include information present in the source text.
        2. COHESION: Connect the event to its context and implications smoothly.
        3. START DIRECTLY: Do not use intros like "This article is about."
        4. UNIVERSAL COVERAGE: Summarize the core driver (Technical, Financial, or Regulatory).

        ARTICLE CONTENT:
        {text[:7000]} # Gemini's large window handles this easily
        """
        return get_llm_summary(prompt)