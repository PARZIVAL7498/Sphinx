# src/sidebar.py
import streamlit as st

from src.llm import DEFAULT_API_VERSION, DEFAULT_DEPLOYMENT, azure_config, validate_azure_key


def _seed_azure_session() -> None:
    config = azure_config()
    st.session_state.setdefault("AZURE_OPENAI_API_KEY", config["api_key"])
    st.session_state.setdefault("AZURE_OPENAI_ENDPOINT", config["endpoint"])
    st.session_state.setdefault("AZURE_OPENAI_DEPLOYMENT", config["deployment"])
    st.session_state.setdefault("AZURE_OPENAI_API_VERSION", config["api_version"])


def render_sidebar():
    _seed_azure_session()

    st.sidebar.markdown("<h2 style='text-align:center; color:#2C3E50;'>🏛️ Project Sphinx</h2>", unsafe_allow_html=True)
    st.sidebar.markdown("<p style='text-align:center; font-size:0.9rem; color:#7F8C8D;'>Multi-Agent Simulation Suite</p>", unsafe_allow_html=True)
    st.sidebar.markdown("---")

    st.sidebar.page_link("app.py", label="🏠 Main Menu")
    st.sidebar.page_link("pages/1_🔬_Adaptive_Strategy_Lab.py", label="🔬 Strategy Lab")
    st.sidebar.page_link("pages/2_⚔️_Colosseum.py", label="⚔️ Colosseum")
    st.sidebar.page_link("pages/3_🏛️_Governance_Lab.py", label="🏛️ Governance Lab")

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Azure AI Foundry**")

    api_key = st.sidebar.text_input(
        "API key",
        type="password",
        value=st.session_state.get("AZURE_OPENAI_API_KEY", ""),
        placeholder="Foundry key",
        key="azure_api_key_global",
    )
    endpoint = st.sidebar.text_input(
        "Endpoint",
        value=st.session_state.get("AZURE_OPENAI_ENDPOINT", ""),
        placeholder="https://<resource>.openai.azure.com",
        key="azure_endpoint_global",
    )
    deployment = st.sidebar.text_input(
        "Deployment",
        value=st.session_state.get("AZURE_OPENAI_DEPLOYMENT", DEFAULT_DEPLOYMENT),
        placeholder=DEFAULT_DEPLOYMENT,
        key="azure_deployment_global",
    )

    st.session_state["AZURE_OPENAI_API_KEY"] = api_key.strip()
    st.session_state["AZURE_OPENAI_ENDPOINT"] = endpoint.strip().rstrip("/")
    st.session_state["AZURE_OPENAI_DEPLOYMENT"] = deployment.strip() or DEFAULT_DEPLOYMENT
    st.session_state.setdefault("AZURE_OPENAI_API_VERSION", DEFAULT_API_VERSION)

    if st.sidebar.button("Apply API Key"):
        st.rerun()

    if api_key and endpoint:
        if validate_azure_key(
            api_key,
            endpoint,
            st.session_state.get("AZURE_OPENAI_API_VERSION", DEFAULT_API_VERSION),
        ):
            st.sidebar.success("Foundry key is valid ✅")
        else:
            st.sidebar.error("Could not reach this Foundry endpoint with that key ❌")
    else:
        st.sidebar.warning("Enter your Azure AI Foundry API key and endpoint.")

    st.sidebar.markdown("---")
    st.sidebar.markdown("<p style='text-align:center; font-size:0.8rem; color:#95A5A6;'>© 2025 Project Sphinx</p>", unsafe_allow_html=True)
