from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from app.config import settings, credential

client = DocumentIntelligenceClient(endpoint=settings.docintel_endpoint, credential=credential)

def extract_text_and_tables(file_bytes: bytes) -> dict:
    poller = client.begin_analyze_document(
        "prebuilt-layout",
        body=file_bytes,
        content_type="application/octet-stream",
    )
    result = poller.result()
    chunks = []
    for page in result.pages:
        page_text = " ".join([line.content for line in (page.lines or [])])
        chunks.append({"page": page.page_number, "text": page_text})
    tables = [t.as_dict() for t in (result.tables or [])]
    return {"chunks": chunks, "tables": tables}