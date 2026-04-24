"""
Streamlit app: Supervisor–Worker (plan then execute WEATHER + EMAIL workers).
Templates for tasks + custom task input.
"""
# --- Imports: add parent dir so we can import utils.llm_client ---
import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from utils.llm_client import LLMClient

import streamlit as st


# --- Simulated workers: WEATHER returns fake weather for a location; EMAIL returns a draft confirmation ---
def weather_worker(loc):
    return f"Weather in {loc} is Sunny, 25C"


def email_worker(content):
    return f"Email drafted: '{content}'"


def _inject_weather_into_email(email_input: str, context: str) -> str:
    """Replace placeholders in the EMAIL step input with actual weather from context."""
    # Extract the actual weather line from context (e.g. "Weather Report: Weather in Tokyo is Sunny, 25C").
    lines = [ln.strip() for ln in context.strip().split("\n") if ln.strip()]
    weather_lines = [ln.replace("Weather Report:", "").strip() for ln in lines if "weather" in ln.lower() or "Sunny" in ln or "C" in ln]
    full_weather = weather_lines[0] if weather_lines else context.strip()
    # Short form for "The weather in X is: ___" (e.g. "Sunny, 25C").
    short_weather = full_weather.split(" is ", 1)[-1].strip() if " is " in full_weather else full_weather
    # Replace common LLM placeholders: use short form when template already says "weather in X is:".
    result = email_input
    placeholders_full = [
        "[weather result]",
        "[weather from step 1]",
        "[result from step 1]",
        "[insert weather here]",
        "[weather]",
    ]
    placeholders_short = ["[insert weather condition here]", "[insert weather info here]"]
    for placeholder in placeholders_short:
        if placeholder in result:
            result = result.replace(placeholder, short_weather)
    for placeholder in placeholders_full:
        if placeholder in result:
            result = result.replace(placeholder, full_weather)
    # Curly-brace placeholders (e.g. from JSON/LLM template style like {weather_result}).
    for ph in ["{weather_result}", "{weather}", "{result}"]:
        if ph in result:
            result = result.replace(ph, short_weather)
    # Fallback: if input references weather/summary but no placeholder was replaced, append the actual weather.
    if full_weather and full_weather not in result and short_weather not in result and ("weather" in result.lower() or "summary" in result.lower()):
        result = f"{result.rstrip().rstrip('.:')}: {short_weather}"
    return result


# --- Predefined tasks for the supervisor; keys are labels shown in the sidebar ---
TEMPLATES = {
    "Check weather in Tokyo and tell the team.": "Check weather in Tokyo and tell the team.",
    "Check weather in London and email the summary to the client.": "Check weather in London and email the summary to the client.",
    "Get weather for Paris and send a brief update to the manager.": "Get weather for Paris and send a brief update to the manager.",
}


# --- Supervisor: ask LLM for a JSON plan of steps; then execute each step (WEATHER / EMAIL) and show results ---
def run_supervisor(task: str, client: LLMClient, container):
    # Ask the LLM to return a list of { worker, input } steps in JSON.
    plan_prompt = f"""
You are a Supervisor.
Task: {task}

Available Workers:
- WEATHER: takes location
- EMAIL: takes content

Return a list of steps in JSON format:
[{{"worker": "WEATHER", "input": "..."}}, {{"worker": "EMAIL", "input": "..."}}]
"""
    plan_raw = client.get_completion(plan_prompt)
    # Strip markdown code fences so we can parse JSON.
    plan_raw = plan_raw.replace("```json", "").replace("```", "").strip()

    try:
        plan = json.loads(plan_raw)
        # If the model returns a single object, wrap it in a list.
        if isinstance(plan, dict):
            plan = [plan]
        with container:
            container.markdown("**Supervisor plan**")
            container.json(plan)

        # Execute each step; accumulate context (e.g. weather result) for steps that reference it.
        context = ""
        for step in plan:
            worker = step.get("worker", "")
            inp = step.get("input", "")

            # Run WEATHER worker and append result to context for later steps.
            if worker == "WEATHER":
                res = weather_worker(inp)
                context += f"Weather Report: {res}\n"
                with container:
                    container.markdown(f"**Worker: WEATHER** — `{inp}`")
                    container.info(res)
            # Run EMAIL worker; if input references weather/team/summary, inject actual weather into placeholders.
            elif worker == "EMAIL":
                if context and ("weather" in inp.lower() or "team" in inp.lower() or "summary" in inp.lower()):
                    inp = _inject_weather_into_email(inp, context)
                res = email_worker(inp)
                with container:
                    container.markdown(f"**Worker: EMAIL** — `{inp}`")
                    container.success(res)
    except json.JSONDecodeError:
        with container:
            container.error("Supervisor did not return valid JSON.")
            container.code(plan_raw)


# -----------------------------------------------------------------------------
# Streamlit UI
# -----------------------------------------------------------------------------

# Page title and short description.
st.set_page_config(page_title="Supervisor Worker", page_icon="👷")
st.title("Supervisor Worker")
st.caption("Supervisor plans steps (WEATHER + EMAIL workers); workers execute. Use a template or your own task.")

# Sidebar: template buttons load the selected task into session state and rerun.
with st.sidebar:
    st.markdown("### 📋 Template tasks")
    st.markdown("Click to load a task.")
    for name in TEMPLATES:
        if st.button(name, key=f"sup_tpl_{hash(name) % 10**8}"):
            st.session_state["sup_task"] = TEMPLATES[name]
            st.rerun()
    st.markdown("---")
    st.markdown("Or enter a **custom task** in the main panel.")

# Main area: text input for the supervisor task; default from session state or first template.
default_task = st.session_state.get("sup_task", list(TEMPLATES.values())[0])
task = st.text_input(
    "Task for the supervisor",
    value=default_task,
    key="sup_task",
    placeholder="e.g. Check weather in Berlin and email the team.",
)

run = st.button("Run supervisor")

# On Run: validate task, create LLM client, run supervisor + workers and show output (or error).
if run:
    if not (task and task.strip()):
        st.warning("Please enter or select a task.")
    else:
        client = LLMClient()
        out = st.container()
        with st.spinner("Supervisor planning and workers executing…"):
            try:
                run_supervisor(task.strip(), client, out)
            except Exception as e:
                st.error(f"Run failed: {e}")