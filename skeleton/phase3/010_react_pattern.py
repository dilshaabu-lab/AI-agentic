import sys
import os
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from utils.llm_client import LLMClient

def react_pattern_demo():
    """
    Demonstrate the ReAct pattern logic: Thought -> Action -> Observation.
    """
    client = LLMClient()
    
    print("--- REACT PATTERN DEMO ---\n")
    
    question = "What is the capital of France multiplied by 2? (Just kidding, what is 25 * 4?)"
    
    prompt_template = """
    Answer the following question using the tools: [CALCULATOR]
    
    Use this format:
    Question: {question}
    Thought: Think about what to do
    Action: CALCULATOR
    Action Input: input
    Observation: result
    Thought: I have the answer
    Final Answer: final answer
    
    Question: {question}
    """
    
    current_prompt = prompt_template.format(question=question)
    
    # Step 1: LLM decides to use calculator
    print("Step 1: LLM Generation (Stop at Observation)")
    response = client.get_completion(current_prompt, stop=["Action:"])
    print(f"LLM Output:\n{response}\n")
    
    # Step 2: Parse
    action_match = re.search(r"Action: (.*)", response)
    input_match = re.search(r"Action Input: (.*)", response)
    
    if action_match and input_match:
        action = action_match.group(1).strip()
        action_input = input_match.group(1).strip()
        
        print(f"Parsers Action: {action}")
        print(f"Parsed Input: {action_input}")
        
        # Step 3: Execute
        observation = ""
        if action == "CALCULATOR":
            try:
                observation = str(eval(action_input))
            except:
                observation = "Error"
        
        print(f"Observation: {observation}\n")
        
        # Step 4: Append and Continue
        print("Step 2: Feeding observation back to LLM")
        next_prompt = current_prompt + response + f"\nObservation: {observation}\n"
        
        final_response = client.get_completion(next_prompt, stop=["Observation:"])
        print(f"LLM Output:\n{final_response}")
    else:
        print("Failed to parse action.")

if __name__ == "__main__":
    react_pattern_demo()