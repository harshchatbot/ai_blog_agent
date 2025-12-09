#(RAG for referencing old posts)

import chromadb
from chromadb.utils import embedding_functions
from config.settings import settings

client = chromadb.Client()

embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
    api_key=settings.OPENAI_API_KEY,  
    model_name="text-embedding-3-small"
)

collection = client.create_collection(
    name="old_posts",
    embedding_function=embedding_fn
)


def add_old_post(title, url, content):
    collection.add(documents=[content], metadatas=[{"title": title, "url": url}], ids=[url])

def query_similar_posts(text, n=3):
    return collection.query(query_texts=[text], n_results=n)
