import requests
from app.config import settings, credential

def analyze_image(image_url: str) -> dict:
    token = credential.get_token("https://cognitiveservices.azure.com/.default").token
    resp = requests.post(
        f"{settings.docintel_endpoint.replace('cognitiveservices', 'vision')}/computervision/imageanalysis:analyze",
        params={"api-version": "2026-03-17", "features": "caption,read"},
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"url": image_url},
    )
    resp.raise_for_status()
    return resp.json()