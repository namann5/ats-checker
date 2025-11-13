from fastapi import FastAPI, Request, Form, Body
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
from dotenv import load_dotenv
import requests
import base64
import json
import re
import json
import os as _os
try:
    import openai
except Exception:
    openai = None

app = FastAPI()

# Load environment (Back4App keys etc.)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'back4app.env'))
APPLICATION_ID = os.getenv('APPLICATION_ID', '')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
if OPENAI_API_KEY and openai is not None:
    try:
        openai.api_key = OPENAI_API_KEY
    except Exception:
        pass

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

STOP_WORDS = None  # let sklearn handle stop words


def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_top_keywords(text: str, top_n: int = 40):
    vect = TfidfVectorizer(stop_words='english', max_features=1000)
    tfidf = vect.fit_transform([text])
    feature_array = vect.get_feature_names_out()
    scores = tfidf.toarray()[0]
    pairs = list(zip(feature_array, scores))
    pairs.sort(key=lambda x: x[1], reverse=True)
    return pairs[:top_n]


def tokenize_set(text: str):
    return set(clean_text(text).split())


def compute_match(jd: str, resume: str):
    jd_clean = clean_text(jd)
    resume_clean = clean_text(resume)
    jd_keywords = extract_top_keywords(jd_clean, top_n=40)
    jd_top_words = [w for w, s in jd_keywords]
    jd_scores = {w: s for w, s in jd_keywords}

    resume_tokens = tokenize_set(resume_clean)

    present = [w for w in jd_top_words if w in resume_tokens]
    missing = [w for w in jd_top_words if w not in resume_tokens]

    # keyword-weighted overlap
    total_score = sum(jd_scores.values()) + 1e-9
    matched_score = sum(jd_scores[w] for w in present)
    keyword_overlap = (matched_score / total_score)

    # cosine similarity between JD and Resume (TF-IDF vectors)
    try:
        vect = TfidfVectorizer(stop_words='english', max_features=2000)
        mat = vect.fit_transform([jd_clean, resume_clean])
        cos_sim = float(cosine_similarity(mat[0], mat[1])[0][0])
    except Exception:
        cos_sim = 0.0

    # Combine both signals: weight cosine more for semantic match
    combined = 0.6 * cos_sim + 0.4 * keyword_overlap
    match_percent = int(round(combined * 100))

    # weak keywords: present but appear only once (approx)
    weak = []
    for w in present:
        count = resume_clean.split().count(w)
        if count <= 1:
            weak.append(w)

    # responsibility match: check per-sentence coverage
    sentences = [s.strip() for s in re.split(r'[\\.\\n]', jd) if s.strip()]
    responsibility = []
    for s in sentences:
        kws = [w for w in jd_top_words if w in clean_text(s).split()]
        covered = any(w in resume_tokens for w in kws)
        responsibility.append({"sentence": s, "required_keywords": kws, "covered": covered})

    return {
        "score": match_percent,
        "top_keywords": jd_keywords,
        "present_keywords": present,
        "missing_keywords": missing,
        "weak_keywords": weak,
        "responsibility": responsibility,
    }


