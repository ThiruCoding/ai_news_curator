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

        # Step 3: Deduplication (Maximal Marginal Relevance)
        # We ensure the Top 10 are unique from one another
        final_selection = []
        for candidate in sorted_pool:
            if len(final_selection) >= limit:
                break
            
            is_redundant = False
            for selected in final_selection:
                # If titles are > 80% similar, consider them the same news story
                # Note: This is a placeholder for a true embedding comparison
                if candidate['title'][:30] == selected['title'][:30]: 
                    is_redundant = True
                    break
            
            if not is_redundant:
                final_selection.append(candidate)

        return final_selection