from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import AnalyzeTextOptions
from app.config import settings, credential

client = ContentSafetyClient(endpoint=settings.contentsafety_endpoint, credential=credential)

def is_safe(text: str) -> bool:
    result = client.analyze_text(AnalyzeTextOptions(text=text))
    return all(cat.severity < 4 for cat in result.categories_analysis)