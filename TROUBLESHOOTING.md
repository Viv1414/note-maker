# Troubleshooting (Windows)

**If uvicorn fails with `[WinError 10013]`:**

Port **8000** is already in use (often a previous uvicorn still running).

```powershell
netstat -ano | findstr ":8000"
taskkill /PID <PID_FROM_LAST_COLUMN> /F
```

Then start again. Or use `.\scripts\run-backend.ps1` — it will offer to free the port.

---

**Cause:** Uvicorn is installed, but its `Scripts` folder is not on your PATH.

**Fix — always use:**

```powershell
cd backend
python -m uvicorn app.main:app --reload
```

Or use the helper script from the repo root:

```powershell
.\scripts\run-backend.ps1
```

---

## 2. TensorFlow / `requirements-ml.txt` fails

**Cause:** You likely have **Python 3.14** as default. TensorFlow has no wheels for 3.14 yet.

Check your version:

```powershell
python --version
```

**Fix options:**

| Goal | What to do |
|------|------------|
| Just run the app | Skip ML entirely. Use `pip install -r requirements.txt` only. Placeholder sheets still work. |
| Real AI transcription | Install **Python 3.12** from [python.org](https://www.python.org/downloads/), create a venv with it, install ML deps there. |

Example with Python 3.12 launcher:

```powershell
cd backend
py -3.12 -m venv .venv-ml
.\.venv-ml\Scripts\activate
pip install -r requirements.txt -r requirements-ml.txt
python -m uvicorn app.main:app --reload
```

If you see **SSL certificate errors** (common with Anaconda):

```powershell
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements-ml.txt
```

---

## 3. `npm` is not recognized / PowerShell blocks `npm`

**Cause A:** Node.js is installed at `C:\Program Files\nodejs\` but that folder is not on PATH.

**Cause B:** PowerShell execution policy blocks `npm.ps1`:

```
running scripts is disabled on this system
```

**Fix for B — use `npm.cmd` instead of `npm`:**

```powershell
$env:Path = "C:\Program Files\nodejs;" + $env:Path
$env:NODE_OPTIONS = "--use-system-ca"
cd frontend
& "C:\Program Files\nodejs\npm.cmd" install
& "C:\Program Files\nodejs\npm.cmd" run dev
```

Or use the helper scripts (they call `npm.cmd` automatically):

```powershell
.\scripts\setup-frontend.ps1
.\scripts\run-frontend.ps1
```

**Optional — allow npm.ps1 for your user only:**

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

**Fix for A — add Node to PATH for this session:**

```powershell
$env:Path = "C:\Program Files\nodejs;" + $env:Path
cd frontend
npm install
npm run dev
```

Or use helper scripts:

```powershell
.\scripts\setup-frontend.ps1
.\scripts\run-frontend.ps1
```

**Permanent PATH fix:**

1. Windows Search → “Environment Variables”
2. Edit **User** `Path` → Add `C:\Program Files\nodejs`
3. Open a **new** terminal

**If `npm install` fails with `UNABLE_TO_VERIFY_LEAF_SIGNATURE`:**

This is an SSL certificate issue (same root cause as some pip/Anaconda errors). Try:

```powershell
$env:Path = "C:\Program Files\nodejs;" + $env:Path
$env:NODE_OPTIONS = "--use-system-ca"
cd frontend
npm install
```

Or use `.\scripts\setup-frontend.ps1` (now sets this automatically).

**If `npm install` runs forever with no output:**

- Check VPN / firewall / corporate proxy
- Try: `npm ping` (should respond in a few seconds)
- Try: `npm install --verbose` to see where it stalls
- `opensheetmusicdisplay` is a large package — first install can take 5+ minutes on slow networks

---

## Quick start (no ML, no PATH headaches)

From the repo root in PowerShell:

```powershell
.\scripts\setup-backend.ps1
.\scripts\run-backend.ps1
```

In a **second** terminal:

```powershell
.\scripts\setup-frontend.ps1
.\scripts\run-frontend.ps1
```

Then open http://127.0.0.1:5173
