"""
Streamlit app: Coordination failure demo (delegation loop Help Desk ↔ Tech).
Templates for queries + custom query input.
"""
# --- Imports: add parent dir so we can import utils.llm_client ---
import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from utils.llm_client import LLMClient

import streamlit as st

# --- Predefined user queries; some can trigger infinite Help Desk ↔ Tech handoff ---
TEMPLATES = {
    "My account is locked.": "My account is locked.",
    "I can't log in to the VPN.": "I can't log in to the VPN.",
    "I need a refund for my subscription.": "I need a refund for my subscription.",
    "My laptop won't connect to the company WiFi.": "My laptop won't connect to the company WiFi.",
}


# --- Simulate handoff: Help Desk delegates "technical" to Tech; Tech delegates "administrative" to Help Desk; loop until resolved or max_iters ---
def run_coordination_demo(query: str, client: LLMClient, container, max_iters=6):
    # Help Desk: if query looks technical, respond with "DELEGATE: TECH"; otherwise answer.
    def agent_a(q):
        prompt = f"""
You are Help Desk. If query is technical, say "DELEGATE: TECH".
Otherwise answer it.
Query: {q}
"""
        return client.get_completion(prompt)

    # Tech Support: if query looks administrative (billing, account), respond with "DELEGATE: HELPDESK"; otherwise fix.
    def agent_b(q):
        prompt = f"""
You are Tech Support. If query is administrative (like billing or simple account status), say "DELEGATE: HELPDESK".
Otherwise fix it.
Query: {q}
"""
        return client.get_completion(prompt)

    # Alternate between agents based on DELEGATE: directives; stop when one agent answers without delegating.
    current_agent = "HELPDESK"
    for i in range(max_iters):
        with container:
            container.markdown(f"**Iteration {i}** — Handled by **{current_agent}**")

        if current_agent == "HELPDESK":
            response = agent_a(query)
        else:
            response = agent_b(query)

        with container:
            container.caption("Response")
            container.write(response)

        # Check for delegation directives to switch agent for next iteration.
        if "DELEGATE: TECH" in response:
            current_agent = "TECH"
        elif "DELEGATE: HELPDESK" in response:
            current_agent = "HELPDESK"
        else:
            with container:
                container.success("Resolved!")
            return

        time.sleep(0.5)

    # Reached max iterations without resolution: show coordination-failure message and suggested fix.
    with container:
        container.error("Infinite loop detected: agents are bouncing the ticket.")
        container.markdown(
            "**FIX:** Introduce a Manager/Router agent or shared state to track handoffs."
        )


# -----------------------------------------------------------------------------
# Streamlit UI
# -----------------------------------------------------------------------------

# Page title and short description.
st.set_page_config(page_title="Coordination Debugging", page_icon="🔄")
st.title("Coordination failure demo")
st.caption("Help Desk ↔ Tech Support delegation. Some queries can trigger an infinite handoff loop.")

# Sidebar: template buttons load the selected query into session state and rerun.
with st.sidebar:
    st.markdown("### 📋 Template queries")
    st.markdown("Click to load a query (some may cause a loop).")
    for name in TEMPLATES:
        if st.button(name, key=f"coord_tpl_{hash(name) % 10**8}"):
            st.session_state["coord_query"] = TEMPLATES[name]
            st.rerun()
    st.markdown("---")
    st.markdown("Or enter a **custom query** in the main panel.")

# Main area: text input for the user query; default from session state or first template.
default_query = st.session_state.get("coord_query", list(TEMPLATES.values())[0])
query = st.text_input(
    "User query",
    value=default_query,
    key="coord_query",
    placeholder="e.g. My account is locked.",
)

run = st.button("Run coordination demo")

# On Run: validate query, create LLM client, run handoff loop and show iterations or loop/fix message (or error).
if run:
    if not (query and query.strip()):
        st.warning("Please enter or select a query.")
    else:
        client = LLMClient()
        out = st.container()
        with st.spinner("Running Help Desk / Tech Support handoff…"):
            try:
                run_coordination_demo(query.strip(), client, out)
            except Exception as e:
                st.error(f"Demo failed: {e}")