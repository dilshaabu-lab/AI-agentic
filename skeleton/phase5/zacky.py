import sys
import os
import json
import logging

import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from utils.llm_client import LLMClient
from utils.tools import web_search

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Helpers ────────────────────────────────────────────────────────────────────

def safe_parse_json(text: str):
    cleaned = text.replace("```json", "").replace("```", "").strip()
    try:
        parsed = json.loads(cleaned)
        return parsed if isinstance(parsed, list) else None
    except json.JSONDecodeError as e:
        logger.error("JSON parse error: %s", e)
        return None


def do_web_search(query: str, use_mock: bool = True) -> str:
    if use_mock:
        return f"Mock findings about {query}..."
    try:
        return web_search(query)
    except Exception as e:
        logger.error("Web search failed: %s", e)
        return f"[Search unavailable] {query}"


# ── Streamlit App ──────────────────────────────────────────────────────────────

st.title("Research Assistant")

# Inputs
topic = st.text_input("Topic", value="Impact of Quantum Computing on Cryptography")
num_questions = st.slider("Number of research questions", min_value=2, max_value=6, value=3)
use_mock = st.checkbox("Use mock search (dev mode)", value=True)

if st.button("Run"):
    client = LLMClient()

    # 1. Planner
    st.write("**[Planner]** Generating research questions...")
    plan_prompt = (
        f"Break down '{topic}' into exactly {num_questions} key research questions. "
        f"Return ONLY a valid JSON array of strings, no other text."
    )
    plan_resp = client.get_completion(plan_prompt)
    questions = safe_parse_json(plan_resp)

    if not questions:
        st.error("Planner failed to return valid questions. Please try again.")
        st.stop()

    st.write(f"Questions: {questions}")
    findings = []

    # 2. Researcher
    for i, q in enumerate(questions, 1):
        st.write(f"**[Researcher {i}/{len(questions)}]** Investigating: {q}")
        search_res = do_web_search(q, use_mock=use_mock)

        summary_prompt = (
            f"You are a research analyst. Summarise these findings in 3-5 sentences.\n\n"
            f"Question: {q}\nFindings: {search_res}"
        )
        summary = client.get_completion(summary_prompt)
        findings.append(f"Q: {q}\nA: {summary}")
        st.write(f"> {summary}")

    # 3. Writer
    st.write("**[Writer]** Compiling report...")
    context = "\n\n".join(findings)
    report_prompt = (
        f"Write a research report with executive summary, key findings, and conclusion "
        f"based on:\n{context}"
    )
    report = client.get_completion(report_prompt)

    st.markdown("---")
    st.subheader("Final Report")
    st.write(report)

    st.download_button(
        label="Download Report",
        data=report,
        file_name="research_report.txt",
        mime="text/plain",
    )