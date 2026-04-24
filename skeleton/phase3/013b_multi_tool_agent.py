import sys
import os
import re

# Enable LangSmith tracing (set LANGSMITH_API_KEY in .env or environment)
os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from utils.llm_client import LLMClient
from utils.tools import calculator, web_search, send_email
from langsmith import traceable  # pip install langsmith


@traceable(name="llm_generate", run_type="llm")
def _traceable_llm(client, history, stop):
    """Wrapped so each LLM call appears as its own span in LangSmith."""
    return client.get_completion(history, stop=stop)


@traceable(name="tool_run", run_type="tool")
def _traceable_tool(tool, args_str):
    """Wrapped so each tool call appears as its own span in LangSmith."""
    if tool == "SEARCH":
        return web_search(args_str)
    if tool == "CALCULATOR":
        return str(calculator(args_str))
    if tool == "EMAIL":
        # specific parsing for email args would be needed if comma separated; keeping it simple
        return send_email("boss@nebula.com", "Revenue Report", "See body")
    return "Error"


@traceable(name="multi_tool_agent", run_type="chain")
def multi_tool_agent():
    """
    Demonstrate a multi-step agent flow.
    """
    client = LLMClient()
    
    print("--- MULTI-TOOL AGENT DEMO ---\n")
    
    task = "Find Apple's Q3 revenue (mock search), compare to Q2's $1.2M, and email the growth percentage to boss@nebula.com"
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
        
        # 1. Generate (traced as LLM span)
        response = _traceable_llm(client, history, ["Observation:"])
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
            args = match.group(2).strip('"').strip("'")  # Simplistic arg parsing
            
            print(f"  [Exec] {tool} with '{args}'")
            
            # 4. Execute (traced as tool span)
            obs = _traceable_tool(tool, args)
            
            print(f"  [Obs] {obs}")
            history += f"\nObservation: {obs}\n"
        else:
            print("  [No Action] waiting...")
            if "email" in response.lower() and "sent" in response.lower():
                print("Agent seems to think it's done.")
                break

if __name__ == "__main__":
    multi_tool_agent()