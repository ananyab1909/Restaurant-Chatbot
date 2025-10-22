import yaml
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# ------------------------
# Load FAQ data
# ------------------------
with open("faq_data.yaml", "r") as f:
    faq_data = yaml.safe_load(f)['faq_data']

# ------------------------
# Load embeddings model
# ------------------------
model = SentenceTransformer('all-MiniLM-L6-v2')

# ------------------------
# Embed FAQ questions locally
# ------------------------
faq_embeddings = []

def load_faq_embeddings():
    """Embed all FAQ questions locally."""
    global faq_embeddings
    faq_embeddings = [(faq, model.encode(faq['question'])) for faq in faq_data]
    print("FAQ embeddings loaded locally ✅")

# ------------------------
# Query FAQ
# ------------------------
def query_faq(user_query, top_k=3, threshold=0.5):
    """Return top FAQ matches for a user query."""
    if not faq_embeddings:
        load_faq_embeddings()

    query_emb = model.encode(user_query)
    sims = [(faq, cosine_similarity([query_emb], [emb])[0][0]) for faq, emb in faq_embeddings]
    sims.sort(key=lambda x: x[1], reverse=True)

    results = [faq for faq, score in sims[:top_k] if score >= threshold]
    return results
