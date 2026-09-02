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
    Always returns OpenAI for vision tasks.
    """
    return ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        api_key=os.environ.get("OPENAI_API_KEY")
    )
