import sys
import os
import chromadb
import uuid

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from utils.llm_client import LLMClient

def semantic_search_demo():
    """
    Implement semantic search using embeddings and a vector database.
    """
    client = LLMClient()
    
    print("--- SEMANTIC SEARCH DEMO ---\n")
    
    # 1. Define Documents
    documents = [
        "The quick brown fox jumps over the lazy dog.",
        "A fast auburn vulpine leaps over a slothful canine.",
        "Python is a high-level programming language.",
        "Pythons represent a family of non-venomous snakes found in Africa/Asia.",
        "The weather in London is often rainy.",
        "NebulaScale policies on remote work are flexible."
    ]
    
    print("Documents:")
    for i, doc in enumerate(documents):
        print(f"  {i}: {doc}")
    print("\n")
    
    # 2. Initialize Vector DB
    print("Initializing ChromaDB...")
    chroma_client = chromadb.Client()
    
    # Delete collection if exists to start fresh
    try:
        chroma_client.delete_collection("demo_collection")
    except:
        pass
        
    collection = chroma_client.create_collection(name="demo_collection")
    
    # 3. Generate Embeddings & Index
    print("Generating embeddings...")
    ids = [str(uuid.uuid4()) for _ in documents]
    metadatas = [{"source": "example"} for _ in documents]
    
    # We use our client to get embeddings to show the "Manual" way
    # In production, Chroma can use an embedding function automatically
    embeddings = [client.get_embedding(doc) for doc in documents]
    
    collection.add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )
    print(f"Indexed {len(documents)} documents.\n")
    
    # 4. Query
    queries = [
        "animal jumping",
        "coding language",
        "reptiles",
        "remote work policy"
    ]
    
    for q in queries:
        print(f"Query: '{q}'")
        q_embedding = client.get_embedding(q)
        
        results = collection.query(
            query_embeddings=[q_embedding],
            n_results=1
        )
        
        # Results structure: {'ids': [['...']], 'distances': [[...]], 'documents': [['...']], ...}
        best_match = results['documents'][0][0]
        distance = results['distances'][0][0] # Lower is better in some metrics, but Chroma uses... wait, default is L2.
        
        print(f"  --> Top Match: '{best_match}'")
        print(f"  --> Distance: {distance:.4f}\n")

if __name__ == "__main__":
    semantic_search_demo()