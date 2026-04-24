import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from utils.llm_client import LLMClient

def prompt_engineering_demo():
    """
    Demonstrate prompt engineering techniques for RAG.
    """
    client = LLMClient()
    
    print("--- PROMPT ENGINEERING DEMO ---\n")
    
    # context = """
    # PRODUCT MANUAL: CloudGazer Telescope
    # - Model: CG-500
    # - Setup: Requires level surface. Calibrate North before use.
    # - Troubleshooting: If image is blurry, adjust focus knob. If black, remove lens cap.
    # - Warranty: 2 years.
    # - Support Email: help@cloudgazer.com
    # """
    context = context = """
    Shadows speak where quiet minds agree,  
    Words become bridges across every tongue,  
    From scattered talks, clear minutes finally see,  
    A meeting’s heart is saved, precise and strong.
    """
    
    # scenarios = [
    #     {"query": "Why is my view just black?", "type": "Trivial"},
    #     {"query": "Can I use it on a boat?", "type": "Inference"},
    #     {"query": "The focus knob broke off.", "type": "Policy"}
    # ]
    scenarios = [
    {"query": "What connects people who speak different languages?", "type": "Trivial"},
    {"query": "Does the system help turn scattered talks into clear meeting minutes?", "type": "Inference"},
    {"query": "Is it allowed to store or share private meeting content?", "type": "Policy"}
    ]
    
    for scenario in scenarios:
        query = scenario["query"]
        q_type = scenario["type"]
        print(f"\nScenario: {q_type} - '{query}'")
        
        # 1. Zero-Shot / Naive
        prompt_naive = f"Context: {context}\nQuestion: {query}"
        print("  [Naive Prompt] Response:")
        print("  " + client.get_completion(prompt_naive).replace("\n", "\n  "))
        
        # 2. Role-Playing + Constraints
        prompt_role = f"""
        You are a helpful technical support agent for CloudGazer.
        Use the context below to answer the customer's question.
        If the answer is not in the context, say "I don't know" and refer them to support.
        Keep answers concise (under 2 sentences).
        
        Context:
        {context}
        
        Customer Question: {query}
        """
        print("  [Role-Play Prompt] Response:")
        print("  " + client.get_completion(prompt_role).replace("\n", "\n  "))
        
        # 3. Chain-of-Thought
        prompt_cot = f"""
        Context: {context}
        Question: {query}
        
        Let's think step by step.
        1. Analyze the user's problem.
        2. Check the manual for relevant sections.
        3. Formulate the answer.
        """
        print("  [CoT Prompt] Response:")
        print("  " + client.get_completion(prompt_cot).replace("\n", "\n  "))

if __name__ == "__main__":
    prompt_engineering_demo()