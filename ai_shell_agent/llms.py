from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
import os

PROVIDER = os.environ.get("PROVIDER", "google")
TEMPERATURE = os.environ.get("TEMPERATURE", 0)

def get_provider():
    return PROVIDER

def get_model():
    if PROVIDER == "google":
        return "gemini-2.0-flash"
    else:
        return "gpt-4o-mini"

def get_llm():
    model = get_model()
    if PROVIDER == "google":
        return ChatGoogleGenerativeAI(model=model, temperature=TEMPERATURE)
    else:
        return ChatOpenAI(model=model, temperature=TEMPERATURE)

