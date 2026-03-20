import config
from utils.embeddings import get_embeddings, calculate_similarity

class NewsCurator:
    def __init__(self, interest_query, business_query, negative_query):
        # Anchor vectors initialized once to save compute cycles
        self.interest_vector = get_embeddings([interest_query])[0]
        self.business_vector = get_embeddings([business_query])[0]
        self.negative_vector = get_embeddings([negative_query])[0]

    def filter_articles(self, articles, source_name, threshold=0.22):
        """
        Processes raw articles and returns a list of dictionaries
        containing metadata for the Orchestrator and Prioritizer.
        An article passes if it scores above threshold on either the
        technical or business interest vector, and scores higher than
        the negative vector on whichever dimension it matched.
        """
        curated_list = []
        for article in articles:
            article_vector = get_embeddings([article['title']])[0]

            # Score against all three vectors
            tech_score = calculate_similarity(self.interest_vector, article_vector)
            biz_score  = calculate_similarity(self.business_vector, article_vector)
            neg_score  = calculate_similarity(self.negative_vector, article_vector)

            # Pass if strong on technical signal
            tech_match = tech_score >= threshold and tech_score > neg_score
            # Pass if strong on business signal
            biz_match  = biz_score >= threshold and biz_score > neg_score

            if tech_match or biz_match:
                # Use the higher of the two positive scores as the relevance score
                relevance_score = round(max(tech_score, biz_score), 4)

                curated_item = {
                    'title': article['title'],
                    'link': article['link'],
                    'summary': article.get('summary', ''),
                    'source': source_name,
                    'relevance_score': relevance_score,
                    'noise_score': round(neg_score, 4),
                    'priority_rank': 0  # Placeholder for the Prioritizer Agent
                }
                curated_list.append(curated_item)

        return curated_list