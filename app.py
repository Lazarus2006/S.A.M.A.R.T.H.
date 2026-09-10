from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import List
from pathlib import Path
from google import genai
import requests
from bs4 import BeautifulSoup
import json, os, io, re

app = FastAPI(
    title="S.A.M.A.R.T.H. API",
    description="Social Action Management And Real Time Help",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

import subprocess
import tempfile


def _text_from_pdf(content: bytes) -> str:
    """Try pypdf, then PyPDF2. Return empty string on total failure."""
    PdfReader = None
    try:
        from pypdf import PdfReader
    except ImportError:
        try:
            from PyPDF2 import PdfReader 
        except ImportError:
            return "[No PDF library installed. Run: sudo apt install python3-pypdf]"

    try:
        reader = PdfReader(io.BytesIO(content))
        parts = []
        for page in reader.pages:
            try:
                parts.append(page.extract_text() or "")
            except Exception:
                pass
        text = "\n".join(parts).strip()
        return text if text else "[PDF contained no extractable text — may be a scanned image]"
    except Exception as e:
        return f"[PDF parse failed: {e}]"


def _text_from_image(content: bytes, filename: str) -> str:
    """Call system tesseract binary via subprocess. No pytesseract needed."""
    try:
        suffix = Path(filename).suffix or ".png"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            result = subprocess.run(
                ["tesseract", tmp_path, "stdout", "-l", "eng"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                return f"[OCR error: {result.stderr.strip()[:200]}]"
            return result.stdout.strip() or "[OCR produced no text]"
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    except FileNotFoundError:
        return "[tesseract not installed — run: sudo apt install tesseract-ocr]"
    except Exception as e:
        return f"[OCR failed: {e}]"


def extract_text(filename: str, content: bytes) -> str:
    name = (filename or "").lower()
    if name.endswith(".pdf"):
        return _text_from_pdf(content)
    if name.endswith((".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff")):
        return _text_from_image(content, filename)
    if name.endswith((".txt", ".md", ".csv")):
        return content.decode("utf-8", errors="ignore")
    return f"[Unsupported file type: {filename}]"

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


def fetch_jobs_live() -> list:
    url = "https://www.sarkariresult.com/latestjob.php"
    r = requests.get(url, headers=BROWSER_HEADERS, timeout=12)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    jobs = []
    seen = set()
    for sel in ["#post", ".post", "#content", "div.post", "article"]:
        container = soup.select_one(sel)
        if not container:
            continue
        for a in container.find_all("a", href=True):
            text = a.get_text(strip=True)
            href = a["href"]
            if not text or len(text) < 12:
                continue
            if any(k in href.lower() for k in ["facebook", "twitter", "whatsapp", "telegram"]):
                continue
            if not href.startswith("http"):
                href = "https://www.sarkariresult.com/" + href.lstrip("/")
            if href in seen:
                continue
            seen.add(href)
            jobs.append({"title": text, "link": href})
            if len(jobs) >= 20:
                break
        if jobs:
            break
    return jobs


@app.get("/jobs")
def get_jobs():
    try:
        jobs = fetch_jobs_live()
        if jobs:
            return {"jobs": jobs, "cached": False}
    except Exception as e:
        print(f"[scraper] live fetch failed: {e}")

    cache_path = BASE_DIR / "cache_jobs.json"
    if cache_path.exists():
        with open(cache_path) as f:
            return {"jobs": json.load(f), "cached": True}
    return {"jobs": [], "error": "no live jobs and no cache file"}

PROFILE_PROMPT = """You are reading a set of personal documents (resume, degree certificates, ID proofs, experience letters, etc.).

Extract a structured profile. Return ONLY valid JSON with these exact fields:

{
"full_name": string or null,
"email": string or null,
"phone": string or null,
"dob": "YYYY-MM-DD" or null,
"qualification": one of ["PhD","Masters","Bachelors","Diploma","12th","10th"] or null,
"field_ofBeautifulSoup_study": string or null,
"experience_years": number (integer) or 0,
"skills": [list of strings],
"location": string or null,
"languages": [list of strings],
"documents_present": [list of short strings naming the documents you found, e.g. "Aadhaar card", "Degree certificate", "Resume", "Experience letter"],
"summary": string (1-2 sentences describing the person)
}

Rules:
- Use null when information is genuinely not present. Do not invent data.
- For qualification, pick the highest degree you can find.
- For documents_present, list every distinct document type you can identify.
- Return ONLY the JSON object. No markdown fences, no commentary.

DOCUMENTS:
"""


@app.post("/extract-profile")
async def extract_profile(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    chunks = []
    for f in files:
        content = await f.read()
        text = extract_text(f.filename or "unknown", content)
        chunks.append(f"=== {f.filename} ===\n{text}")

    combined = "\n\n".join(chunks)[:20000]

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=PROFILE_PROMPT + combined,
            config={"response_mime_type": "application/json"},
        )
        raw = response.text.strip()
        raw = re.sub(r"^```(?:json|JSON)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        profile = json.loads(raw)
    except Exception as e:
        return {
            "error": f"Profile extraction failed: {e}",
            "raw_preview": combined[:500],
        }

    return {"profile": profile, "files_processed": [f.filename for f in files]}

REQUIREMENTS_PROMPT = """From the following government job notification text, extract:

{
"organization": string or null,
"post_name": string or null,
"qualification": [list of allowed degrees, e.g. "Bachelors","Masters"] or [],
"age_limit": number (max age) or null,
"application_fee": string or null,
"last_date": string or null,
"required_documents": [list of documents the applicant must submit] or [],
"application_link": string or null
}

Return ONLY valid JSON. Use null or [] when a field is not mentioned. No markdown, no commentary.

TEXT:
"""


@app.post("/extract")
def extract_requirements(job_url: str):
    try:
        r = requests.get(job_url, headers=BROWSER_HEADERS, timeout=12)
        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text(separator="\n", strip=True)[:12000]
    except Exception as e:
        return {"error": f"Could not fetch job page: {e}"}

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=REQUIREMENTS_PROMPT + text,
            config={"response_mime_type": "application/json"},
        )
        raw = response.text.strip()
        raw = re.sub(r"^```(?:json|JSON)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        return json.loads(raw)
    except Exception as e:
        return {"error": f"Extraction failed: {e}"}


QUAL_RANK = {"10th": 1, "12th": 2, "Diploma": 3, "Bachelors": 4, "Masters": 5, "PhD": 6}


def _qual_ok(user_qual: str, allowed: list) -> str:
    """Returns 'eligible', 'partial', or 'not_eligible'."""
    if not user_qual or not allowed:
        return "unknown"
    uq = QUAL_RANK.get(user_qual, 0)
    ranks = [QUAL_RANK.get(a, 0) for a in allowed]
    if not ranks or uq == 0:
        return "unknown"
    if uq >= max(ranks):
        return "eligible"
    if uq >= min(ranks):
        return "partial"
    return "not_eligible"


def _doc_gap(have: list, need: list) -> dict:
    """Compare user's documents against required ones."""
    have_lower = [h.lower() for h in (have or [])]
    missing = []
    present = []
    for doc in (need or []):
        d = doc.lower()
        matched = any(
            any(word in h for word in d.split() if len(word) > 3)
            for h in have_lower
        )
        (present if matched else missing).append(doc)
    return {"have": present, "missing": missing}


@app.post("/match")
async def match(profile: dict):
    jobs_resp = get_jobs()
    jobs = jobs_resp.get("jobs", [])[:5]

    if not jobs:
        return {"results": [], "note": "No jobs available from scraper or cache."}

    results = []
    for job in jobs:
        req = extract_requirements(job["link"])
        if "error" in req:
            results.append({
                "title": job["title"],
                "link": job["link"],
                "eligibility": "unknown",
                "source": "SarkariResult",
                "note": f"Could not extract requirements: {req['error']}",
            })
            continue

        qual_status = _qual_ok(
            profile.get("qualification"),
            req.get("qualification") or [],
        )

        doc_gap = _doc_gap(
            profile.get("documents_present") or [],
            req.get("required_documents") or [],
        )

        age_ok = "unknown"
        if profile.get("age") and req.get("age_limit"):
            age_ok = "eligible" if profile["age"] <= req["age_limit"] else "not_eligible"

        statuses = [qual_status, age_ok]
        if "not_eligible" in statuses:
            eligibility = "not_eligible"
        elif all(s == "eligible" for s in statuses) and not doc_gap["missing"]:
            eligibility = "eligible"
        elif "unknown" in statuses:
            eligibility = "unknown"
        else:
            eligibility = "partial"

        results.append({
            "title": req.get("post_name") or job["title"],
            "link": job["link"],
            "organization": req.get("organization"),
            "qualification": req.get("qualification"),
            "age_limit": req.get("age_limit"),
            "fee": req.get("application_fee"),
            "last_date": req.get("last_date"),
            "documents": req.get("required_documents") or [],
            "documents_you_have": doc_gap["have"],
            "documents_missing": doc_gap["missing"],
            "eligibility": eligibility,
            "source": "SarkariResult",
        })

    order = {"eligible": 0, "partial": 1, "unknown": 2, "not_eligible": 3}
    results.sort(key=lambda r: order.get(r["eligibility"], 4))

    return {"results": results}

@app.get("/")
def serve_frontend():
    return FileResponse(BASE_DIR / "index.html")