import sys
import os
import re

# Enable LangSmith tracing (set LANGCHAIN_API_KEY in .env or environment)
os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from utils.llm_client import LLMClient
from utils.tools import web_search, calculator
from langsmith import traceable  # pip install langsmith


@traceable(name="llm_generate", run_type="llm")
def _traceable_llm(client, history, stop):
    """Wrapped so each LLM call appears as its own span in LangSmith."""
    return client.get_completion(history, stop=stop)


@traceable(name="tool_run", run_type="tool")
def _traceable_tool(tool, arg):
    """Wrapped so each tool call appears as its own span in LangSmith."""
    if tool == "WEB_SEARCH":
        return web_search(arg)
    if tool == "CALCULATOR":
        return calculator(arg)
    return f"Error: Tool {tool} not found"


@traceable(name="agent_loop", run_type="chain")
def agent_loop(question, max_iterations=5):
    """
    A simple ReAct agent loop.
    """
    client = LLMClient()
    
    prompt = f"""
    Answer the question using tools: [WEB_SEARCH, CALCULATOR].
    Format:
    Question: {question}
    Thought: ...
    Action: TOOL_NAME
    Action Input: INPUT
    Observation: RESULT
    ...
    Final Answer: RESULT
    
    Begin!
    Question: {question}
    """
    
    history = prompt
    
    for i in range(max_iterations):
        print(f"\n--- Iteration {i+1} ---")
        
        # 1. Generate (traced as LLM span)
        response = _traceable_llm(client, history, ["Observation:"])
        print(f"LLM: {response}")
        history += response
        
        # 2. Check for Final Answer
        if "Final Answer:" in response:
            return response.split("Final Answer:")[-1].strip()
            
        # 3. Parse Action
        action_match = re.search(r"Action: (.*)", response)
        input_match = re.search(r"Action Input: (.*)", response)
        
        if action_match and input_match:
            tool = action_match.group(1).strip()
            arg = input_match.group(1).strip()
            
            # 4. Execute (traced as tool span)
            observation = _traceable_tool(tool, arg)
            print(f"Observation: {observation}")
            
            # 5. Update History
            history += f"\nObservation: {observation}\n"
        else:
            print("No action detected. Ending.")
            break
            
    return "No answer found."

if __name__ == "__main__":
    print(agent_loop("What is the stock price of AAPL doubled?"))