def generate_bullets_for_role(role_text: str, jd_top_words: list):
    """Generate 3-5 role-specific bullets for a role description.
    This is heuristic-based: finds matched skills and composes achievement-oriented bullets.
    """
    verbs = [
        "Improved", "Optimized", "Led", "Spearheaded", "Implemented", "Designed",
        "Reduced", "Increased", "Automated", "Built", "Delivered"
    ]
    lines = [l.strip() for l in role_text.splitlines() if l.strip()]
    title = lines[0] if lines else "Role"
    body = ' '.join(lines[1:]) if len(lines) > 1 else ' '.join(lines)
    body_clean = clean_text(body)
    tokens = set(body_clean.split())

    matched_skills = [w for w, s in jd_top_words if w in tokens]
    # pick up to 6 skills
    skills_excerpt = matched_skills[:6]

    bullets = []

    # detect explicit metrics in role body (e.g., 'reduced latency by 30%', 'saved $1.2M', 'improved throughput 2x')
    metrics = []
    # percent patterns
    for m in re.findall(r"\b\d{1,3}%\b", body):
        metrics.append(m)
    # dollar amounts
    for m in re.findall(r"\$\s?\d+[\d,\.]*[kKmM]?", body):
        metrics.append(m)
    # multiplier / times
    for m in re.findall(r"\b\d+(?:\.\d+)?x\b", body):
        metrics.append(m)
    # explicit phrases like 'reduced .* by X%'
    for m in re.findall(r"reduced[^\.\n]{0,60}?\b\d{1,3}%\b", body, flags=re.I):
        metrics.append(m)

    if skills_excerpt:
        # If we found an explicit metric, use it in the first bullet
        if metrics:
            bullets.append(f"{verbs[0]} {skills_excerpt[0]}-related processes, {metrics[0]}, delivering measurable improvements.")
        else:
            bullets.append(f"{verbs[0]} {skills_excerpt[0]}-related process, resulting in measurable improvements (e.g., reduced time or cost by X%).")

        if len(skills_excerpt) > 1:
            bullets.append(f"{verbs[1]} system performance using {skills_excerpt[1]} and {skills_excerpt[2] if len(skills_excerpt)>2 else 'related tools'}, achieving improved scalability and reliability.")
    else:
        bullets.append(f"{verbs[2]} cross-functional initiatives to deliver key business outcomes and improve processes.")

    # Responsibility / result bullet
    skills_list = ', '.join([s for s in skills_excerpt[:4]]) if skills_excerpt else 'relevant technologies'
    bullets.append(f"Applied {skills_list} to deliver on core responsibilities and exceed stakeholder expectations.")

    # Process / automation bullet, include metric if present
    if metrics:
        bullets.append(f"Automated routine workflows and reporting using {skills_excerpt[0] if skills_excerpt else 'relevant tools'}, reducing manual effort and errors; example impact: {metrics[0]}.")
    else:
        bullets.append(f"Automated routine workflows and reporting using {skills_excerpt[0] if skills_excerpt else 'relevant tools'}, reducing manual effort and errors.")

    # Keep to 4 bullets
    return [b for b in bullets][:5]


def recommend_actions(missing_keywords, weak_keywords):
    recs = []
    if missing_keywords:
        recs.append(f"Add missing technical keywords/skills: {', '.join(missing_keywords[:10])}.")
    if weak_keywords:
        recs.append(f"Strengthen mentions of: {', '.join(weak_keywords[:10])} (add measurable impact).")
    recs.append("Include a Skills section listing core technologies from the JD.")
    recs.append("Tailor the resume summary to include 3–5 of the JD's top keywords.")
    recs.append("Use exact phrasing from the JD for key responsibilities where it matches your experience.")
    return recs


def find_summary(resume: str):
    # naive search for summary section
    m = re.search(r"(professional summary|summary|profile)[:\n\r]+(.{20,300})", resume, re.I)
    if m:
        return m.group(2).strip()
    # fallback: first 2 lines
    lines = [l.strip() for l in resume.splitlines() if l.strip()]
    if lines:
        return ' '.join(lines[:2])
    return ''


def generate_summary(jd_top_words, resume_summary):
    top = [w for w, s in jd_top_words[:8]]
    if resume_summary:
        # include top keywords into the user's summary (naive)
        add = ' '.join(top[:5])
        return f"{resume_summary} Key skills: {add}."
    else:
        return f"Experienced professional with expertise in {', '.join(top[:6])}. Proven track record delivering results in related responsibilities."


def generate_improved_resume(jd_top_words, resume_text):
    skills = ', '.join([w for w, s in jd_top_words[:20]])
    summary = generate_summary(jd_top_words, find_summary(resume_text))
    optimized = []
    optimized.append("SUMMARY")
    optimized.append(summary)
    optimized.append("")
    optimized.append("SKILLS")
    optimized.append(skills)
    optimized.append("")
    optimized.append("EXPERIENCE")
    # Try to extract roles under an Experience section; otherwise create a single role
    lines = resume_text.splitlines()
    roles = []
    in_exp = False
    current_role = []
    for l in lines:
        if re.search(r"experience|professional experience", l, re.I):
            in_exp = True
            continue
        if in_exp:
            # assume blank line separates roles
            if not l.strip():
                if current_role:
                    roles.append('\n'.join(current_role))
                    current_role = []
                continue
            current_role.append(l)
    if current_role:
        roles.append('\n'.join(current_role))

    if not roles:
        # fallback: create one role using first few lines
        first_lines = [ln for ln in lines if ln.strip()][:6]
        roles = ['\n'.join(first_lines) if first_lines else '']

    # For each role, generate bullets
    for r in roles:
        title_line = r.splitlines()[0] if r else 'Role'
        optimized.append(f"- {title_line}")
        bullets = generate_bullets_for_role(r, jd_top_words)
        for b in bullets:
            optimized.append(f"  - {b}")

    return '\n'.join(optimized)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # show quick Back4App validation/status on the main page
    try:
        validate = await api_validate_back4app()
    except Exception:
        validate = {"ok": False, "error": "validation failed"}
    return templates.TemplateResponse("index.html", {"request": request, "app_id": APPLICATION_ID, "validate": validate})


