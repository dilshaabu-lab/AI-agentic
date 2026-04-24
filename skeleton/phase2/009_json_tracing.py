import sys
import os
import json
import utils.llm_client
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from utils.llm_client import LLMClient
from utils.tracer import SimpleTracer # Using the one we implemented in trainer/utils

def json_tracing_demo():
    """
    Demonstrate structured JSON tracing using the SimpleTracer utility.
    """
    # 1. Init Tracer
    trace_path = os.path.join(os.path.dirname(__file__), "../../data/traces/demo_trace.json")
    tracer = SimpleTracer(trace_path)
    tracer.clear() # clear previous run
    
    print(f"Tracing to: {trace_path}")
    
    client = LLMClient()
    query = "Summarize the benefits of apples."
    
    # 2. Log Start
    tracer.log_event("session_start", {"query": query})
    
    # 3. Simulated Steps
    # Step 1: Retrieval
    tracer.log_event("retrieval_start", {"query": query})
    docs = ["Apples are rich in fiber.", "Apples contain Vitamin C."]
    tracer.log_event("retrieval_end", {"documents": docs})
    
    context = "\n".join(docs)
    
    # Step 2: Generation
    prompt = f"Context: {context}\nQuestion: {query}"
    tracer.log_event("llm_call", {"prompt": prompt, "model": "gpt-3.5-turbo"})
    
    response = client.get_completion(prompt)
    tracer.log_event("llm_response", {"text": response})
    
    print("Response generated.")
    
    # 4. Save
    tracer.save()
    print("Trace saved.")
    
    # 5. Verify
    with open(trace_path, 'r') as f:
        data = json.load(f)
        print(f"Trace contains {len(data)} events.")

if __name__ == "__main__":
    json_tracing_demo()