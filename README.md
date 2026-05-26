# ANHS Streamlit — upload this entire folder to GitHub

This folder has **everything** needed for [Streamlit Cloud](https://share.streamlit.io).  
Upload **all files and subfolders** to your repo (replace what is there now).

## What’s inside

```text
ANHS-streamlit-deploy/
  app.py                 ← Streamlit entry (set this in Streamlit Cloud)
  anhs_data.py           ← load/save school data
  requirements.txt
  data/
    school_data.json     ← your numbers (edit via app or file)
  dashboard/
    index.html           ← charts & UI
  .streamlit/
    config.toml          ← theme (optional)
  DEPLOY.md              ← troubleshooting
```

## GitHub steps

1. Open your repo on GitHub (e.g. `cometooo23-design/ANHS`).
2. **Add file** → **Upload files**.
3. Drag **every item** from this folder into the upload area (include `data`, `dashboard`, `.streamlit`).
4. Commit to **main**.
5. Streamlit Cloud → your app → **Manage app** → **Reboot app**.
6. Confirm **Main file path** is `app.py`.

## Run on your computer

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Do not upload

Old drafts like `arayat_nhs_dashboard_v4.html` are **not** in this folder on purpose.  
Use only `dashboard/index.html` here.
