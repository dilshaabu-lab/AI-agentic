import sys
import os
import json
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from utils.llm_client import LLMClient

def retry(times=3, delay=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for i in range(times):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Attempt {i+1} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
            raise Exception(f"Failed after {times} attempts")
        return wrapper
    return decorator

def reliable_agent_demo():
    """
    Demonstrate reliability wrapper.
    """
    client = LLMClient()
    print("--- RELIABILITY DEMO ---\n")
    
    def parse_json_response(prompt):
        print("Requesting JSON...")
        # We ask for JSON. Sometimes models return markdown blocks ```json ... ```
        response = client.get_completion(prompt, temperature=0.7) 
        
        # Strip markdown if present
        cleaned = response.replace("```json", "").replace("```", "").strip()
        
        return json.loads(cleaned)
    
    prompt = "Generate a JSON object for thriller shows."
    
    try:
        data = parse_json_response(prompt)
        print(f"Success! Valid JSON Parsed:\n{json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"Final failure: {e}")

if __name__ == "__main__":
    reliable_agent_demo()