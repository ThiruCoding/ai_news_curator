from utils.embeddings import get_embeddings, calculate_similarity

class NewsCurator:
    def __init__(self, interest_query, negative_query):
        # Anchor vectors initialized once to save compute cycles
        self.interest_vector = get_embeddings([interest_query])[0]
        self.negative_vector = get_embeddings([negative_query])[0]

    def filter_articles(self, articles, source_name, threshold=0.22):
        """
        Processes raw articles and returns a list of dictionaries 
        containing metadata for the Orchestrator and Prioritizer.
        """
        curated_list = []
        for article in articles:
            article_vector = get_embeddings([article['title']])[0]
            
            # Distance from focus
            pos_score = calculate_similarity(self.interest_vector, article_vector)
            # Distance from noise (Hype/PR/Tutorials)
            neg_score = calculate_similarity(self.negative_vector, article_vector)
            
            # Contrastive Filtering Logic
            if pos_score >= threshold and pos_score > neg_score:
                # We augment the article dictionary with technical metadata
                # This package is what the Orchestrator will pass to the Prioritizer
                curated_item = {
                    'title': article['title'],
                    'link': article['link'],
                    'summary': article.get('summary', ''),
                    'source': source_name,
                    'relevance_score': round(pos_score, 4),
                    'noise_score': round(neg_score, 4),
                    'priority_rank': 0  # Placeholder for the Prioritizer Agent
                }
                curated_list.append(curated_item)
        
        return curated_list