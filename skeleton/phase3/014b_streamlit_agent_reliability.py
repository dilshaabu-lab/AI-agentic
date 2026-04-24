import sys
import os
import importlib.util
import streamlit as st
from langsmith import traceable  # pip install langsmith

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
# Enable LangSmith tracing (set LANGSMITH_API_KEY in .env or environment)
os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
# Load reliability logic from 014 (retry + classify_intent) so we reuse the same retry attempts

_here = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "agent_reliability",
    os.path.join(_here, "014_agent_reliability.py"),
)
_ar = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ar)

LLMClient = _ar.LLMClient
classify_intent = _ar.classify_intent
INTENTS = _ar.INTENTS

# -----------------------------------------------------------------------------
# Streamlit UI
# -----------------------------------------------------------------------------

st.set_page_config(page_title="Agent reliability", page_icon="🔄")
st.title("Intent classification (with retries)")
st.caption("Classify your message into an intent. Uses up to 3 retries if the LLM returns invalid JSON.")

user_input = st.text_input(
    "Your message",
    placeholder="e.g. Hi there! / What's the weather? / Search for AI news",
    label_visibility="collapsed",
)
button = st.button("Classify intent")

if button and user_input.strip():
    with st.spinner("Classifying (retries on parse failure)…"):
        @traceable(name="classify_intent_with_retries", run_type="chain")
        def handle_intent_classification(user_input):
            try:
                client = LLMClient()
                result = classify_intent(client, user_input.strip())

                intent = result.get("intent", "unknown")
                confidence = result.get("confidence")

                st.success(f"**Intent:** `{intent}`")

                if confidence is not None:
                    st.metric("Confidence", f"{confidence:.2f}")

                st.json(result)

            except Exception as e:
                st.error(f"Classification failed after retries: {e}")
        handle_intent_classification(user_input)
elif button and not user_input.strip():
    st.warning("Please enter a message.")

with st.sidebar:
    st.markdown("### About")
    st.markdown("Intent classes: **greeting**, **query**, **command**, **out_of_scope**.")
    st.markdown("Classification uses **up to 3 retries** (with 1s delay) if the model returns invalid or markdown-wrapped JSON.")