"""
LLM provider configuration factory for DisputeSentinel AI.
"""
import os
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

def get_text_llm() -> BaseChatModel:
    """
    Returns the configured text LLM based on LLM_PROVIDER environment variable.
    Defaults to groq if not specified.
    """
    provider = os.environ.get("LLM_PROVIDER", "groq").lower()
    
    if provider == "openai":
        return ChatOpenAI(
            model="gpt-4o",
            temperature=0,
            api_key=os.environ.get("OPENAI_API_KEY")
        )
    else:
        return ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0,
            api_key=os.environ.get("GROQ_API_KEY")
        )

def get_vision_llm() -> BaseChatModel:
    """
    Returns Vision LLM model.
    Uses OpenAI gpt-4o if OPENAI_API_KEY is available,
    otherwise uses Groq's high-speed multimodal vision model llama-3.2-11b-vision-preview.
    """
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key and not openai_key.startswith("your-") and not openai_key.startswith("sk-placeholder"):
        return ChatOpenAI(
            model="gpt-4o",
            temperature=0,
            api_key=openai_key
        )
    
    # Use Groq Vision model
    groq_key = os.environ.get("GROQ_API_KEY")
    return ChatGroq(
        model="llama-3.2-11b-vision-preview",
        temperature=0,
        api_key=groq_key
    )
