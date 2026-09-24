# Project Sphinx

Project Sphinx is an ecosystem for trustworthy strategic AI agents. Each decision is produced by three layers working in order: a language model proposes actions, a formally checked rule engine blocks or repairs unsafe ones, and a causal model estimates which surviving action is worth taking.

The interactive labs are a Streamlit app. A separate paper-trading agent applies the same loop to BTC/USD on Alpaca's paper API.

## How a decision is made

1. **Neuro.** An Azure AI Foundry chat deployment (default name `gpt-4o`) brainstorms several candidate actions and must call tools before it commits.
2. **Symbolic.** A guardian checks each candidate against a CSL policy in [`policies/`](policies/). CSL-Core verifies those policies with Z3 when the policy is loaded. If `csl-core` cannot be imported, the guardian falls back to the same limits written in Python.
3. **Causal.** A [Causal Forest](https://econml.azurewebsites.net/) (`econml.dml.CausalForestDML`) estimates the effect of each valid action. The agent keeps the action with the best estimated outcome. The Strategy Lab and Governance Lab can also explain that estimate with SHAP.

E-commerce actions are a weekly price change and an advertising budget. Trading actions are `BUY`, `SELL`, `SHORT`, or `HOLD`, each with an amount from 0 to 1.

## Interactive labs

Start them with `streamlit run app.py`. The main menu (v1.7.0, "The Great Unification") links to three pages. Strategy Lab, Colosseum, and Governance Lab stay blocked until an Azure AI Foundry key and endpoint are set.

### Adaptive Strategy Lab

A single-agent walkthrough of a simulated online store. You set a strategic goal. A small interpreter model turns that goal into a trust multiplier (about 100,000 for extreme profit, 200,000 for a balanced goal, 500,000 for extreme brand trust; the default is 120,000). The store then advances week by week.

You can run three agent types side by side in spirit:

| Agent | Tools |
| --- | --- |
| Full Neuro-Symbolic-Causal (Sphinx) | Rule check, then causal estimate |
| LLM + Symbolic | Rule check only |
| LLM-Only | No tools; the guardian still repairs the action before it is applied |

The store starts near price $100, weekly ad spend $500, and brand trust 0.7. Unit cost is $50. Demand responds to price, ads, trust, and a seasonal term. The lab records profit, sales, and trust, and opens an explanation view for the chosen action.

### The Colosseum

A multi-agent contest in a shared store. You name gladiators and assign one of three doctrines: full neuro-symbolic-causal, LLM plus symbolic rules, or LLM-only. They act in the same week, and an agent whose running result falls below −25,000 is eliminated. Charts track the bout.

### Governance Lab

A local voting demo, not a connection to a live chain. Three treasury proposals are fixed economic actions:

| Proposal | Price change | Weekly ad spend |
| --- | ---: | ---: |
| Aggressive Growth | −20% | $3,000 |
| Balanced Approach | 0% | $1,500 |
| Profitability Focus | +10% | $500 |

**Simulate Impact** scores the proposal with the e-commerce causal model and a SHAP explanation, against a fixed store state (price $100, trust 0.7, ads $1,000). You then cast an AYE vote with a token slider and a conviction multiplier (1x, 2x, 4x, or 6x). **Simulate 100 Community Voters** fills in a synthetic electorate. Votes live in the browser session only.

## E-commerce safety limits

[`policies/ecommerce_guard.csl`](policies/ecommerce_guard.csl) blocks an action when any of these fail. The Python fallback in [`src/csl_guardian.py`](src/csl_guardian.py) enforces the same defaults.

| Limit | Default |
| --- | --- |
| Weekly discount | 40% |
| Weekly price increase | 50% |
| Price ceiling | $150 |
| Minimum profit margin | 15% above a $50 unit cost, plus a 1% safety buffer |
| Weekly ad spend | $5,000 |
| Week-over-week ad increase | $1,000 |
| Negative ad spend | rejected |

If a proposal fails, the Strategy Lab asks the guardian to repair it and tells the agent what was changed.

## Sphinx-Quant

[`agents/quant_agent.py`](agents/quant_agent.py) is the trading agent. It must propose four hypotheses, validate each with the guardian, estimate profit only for valid ones, and return one JSON decision.

[`policies/quant_guard.csl`](policies/quant_guard.csl) rejects a non-HOLD action when the portfolio or price is invalid, a SELL when there is no long position, a SHORT when shorting is disabled, or an amount above the configured cap. Defaults in [`src/config.py`](src/config.py): at most 95% of the portfolio long, 50% short, shorting allowed, amount at most 1.0. The paper endpoint is `https://paper-api.alpaca.markets`. The traded pair is BTC/USD (`BTCUSD` on Alpaca).

The causal model is fit at startup from [`causal_training_data_balanced.csv`](causal_training_data_balanced.csv). Features are RSI(14), MACD histogram, 15-period rate of change, price versus the 20-day average, the 20-day versus 100-day average, Bollinger position, and ATR(14).

[`scripts/quant/live_paper_trader.py`](scripts/quant/live_paper_trader.py) runs that agent once at startup and then every day at 00:00 UTC, places paper orders, and writes `trader_activity.log`. It also imports the `schedule` package, which is not pinned in `requirements.txt`:

```bash
pip install schedule
```

Running `python -m agents.quant_agent` sends two scripted market states (one bullish, one bearish) through the live model and prints whether the JSON decision matched BUY or SHORT. That requires Foundry credentials and the training CSV. It is not a pytest suite.

## Layout

| Path | Purpose |
| --- | --- |
| [`app.py`](app.py) | Streamlit entry point |
| [`src/Main_Menu.py`](src/Main_Menu.py) | Main menu |
| [`pages/`](pages/) | Strategy Lab, Colosseum, Governance Lab |
| [`src/llm.py`](src/llm.py) | Azure AI Foundry chat client |
| [`src/sidebar.py`](src/sidebar.py) | Navigation and Foundry credentials |
| [`src/components.py`](src/components.py) | Store simulators, market simulator, causal engines |
| [`src/csl_guardian.py`](src/csl_guardian.py) | Guardian: CSL policies, Python fallback |
| [`src/config.py`](src/config.py) | Quant features, risk limits, Alpaca paper URL |
| [`agents/quant_agent.py`](agents/quant_agent.py) | Sphinx-Quant agent |
| [`policies/`](policies/) | CSL safety policies |
| [`models/`](models/) | `trained_causal_model.pkl`, loaded by the labs |
| [`causal_training_data_balanced.csv`](causal_training_data_balanced.csv) | Training data for the quant causal engine |
| [`scripts/quant/live_paper_trader.py`](scripts/quant/live_paper_trader.py) | Scheduled paper-trading agent |
| [`scripts/quant/quant_prepare_training_data.py`](scripts/quant/quant_prepare_training_data.py) | Rebuilds the quant training CSV from Alpaca bars |
| [`scripts/ecom/ecom_train_and_save_model.py`](scripts/ecom/ecom_train_and_save_model.py) | Retrains the e-commerce causal model |

## Requirements

- Python 3.10 or newer (NumPy 2.2 requires it)
- An Azure AI Foundry chat deployment for every lab and for both quant agents
- Alpaca paper keys for the live trader and for regenerating quant training data
- The labs also need `models/trained_causal_model.pkl`. If that file is missing, Strategy Lab and Governance Lab stop with a file-not-found error. Retrain it with the command in [Retrain the models](#retrain-the-models).

Pinned libraries live in [`requirements.txt`](requirements.txt): Streamlit 1.49, LangChain, `openai` 1.105, EconML, LightGBM, SHAP, Z3, Alpaca's trade API, and `csl-core`.

## Setup

From the project root:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

On macOS or Linux, activate with `source venv/bin/activate` instead.

Create a `.env` file in the project root. It is gitignored. The labs and the paper trader read it on startup.

```bash
AZURE_OPENAI_API_KEY='...'
AZURE_OPENAI_ENDPOINT='https://<resource>.openai.azure.com'
AZURE_OPENAI_DEPLOYMENT='gpt-4o'
AZURE_OPENAI_API_VERSION='2024-10-21'
ALPACA_API_KEY='...'
ALPACA_SECRET_KEY='...'
```

`AZURE_OPENAI_DEPLOYMENT` must match the deployment name in Foundry, which can differ from the model name. `AZURE_OPENAI_API_VERSION` defaults to `2024-10-21` when omitted. Alpaca keys are required only for `scripts/quant/live_paper_trader.py`, `scripts/quant/quant_prepare_training_data.py`, and any run that pulls live bars.

## Configure Foundry

The neuro step calls your Azure AI Foundry deployment. A Foundry key is not an OpenAI `sk-` key: requests go to your resource endpoint with the `api-key` header, and the model id is the deployment name.

1. In [Microsoft Foundry](https://ai.azure.com), open the project that hosts the model.
2. Deploy a chat model. This repo calls a deployment named `gpt-4o` unless you set another name.
3. Copy the key, the endpoint (`https://<resource>.openai.azure.com`), and the deployment name from that deployment's code sample.
4. Put them in `.env` as shown above.

`streamlit run app.py` loads `.env` into the sidebar. You can paste a different key, endpoint, or deployment there and click **Apply API Key**. The sidebar checks the key by listing models on that endpoint (`GET {endpoint}/openai/models`).

`python -m scripts.quant.live_paper_trader` and `python -m agents.quant_agent` read the four `AZURE_OPENAI_*` variables from the environment. They do not use the sidebar.

## Run

Run these from the project root:

```bash
streamlit run app.py
python -m scripts.quant.live_paper_trader
```

The paper trader needs `.env`, the `schedule` package, and `causal_training_data_balanced.csv` in the working directory. It fits a causal forest on startup, so the first launch is slower than a later decision.

## Retrain the models

Both commands are run from the project root.

E-commerce model used by the labs. The script simulates 2,000 runs of 50 weeks, fits a causal forest on profit change, and writes `trained_causal_model.pkl` in the current directory. The labs load `models/trained_causal_model.pkl`, so move the file after training:

```bash
python -m scripts.ecom.ecom_train_and_save_model
move trained_causal_model.pkl models\
```

Quant training CSV. This downloads daily BTC/USD bars from Alpaca (about five years), builds the features in `src/config.py`, and labels a 3-day forward return for BUY, SELL, SHORT, and HOLD. It overwrites `causal_training_data_balanced.csv` and needs Alpaca keys:

```bash
python -m scripts.quant.quant_prepare_training_data
```

## License

GNU AGPLv3. See [`LICENSE.md`](LICENSE.md). Based on original work by Aytug Akarlar.
