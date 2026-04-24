import sys
import os
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from utils.llm_client import LLMClient
from utils.tracer import SimpleTracer

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

trace_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/traces/trace_streamlit.json"))
tracer = SimpleTracer(trace_path)
tracer.clear()  # clear previous run

st.set_page_config(page_title="PDF RAG", page_icon=":robot_face:")

# ---- Left panel: PDF upload as knowledge source ----
with st.sidebar:
    st.subheader("PDF source")
    st.caption("Upload a PDF to use as context for answers.")
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"], key="pdf_upload")

# Extract text from uploaded PDF and store as context (replaces context_str)
if "pdf_context" not in st.session_state:
    st.session_state.pdf_context = None

if uploaded_file is not None:
    if PdfReader is None:
        st.sidebar.error("Install `pypdf` to use PDF upload: pip install pypdf")
    else:
        try:
            reader = PdfReader(uploaded_file)
            chunks = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    chunks.append(text.strip())
            st.session_state.pdf_context = "\n\n".join(chunks) if chunks else None
            st.sidebar.success(f"Loaded {len(reader.pages)} page(s).")
        except Exception as e:
            st.sidebar.error(f"Could not read PDF: {e}")
            st.session_state.pdf_context = None
else:
    st.session_state.pdf_context = None

# Build system prompt from PDF context (instead of hardcoded context_str)
context_str = st.session_state.pdf_context
if not context_str:
    context_str = "[No PDF uploaded. Please add a PDF in the sidebar to use as knowledge base.]"

SYSTEM_PROMPT = (
    "You are a helpful assistant. You must answer ONLY using the context below from the uploaded PDF.\n"
    "STRICT RULES:\n"
    "- Use ONLY information that appears in the context. Do not use any external or general knowledge.\n"
    "- If the answer is not in the context, say so and do not invent an answer.\n"
    "- Do not combine context information with outside knowledge.\n"
    f"\nContext from PDF:\n{context_str}\n"
)

# ---- Main area: chat ----
st.title("PDF RAG")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Ask a question based on the uploaded PDF!"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    api_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages

    client = LLMClient()
    with st.spinner("Thinking…"):
        response = client.get_chat_completion(api_messages, temperature=0.2, max_tokens=100)
        tracer.log_event("send_llm_query", {"query": api_messages, "model": client._get_default_model()})

    answer = response.content if response else "⚠️ No response from the model."
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.chat_message("assistant").write(answer)