# Marketplace Customer Complaint Management System

**Student:** Diti Solanki 
**SAP ID:** 60004230033  
**Roll Number:** C054    
**Academic year:** 2026-2027

## 1. Project overview

This beginner-friendly OJT prototype accepts a marketplace complaint, categorizes it, assigns a priority, creates a short summary, and recommends a next step. The Streamlit app keeps complaint history in the current session only.

It does not process payments, issue refunds, contact sellers or delivery partners, or change customer accounts.

## 2. The three-agent workflow

The orchestrator runs exactly three agents in order:

1. **Classification Agent** (`agents/classification_agent.py`) uses keyword rules to choose Delivery, Product Quality, Payment, Refund, or Other and explains the match.
2. **Priority Agent** (`agents/priority_agent.py`) applies simple rules to assign Low, Medium, or High and gives a reason. Damage and duplicate charges are High; ordinary delivery, refund, and payment issues are Medium; general questions are Low.
3. **GPT Resolution Assistant Agent** (`agents/resolution_agent.py`) optionally uses OpenAI GPT to summarize the complaint in one short factual sentence. Python rules select the resolution recommendation locally.

`services/orchestrator.py` coordinates these agents; it is not an additional agent.

## 3. Project structure

```text
ojt_marketplace_multi_agent/
|-- app.py
|-- agents/
|   |-- __init__.py
|   |-- classification_agent.py
|   |-- priority_agent.py
|   `-- resolution_agent.py
|-- services/
|   |-- __init__.py
|   `-- orchestrator.py
|-- tests/
|   |-- test_agents.py
|   `-- test_orchestrator.py
|-- requirements.txt
|-- .env.example
|-- .gitignore
|-- README.md
|-- Dockerfile
`-- pytest.ini
```

## 4. Technology and prerequisites

- Python 3.10 or newer
- Streamlit for the web interface
- OpenAI's official Python SDK for optional GPT summaries
- `python-dotenv` for local `.env` settings
- pytest for automated checks

No database is required.

## 5. Windows PowerShell setup

The project files stay directly in `C:\Users\LENOVO\ojt_marketplace_multi_agent`. Run these commands in PowerShell:

```powershell
Set-Location C:\Users\LENOVO\ojt_marketplace_multi_agent
if (-not (Test-Path .venv\Scripts\python.exe)) { py -m venv .venv }
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
notepad .env
streamlit run app.py
```

If `.venv\Scripts\python.exe` already exists and works, reuse it rather than running `python -m venv .venv` over it again. If PowerShell blocks activation, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` once, then activate the environment.

Streamlit normally opens at `http://localhost:8501`. To choose another local port, run `streamlit run app.py --server.port 8502`.

## 6. Configure the OpenAI key privately

For local use, edit `.env` and set:

```text
OPENAI_API_KEY=your_private_key_here
OPENAI_MODEL=gpt-4o-mini
```

Replace the placeholder with your own API key. Keep `.env` private: it is ignored by Git and must not be uploaded or committed. `OPENAI_MODEL` is optional; the default is `gpt-4o-mini`.

Without a key, the app does not call OpenAI and Agent 3 uses a short local extractive summary. The UI explains this fallback. If a GPT request fails, the agent also falls back safely.

## 7. Try the app

```powershell
streamlit run app.py
```

Try these complaints:

- My order was delivered late.
- I received a damaged product.
- I was charged twice for the same order.
- My refund has not arrived.

The app shows each agent's result, the final complaint ID, a recommended resolution, and session-only history. Customer name and order ID are optional and are not sent to GPT. Use **Clear history** to clear the current session's list.

## 8. Run the tests

```powershell
python -m pytest -v
```

The GPT tests use mocked responses. They do not make real API calls and need no API key or paid API access.

## 9. Deploy on Streamlit Community Cloud

Streamlit Community Cloud deploys from a GitHub repository and currently describes its service as free. See the [official deploy guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy).

1. Push this project to a GitHub repository. Include `app.py`, `agents/`, `services/`, `requirements.txt`, and this README. Do not upload `.env` or `.venv/`; `.gitignore` excludes them.
2. Go to [share.streamlit.io](https://share.streamlit.io/) and sign in with GitHub.
3. Choose **Create app**, select the repository and branch, and set the main file to `app.py`.
4. In **Advanced settings**, select Python 3.11 if available, then deploy.
5. After deployment, open the app settings and add secrets in TOML format:

   ```toml
   OPENAI_API_KEY = "your_private_key_here"
   OPENAI_MODEL = "gpt-4o-mini"
   ```

   Store the real key only in the app's **Secrets** settings, never in GitHub. The app reads Streamlit secrets at runtime. `OPENAI_MODEL` is optional.
6. Open the app URL, try a sample complaint, and review the app logs if startup fails. Community Cloud apps can sleep after inactivity and wake when visited again.

The app works without the API secret by using its local summary fallback. This project has not been deployed as part of this setup.

## 10. GPT usage and privacy

Only Agent 3 makes an OpenAI request. It sends the complaint text and category with a short system instruction and a 60-token output limit. It does not send customer name, order ID, complaint history, priority, priority reason, or unrelated details. GPT only summarizes; Python rules select the recommendation. The API key is never displayed in the app or returned in complaint history.

## 11. Demonstration video

Run the app locally, show a late delivery and a damaged product complaint, and explain each agent's category, priority, summary, and recommendation. Show the session history and clear-history button. Review the recording for private keys or personal data before sharing it.

## 12. Limitations

This is an educational prototype, not a production support system. Keyword rules may miss nuanced complaints. Recommendations are informational only; the application does not perform real marketplace transactions.
