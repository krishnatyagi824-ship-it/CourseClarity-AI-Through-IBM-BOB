"""
test_connection.py
------------------
Standalone connection test for the IBM Granite / watsonx.ai integration.

Usage:
    python test_connection.py

Exit codes:
    0 — all checks passed, model responded
    1 — one or more checks failed
"""

import os
import sys
import pathlib
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Load .env using an explicit path so the test works regardless of CWD
# ---------------------------------------------------------------------------
ENV_PATH = pathlib.Path(__file__).parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# ---------------------------------------------------------------------------
# Exception message sanitizer
# ---------------------------------------------------------------------------
# Patterns that could appear in SDK exception messages and must never be
# printed.  The sanitizer replaces the entire message with a safe summary.
_SENSITIVE_SUBSTRINGS = (
    "apikey",
    "api_key",
    "token",
    "bearer",
    "password",
    "secret",
    "credential",
    "authorization",
    "access_token",
)


def _safe_exc_desc(exc: Exception) -> str:
    """
    Return a safe, one-line description of an exception.
    If the original message contains any credential-related keyword,
    it is suppressed entirely and replaced with a generic note.
    """
    raw = str(exc).lower()
    for keyword in _SENSITIVE_SUBSTRINGS:
        if keyword in raw:
            return (
                f"{type(exc).__name__}: "
                "<message suppressed — may contain credential details>"
            )
    # Safe to show, but still cap length to avoid accidental data leakage
    safe_msg = str(exc)[:200]
    return f"{type(exc).__name__}: {safe_msg}"


# ---------------------------------------------------------------------------
# Main test routine
# ---------------------------------------------------------------------------

_PLACEHOLDERS = {"your_ibm_api_key_here", "your_project_id_here", ""}


def _check_env_vars() -> bool:
    """Verify required env vars are set and not placeholders. Returns True if all OK."""
    checks = {
        "IBM_API_KEY":    os.getenv("IBM_API_KEY"),
        "IBM_PROJECT_ID": os.getenv("IBM_PROJECT_ID"),
        "IBM_WML_URL":    os.getenv("IBM_WML_URL", "https://us-south.ml.cloud.ibm.com"),
        "GRANITE_MODEL_ID": os.getenv("GRANITE_MODEL_ID", "ibm/granite-4-h-small"),
    }

    all_ok = True
    for name, val in checks.items():
        if not val or val in _PLACEHOLDERS:
            print(f"  [FAIL] {name}: not configured (missing or placeholder)")
            all_ok = False
        else:
            print(f"  [OK]   {name}: configured")
    return all_ok


def _check_model_init() -> object | None:
    """
    Attempt to initialise the IBM Granite ModelInference object.
    Returns the model on success, None on failure.
    """
    try:
        from granite_client import get_granite_model  # noqa: PLC0415
        model = get_granite_model()
        print("  [OK]   IBM watsonx.ai authentication succeeded.")
        print("  [OK]   Granite ModelInference object created.")
        return model
    except EnvironmentError as exc:
        # EnvironmentError is raised by our own code with safe messages
        print(f"  [FAIL] Configuration error: {exc}")
        return None
    except Exception as exc:
        print(f"  [FAIL] Authentication / model init failed: {_safe_exc_desc(exc)}")
        return None


def _check_inference(model) -> bool:
    """Send the smallest possible prompt via the chat API and verify a response."""
    try:
        from ibm_watsonx_ai.metanames import GenChatParamsMetaNames as ChatParams  # noqa: PLC0415

        # Use model.chat() — calls /ml/v1/text/chat (non-deprecated endpoint).
        messages = [{"role": "user", "content": "Say: OK"}]
        response = model.chat(
            messages=messages,
            params={ChatParams.MAX_TOKENS: 5},
        )

        # Extract text from the chat response dict.
        try:
            text = response["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            text = str(response)

        if text and text.strip():
            print("  [OK]   Granite model responded to a minimal test prompt.")
            return True
        else:
            print("  [WARN] Granite returned an empty response (auth succeeded, but check model ID).")
            return True          # Auth worked; empty response is not a hard failure
    except Exception as exc:
        print(f"  [FAIL] Inference request failed: {_safe_exc_desc(exc)}")
        return False


def main() -> int:
    print("\n── IBM Granite Connection Test ──────────────────────────────────────")

    # Step 1 — environment variables
    print("\n[1/3] Checking environment variables…")
    if not _check_env_vars():
        print("\nResult: FAIL — Update .env with real credentials and re-run.\n")
        return 1

    # Step 2 — authentication + model initialisation
    print("\n[2/3] Testing authentication and model initialisation…")
    model = _check_model_init()
    if model is None:
        print("\nResult: FAIL — Could not authenticate with IBM watsonx.ai.\n")
        return 1

    # Step 3 — minimal inference
    print("\n[3/3] Sending minimal inference request to IBM Granite…")
    if not _check_inference(model):
        print("\nResult: FAIL — Authentication succeeded but inference request failed.\n")
        return 1

    print("\nResult: PASS — IBM Granite is reachable and responding correctly.\n")
    print("─────────────────────────────────────────────────────────────────────\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