@app.post("/analyze")
async def analyze(request: Request, job_description: str = Form(...), resume: str = Form(...)):
    result = compute_match(job_description, resume)
    recs = recommend_actions(result['missing_keywords'], result['weak_keywords'])
    summary = generate_summary(result['top_keywords'], find_summary(resume))
    optimized_resume = generate_improved_resume(result['top_keywords'], resume)

    out = {
        "ats_score": result['score'],
        "missing_keywords": result['missing_keywords'],
        "weak_keywords": result['weak_keywords'],
        "top_keywords": [w for w, s in result['top_keywords']],
        "responsibility": result['responsibility'],
        "recommendations": recs,
        "rewritten_summary": summary,
        "optimized_resume": optimized_resume,
    }
    return templates.TemplateResponse("index.html", {"request": request, "result": out, "jd": job_description, "resume": resume})


@app.get('/admin', response_class=HTMLResponse)
async def admin_page(request: Request):
    # call validation and show app id
    validate = await api_validate_back4app()
    return templates.TemplateResponse('admin.html', {"request": request, "app_id": APPLICATION_ID, "validate": validate})


@app.post('/admin/create-class')
async def admin_create_class(request: Request, schema: str = Form(...)):
    try:
        payload = json.loads(schema)
    except Exception as e:
        return templates.TemplateResponse('admin.html', {"request": request, "app_id": APPLICATION_ID, "validate": {"ok": False, "error": f"Invalid JSON: {e}"}})
    res = await api_create_class(payload)
    return templates.TemplateResponse('admin.html', {"request": request, "app_id": APPLICATION_ID, "validate": res})


@app.post('/admin/upload-file')
async def admin_upload_file(request: Request, filename: str = Form(...), content: str = Form(...)):
    # encode content to base64 and call upload
    try:
        content_b64 = base64.b64encode(content.encode('utf-8')).decode('ascii')
    except Exception as e:
        return templates.TemplateResponse('admin.html', {"request": request, "app_id": APPLICATION_ID, "validate": {"ok": False, "error": str(e)}})
    res = await api_upload_file({'filename': filename, 'content_base64': content_b64})
    return templates.TemplateResponse('admin.html', {"request": request, "app_id": APPLICATION_ID, "validate": res})


@app.post("/api/analyze")
async def api_analyze(payload: dict = Body(...)):
    """JSON API endpoint. Accepts: { "job_description": str, "resume": str }
    Returns JSON with the analysis result.
    """
    jd = payload.get('job_description', '')
    resume = payload.get('resume', '')
    if not jd or not resume:
        return {"error": "Please provide 'job_description' and 'resume' in JSON body."}

    result = compute_match(jd, resume)
    recs = recommend_actions(result['missing_keywords'], result['weak_keywords'])
    summary = generate_summary(result['top_keywords'], find_summary(resume))
    optimized_resume = generate_improved_resume(result['top_keywords'], resume)

    out = {
        "ats_score": result['score'],
        "missing_keywords": result['missing_keywords'],
        "weak_keywords": result['weak_keywords'],
        "top_keywords": [w for w, s in result['top_keywords']],
        "responsibility": result['responsibility'],
        "recommendations": recs,
        "rewritten_summary": summary,
        "optimized_resume": optimized_resume,
    }
    return out


@app.get('/api/app-id')
async def api_app_id():
    return {"application_id": APPLICATION_ID}


