# llm_factory.py

from crewai import LLM as CrewLLM
from config.settings import settings


def get_default_llm():
    """
    Returns an LLM object depending on environment:
    - If USE_LOCAL_LLM=true → use local Ollama model (phi3:mini) via OpenAI-compatible API
    - Else → use OpenAI (gpt-4.1-mini or whatever you set)
    """
    if settings.USE_LOCAL_LLM:
        print(f"🧠 Using LOCAL Ollama model: {settings.LOCAL_LLM_MODEL}")
        # Ollama's OpenAI-compatible endpoint
        return CrewLLM(
            model=settings.LOCAL_LLM_MODEL,      # e.g. "phi3:mini"
            base_url="http://localhost:11434/v1", # Ollama OpenAI-compatible URL
            api_key="ollama"                     # dummy, not actually checked
        )
    else:
        print(f"🧠 Using OPENAI model: {settings.OPENAI_LLM_MODEL}")
        return CrewLLM(
            model=settings.OPENAI_LLM_MODEL,     # e.g. "gpt-4.1-mini"
            api_key=settings.OPENAI_API_KEY      # from your .env / settings
        )


