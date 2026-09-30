# streamlit-keepalive

Keeps my Streamlit Community Cloud apps awake. A GitHub Actions job opens each
app in headless Chromium every 6 hours and clicks the wake button if an app
has gone to sleep.

## Setup

1. Push this folder to a **public** GitHub repo (Actions minutes are free there).
2. Repo → **Settings → Actions → General → Workflow permissions** → select
   **Read and write permissions** → Save.
3. Repo → **Actions** tab → enable workflows if asked → **Keep Streamlit apps
   awake** → **Run workflow** to test it once.

To add or remove an app, edit the `APPS` list in `wake.py`.
