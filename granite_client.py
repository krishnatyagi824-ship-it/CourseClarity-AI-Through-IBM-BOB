"""
granite_client.py
-----------------
IBM watsonx.ai / Granite model client for CourseClarity AI.
Handles authentication and text generation using the ibm-watsonx-ai SDK.

Credential resolution order:
  1. Streamlit secrets (st.secrets) — used on Streamlit Community Cloud.
  2. Environment variables / .env file — used for local development.

API note:
  Uses ModelInference.chat() which calls /ml/v1/text/chat (current endpoint).
  The older generate_text() / /ml/v1/text/generation endpoint is deprecated.
"""

import os
from dotenv import load_dotenv
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenChatParamsMetaNames as ChatParams

load_dotenv()  # no-op if variables are already set (e.g. from platform env)


# Sentinel values that indicate a credential has not been filled in.
_UNFILLED = {"your_ibm_api_key_here", "your_project_id_here", "", None}


def _get_secret(key: str, default: str | None = None) -> str | None:
    """
    Retrieve a configuration value, preferring Streamlit secrets over env vars.
    Falls back to `default` if the key is absent in both sources.
    """
    # Try Streamlit secrets first (available on Streamlit Community Cloud).
    try:
        import streamlit as st
        val = st.secrets.get(key)
        if val not in _UNFILLED:
            return str(val)
    except Exception:
        pass  # Streamlit not importable in non-Streamlit contexts (e.g. test_connection.py)

    return os.getenv(key, default)


def _get_credentials() -> Credentials:
    """Build IBM Cloud credentials from Streamlit secrets or environment variables."""
    api_key = _get_secret("IBM_API_KEY")
    url = _get_secret("IBM_WML_URL", "https://us-south.ml.cloud.ibm.com")

    if api_key in _UNFILLED:
        raise EnvironmentError("not_configured")

    return Credentials(url=url, api_key=api_key)


def get_granite_model() -> ModelInference:
    """Instantiate and return an IBM Granite ModelInference object."""
    credentials = _get_credentials()
    project_id = _get_secret("IBM_PROJECT_ID")

    if project_id in _UNFILLED:
        raise EnvironmentError("not_configured")

    model_id = _get_secret("GRANITE_MODEL_ID", "ibm/granite-4-h-small")

    # Chat-API generation parameters (GenChatParamsMetaNames — SDK 1.9+)
    # Note: the chat endpoint uses MAX_TOKENS, not MAX_NEW_TOKENS.
    params = {
        ChatParams.MAX_TOKENS:         int(_get_secret("MAX_NEW_TOKENS", "1024")),
        ChatParams.TEMPERATURE:        float(_get_secret("TEMPERATURE", "0.3")),
        ChatParams.TOP_P:              float(_get_secret("TOP_P", "0.9")),
        ChatParams.REPETITION_PENALTY: 1.1,
    }

    model = ModelInference(
        model_id=model_id,
        credentials=credentials,
        project_id=project_id,
        params=params,
    )
    return model


def generate_text(prompt: str) -> str:
    """
    Send a prompt to IBM Granite via the chat API and return the response text.

    Converts the legacy prompt string into a single user message so all
    existing agent prompt templates continue to work unchanged.

    Uses ModelInference.chat() which calls /ml/v1/text/chat — the current,
    non-deprecated endpoint.

    Args:
        prompt: The full prompt string to send.

    Returns:
        The model's generated response as a plain string.

    Raises:
        EnvironmentError: If IBM credentials are missing/invalid.
        Exception: On API errors from watsonx.ai.
    """
    model = get_granite_model()

    # Wrap the prompt as a single user turn for the chat endpoint.
    messages = [{"role": "user", "content": prompt}]
    response = model.chat(messages=messages)

    # The chat response is a dict:
    # {"choices": [{"message": {"role": "assistant", "content": "<text>"}}], ...}
    try:
        text = response["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        # Graceful fallback: coerce whatever we got to a string.
        text = str(response)

    return text.strip()
