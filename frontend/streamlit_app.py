import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.title("DocuAgent")

uploaded = st.file_uploader("Upload a document", type=["pdf", "png", "jpg"])
if uploaded and st.button("Ingest"):
    r = requests.post(f"{API_URL}/ingest", files={"file": uploaded})
    st.success(r.json())

question = st.text_input("Ask a question about your documents")
if question and st.button("Ask"):
    r = requests.post(f"{API_URL}/ask", json={"question": question})
    st.write(r.json()["answer"])