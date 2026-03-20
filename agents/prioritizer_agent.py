import config
from utils.embeddings import calculate_similarity

class Prioritizer:
    def __init__(self):
        self.weights = config.SOURCE_WEIGHTS
        self.default_weight = self.weights.get("DEFAULT", 1.0)

    def get_top_priority(self, articles, limit=10):
        """
        Ranks articles based on authority-weighted relevance 
        and removes redundant coverage.
        """
        if not articles:
            return []

        # Step 1: Apply Authority Weights
        for art in articles:
            source_weight = self.weights.get(art['source'], self.default_weight)
            # Final Score = Curator Relevance * Source Authority
            art['priority_score'] = round(art['relevance_score'] * source_weight, 4)

        # Step 2: Global Sort by Priority
        sorted_pool = sorted(articles, key=lambda x: x['priority_score'], reverse=True)

        # Step 3: Deduplication + Source Diversity Cap
        # We ensure the Top 10 are unique and no single source dominates
        final_selection = []
        source_counts = {}

        for candidate in sorted_pool:
            if len(final_selection) >= limit:
                break

            # Diversity cap — max 2 articles per source
            source = candidate['source']
            if source_counts.get(source, 0) >= 2:
                continue

            # Deduplication — skip if title is too similar to an already selected article
            is_redundant = False
            for selected in final_selection:
                if candidate['title'][:30] == selected['title'][:30]:
                    is_redundant = True
                    break

            if not is_redundant:
                final_selection.append(candidate)
                source_counts[source] = source_counts.get(source, 0) + 1

        return final_selection