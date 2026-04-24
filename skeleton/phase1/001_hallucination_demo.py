import sys
import os

# Add parent directory to path to import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from utils.llm_client import LLMClient

def demonstrate_hallucination():
    """
    Demonstrate how LLMs can hallucinate facts about non-existent things.
    """
    client = LLMClient()
    
    # A completely made up library name that sounds plausible
    fake_library = "PyGundam-7B"
    
    prompt = f"Tell me about the {fake_library} python library. What are its main features and how do I install it?"
    
    print(f"User: {prompt}\n")
    
    # TODO: Get completion from LLM
    response = client.get_completion(prompt)
    
    # TODO: Print the response
    print(f"LLM: {response}")
    
    # TODO: Analyze/Discuss why this is dangerous
    
    # ========================================================================
    # BONUS: Compare hallucination across different LLM providers
    # ========================================================================
    # Uncomment the blocks below after setting up the provider in llm_client.py
    # to see how different models handle the same fake library question.
    #
    # --- Groq (Llama 3.3) ---
    # groq_client = LLMClient(provider="groq")
    # groq_response = groq_client.get_completion(prompt)
    # print(f"\n--- Groq (Llama 3.3) ---\n{groq_response}")
    #
    # --- Google Gemini ---
    # google_client = LLMClient(provider="google")
    # google_response = google_client.get_completion(prompt)
    # print(f"\n--- Google Gemini ---\n{google_response}")
    #
    # --- Anthropic (Claude) ---
    # anthropic_client = LLMClient(provider="anthropic")
    # anthropic_response = anthropic_client.get_completion(prompt)
    # print(f"\n--- Anthropic (Claude) ---\n{anthropic_response}")
    #
    # Discussion: Which model hallucinates most confidently?
    # Does any model refuse to answer about a fake library?
    # ========================================================================

if __name__ == "__main__":
    demonstrate_hallucination()
