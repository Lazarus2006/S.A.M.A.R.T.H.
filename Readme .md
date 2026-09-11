# S.A.M.A.R.T.H. 🤖

**Social Action Management And Real Time Help**

A platform that reads your documents, builds your profile, and matches you
with live government job opportunities you're actually eligible for.

> Upload your documents once. Get matched automatically.
> Never miss the right opportunity because you didn't know about it.

---

## 🚨 The Problem

Every year, crores of qualified Indians miss government job opportunities — not because
they're unqualified, but because the information never reaches them in time.

- **Scattered sources** — SarkariResult, Employment News, department sites, PDF circulars.
  No single place to look.
- **Bureaucratic language** — long, dense, written for officials, not applicants.
- **Buried eligibility** — qualification, age, category, fee, documents — all hidden in fine print.
- **Document confusion** — applicants don't know which certificates they already have vs.
  which ones they still need to arrange.
- **Language barrier** — most official info is formal English; millions are more comfortable
  in Hindi or regional languages.
- **Missed deadlines** — no proactive matching; people find out after the last date has passed.

**Result:** qualified candidates lose opportunities to those who simply had better
information access.

> *The problem isn't a lack of opportunities — it's a lack of access to them.*

---

## 💡 Our Solution

S.A.M.A.R.T.H. flips the traditional job-portal flow:

**Traditional portals:** fill a long form → filter manually → check each notification → apply

**S.A.M.A.R.T.H.:** upload your documents → AI builds your profile → get matched → apply

### How it works, in one sentence

> You upload your resume, degree certificate, ID proof, and experience letters.
> S.A.M.A.R.T.H. reads them, extracts your profile, matches it against live government
> job openings, and shows you which ones you qualify for — **plus which documents you're
> still missing**.

### Example

**Instead of:**
> Website 1 → Website 2 → Government Portal → 8 different PDFs → manual eligibility check

**You get:**
> One upload → AI-extracted profile → ranked list of eligible jobs → document gap analysis → direct apply link

---

## ⚙️ How It Works
USER
│
▼
┌──────────────────────┐
│ Upload Documents │
│ Resume · Degree │
│ Aadhaar · Exp. letter│
└──────────┬───────────┘
│
▼
┌──────────────────────┐
│ Text Extraction │
│ PDF → pypdf │
│ Image → Tesseract │
└──────────┬───────────┘
│
▼
┌──────────────────────┐
│ Gemini Profile │
│ Extraction │
│ → structured JSON │
└──────────┬───────────┘
│
▼
┌──────────────────────┐
│ Live Job Fetch │
│ SarkariResult + │
│ cached fallback │
└──────────┬───────────┘
│
▼
┌──────────────────────┐
│ Gemini Requirement │
│ Extraction per job │
└──────────┬───────────┘
│
▼
┌──────────────────────┐
│ Eligibility + Doc │
│ Gap Matching │
└──────────┬───────────┘
│
▼
┌──────────────────────┐
│ Ranked Results │
│ ✅ eligible │
│ ⚠️ partially │
│ ❌ not eligible │
└──────────────────────┘


---

## ✨ Key Features

### 📄 Document-First Profile
Upload a PDF, image, or text file — resume, degree, ID, experience letter.
S.A.M.A.R.T.H. extracts the profile automatically. No long form.

### 🤖 AI-Powered Extraction
Gemini reads both your documents **and** the job notifications.
Extracts qualification, age limit, fees, deadlines, and required documents into clean JSON.

### 🎯 Eligibility Matching
Each job is scored against your profile:
- **✅ Eligible** — you meet every stated requirement
- **⚠️ Partially eligible** — you meet some, not all
- **❌ Not eligible** — you don't meet the core criteria
- **❓ Needs verification** — the notification didn't specify enough to decide

### 📋 Document Gap Analysis *(killer feature)*
For every job, S.A.M.A.R.T.H. shows:
- ✅ **Documents you already have** (matched against your uploads)
- ❌ **Documents you still need** (so you know what to arrange before the deadline)

### 🔗 Source-Backed Answers
Every result links back to the official notification on SarkariResult.
No black-box eligibility calls — you can verify everything.

### 🌐 Multilingual *(planned)*
Ask questions in Hindi: *"Isko simple Hindi mein samjhao."*
Underlying document remains the official source.

### ⚠️ Honest Uncertainty
When the system can't determine eligibility with confidence, it says so:
> *"The available information does not clearly specify whether this requirement applies
> to your profile. Please check the official notification."*

---

## 🎯 Target Users

- College students and fresh graduates
- Government-job aspirants (Railways, SSC, Police, Civil Services, Banking)
- Scholarship seekers
- Anyone hunting public-sector opportunities with scattered information

---

## 🛠️ Technology Stack

**Frontend**
- Vanilla HTML + CSS + JavaScript (no build step, single file)

**Backend**
- Python 3.10+
- FastAPI + Uvicorn

**AI**
- Google Gemini 2.5 Flash
- Structured JSON extraction via `response_mime_type`
- Profile extraction from documents
- Requirement extraction from notifications
- Eligibility reasoning

**Document Processing**
- `pypdf` / `PyPDF2` — PDF text extraction
- Tesseract OCR (`tesseract-ocr`) — scanned PDFs and images
- System binary called via `subprocess` (no Python wrapper needed)

