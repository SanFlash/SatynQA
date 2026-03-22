# PlaywrightAI — Automation CheatSheet Generator

> AI-Powered Playwright automation code generator. Type any automation task, get working Python code instantly.

---

## 🚀 Deploy to Render (5 minutes)

### Option A — One-click via render.yaml
1. Push this folder to a GitHub repo
2. Go to [render.com](https://render.com) → **New → Web Service**
3. Connect your GitHub repo
4. Render auto-detects `render.yaml` — click **Deploy**
5. Your app is live at `https://playwrightai.onrender.com`

### Option B — Manual setup on Render
| Setting | Value |
|---|---|
| **Environment** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120` |
| **Health Check Path** | `/health` |

---

## 💻 Run Locally

```bash
# 1. Install dependencies
pip install flask gunicorn

# 2. Run with Flask dev server
python app.py

# OR run with gunicorn (same as Render)
gunicorn app:app --bind 0.0.0.0:5000 --workers 2

# 3. Open
http://localhost:5000
```

---

## 📁 Project Structure

```
playwrightai/
├── app.py            ← Entire app (Flask + HTML + CSS + JS in one file)
├── requirements.txt  ← flask + gunicorn (no playwright needed on server)
├── Procfile          ← gunicorn start command for Render
├── render.yaml       ← One-click Render deploy config
├── runtime.txt       ← Python 3.11 pin
└── .gitignore
```

> **Note:** Playwright is NOT in requirements.txt intentionally.
> The app generates code — it doesn't *run* it. Users copy/download
> the `.py` files and run them locally with Playwright installed.

---

## 🧩 10 Automation Modules

| Module | Keywords |
|--------|---------|
| 🔐 Login | login, sign in, auth, password |
| 📝 Signup | signup, register, create account |
| 🖱️ Click | click, button, modal, dialog, alert |
| 📦 iFrame | iframe, frame, embed |
| 📜 Scroll | scroll, infinite, feed |
| ⬇️ Dropdown | dropdown, select, option |
| 🧭 Hover | hover, menu, tooltip |
| ⏱️ Waits | wait, timeout, network idle |
| 📎 Upload | upload, file, download |
| ⚠️ Errors | error, retry, exception |

---

## 🔌 API Endpoints

```
GET  /           → Main UI
GET  /health     → Health check (returns {"status":"ok"})
POST /generate   → { "query": "login form" } → cheatsheet JSON
POST /download   → { "code": "...", "filename": "x.py" } → .py file
GET  /categories → list of all 10 categories
```
