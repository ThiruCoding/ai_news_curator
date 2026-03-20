from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Initialize the model (This uses a lightweight but powerful transformer)
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embeddings(text_list):
    """
    Converts a list of strings into numerical vectors (embeddings).
    """
    return model.encode(text_list)

def calculate_similarity(vector_a, vector_b):
    """
    Uses cosine similarity to determine how related two text vectors are.
    """
    return cosine_similarity(vector_a.reshape(1, -1), vector_b.reshape(1, -1))[0][0]