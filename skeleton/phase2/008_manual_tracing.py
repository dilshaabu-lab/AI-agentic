import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from utils.llm_client import LLMClient

def manual_tracing_agent():
    """
    Demonstrates manual tracing (print debugging) best practices.
    """
    client = LLMClient()
    
    query = "Who is the CEO of OpenAI?"
    print(f"--- [TRACE] New Session | Query: '{query}' ---")
    
    max_steps = 3
    for i in range(max_steps):
        print(f"\n[TRACE] Step {i+1}/{max_steps}")
        
        # 1. Thought
        print(f"[TRACE] Generating thought...")
        thought = "I need to search for the current CEO."
        print(f"[TRACE] Thought: {thought}")
        #Here we must call the LLM
        
        # 2. Action
        tool = "web_search"
        tool_input = "OpenAI CEO current"
        print(f"[TRACE] Selected Tool: {tool}")
        print(f"[TRACE] Tool Input: '{tool_input}'")
        
        # 3. Observation
        # Simulation
        observation = "Sam Altman is the CEO of OpenAI."
        print(f"[TRACE] Observation: {observation}")
        
        # 4. Final Answer
        if "CEO" in observation:
            final_answer = "Sam Altman"
            print(f"[TRACE] Final Answer Derived: {final_answer}")
            print(f"\nFinal Result: {final_answer}")
            return
            
    print("[TRACE] Reached max steps without answer.")

if __name__ == "__main__":
    manual_tracing_agent()