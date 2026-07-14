# AI Content Repurposer — Local Setup Guide

**Repository:** [github.com/vandana-yadav-8686/content-generator](https://github.com/vandana-yadav-8686/content-generator)  
**Live app:** [content-generator-flax-nine.vercel.app](https://content-generator-flax-nine.vercel.app/)  
**Project docs:** [DOCUMENTATION.md](./DOCUMENTATION.md) — architecture, approach, why, and future plan

Turn one article into multiple formats (YouTube script, Reel, LinkedIn post, Instagram carousel, voiceover) using **FastAPI + LangGraph** (backend) and **Next.js** (frontend).

Follow the steps below **in order**. Do not skip a step — each one builds on the previous.

---

## Table of contents

1. [What you need before starting](#step-1-what-you-need-before-starting)
2. [Get the code](#step-2-get-the-code)
3. [Set up MongoDB Atlas](#step-3-set-up-mongodb-atlas)
4. [Set up the backend (API)](#step-4-set-up-the-backend-api)
5. [Set up the frontend (web app)](#step-5-set-up-the-frontend-web-app)
6. [Configure the app (first login)](#step-6-configure-the-app-first-login)
7. [Generate your first content](#step-7-generate-your-first-content)
8. [Run the project every day](#step-8-run-the-project-every-day)
9. [Project structure](#project-structure)
10. [Troubleshooting](#troubleshooting)
11. [Production deployment (optional)](#production-deployment-optional)

---

## Step 1: What you need before starting

Install these on your computer first.

| Requirement | Version | How to check |
|-------------|---------|--------------|
| **Python** | 3.12.x | `python --version` or `python3 --version` |
| **Node.js** | 18+ (20 LTS recommended) | `node --version` |
| **npm** | Comes with Node.js | `npm --version` |
| **Git** | Any recent version | `git --version` |

You also need:

- A free **[MongoDB Atlas](https://www.mongodb.com/cloud/atlas)** account (cloud database)
- At least **one LLM API key** (OpenAI, OpenRouter, Groq, Gemini, etc.)

> **Tip:** If Python is not 3.12, install it from [python.org](https://www.python.org/downloads/) or use `pyenv`. The project expects **3.12.8** (see `backend/runtime.txt`).

---

## Step 2: Get the code

Open a terminal and clone the repository:

```bash
git clone https://github.com/vandana-yadav-8686/content-generator.git
cd content-generator
```

You should now have this folder structure:

```
content-generator/
├── backend/     ← Python API (run from here)
├── frontend/    ← Next.js app (run from here)
└── README.md
```

**Checkpoint:** You are inside the `content-generator` folder.

---

## Step 3: Set up MongoDB Atlas

The app stores users, API keys, and generated content in MongoDB Atlas (not on your disk).

### 3.1 Create a cluster

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) and sign in.
2. Click **Build a Database** → choose **M0 Free** → create the cluster.
3. Pick a cloud region close to you → **Create**.

### 3.2 Create a database user

1. Go to **Database Access** → **Add New Database User**.
2. Choose **Password** authentication.
3. Set a username and a strong password (save these — you need them for the connection string).
4. Role: **Atlas admin** or **Read and write to any database**.
5. Click **Add User**.

### 3.3 Allow network access

1. Go to **Network Access** → **Add IP Address**.
2. For local development, click **Allow Access from Anywhere** (`0.0.0.0/0`)  
   *(For production, restrict to your server IP only.)*
3. Click **Confirm**.

### 3.4 Copy the connection string

1. Go to **Database** → **Connect** on your cluster.
2. Choose **Drivers** → copy the connection string. It looks like:

   ```
   mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```

3. Replace `<username>` and `<password>` with your database user credentials.
4. If your password contains special characters (`@`, `#`, `:`, etc.), [URL-encode](https://www.urlencoder.org/) them.

**Checkpoint:** You have a working `mongodb+srv://...` connection string. Keep it for Step 4.

---

## Step 4: Set up the backend (API)

All commands in this section run from the **`backend`** folder.

### 4.1 Open the backend folder

**Windows (PowerShell):**

```powershell
cd backend
```

**macOS / Linux:**

```bash
cd backend
```

### 4.2 Create a Python virtual environment

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

You should see `(.venv)` at the start of your terminal prompt.

> **Windows note:** If activation is blocked, run once:  
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### 4.3 Install Python packages

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Wait until all packages install without errors.

### 4.4 Create the `.env` file

**Windows (PowerShell):**

```powershell
Copy-Item .env.example .env
```

**macOS / Linux:**

```bash
cp .env.example .env
```

### 4.5 Generate secrets

Run these **two commands** and save the output — you will paste them into `.env`.

**Encryption key** (required — encrypts API keys in MongoDB):

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**JWT secret** (recommended — keeps login sessions stable across restarts):

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

### 4.6 Edit `backend/.env`

Open `backend/.env` in any text editor and fill in every required value:

```env
# Paste the Fernet key from the command above (required)
ENCRYPTION_KEY=paste-your-fernet-key-here

# Optional — auto-generated in ./data if left empty
JWT_SECRET=paste-your-jwt-secret-here

# Local data folder for auto-generated secrets
DATA_DIR=./data

# Must include your frontend URL (add more ports if you change them)
CORS_ORIGINS=http://localhost:3000,http://localhost:3003

# Paste your MongoDB Atlas connection string from Step 3
MONGODB_URI=mongodb+srv://USER:PASSWORD@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB=content_repurposing

# Optional — only used if no provider is enabled in Settings UI
OPENAI_API_KEY=
```

| Variable | Required? | Notes |
|----------|-----------|-------|
| `ENCRYPTION_KEY` | **Yes** | Must be a valid Fernet key — not a random string |
| `JWT_SECRET` | Recommended | If omitted, saved to `backend/data/.jwt_secret` |
| `MONGODB_URI` | **Yes** | From MongoDB Atlas Step 3 |
| `MONGODB_DB` | **Yes** | Keep as `content_repurposing` unless you change it everywhere |
| `CORS_ORIGINS` | **Yes** | Must match the URL where the frontend runs |
| `OPENAI_API_KEY` | No | Configure providers in the Settings UI instead |

> **Important:** Never commit `.env` to Git. It contains secrets.

### 4.7 Start the backend server

Make sure your virtual environment is still active (`(.venv)` in the prompt), then run:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Leave this terminal **open and running**.

### 4.8 Verify the backend works

Open these URLs in your browser:

| URL | Expected result |
|-----|-----------------|
| http://127.0.0.1:8000/ | JSON with `"status": "ok"` |
| http://127.0.0.1:8000/api/health | `"mongodb": "ok"` or `"mongodb": "ok (...)"` |
| http://127.0.0.1:8000/docs | Swagger API documentation |

**If `mongodb` is `"missing"`:** `MONGODB_URI` is empty in `.env` — fix and restart.

**If `mongodb` is `"unreachable"`:** Check Atlas network access (Step 3.3) and your connection string credentials.

**Checkpoint:** Backend is running and health check shows MongoDB is OK.

---

## Step 5: Set up the frontend (web app)

Open a **new terminal** window. Keep the backend terminal running.

### 5.1 Install Node packages

**Windows / macOS / Linux:**

```bash
cd frontend
npm install
```

### 5.2 Environment file (usually not needed locally)

For local development, **you do not need** a `.env` file. The frontend automatically proxies API requests to `http://localhost:8000`.

Only create `frontend/.env.local` if your backend runs on a **different port or host**:

```env
BACKEND_URL=http://localhost:8000
```

### 5.3 Start the frontend server

```bash
npm run dev
```

Leave this terminal **open and running**.

### 5.4 Verify the frontend works

Open in your browser:

**http://localhost:3000**

You should see the Repurposer home page (login/register or the main create screen).

**Checkpoint:** Both servers are running:

| Service | URL | Terminal folder |
|---------|-----|-----------------|
| Backend | http://127.0.0.1:8000 | `backend/` |
| Frontend | http://localhost:3000 | `frontend/` |

---

## Step 6: Configure the app (first login)

Do this once after a fresh setup.

### 6.1 Create an account

1. Open http://localhost:3000/register
2. Enter email and password → **Register**
3. You are logged in automatically

This creates your user in MongoDB and seeds default provider settings.

### 6.2 Add an LLM provider

1. Go to **Settings** (top navigation).
2. Pick a provider (e.g. **OpenRouter** or **OpenAI**).
3. Toggle **Enable**.
4. Paste your **API key**.
5. Select a **model**.
6. Click **Save**.
7. Click **Test Connection** — you should see a success message.

Supported providers:

- OpenAI · Google Gemini · Anthropic · Groq · OpenRouter · Mistral · Cohere · DeepSeek

**Checkpoint:** Test Connection succeeds for at least one enabled provider.

---

## Step 7: Generate your first content

1. Go to the **home page** (Create).
2. **Step 1 — Choose formats:** Select one or more formats (or **Select all**).
3. **Step 2 — Paste your article:** Paste at least **50 characters** of text.
4. **Step 3 — Generate:** Click the generate button.

Generation uses LangGraph and can take **1–3 minutes** for all five formats.

When finished, output cards appear below with copyable content for each format.

**Checkpoint:** At least one format shows generated content.

---

## Step 8: Run the project every day

After the one-time setup, you only need two terminals:

### Terminal 1 — Backend

**Windows:**

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**macOS / Linux:**

```bash
cd backend
source .venv/bin/activate
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Terminal 2 — Frontend

```bash
cd frontend
npm run dev
```

Then open **http://localhost:3000**.

---

## Project structure

```
content-generator/
├── backend/
│   ├── app/
│   │   ├── graph/           # LangGraph workflow
│   │   ├── routers/         # API routes (auth, settings, repurpose)
│   │   ├── services/        # Auth, settings, LLM logic
│   │   └── database/        # MongoDB connection
│   ├── main.py              # Entry point for uvicorn
│   ├── requirements.txt     # Python dependencies
│   ├── runtime.txt          # Python version (3.12.8)
│   ├── .env.example         # Template for environment variables
│   └── .env                 # Your secrets (create this — not in Git)
├── frontend/
│   ├── app/                 # Next.js pages (home, settings, login, register)
│   ├── components/          # UI components
│   ├── lib/                 # API client, auth helpers
│   └── package.json         # Node dependencies
├── render.yaml              # Render deployment config (backend)
└── README.md
```

---

## Troubleshooting

### Setup checklist (read this first)

If something fails, confirm each item:

- [ ] Python 3.12 is installed and venv is activated
- [ ] `backend/.env` exists with `ENCRYPTION_KEY`, `MONGODB_URI`, and `CORS_ORIGINS`
- [ ] Backend is running from the **`backend/`** folder (not repo root)
- [ ] http://127.0.0.1:8000/api/health shows `"mongodb": "ok"`
- [ ] Frontend is running with `npm run dev` in **`frontend/`**
- [ ] You registered a user and enabled a provider in Settings
- [ ] Test Connection passes in Settings

---

### "Failed to fetch" on Settings or Generate

**Cause:** Frontend cannot reach the backend.

**Fix:**

1. Confirm backend is running: http://127.0.0.1:8000/api/health
2. Check `CORS_ORIGINS` in `backend/.env` includes `http://localhost:3000`
3. Restart both backend and frontend after changing `.env`

---

### MongoDB connection errors

**Cause:** Wrong URI, blocked IP, or bad credentials.

**Fix:**

1. Atlas → **Network Access** → allow your IP (or `0.0.0.0/0` for dev)
2. Verify username/password in `MONGODB_URI`
3. URL-encode special characters in the password
4. Restart the backend after editing `.env`

---

### API key saved but Test Connection fails

**Cause:** Invalid or missing `ENCRYPTION_KEY`.

**Fix:**

1. Generate a new Fernet key (Step 4.5)
2. Put it in `ENCRYPTION_KEY` in `backend/.env`
3. Restart the backend
4. Re-save your API key in Settings

> Changing `ENCRYPTION_KEY` invalidates previously encrypted keys — always re-save keys after changing it.

---

### Register returns 404

**Cause:** Backend is not running or is an old version without auth routes.

**Fix:**

1. Stop any old backend process
2. From `backend/` run: `uvicorn main:app --reload --host 127.0.0.1 --port 8000`
3. Confirm http://127.0.0.1:8000/docs shows `/api/auth/register`

---

### Generation fails or times out

**Fix:**

1. Run **Test Connection** in Settings first
2. Try **one format** instead of all five
3. Use a free/cheap model (e.g. `openrouter/free` on OpenRouter)
4. Restart the backend after pulling latest code

---

### Port already in use

**Backend — use port 8001:**

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8001
```

Create `frontend/.env.local`:

```env
BACKEND_URL=http://localhost:8001
```

**Frontend — use port 3001:**

```bash
npm run dev -- -p 3001
```

Add to `backend/.env`:

```env
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

Restart both servers after port changes.

---

## Production deployment (optional)

### Live URLs (this project)

| Service | URL |
|---------|-----|
| **Frontend (Vercel)** | https://content-generator-flax-nine.vercel.app |
| **Backend API (Render)** | https://content-generator-wv8n.onrender.com |
| **API health check** | https://content-generator-wv8n.onrender.com/api/health |

| Part | Platform | Folder |
|------|----------|--------|
| Backend API | [Render](https://render.com) | `backend/` |
| Frontend | [Vercel](https://vercel.com) | `frontend/` |

### Backend (Render) — required environment variables

| Variable | Example / notes |
|----------|-----------------|
| `PYTHON_VERSION` | `3.12.8` |
| `MONGODB_URI` | Your Atlas connection string |
| `MONGODB_DB` | `content_repurposing` |
| `ENCRYPTION_KEY` | Same Fernet key as local (if sharing data) |
| `JWT_SECRET` | Random secret string |
| `CORS_ORIGINS` | `https://content-generator-flax-nine.vercel.app` |

See `render.yaml` for the full Render blueprint.

### Frontend (Vercel)

Default production backend URL is set in `frontend/lib/backend-url.js`:

```
https://content-generator-wv8n.onrender.com
```

Override with `BACKEND_URL` in Vercel environment variables if needed.

---

## Quick reference

| What | Command / URL |
|------|----------------|
| **Live app** | https://content-generator-flax-nine.vercel.app |
| **Live API** | https://content-generator-wv8n.onrender.com |
| Backend health (local) | http://127.0.0.1:8000/api/health |
| API docs (local) | http://127.0.0.1:8000/docs |
| Web app (local) | http://localhost:3000 |
| Backend start | `uvicorn main:app --reload --host 127.0.0.1 --port 8000` (from `backend/`) |
| Frontend start | `npm run dev` (from `frontend/`) |
| Min article length | 50 characters |
| LLM config | Settings page in the app |

---

If you complete Steps 1–7 in order and pass each **Checkpoint**, the project should run without issues on a new machine.
