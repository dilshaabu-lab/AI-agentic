"""
Streamlit app: Debate chain (Pro → Con → Judge).
Templates for debate topics + custom topic input.
"""
# --- Imports: add parent dir so we can import utils.llm_client ---
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from utils.llm_client import LLMClient

import streamlit as st

# --- Predefined debate topics; keys are labels, values are the topic text loaded into the input ---
TEMPLATES = {
    "Should we rewrite our backend in Rust?": "Should we rewrite our backend in Rust?",
    "Should we adopt microservices?": "Should we adopt microservices?",
    "Remote work vs office-first?": "Remote work vs office-first?",
    "Build vs buy for internal tools?": "Build vs buy for internal tools?",
}


# --- Run three-round debate: Pro argues for, Con argues against, Judge decides; append each to history ---
def run_debate(topic: str, client: LLMClient, container):
    sys_prompt = "You are participating in a debate. Keep your answers short (2-3 sentences)."
    history = f"Topic: {topic}\n"

    # Round 1: Proponent argues FOR the topic.
    prompt_pro = f"{sys_prompt}\nYou are a Rust Evangelist. Argue FOR the topic.\nHistory:\n{history}"
    response_pro = client.get_completion(prompt_pro)
    history += f"Proponent: {response_pro}\n"
    with container:
        container.markdown("**PRO (for)**")
        container.info(response_pro)

    # Round 2: Opponent argues AGAINST the proponent (using debate history).
    prompt_con = (
        f"{sys_prompt}\nYou are a Pragmatic Tech Lead who loves Python. Argue AGAINST the proponent.\nHistory:\n{history}"
    )
    response_con = client.get_completion(prompt_con)
    history += f"Opponent: {response_con}\n"
    with container:
        container.markdown("**CON (against)**")
        container.warning(response_con)

    # Round 3: Judge reviews full history and gives a final decision.
    prompt_judge = f"You are a CTO. Review the debate and make a final decision.\nHistory:\n{history}"
    decision = client.get_completion(prompt_judge)
    with container:
        container.markdown("**JUDGE (decision)**")
        container.success(decision)


# -----------------------------------------------------------------------------
# Streamlit UI
# -----------------------------------------------------------------------------

# Page title and short description.
st.set_page_config(page_title="Debate Consensus", page_icon="⚖️")
st.title("Debate Consensus")
st.caption("Pro → Con → Judge. Pick a template or enter your own topic.")

# Sidebar: template buttons load the selected topic into session state and rerun.
with st.sidebar:
    st.markdown("### 📋 Template topics")
    st.markdown("Click to use as the debate topic.")
    for name, topic in TEMPLATES.items():
        if st.button(name, key=f"debate_tpl_{hash(name) % 10**8}"):
            st.session_state["debate_topic"] = topic
            st.rerun()
    st.markdown("---")
    st.markdown("Or type a **custom topic** in the main panel.")

# Main area: text input for debate topic; default from session state or first template.
default_topic = st.session_state.get("debate_topic", list(TEMPLATES.values())[0])
topic = st.text_input(
    "Debate topic",
    value=default_topic,
    key="debate_topic",
    placeholder="e.g. Should we migrate to the cloud?",
)

run = st.button("Run debate")

# On Run: validate topic, create LLM client, run three-round debate and show output (or error).
if run:
    if not (topic and topic.strip()):
        st.warning("Please enter or select a topic.")
    else:
        client = LLMClient()
        out = st.container()
        with st.spinner("Running debate (Pro → Con → Judge)…"):
            try:
                run_debate(topic.strip(), client, out)
            except Exception as e:
                st.error(f"Debate failed: {e}")