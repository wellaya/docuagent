from fastapi import FastAPI, UploadFile, File
from azure.monitor.opentelemetry import configure_azure_monitor
import os

from app.ingestion.extract import extract_text_and_tables
from app.ingestion.chunk_embed import chunk_text, embed_chunks
from app.retrieval.search_client import upload_chunks
from app.agent.agent_service import run_agent

if os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING"):
    configure_azure_monitor()

app = FastAPI(title="DocuAgent")

@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    content = await file.read()
    extracted = extract_text_and_tables(content)
    docs = []
    for chunk in extracted["chunks"]:
        pieces = chunk_text(chunk["text"])
        vectors = embed_chunks(pieces) if pieces else []
        for i, (piece, vec) in enumerate(zip(pieces, vectors)):
            docs.append({
                "id": f"{file.filename}-{chunk['page']}-{i}",
                "content": piece,
                "page": chunk["page"],
                "content_vector": vec,
            })
    if docs:
        upload_chunks(docs)
    return {"ingested_chunks": len(docs)}

@app.post("/ask")
async def ask(payload: dict):
    result = run_agent(payload["question"])
    return result

@app.get("/health")
async def health():
    return {"status": "ok"}