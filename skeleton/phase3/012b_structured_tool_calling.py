import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from utils.llm_client import LLMClient

def structured_tool_calling_demo():
    """
    Demonstrate OpenAI's native Function Calling.
    """
    client = LLMClient()
    
    print("--- STRUCTURED TOOL CALLING DEMO ---\n")
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                    },
                    "required": ["location"],
                },
            },
        }
    ]
    
    query = "Calculate 10 * 5"
    print(f"Query: {query}")
    
    try:
        # Use client's default model so this works with Groq or OpenAI
        model = client._get_default_model()
        response = client.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": query}],
            tools=tools,
            tool_choice="auto",
        )
        
        message = response.choices[0].message
        tool_calls = message.tool_calls
        
        if tool_calls:
            print(f"LLM decided to call {len(tool_calls)} tools:")
            for tc in tool_calls:
                fn_name = tc.function.name
                args = json.loads(tc.function.arguments)
                print(f"  - Function: {fn_name}")
                print(f"    Arguments: {args}")
        else:
            print("No tool calls generated.")
            
    except Exception as e:
        print(f"Error (requires valid OpenAI key): {e}")

if __name__ == "__main__":
    structured_tool_calling_demo()