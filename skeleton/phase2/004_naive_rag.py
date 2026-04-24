import sys
import os
import glob

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from utils.llm_client import LLMClient

def naive_rag():
    """
    Implement a naive RAG system that simply concatenates all documents into the context window.
    """
    client = LLMClient()
    
    print("--- NAIVE RAG DEMO ---\n")
    
    # 1. Load Documents
    docs_path = os.path.join(os.path.dirname(__file__), "../../data/sample_documents/*.txt")
    files = glob.glob(docs_path)
    documents = []
    for f in files:
        with open(f, 'r') as file:
            documents.append(file.read())
            
    print(f"Loaded {len(documents)} documents.")
    
    # 2. Concatenate
    context = "\n\n".join(documents)
    print(f"Total context length: {len(context)} chars")
    
    # 3. Query
    query = "What is the policy on remote work?"
    print(f"Query: {query}")
    
    prompt = f"""
    Use the following documents to answer the question.
    
    Documents:
    {context}
    
    Question: {query}
    """
    
    response = client.get_completion(prompt)
    print(f"Response:\n{response}\n")
    
    print("-" * 50 + "\n")
    
    # 4. Demonstrate Failure (Context Overflow)
    print("Demonstrating Scalability Failure...")
    # Simulate a massive knowledge base
    massive_doc = "This is irrelevant text. " * 50000 
    documents.append(massive_doc)
    
    context_overflow = "\n\n".join(documents)
    print(f"New context length: {len(context_overflow)} chars")
    
    prompt_overflow = f"""
    Use the following documents to answer the question.
    
    Documents:
    {context_overflow}
    
    Question: {query}
    """
    
    try:
        # This might fail or be truncated depending on the model/client
        # For modern models with 128k context, 50k chars is fine, but this demonstrates the token cost/limit.
        response_overflow = client.get_completion(prompt_overflow)
        print("Response (might be successful if model context is large enough, but notice latency/cost):")
        print(response_overflow[:100] + "...") 
        print("\nANALYSIS: Simply stuffing ALL docs into context is expensive and eventually hits token limits.")
    except Exception as e:
        print(f"API Error as expected: {e}")

if __name__ == "__main__":
    naive_rag()