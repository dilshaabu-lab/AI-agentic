import sys
import os
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from utils.llm_client import LLMClient


# Context
context_str = [
    "Stranger Things is a science fiction series set in the town of Hawkins.",
    "A group of young friends discover a secret government laboratory.",
    "A girl with special powers helps them fight a dangerous creature.",
    "A mysterious parallel world called the Upside Down threatens the town."
]   

system_prompt = f"""
Answer the question using the context below.

Context:
{context_str}

Instruction:
- Ignore irrelevant information.
- If query is irrelevant to the context, redirect user back to context topics.
"""


# Streamlit page config
st.set_page_config(page_title="Stranger Things", page_icon="🤖")
st.title("Stranger Things")


# ✅ Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []


# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])


# User input
if prompt := st.chat_input("Ask about stranger things!"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Create full prompt
    full_prompt = system_prompt + "\nUser Question: " + prompt

    # Generate response
    client = LLMClient()
    response = client.get_completion(full_prompt)

    # Store assistant reply
    st.session_state.messages.append({"role": "assistant", "content": response})

    st.chat_message("assistant").write(response)
        
        
        
# def rag_debugging_demo():
#     """
#     Simulate a RAG pipeline failure and the debugging process.
#     """
#     client = LLMClient()
#     context_str = [
#         "France has many cities.",
#         "Paris is a city in Texas.", # Misleading
#         "The capital of France is Paris." # Correct but buried
#     ]
#     SYSTEM_PROMPT =f"You are a helpfull assistant of geography\nAnswer the question\ncontext: {context_str}\nInstruction:Ignore irrelevent information and focus on the correct answer.If the query is Irrevelent to the Geography, force the user back to topics in the context.Do not answer."
    
#     print("--- RAG DEBUGGING DEMO ---\n")
    
#     # CASE 1: Retrieval Failure (Noise)
#     print("CASE 1: Noisy Retrieval")
#     # query = "What is the capital of France?"
#     query ="Why  do crow flew?"
    
#     # Simulate a retriever that pulls irrelevant docs with high similarity scores due to keyword matching
#     retrieved_docs = "One hot summer day, a thirsty crow flew around searching for water. He was very tired and felt like he might faint. Finally, he saw a pitcher on the ground. He flew down, but there was only a little bit of water at the very bottom."
    
#     # Bad prompt doesn't prioritize or handle conflict
#     context_str = "\n".join(retrieved_docs)
#     prompt_bad = f"Answer: {query}\nContext: {context_str}"
    
#     print(f"Docs:\n{context_str}")
#     print("Generating...")
#     # Might get confused by "Paris, Texas"
#     response = client.get_completion(prompt_bad)
#     print(f"Response (BAD): {response}")
#     print("FIX: Better specific prompt instructions ('Ignore irrelevant info').\n")
    
#     prompt_fixed=f"Answer the question {query}\ncontext: {context_str}\nInstruction:Ignore irrelevent information and focus on the correct answer.If the query is Irrevelent to the context, force the user back to topics in the context.Do not answer."
    
#     response_fixed = client.get_completion(prompt_fixed)
#     print(f"Response fixed: {response_fixed}")