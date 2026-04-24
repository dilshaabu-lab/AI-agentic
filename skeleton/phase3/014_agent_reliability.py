import sys
import os
import json
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from utils.llm_client import LLMClient

# -----------------------------------------------------------------------------
# Retries
# -----------------------------------------------------------------------------
def retry(times=3, delay=1):
    """Decorator: retry a function up to `times` with `delay` seconds between attempts."""
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

# -----------------------------------------------------------------------------
# Intent classification
# -----------------------------------------------------------------------------

INTENTS = ("greeting", "query", "command", "out_of_scope")

def _clean_json_string(raw: str) -> str:
    """Strip markdown code fences and whitespace so we can parse JSON."""
    cleaned = raw.replace("```json", "").replace("```", "").strip()
    return cleaned


@retry(times=3, delay=1)
def classify_intent(client: LLMClient, user_message: str) -> dict:
    """
    Classify user message into one of INTENTS. Returns JSON like:
    {"intent": "query", "confidence": 0.9}
    Uses retries for robustness against malformed LLM output.
    """
    prompt = f"""Classify the user message into exactly one intent. Reply with only a JSON object, no other text.

Allowed intents: {", ".join(INTENTS)}
- greeting: hello, hi, thanks, bye
- query: questions, "what is", "how do I", "tell me about"
- command: requests to do something (search, send, calculate, run)
- out_of_scope: irrelevant, unclear, or off-topic

User message: "{user_message}"

Reply with only: {{"intent": "<one of the allowed intents>", "confidence": <0.0 to 1.0>}}"""
    response = client.get_completion(prompt, temperature=0.2)
    if not response:
        raise ValueError("Empty LLM response")
    cleaned = _clean_json_string(response)
    data = json.loads(cleaned)
    intent = data.get("intent", "").strip().lower()
    if intent not in INTENTS:
        data["intent"] = "out_of_scope"
    return data

# -----------------------------------------------------------------------------
# Reliable JSON parsing (with retries)
# -----------------------------------------------------------------------------

@retry(times=3)
def parse_json_response(client: LLMClient, prompt: str) -> dict:
    """Ask LLM for JSON; strip markdown if present; parse. Retries on parse failure."""
    print("Requesting JSON...")
    response = client.get_completion(prompt, temperature=0.7)
    if not response:
        raise ValueError("Empty LLM response")
    cleaned = _clean_json_string(response)
    return json.loads(cleaned)

# -----------------------------------------------------------------------------
# Demo
# -----------------------------------------------------------------------------

def reliable_agent_demo():
    """
    Demonstrate reliability: retries, intent classification, and robust JSON parsing.
    """
    client = LLMClient()
    print("--- RELIABILITY DEMO ---\n")

    # 1) Intent classification (with retries on parse failure)
    print("1) Intent classification (retried if JSON parse fails)\n")
    test_messages = [
        "Hi there!",
        "What's the weather in Paris?",
        "Search for latest news about AI",
        "asdfghjkl",
    ]
    for msg in test_messages:
        try:
            result = classify_intent(client, msg)
            print(f"  \"{msg}\" -> intent={result.get('intent')}, confidence={result.get('confidence')}")
        except Exception as e:
            print(f"  \"{msg}\" -> failed: {e}")
    print()

    # 2) Robust JSON generation (with retries)
    print("2) Robust JSON parsing (retries on invalid/markdown-wrapped JSON)\n")
    prompt = "Generate a JSON object for a user named 'Alice' with 3 random hobbies."
    try:
        data = parse_json_response(client, prompt)
        print(f"Success! Valid JSON Parsed:\n{json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"Final failure: {e}")

if __name__ == "__main__":
    reliable_agent_demo()