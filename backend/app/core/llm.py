import os
import json
import re
from typing import Optional, Type, TypeVar
from pydantic import BaseModel
from app.core.config import settings
from app.models.schemas import RouterOutput, ToneOutput, PolicyOutput

T = TypeVar("T", bound=BaseModel)

def get_llm():
    """Initializes Google Gemini via langchain_google_genai or returns None if no key configured."""
    api_key = settings.GOOGLE_API_KEY or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return None
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        # Support gemini-2.5-flash, gemini-2.0-flash, or gemini-1.5-flash
        model_name = settings.LLM_MODEL or "gemini-2.5-flash"
        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.0
        )
    except Exception as e:
        print(f"Warning: Failed to initialize ChatGoogleGenerativeAI: {e}")
        return None

def extract_structured_data(prompt: str, schema_cls: Type[T], default_factory) -> T:
    """
    Invokes Gemini with structured output if available; otherwise uses deterministic entity parsing.
    """
    llm = get_llm()
    if llm and not settings.MOCK_LLM:
        try:
            # Langchain structured output support
            structured_llm = llm.with_structured_output(schema_cls)
            result = structured_llm.invoke(prompt)
            if isinstance(result, schema_cls):
                return result
            if isinstance(result, dict):
                return schema_cls(**result)
        except Exception as e:
            print(f"Structured output LLM call failed, falling back to deterministic parser: {e}")

    return default_factory()
