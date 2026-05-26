# Fix blank Streamlit page — upload checklist

Your GitHub repo (`cometooo23-design/ANHS`) is **missing files** the app needs.

## What your repo has now

- `app.py`
- `anhs_data.py`
- `index.html` (old static file at the **root**)
- `requirements.txt`

## What it still needs

| Upload this | Why |
|-------------|-----|
| **`data/school_data.json`** | All enrollment, promotion, teacher numbers |
| **`dashboard/index.html`** | The **new** dashboard (works with school years) |

Do **not** rely on the root `index.html` alone — that is the old static version.

## Steps on GitHub

1. On your PC, open folder: `Downloads\anhs dashboard`
2. In GitHub → your **ANHS** repo → **Add file** → **Upload files**
3. Drag the whole **`data`** folder (contains `school_data.json`)
4. Drag the whole **`dashboard`** folder (contains `index.html`)
5. Commit to **main**
6. Streamlit Cloud → **Manage app** → **Reboot app**

## Correct repo layout

```text
ANHS/
  app.py
  anhs_data.py
  requirements.txt
  data/
    school_data.json
  dashboard/
    index.html
```

After reboot you should see the green header, tabs, and charts — not a blank white page.
