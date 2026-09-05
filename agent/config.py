import os
import time
import logging
from typing import Any
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)

DATA_MODE = os.getenv("DATA_MODE", "synthetic")

if DATA_MODE == "synthetic":
    logger.warning(
        "[DATA MODE: SYNTHETIC] Running with synthetic evaluation/demo data. "
        "No production merchant data is being used."
    )

def get_text_llm() -> BaseChatModel:
    """
    Returns the configured text LLM based on LLM_PROVIDER environment variable.
    Defaults to groq (llama-3.3-70b-versatile) if not specified.
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

async def ainvoke_llm(llm: BaseChatModel, messages: Any) -> Any:
    """
    Asynchronous LLM invocation with structured telemetry, latency profiling,
    and token usage capture for Groq & OpenAI.
    """
    start = time.perf_counter()
    provider = os.environ.get("LLM_PROVIDER", "groq")
    model_name = getattr(llm, "model_name", getattr(llm, "model", "llama-3.3-70b-versatile"))

    try:
        response = await llm.ainvoke(messages)
        elapsed_ms = (time.perf_counter() - start) * 1000

        # Extract token usage metadata from response
        metadata = getattr(response, "response_metadata", {}) or {}
        usage = (
            metadata.get("token_usage")
            or metadata.get("usage")
            or getattr(response, "usage_metadata", {})
            or {}
        )
        prompt_tokens = usage.get("prompt_tokens") or usage.get("input_tokens") or 0
        completion_tokens = usage.get("completion_tokens") or usage.get("output_tokens") or 0
        total_tokens = usage.get("total_tokens") or (prompt_tokens + completion_tokens)

        logger.info(
            "LLM_CALL_SUCCESS provider=%s model=%s latency_ms=%.0f",
            provider,
            model_name,
            elapsed_ms,
        )
        if total_tokens > 0:
            logger.info(
                "LLM_USAGE input=%s output=%s total=%s",
                prompt_tokens,
                completion_tokens,
                total_tokens,
            )

        return response

    except Exception:
        logger.exception("LLM_CALL_FAILED provider=%s model=%s", provider, model_name)
        raise