@app.get('/api/validate-back4app')
async def api_validate_back4app():
    """Validate Back4App credentials by making a lightweight REST call.
    Reads `APPLICATION_ID` and `MASTER_KEY` from the environment (back4app.env).
    Returns JSON describing whether the credentials worked.
    """
    master = os.getenv('MASTER_KEY', '')
    app_id = APPLICATION_ID
    if not app_id or not master:
        return {"ok": False, "error": "Missing APPLICATION_ID or MASTER_KEY in back4app.env"}

    url = 'https://parseapi.back4app.com/classes/_User?limit=1'
    headers = {
        'X-Parse-Application-Id': app_id,
        'X-Parse-Master-Key': master,
        'Content-Type': 'application/json'
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code >= 200 and resp.status_code < 300:
            data = resp.json()
            return {"ok": True, "status_code": resp.status_code, "sample_response_keys": list(data.keys())}
        else:
            return {"ok": False, "status_code": resp.status_code, "response_text": resp.text}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def back4app_request(method: str, path: str, json_body=None, files=None, raw_bytes=None, filename=None):
    """Helper to call Back4App REST API endpoints.
    `path` should start with '/'. Returns (ok, status_code, response_json_or_text).
    """
    app_id = APPLICATION_ID
    master = os.getenv('MASTER_KEY', '')
    if not app_id or not master:
        return False, 0, {"error": "Missing APPLICATION_ID or MASTER_KEY"}

    base = 'https://parseapi.back4app.com'
    url = base + path
    headers = {
        'X-Parse-Application-Id': app_id,
        'X-Parse-Master-Key': master,
    }
    try:
        if raw_bytes is not None and filename:
            # upload file
            furl = f"{base}/files/{filename}"
            resp = requests.post(furl, headers=headers, data=raw_bytes, timeout=20)
        else:
            if method.upper() == 'GET':
                resp = requests.get(url, headers=headers, timeout=20)
            elif method.upper() == 'POST':
                resp = requests.post(url, headers={**headers, 'Content-Type': 'application/json'}, json=json_body, timeout=20)
            elif method.upper() == 'PUT':
                resp = requests.put(url, headers={**headers, 'Content-Type': 'application/json'}, json=json_body, timeout=20)
            else:
                return False, 0, {"error": f"Unsupported method {method}"}

        try:
            return True, resp.status_code, resp.json()
        except Exception:
            return (resp.status_code >= 200 and resp.status_code < 300), resp.status_code, resp.text
    except Exception as e:
        return False, 0, {"error": str(e)}


@app.post('/api/create-class')
async def api_create_class(payload: dict = Body(...)):
    """Create a Parse class/schema on Back4App.
    Body should be the JSON schema object e.g. { "className": "MyClass", "fields": { ... } }
    Requires MASTER_KEY in env.
    """
    ok, status, resp = back4app_request('POST', '/schemas', json_body=payload)
    return {"ok": ok, "status_code": status, "response": resp}


@app.post('/api/upload-file')
async def api_upload_file(payload: dict = Body(...)):
    """Upload a file to Back4App Parse Server. Provide { "filename": "name.ext", "content_base64": "..." }.
    Returns uploaded file metadata on success.
    """
    filename = payload.get('filename')
    content_b64 = payload.get('content_base64')
    if not filename or not content_b64:
        return {"ok": False, "error": "Provide 'filename' and 'content_base64' in payload."}
    try:
        raw = base64.b64decode(content_b64)
    except Exception as e:
        return {"ok": False, "error": f"Invalid base64: {e}"}
    ok, status, resp = back4app_request('POST', f'/files/{filename}', raw_bytes=raw, filename=filename)
    return {"ok": ok, "status_code": status, "response": resp}


def rewrite_bullets_with_llm(role_text: str, jd: str, max_bullets: int = 4) -> list:
    """Attempt to rewrite bullets using OpenAI. Falls back to heuristics if no key or failure."""
    # If openai is not installed or no key, return heuristic bullets
    if openai is None or not OPENAI_API_KEY:
        return generate_bullets_for_role(role_text, extract_top_keywords(jd, top_n=20))

    prompt = (
        "You are a resume-writing assistant. Given a role description and the job description, "
        "rewrite the role as 3-4 concise, achievement-focused resume bullets. Include measurable results if present. "
        "Output each bullet on a separate line without numbering.\n\n"
        f"Job description:\n{jd}\n\nRole text:\n{role_text}\n\nBullets:\n"
    )
    try:
        # Use ChatCompletion if available
        if hasattr(openai, 'ChatCompletion'):
            completion = openai.ChatCompletion.create(
                model='gpt-3.5-turbo',
                messages=[{'role': 'system', 'content': 'You are a helpful resume writer.'},
                          {'role': 'user', 'content': prompt}],
                max_tokens=400,
                temperature=0.3,
            )
            text = completion.choices[0].message.content
        else:
            completion = openai.Completion.create(
                model='text-davinci-003',
                prompt=prompt,
                max_tokens=400,
                temperature=0.3,
            )
            text = completion.choices[0].text
        # split into lines and return top max_bullets
        bullets = [line.strip('-* \t') for line in text.splitlines() if line.strip()]
        return bullets[:max_bullets] if bullets else generate_bullets_for_role(role_text, extract_top_keywords(jd, top_n=20))
    except Exception:
        return generate_bullets_for_role(role_text, extract_top_keywords(jd, top_n=20))


@app.post('/api/rewrite-bullets')
async def api_rewrite_bullets(payload: dict = Body(...)):
    """Rewrite bullets for a role using LLM if available; payload: { role_text, jd }
    Returns JSON: { bullets: [...] }
    """
    role = payload.get('role_text', '')
    jd = payload.get('jd', '')
    if not role:
        return {"error": "Provide 'role_text' in payload."}
    bullets = rewrite_bullets_with_llm(role, jd)
    return {"bullets": bullets}
