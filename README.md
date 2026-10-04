# CareCompass AI

Multi-agent care navigation and outreach for hospitals, built with Streamlit and Google Gemini.
Based on the healthcare care-navigation project in the Pak Angels white paper *AI Across 24 Industries*.

## Agents

| Agent | Job | Human control |
|---|---|---|
| Safety screen | Rule-based emergency detection before any AI call | Always shows 1122 guidance |
| Triage | Urgency and department from the patient's words (Gemini) | Never diagnoses or prescribes |
| Scheduler | Finds open slots and books with consent | Patient confirms |
| Follow-up | Finds due follow-ups, drafts reminders | Staff approve |
| Outreach | Finds eligible groups (antenatal, immunization, diabetes, BP) and drafts invitations | Staff approve |

Extra features: English, Urdu and Roman Urdu; demo mode without a key; sidebar Tech panel for judges (AI status, connection test, live trace of each step, tech stack); audit log with CSV export; operations dashboard; consent checkbox before booking.

## Run locally

```bash
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # then paste your Gemini key
streamlit run app.py
```

Get a key at https://aistudio.google.com/apikey. Without a key the app runs in demo mode.

## Deploy on Streamlit Community Cloud

1. Push this folder to GitHub. `.gitignore` already excludes `.env` and `.streamlit/secrets.toml`, so your key is not uploaded.
2. On share.streamlit.io choose the repo and `app.py`.
3. Open **App settings > Secrets** and paste: `GEMINI_API_KEY = "your-key"`.

Before the first push, run `git status` and confirm no secrets file is listed. If a key was ever committed, revoke it and create a new one.

## Tests

```bash
pip install -r requirements-dev.txt && pytest
```

## Important

This is a demo with fictional patients in `datasets/sample_data.py`. It is not a medical device. Before real use you need clinical sign-off, a real patient database, authentication, privacy compliance and a messaging integration. Replace the sample data and keep staff approval on all outgoing messages.

## Where the Gemini key can go

Put it in `.streamlit/secrets.toml` (local) or in the Secrets box of Streamlit Community Cloud. The app also accepts the `GEMINI_API_KEY` environment variable or a `.env` file. The Tech panel shows which source was used, and **Test Gemini connection** shows Google's real error if the key is rejected.

## Key not connecting?

Run `python check_key.py`. It says whether the key file was found and whether Google accepts the key, with Google's own error message if not.
