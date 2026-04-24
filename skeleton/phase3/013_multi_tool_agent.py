import sys
import os
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from utils.llm_client import LLMClient
from utils.tools import calculator, web_search, send_email

def multi_tool_agent():
    """
    Demonstrate a multi-step agent flow.
    """
    client = LLMClient()
    
    print("--- MULTI-TOOL AGENT DEMO ---\n")
    
    task = "Check weather can multilingual can be applied using NLP then mail to dilsha@gmail.com"
    print(f"Task: {task}\n")
    
    prompt = f"""
    You are an AI assistant.
    Goal: {task}
    
    Tools:
    - SEARCH(query): Search the web.
    - CALCULATOR(expression): Evaluate math.
    - EMAIL(to, subject, body): Send email.
    
    Format:
    Thought: ...
    Action: TOOL(args)
    Observation: ...
    
    Begin.
    """
    
    history = prompt
    max_steps = 5
    
    for i in range(max_steps):
        print(f"Step {i+1}")
        
        # 1. Generate
        response = client.get_completion(history, stop=["Observation:"])
        print(f"LLM: {response}")
        history += response
        
        # 2. Check Done
        if "DONE" in response:
            break
            
        # 3. Parse (Simple regex for TOOL(args))
        # Matches: Action: SEARCH("query")
        match = re.search(r"Action: (\w+)\((.*)\)", response)
        if match:
            tool = match.group(1)
            args = match.group(2).strip('"').strip("'") # Simplistic arg parsing
            
            print(f"  [Exec] {tool} with '{args}'")
            
            obs = "Error"
            if tool == "SEARCH":
                obs = web_search(args)
            elif tool == "CALCULATOR":
                obs = str(calculator(args))
            elif tool == "EMAIL":
                # specific parsing for email args would be needed if comma separated
                # keeping it simple:
                obs = send_email("boss@nebula.com", "Revenue Report", "See body") 
            
            print(f"  [Obs] {obs}")
            history += f"\nObservation: {obs}\n"
        else:
            print("  [No Action] waiting...")
            if "email" in response.lower() and "sent" in response.lower():
                print("Agent seems to think it's done.")
                break

if __name__ == "__main__":
    multi_tool_agent()