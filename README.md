# Project Sphinx

A neuro-symbolic-causal AI agent for strategic decision-making.

- **Neuro:** an LLM on Azure AI Foundry (a `gpt-4o` deployment) brainstorms several candidate actions.
- **Symbolic:** a guardian rule engine (CSL policies in `policies/`) blocks or repairs unsafe actions.
- **Causal:** a causal-forest engine estimates the impact of each valid action, and the best one is chosen.

## Layout

| Path | Purpose |
|------|---------|
| `app.py`, `src/Main_Menu.py` | Streamlit entry point and main menu |
| `pages/` | Adaptive Strategy Lab, Colosseum, Governance Lab |
| `src/llm.py` | Azure AI Foundry chat client |
| `src/components.py` | Simulators and causal engines |
| `src/csl_guardian.py` | Guardian (CSL policies with legacy Python fallback) |
| `agents/quant_agent.py` | Sphinx-Quant trading agent |
| `policies/` | CSL safety policies |
| `models/` | Trained e-commerce causal model and its training data |
| `causal_training_data_balanced.csv` | Training data for the quant causal engine |
| `scripts/quant/live_paper_trader.py` | Live paper-trading agent |
| `scripts/quant/quant_prepare_training_data.py` | Regenerates the quant training data |
| `scripts/ecom/ecom_train_and_save_model.py` | Retrains the e-commerce causal model |

## Setup

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Create a `.env` file in the project root. The labs and the paper trader read it on startup. See [Usage](#usage) for where each value comes from in Azure AI Foundry.

```bash
AZURE_OPENAI_API_KEY='...'
AZURE_OPENAI_ENDPOINT='https://<resource>.openai.azure.com'
AZURE_OPENAI_DEPLOYMENT='gpt-4o'
AZURE_OPENAI_API_VERSION='2024-10-21'
ALPACA_API_KEY='...'
ALPACA_SECRET_KEY='...'
```

`AZURE_OPENAI_DEPLOYMENT` must match the deployment name in Foundry, which can differ from the model name. `AZURE_OPENAI_API_VERSION` defaults to `2024-10-21` when omitted.

## Usage

The neuro step calls your Azure AI Foundry deployment. A Foundry key is not an OpenAI `sk-` key: requests go to your resource endpoint with the `api-key` header, and the model id is the deployment name.

1. In [Microsoft Foundry](https://ai.azure.com), open the project that hosts the model.
2. Deploy a chat model (this repo calls a deployment named `gpt-4o` unless you set another name).
3. Copy the key, the endpoint (`https://<resource>.openai.azure.com`), and the deployment name from the deployment's code sample.
4. Put them in `.env` as shown above. Alpaca keys are only required for `scripts/quant/live_paper_trader.py`.

**Interactive labs.** `streamlit run app.py` loads `.env` into the sidebar. You can paste a different key, endpoint, or deployment there and click **Apply API Key**. The sidebar checks the key by listing models on that endpoint. Strategy Lab, Colosseum, and Governance Lab stay blocked until both the key and the endpoint are set.

**Paper trading.** `python -m scripts.quant.live_paper_trader` and `agents/quant_agent.py` read the same four `AZURE_OPENAI_*` variables from the environment. They do not use the sidebar.

## Run

Run these from the project root:

```bash
# Interactive labs (Foundry key and endpoint in .env or the sidebar)
streamlit run app.py

# Live quant paper-trading agent (needs .env)
python -m scripts.quant.live_paper_trader
```

## License

GNU AGPLv3, see `LICENSE.md`. Based on original work by Aytug Akarlar.
