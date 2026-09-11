# Requirements Specification

Formal requirements for S.A.M.A.R.T.H. — Social Action Management And Real Time Help.

This document defines **what the system must do** (functional requirements),
**how well it must do it** (non-functional requirements), and the **constraints**
under which it was built.

For how to install and run it, see [`SETUP.md`](SETUP.md).
For how it works internally, see [`ARCHITECTURE.md`](ARCHITECTURE.md).

---

## 1. Purpose

S.A.M.A.R.T.H. is a prototype platform that reduces the friction between
qualified Indian citizens and government job opportunities. It does this by:

1. Reading a user's personal documents (resume, degree, ID, etc.)
2. Extracting a structured profile using AI
3. Fetching live government job notifications from trusted sources
4. Matching the profile against each job's requirements
5. Presenting ranked, source-backed results with document gap analysis

This document covers the prototype scope. Production requirements are noted
separately where they differ.

---

## 2. Scope

### In Scope

- Document upload and processing (PDF, image, text)
- AI-powered profile extraction
- Live job aggregation from a public source
- AI-powered requirement extraction from notifications
- Eligibility matching (qualification, age, documents)
- Document gap analysis (what the user has vs. what's needed)
- Ranked, source-linked results in a browser UI

### Out of Scope (for the prototype)

- User accounts, authentication, or session persistence
- Database storage of profiles or results
- Mobile application
- Hindi or regional-language output
- Free-form Q&A over notifications
- Automated deadline reminders
- Application tracking
- Integration with private-sector job boards
- Payment processing for application fees

These are documented in [`../README.md#-future-improvements`](../README.md#-future-improvements).

---

## 3. Functional Requirements

Numbered for traceability. **Must** = mandatory; **Should** = expected but
droppable under time pressure; **May** = nice to have.

### 3.1 Document Ingestion

| ID | Requirement | Priority | Status |
|---|---|---|---|
| FR-1.1 | The system **must** accept multiple uploaded files in a single submission | Must | ✅ Done |
| FR-1.2 | The system **must** accept PDF files | Must | ✅ Done |
| FR-1.3 | The system **must** accept common image formats (PNG, JPG, JPEG, WEBP, BMP, TIFF) | Must | ✅ Done |
| FR-1.4 | The system **must** accept plain-text files (TXT, MD, CSV) | Should | ✅ Done |
| FR-1.5 | The system **must** extract text from native PDFs | Must | ✅ Done |
| FR-1.6 | The system **must** extract text from images and scanned PDFs using OCR | Must | ✅ Done |
| FR-1.7 | The system **should** support Hindi OCR as an optional add-on | Should | ⚠️ Supported via `tesseract-ocr-hin`, not enabled by default |
| FR-1.8 | The system **must not** persist uploaded files to disk | Must | ✅ Done |
| FR-1.9 | The system **should** cap total input text to protect against oversized prompts | Should | ✅ Done (20,000 chars) |

### 3.2 Profile Extraction

| ID | Requirement | Priority | Status |
|---|---|---|---|
| FR-2.1 | The system **must** use an LLM to structure extracted text into a profile | Must | ✅ Done |
| FR-2.2 | The profile **must** include: name, email, phone, DOB, qualification, field of study, experience, skills, location, languages, documents present | Must | ✅ Done |
| FR-2.3 | The system **must** return structured JSON, not free-form text | Must | ✅ Done |
| FR-2.4 | The system **must** return `null` for fields it cannot determine — never fabricate | Must | ✅ Done |
| FR-2.5 | The user **must** be able to review and edit every extracted field before matching | Must | ✅ Done |
| FR-2.6 | The system **should** warn the user when a field could not be extracted | Should | ⚠️ Partial — empty fields shown blank |
| FR-2.7 | The system **must** display which documents were detected during extraction | Must | ✅ Done |

### 3.3 Job Aggregation

| ID | Requirement | Priority | Status |
|---|---|---|---|
| FR-3.1 | The system **must** fetch live government job listings from a public source | Must | ✅ Done (SarkariResult) |
| FR-3.2 | The system **must** fall back to a cached list when the live source is unreachable | Must | ✅ Done |
| FR-3.3 | The system **should** indicate to the client whether data is live or cached | Should | ✅ Done (`cached` field) |
| FR-3.4 | The system **must** cap the number of jobs processed per match request for latency | Must | ✅ Done (5 jobs) |
| FR-3.5 | The system **should** support adding new sources without restructuring the code | Should | ⚠️ Partial — scraper logic is source-specific |

### 3.4 Requirement Extraction

| ID | Requirement | Priority | Status |
|---|---|---|---|
| FR-4.1 | The system **must** extract: organization, post name, qualification, age limit, fee, last date, required documents, apply link | Must | ✅ Done |
| FR-4.2 | Extraction **must** return structured JSON | Must | ✅ Done |
| FR-4.3 | Missing fields **must** be returned as `null` or empty arrays, not invented | Must | ✅ Done |
| FR-4.4 | The system **should** cache extracted requirements per job URL to avoid repeat calls | Should | ❌ Not implemented |

### 3.5 Eligibility Matching

| ID | Requirement | Priority | Status |
|---|---|---|---|
| FR-5.1 | The system **must** compare the user's highest qualification against the job's allowed qualifications | Must | ✅ Done |
| FR-5.2 | The system **must** compare the user's age against the job's maximum age | Must | ✅ Done |
| FR-5.3 | The system **should** compare the user's category against the job's eligible categories | Should | ⚠️ Partial — captured but not enforced |
| FR-5.4 | The system **must** produce one of four eligibility states: `eligible`, `partial`, `not_eligible`, `unknown` | Must | ✅ Done |
| FR-5.5 | The system **must** default to `unknown` rather than guessing when data is insufficient | Must | ✅ Done |
| FR-5.6 | The system **must** rank results with eligible jobs first | Must | ✅ Done |

### 3.6 Document Gap Analysis

| ID | Requirement | Priority | Status |
|---|---|---|---|
| FR-6.1 | The system **must** compare the user's detected documents against each job's required documents | Must | ✅ Done |
| FR-6.2 | The system **must** display two distinct lists per job: documents the user has, and documents still needed | Must | ✅ Done |
| FR-6.3 | Matching **should** use fuzzy keyword matching rather than exact string equality | Should | ✅ Done |

### 3.7 User Interface

| ID | Requirement | Priority | Status |
|---|---|---|---|
| FR-7.1 | The UI **must** be a browser-based single-page application | Must | ✅ Done |
| FR-7.2 | The UI **must** support drag-and-drop file upload | Must | ✅ Done |
| FR-7.3 | The UI **must** show a loading state during long operations | Must | ✅ Done |
| FR-7.4 | The UI **must** display backend errors inline, not silently fail | Must | ✅ Done |
| FR-7.5 | The UI **should** be usable on mobile viewports | Should | ✅ Done (responsive CSS) |
| FR-7.6 | The UI **must** link each result to its official source notification | Must | ✅ Done |

### 3.8 Source Transparency

| ID | Requirement | Priority | Status |
|---|---|---|---|
| FR-8.1 | Every result **must** include the source URL of the official notification | Must | ✅ Done |
| FR-8.2 | The system **must not** display eligibility without an associated source | Must | ✅ Done |
| FR-8.3 | The system **should** show the raw snippet the AI used to derive a requirement | Should | ❌ Not implemented |

---

## 4. Non-Functional Requirements

### 4.1 Performance

| ID | Requirement | Target | Status |
|---|---|---|---|
| NFR-1.1 | Profile extraction latency (per upload batch) | ≤ 10 seconds | ✅ ~5 s typical |
| NFR-1.2 | Match latency (5 jobs, free Gemini tier) | ≤ 40 seconds | ✅ ~15–30 s |
| NFR-1.3 | Frontend initial load (cold) | ≤ 2 seconds | ✅ ~500 ms |
| NFR-1.4 | Server startup time | ≤ 3 seconds | ✅ < 2 s |

Latency is measured on a 4-core Linux machine with a standard broadband
connection. Gemini API is the dominant factor.

### 4.2 Reliability

| ID | Requirement | Status |
|---|---|---|
| NFR-2.1 | System **must** remain functional when the live scraper fails | ✅ Cache fallback |
| NFR-2.2 | System **must** return a clear error message when the LLM is unavailable | ✅ Shown inline |
| NFR-2.3 | System **must not** crash on malformed or password-protected PDFs | ✅ Wrapped in try/except |
| NFR-2.4 | System **must not** expose API keys or stack traces to the client | ✅ Only generic messages shown |

### 4.3 Security & Privacy

| ID | Requirement | Status |
|---|---|---|
| NFR-3.1 | Gemini API key **must** be read from an environment variable, never hardcoded | ✅ Done |
| NFR-3.2 | Uploaded files **must** be processed in memory and never written to persistent storage | ✅ Done |
| NFR-3.3 | The system **must not** store user PII across sessions | ✅ Stateless |
| NFR-3.4 | CORS **should** be restricted to known origins | ⚠️ Currently `*` — prototype only |
| NFR-3.5 | The system **should** rate-limit the `/extract-profile` endpoint | ❌ Not implemented |

### 4.4 Usability

| ID | Requirement | Status |
|---|---|---|
| NFR-4.1 | A first-time user **must** be able to complete the flow without instructions | ✅ Validated |
| NFR-4.2 | The system **must** give clear feedback within 1 second of every user action | ✅ Spinners and status messages |
| NFR-4.3 | Error messages **must** be in plain English, not stack traces | ✅ Done |

### 4.5 Compatibility

| ID | Requirement | Status |
|---|---|---|
| NFR-5.1 | Backend **must** run on Linux, macOS, and WSL2 | ✅ Validated on Pop!_OS |
| NFR-5.2 | Frontend **must** work on current Chrome, Firefox, and Edge | ✅ Validated |
| NFR-5.3 | Python version **must** be 3.10 or newer | ✅ Uses modern syntax |

### 4.6 Maintainability

| ID | Requirement | Status |
|---|---|---|
| NFR-6.1 | The system **must** run without a build step for the frontend | ✅ Vanilla HTML/JS |
| NFR-6.2 | The backend **must** be a single file for easy review | ✅ `app.py` |
| NFR-6.3 | New job sources **should** be addable without modifying existing endpoints | ⚠️ Partial |
| NFR-6.4 | All prompts to the LLM **should** be in one place per extraction task | ✅ Constants at top |

---

## 5. System Requirements

### Minimum (to run the prototype)

| Component | Requirement |
|---|---|
| OS | Linux (Debian/Ubuntu/Pop!_OS), macOS, or WSL2 |
| Python | 3.10 or newer |
| System packages | `tesseract-ocr`, `python3-pypdf`, `python3-pil` |
| Disk | ~500 MB (dependencies + OS packages) |
| RAM | 1 GB free |
| Network | Outbound HTTPS to `generativelanguage.googleapis.com` and `sarkariresult.com` |
| Credentials | A free Google Gemini API key |

### Recommended (for demo use)

| Component | Recommendation |
|---|---|
| OS | Pop!_OS 22.04 or Ubuntu 22.04 (tested) |
| Python | 3.12 |
| RAM | 2 GB free |
| Browser | Chromium-based (Chrome, Brave, Edge) |
| Network | Stable broadband (not mobile hotspot) |

---

## 6. Constraints

| ID | Constraint | Impact |
|---|---|---|
| C-1 | Gemini free tier is limited to 15 req/min and 1M tokens/day | Caps match batch size; production needs a paid tier |
| C-2 | SarkariResult has no official API and protects against scraping | Live fetch may fail; cached fallback required |
| C-3 | Tesseract OCR quality depends on image resolution and preprocessing | Scanned documents may extract imperfectly |
| C-4 | The prototype must run without a database | No persistence, no multi-user support |
| C-5 | Hackathon scope: ~3 weeks of part-time development | Features were prioritized for demo impact |
| C-6 | Government notifications do not follow a standard format | Requirement extraction is heuristic, not guaranteed |

---

## 7. Assumptions

| ID | Assumption | Risk if Invalid |
|---|---|---|
| A-1 | Users have a digital copy of their documents | Users without digital copies cannot use the platform |
| A-2 | Users can upload files from the device running the browser | Mobile users may struggle with PDFs stored elsewhere |
| A-3 | Government notifications are in English or Hindi | Other-language notifications may extract poorly |
| A-4 | SarkariResult remains publicly accessible | Cache fallback becomes the primary source |
| A-5 | The Gemini API remains freely available at current tier | Prototype becomes non-functional without payment |

---

## 8. Acceptance Criteria

The prototype is considered **complete and demo-ready** when all of the
following are true:

- [x] A user can upload multiple documents in one action
- [x] The system extracts a structured profile from those documents
- [x] The extracted profile is editable before matching
- [x] The system fetches live jobs from SarkariResult
- [x] The system falls back to cache when the live fetch fails
- [x] The system extracts job requirements with AI
- [x] The system produces a ranked list of matched jobs
- [x] Each result shows eligibility, required documents, deadline, fee, and source link
- [x] Each result distinguishes between documents the user has vs. documents still needed
- [x] The full flow runs in under 60 seconds on a typical laptop
- [x] The system is demoable without internet access (via cache fallback)

All criteria are met as of the current commit.

---

## 9. Requirements Traceability

Mapping from functional requirements to implementation:

| Requirement | Where implemented |
|---|---|
| FR-1.x (upload, OCR, PDF) | `app.py` → `extract_text`, `_text_from_pdf`, `_text_from_image` |
| FR-2.x (profile extraction) | `app.py` → `PROFILE_PROMPT`, `extract_profile` |
| FR-3.x (job aggregation) | `app.py` → `fetch_jobs_live`, `get_jobs` |
| FR-4.x (requirement extraction) | `app.py` → `REQUIREMENTS_PROMPT`, `extract_requirements` |
| FR-5.x (eligibility matching) | `app.py` → `QUAL_RANK`, `_qual_ok`, `match` |
| FR-6.x (document gap) | `app.py` → `_doc_gap`, `match` |
| FR-7.x (UI) | `index.html` → entire file |
| FR-8.x (source transparency) | `index.html` → `renderResults` |

---

## 10. Change Log

| Version | Date | Change |
|---|---|---|
| 0.1.0 | Sprint 1 | Original form-based flow (qualification dropdown) |
| 0.2.0 | Sprint 3 | Pivoted to document-first flow with AI extraction |
| 0.2.1 | Sprint 3 | Added document gap analysis |
| 0.2.2 | Sprint 3 | Added cache fallback for demo reliability |

---

