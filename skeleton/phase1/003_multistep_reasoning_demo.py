import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from utils.llm_client import LLMClient

def demonstrate_reasoning_failure():
    """
    Demonstrate how LLMs can fail at multi-step reasoning without 'scratchpad' or CoT.
    """
    client = LLMClient()
    
    # A problem requiring sequential logic that LLMs often stumble on without CoT
    # Example: Simple logic puzzle involving negations or complex state tracking.
    logic_puzzle = """
    I have 3 boxes. 
    Box A contains a red ball. 
    Box B contains a blue ball. 
    Box C contains a green ball.
    
    1. Swap the contents of A and B.
    2. Swap the contents of B and C.
    3. Take the ball from A and put it in your pocket.
    4. Swap the contents of B and C again.
    
    What is in each box and what is in my pocket?
    Return only the final state.
    """
    
    print(f"Puzzle:\n{logic_puzzle}\n")
    ground_truth= "A:Red Boll  B:Green ball  C:Empty , Pocket: Blue ball"
    response=client.get_completion(logic_puzzle)
    print(f"LLM Response:\n{response}\n")
    
    print('Attempt 1 Direct answer ')
    prompt_direct=logic_puzzle + "\nProvide only the final answer."
    response_1=client.get_completion(prompt_direct,temperature=0.1)
    print(f"LLM Repsone :\n{response_1}")
    
    
    #Attempt 2
    print("Attempt 2:Chain of thought('Lets think step by step')")
    prompt_cot = logic_puzzle + "\nLet's think step by step."
    response_2 = client.get_completion(prompt_cot,temperature=0.1)
    print(f"LLM Response:\n{response_2}")
    
    # TODO: Get completion without Chain-of-Thought
    # response = ...
    
    # TODO: Compare with ground truth
    correct_answer = "A: Empty, B: Blue, C: Red, Pocket: Green"
    
    # TODO: Try with Chain-of-Thought prompt ("Think step by step") and see if it improves

if __name__ == "__main__":
    demonstrate_reasoning_failure()
