#(RAG for referencing old posts)

import os
import chromadb
from chromadb.utils import embedding_functions

client = chromadb.Client()

collection = client.create_collection(
    name="old_posts",
    embedding_function=embedding_functions.OpenAIEmbeddingFunction(model_name="text-embedding-3-small")
)

def add_old_post(title, url, content):
    collection.add(documents=[content], metadatas=[{"title": title, "url": url}], ids=[url])

def query_similar_posts(text, n=3):
    return collection.query(query_texts=[text], n_results=n)
