"""
Agentic orchestration layer.
Demonstrates: function/tool calling, multi-step reasoning, grounding via RAG,
and a swappable model backend — the core AI-103 'generative AI + agentic solutions' skill.
"""
from openai import AzureOpenAI
from azure.identity import get_bearer_token_provider
from app.config import settings, credential
from app.retrieval.search_client import hybrid_search
from app.ingestion.chunk_embed import embed_chunks
from app.tools.vision_tool import analyze_image
from app.safety.content_safety_client import is_safe

token_provider = get_bearer_token_provider(credential, "https://cognitiveservices.azure.com/.default")
client = AzureOpenAI(azure_endpoint=settings.foundry_endpoint, azure_ad_token_provider=token_provider, api_version="2026-03-17")

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_documents",
            "description": "Search the indexed document corpus for relevant passages.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_image",
            "description": "Analyze an image URL to get a caption and OCR text.",
            "parameters": {
                "type": "object",
                "properties": {"image_url": {"type": "string"}},
                "required": ["image_url"],
            },
        },
    },
]

def _dispatch_tool(name: str, args: dict) -> str:
    if name == "search_documents":
        vec = embed_chunks([args["query"]])[0]
        hits = hybrid_search(args["query"], vec)
        return "\n".join(f"[p{h['page']}] {h['content']}" for h in hits)
    if name == "analyze_image":
        return str(analyze_image(args["image_url"]))
    return "Unknown tool"

def run_agent(user_message: str, history: list[dict] | None = None) -> dict:
    if not is_safe(user_message):
        return {"answer": "I can't process that request.", "citations": []}

    messages = (history or []) + [
        {"role": "system", "content": "You are DocuAgent. Use tools to ground answers in retrieved documents. Cite page numbers."},
        {"role": "user", "content": user_message},
    ]

    response = client.chat.completions.create(
        model=settings.foundry_deployment,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
    )
    msg = response.choices[0].message

    # Multi-step: execute any tool calls, then feed results back
    if msg.tool_calls:
        messages.append(msg)
        for call in msg.tool_calls:
            import json
            args = json.loads(call.function.arguments)
            result = _dispatch_tool(call.function.name, args)
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
        response = client.chat.completions.create(model=settings.foundry_deployment, messages=messages)
        msg = response.choices[0].message

    if not is_safe(msg.content or ""):
        return {"answer": "Response withheld by content safety.", "citations": []}

    return {"answer": msg.content, "citations": []}