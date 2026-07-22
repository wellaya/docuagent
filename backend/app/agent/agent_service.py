"""
Agentic orchestration layer.
Demonstrates:
- Function/tool calling
- Multi-step reasoning
- RAG grounding
- Azure AI Foundry model backend
"""

import json
from openai import AzureOpenAI
from azure.identity import get_bearer_token_provider

from app.config import settings, credential
from app.retrieval.search_client import hybrid_search
from app.ingestion.chunk_embed import embed_chunks
from app.tools.vision_tool import analyze_image
from app.safety.content_safety_client import is_safe


token_provider = get_bearer_token_provider(
    credential,
    "https://cognitiveservices.azure.com/.default"
)


client = AzureOpenAI(
    azure_endpoint=settings.foundry_endpoint,
    azure_ad_token_provider=token_provider,
    api_version="2025-04-01-preview",
)


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_documents",
            "description": "Search indexed documents for relevant information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string"
                    }
                },
                "required": [
                    "query"
                ],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_image",
            "description": "Analyze an image and extract useful information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "image_url": {
                        "type": "string"
                    }
                },
                "required": [
                    "image_url"
                ],
            },
        },
    },
]


def _dispatch_tool(name: str, args: dict) -> str:

    if name == "search_documents":

        query = args["query"]

        vector = embed_chunks([query])[0]

        hits = hybrid_search(
            query,
            vector
        )

        if not hits:
            return "No relevant documents found."

        return "\n".join(
            f"[Page {h['page']}] {h['content']}"
            for h in hits
        )


    if name == "analyze_image":

        return str(
            analyze_image(
                args["image_url"]
            )
        )


    return "Unknown tool"



def run_agent(
    user_message: str,
    history: list[dict] | None = None
) -> dict:


    if not is_safe(user_message):
        return {
            "answer": "I can't process that request.",
            "citations": []
        }


    print("========== Azure OpenAI Debug ==========")
    print("Endpoint:", settings.foundry_endpoint)
    print("Deployment:", settings.foundry_deployment)
    print("========================================")


    messages = []


    if history:
        messages.extend(history)


    messages.append(
        {
            "role": "system",
            "content": (
                "You are DocuAgent. "
                "Answer using retrieved document information. "
                "Always mention page numbers when available."
            ),
        }
    )


    messages.append(
        {
            "role": "user",
            "content": user_message,
        }
    )


    response = client.chat.completions.create(
        model=settings.foundry_deployment,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
    )


    msg = response.choices[0].message


    if msg.tool_calls:

        messages.append(
            msg
        )


        for call in msg.tool_calls:

            args = json.loads(
                call.function.arguments
            )


            tool_result = _dispatch_tool(
                call.function.name,
                args
            )


            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": tool_result,
                }
            )


        response = client.chat.completions.create(
            model=settings.foundry_deployment,
            messages=messages,
        )


        msg = response.choices[0].message



    answer = msg.content or ""


    if not is_safe(answer):
        return {
            "answer": "Response withheld by content safety.",
            "citations": []
        }


    return {
        "answer": answer,
        "citations": []
    }
