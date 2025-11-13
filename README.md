# ATS Analyzer (FastAPI)

A small self-hosted web app to analyze a Resume against a Job Description and produce:

- ATS Match Score (0–100)
- Missing keywords
- Weak keywords
- Responsibility match
- Skill gap analysis
- Recommendations to increase ATS score
- Rewritten resume summary
- Improved bullet suggestions
- Optimized ATS-friendly resume (text)

Quick start (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Open `http://127.0.0.1:8000` in your browser, paste the Job Description and your Resume, then click Analyze.

Notes:
- This is a lightweight tool using TF-IDF and keyword overlap heuristics. It provides helpful suggestions but not human-level rewriting in every case.
- You can extend the analysis logic to integrate an LLM for higher-quality rewrite outputs.
 
Back4App App ID
----------------
If you have a Back4App application ID you want the project to reference, place it in `back4app.env` at the project root. A sample file is included with the key `APPLICATION_ID` already set.

Example `back4app.env`:

```
APPLICATION_ID=kyP3SPbgtwvbKZXLPPOpMIFBw4uFrFnULklbTrFu
MASTER_KEY=your_master_key_here
JAVASCRIPT_KEY=your_js_key_here
```

The app currently does not automatically use Back4App runtime keys, but the env file is provided for convenience when you extend the project to call Back4App APIs or to store credentials securely.

What's been implemented
- Admin page: `GET /admin` shows Application ID and validation result and provides forms to create a class and upload a file to Back4App.
- Back4App operations: `POST /api/create-class` and `POST /api/upload-file` (use `content_base64`) are available; these require `MASTER_KEY` in `back4app.env`.
- Bullet generation: heuristics now detect simple metrics like percentages, dollar amounts, and multipliers and will include them in generated bullets when present.

JSON API
--------
The project exposes a JSON API for automated use:

- `POST /api/analyze` — accepts JSON { "job_description": "...", "resume": "..." } and returns the analysis JSON (ATS score, keywords, recommendations, rewritten summary, optimized resume preview).
- `GET /api/app-id` — returns the configured Back4App `APPLICATION_ID` (read from `back4app.env`).

Example PowerShell `curl` call:

```powershell
$body = @{ job_description = Get-Content .\jd.txt -Raw; resume = Get-Content .\resume.txt -Raw } | ConvertTo-Json
curl -X POST http://127.0.0.1:8000/api/analyze -H "Content-Type: application/json" -d $body | ConvertFrom-Json
```

Or using `requests` in Python (after installing requirements):

```python
import requests
jd = open('jd.txt').read()
resume = open('resume.txt').read()
resp = requests.post('http://127.0.0.1:8000/api/analyze', json={'job_description': jd, 'resume': resume})
print(resp.json())
```

Validate Back4App Keys
----------------------
You can validate that your `APPLICATION_ID` and `MASTER_KEY` are correct using the lightweight endpoint:

```powershell
curl http://127.0.0.1:8000/api/validate-back4app | ConvertFrom-Json
```

It returns `{"ok": true, ...}` when the call succeeds, or an error message otherwise.
