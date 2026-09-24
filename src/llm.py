"""Azure AI Foundry chat client used by the labs and quant agents."""
import os

import requests
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

load_dotenv()

DEFAULT_API_VERSION = "2024-10-21"
DEFAULT_DEPLOYMENT = "gpt-4o"


def azure_config() -> dict:
    """Read Azure AI Foundry settings from the environment."""
    return {
        "api_key": os.getenv("AZURE_OPENAI_API_KEY", "").strip(),
        "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT", "").strip().rstrip("/"),
        "deployment": os.getenv("AZURE_OPENAI_DEPLOYMENT", DEFAULT_DEPLOYMENT).strip() or DEFAULT_DEPLOYMENT,
        "api_version": os.getenv("AZURE_OPENAI_API_VERSION", DEFAULT_API_VERSION).strip() or DEFAULT_API_VERSION,
    }


def streamlit_config() -> dict:
    """Prefer values typed in the Streamlit sidebar, then fall back to the environment."""
    import streamlit as st

    config = azure_config()
    return {
        "api_key": (st.session_state.get("AZURE_OPENAI_API_KEY") or config["api_key"]).strip(),
        "endpoint": (st.session_state.get("AZURE_OPENAI_ENDPOINT") or config["endpoint"]).strip().rstrip("/"),
        "deployment": (st.session_state.get("AZURE_OPENAI_DEPLOYMENT") or config["deployment"]).strip() or DEFAULT_DEPLOYMENT,
        "api_version": (st.session_state.get("AZURE_OPENAI_API_VERSION") or config["api_version"]).strip() or DEFAULT_API_VERSION,
    }


def missing_azure_settings(config: dict | None = None) -> list[str]:
    config = config or azure_config()
    missing = []
    if not config["api_key"]:
        missing.append("AZURE_OPENAI_API_KEY")
    if not config["endpoint"]:
        missing.append("AZURE_OPENAI_ENDPOINT")
    return missing


def validate_azure_key(api_key: str, endpoint: str, api_version: str = DEFAULT_API_VERSION) -> bool:
    """Return True when the Foundry key can list models on the given endpoint."""
    endpoint = (endpoint or "").strip().rstrip("/")
    if not api_key or not endpoint:
        return False
    try:
        resp = requests.get(
            f"{endpoint}/openai/models",
            headers={"api-key": api_key},
            params={"api-version": api_version or DEFAULT_API_VERSION},
            timeout=8,
        )
        return resp.status_code == 200
    except Exception:
        return False


def make_chat_model(temperature: float, config: dict | None = None) -> AzureChatOpenAI:
    """Build a chat model against the configured Azure AI Foundry deployment."""
    config = config or azure_config()
    missing = missing_azure_settings(config)
    if missing:
        raise ValueError(
            "Set " + " and ".join(missing) + " in your environment or a .env file."
        )
    return AzureChatOpenAI(
        azure_endpoint=config["endpoint"],
        api_key=config["api_key"],
        azure_deployment=config["deployment"],
        api_version=config["api_version"],
        temperature=temperature,
    )
