"""
Streamlit app: Sequential Pipeline (Classifier → Extractor → Writer).
Templates for support email triage + custom input.
"""
# --- Imports: add parent dir so we can import utils.llm_client ---
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from utils.llm_client import LLMClient

import streamlit as st


# --- Agent: reusable LLM agent with a role prompt; act() sends input and returns completion ---
class Agent:
    def __init__(self, name, role_prompt, client):
        self.name = name
        self.role_prompt = role_prompt
        self.client = client

    def act(self, input_text):
        prompt = f"{self.role_prompt}\nInput: {input_text}"
        return self.client.get_completion(prompt)


# --- Predefined support-email templates; keys are labels shown in the sidebar ---
TEMPLATES = {
    "Login / password reset (premium user)": """
Subject: LOGIN ISSUE
Body:
Hi support,
I've been trying to reset my password for 3 days.
The link you sent is expired.
This is ridiculous. Fix it now context: I'm a premium user ID 999.
- Bob
""".strip(),
    "Refund request (order not received)": """
Subject: REFUND REQUEST
Body:
Hello,
I never received my order #8821 from two weeks ago.
I've emailed twice with no response. I want a full refund.
Customer ID: 4455. Please escalate.
- Jane
""".strip(),
    "Feature request (enterprise)": """
Subject: Feature request - API rate limits
Body:
We're an enterprise client (Account ID: ENT-77).
We need higher API rate limits for our production pipeline.
Our current limit is blocking nightly jobs. Can you increase it?
Thanks,
- Alex
""".strip(),
}


# --- Pipeline: create three agents, run classifier then extractor then writer, render each step into container ---
def run_pipeline(user_email: str, client: LLMClient, container):
    # Build the three agents (triage, extractor, support writer).
    classifier = Agent(
        "Classifier",
        "You are a triage agent. Classify the email as URGENT or NORMAL. Return only the class.",
        client,
    )
    extractor = Agent(
        "Extractor",
        "Extract the User ID and specific issue from the text. Return JSON format.",
        client,
    )
    writer = Agent(
        "Writer",
        "You are a support agent. Write a short, empathetic response based on urgency and issue.",
        client,
    )

    # Show the email we are processing.
    with container:
        container.markdown("**Original input**")
        container.text(user_email)

    # Step 1: classify urgency (URGENT / NORMAL).
    urgency = classifier.act(user_email)
    with container:
        container.markdown("**1. Classifier (urgency)**")
        container.info(urgency)

    # Step 2: extract user ID and issue as JSON.
    details = extractor.act(user_email)
    with container:
        container.markdown("**2. Extractor (details)**")
        container.code(details, language="json")

    # Step 3: pass accumulated state to writer and get final support response.
    writer_input = f"Urgency: {urgency}\nDetails: {details}\nOriginal Email: {user_email}"
    response = writer.act(writer_input)
    with container:
        container.markdown("**3. Writer (final response)**")
        container.success(response)


# -----------------------------------------------------------------------------
# Streamlit UI
# -----------------------------------------------------------------------------

# Page title and short description.
st.set_page_config(page_title="Sequential Pipeline", page_icon="🔀")
st.title("Sequential Pipeline")
st.caption("Classifier → Extractor → Writer. Use a template or your own support email.")

# Sidebar: template buttons; clicking one loads that template into session state and reruns.
with st.sidebar:
    st.markdown("### 📋 Templates")
    st.markdown("Click to load a use case into the input below.")
    for name in TEMPLATES:
        if st.button(name, key=f"tpl_{hash(name) % 10**8}"):
            st.session_state["pipe_input"] = TEMPLATES[name]
            st.rerun()
    st.markdown("---")
    st.markdown("**Custom input** is in the main panel.")

# Main area: text area for the support email; default from session state or first template.
default = st.session_state.get("pipe_input", TEMPLATES["Login / password reset (premium user)"])
user_email = st.text_area(
    "Support email (edit or use a template from the sidebar)",
    value=default,
    height=180,
    key="pipe_input",
    label_visibility="visible",
)

run = st.button("Run pipeline")

# On Run: validate input, create LLM client, run pipeline and show output (or show error).
if run:
    if not (user_email and user_email.strip()):
        st.warning("Please enter or select an email to process.")
    else:
        client = LLMClient()
        out = st.container()
        with st.spinner("Running classifier → extractor → writer…"):
            try:
                run_pipeline(user_email.strip(), client, out)
            except Exception as e:
                st.error(f"Pipeline failed: {e}")