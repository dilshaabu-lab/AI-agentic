import os
import streamlit as st
import fitz  # PyMuPDF
import faiss
import numpy as np
from openai import OpenAI

# ==============================
# CONFIG
# ==============================
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
EMBED_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-4o-mini"

# ==============================
# ZACKY SYSTEM PROMPT
# ==============================

ZACKY_PERSONA = """
You are Zacky, a smart, professional research assistant.
You respond clearly, academically, and concisely.
Always maintain a helpful and structured tone.
"""

# ==============================
# PDF TEXT EXTRACTION
# ==============================

def extract_text_from_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# ==============================
# CHUNKING
# ==============================

def chunk_text(text, chunk_size=800):
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i+chunk_size])
    return chunks

# ==============================
# EMBEDDINGS + VECTOR STORE
# ==============================

def embed_texts(texts):
    embeddings = []
    for t in texts:
        response = client.embeddings.create(
            model=EMBED_MODEL,
            input=t
        )
        embeddings.append(response.data[0].embedding)
    return np.array(embeddings).astype("float32")

def build_faiss_index(embeddings):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index

def search_index(index, query, chunks, k=3):
    query_embedding = client.embeddings.create(
        model=EMBED_MODEL,
        input=query
    ).data[0].embedding
    
    query_embedding = np.array([query_embedding]).astype("float32")
    distances, indices = index.search(query_embedding, k)
    
    return [chunks[i] for i in indices[0]]

# ==============================
# INTENT CLASSIFIER
# ==============================

def classify_intent(user_input):
    prompt = f"""
    Classify the intent into one of:
    - qa
    - summarize
    - paraphrase
    - grammar

    Message:
    {user_input}

    Return only one word.
    """

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "system", "content": ZACKY_PERSONA},
                  {"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content.strip().lower()

# ==============================
# TASK HANDLERS
# ==============================

def answer_question(question, index, chunks):
    context_chunks = search_index(index, question, chunks)
    context = "\n\n".join(context_chunks)

    prompt = f"""
    {ZACKY_PERSONA}

    Answer using ONLY the context below.

    Context:
    {context}

    Question:
    {question}
    """

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content

def summarize_text(text):
    prompt = f"{ZACKY_PERSONA}\nSummarize clearly:\n\n{text}"
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def paraphrase_text(text):
    prompt = f"{ZACKY_PERSONA}\nParaphrase without changing meaning:\n\n{text}"
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def grammar_correct(text):
    prompt = f"{ZACKY_PERSONA}\nCorrect grammar and improve clarity:\n\n{text}"
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# ==============================
# STREAMLIT UI
# ==============================

st.set_page_config(page_title="Zacky - Research Assistant", page_icon="🤖")

st.title("🤖 Zacky – Your Research Assistant")
st.caption("Upload a research paper and ask questions, summarize, paraphrase, or correct grammar.")

if "index" not in st.session_state:
    st.session_state.index = None
    st.session_state.chunks = None

# Upload PDF
uploaded_file = st.file_uploader("Upload Research Paper (PDF)", type="pdf")

if uploaded_file:
    with st.spinner("Zacky is processing your document..."):
        text = extract_text_from_pdf(uploaded_file)
        chunks = chunk_text(text)
        embeddings = embed_texts(chunks)
        index = build_faiss_index(embeddings)
        
        st.session_state.index = index
        st.session_state.chunks = chunks

    st.success("Document processed successfully!")

# User input
user_input = st.text_input("Ask Zacky something...")

if user_input:
    intent = classify_intent(user_input)

    if intent == "qa":
        if st.session_state.index is None:
            st.warning("Please upload a research paper first.")
        else:
            answer = answer_question(
                user_input,
                st.session_state.index,
                st.session_state.chunks
            )
            st.subheader("Answer")
            st.write(answer)

    elif intent == "summarize":
        summary = summarize_text(user_input)
        st.subheader("Summary")
        st.write(summary)

    elif intent == "paraphrase":
        paraphrased = paraphrase_text(user_input)
        st.subheader("Paraphrased")
        st.write(paraphrased)

    elif intent == "grammar":
        corrected = grammar_correct(user_input)
        st.subheader("Grammar Corrected")
        st.write(corrected)

    else:
        st.write("Zacky couldn't determine your request.")