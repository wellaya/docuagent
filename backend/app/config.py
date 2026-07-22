import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential

load_dotenv()

class Settings:
    search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    search_index = os.getenv("AZURE_SEARCH_INDEX", "docuagent-index")
    docintel_endpoint = os.getenv("AZURE_DOCINTEL_ENDPOINT")
    speech_endpoint = os.getenv("AZURE_SPEECH_ENDPOINT")
    speech_region = os.getenv("AZURE_SPEECH_REGION", "eastus")
    contentsafety_endpoint = os.getenv("AZURE_CONTENTSAFETY_ENDPOINT")
    foundry_endpoint = os.getenv("AZURE_FOUNDRY_ENDPOINT")
    foundry_deployment = os.getenv("AZURE_FOUNDRY_DEPLOYMENT", "gpt-5.4-mini")

settings = Settings()
credential = DefaultAzureCredential()