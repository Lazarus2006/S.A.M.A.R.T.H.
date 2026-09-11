# Setup Guide

Everything needed to run S.A.M.A.R.T.H. on your machine.

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Linux / macOS | any modern | Tested on Pop!_OS 24.04 |
| Python | 3.10 or newer | `python3 --version` to check |
| Internet | required | For SarkariResult + Gemini API |
| Google account | — | For the free Gemini API key |

Windows users: WSL2 is recommended. Native Windows works but Tesseract paths differ.

## Step 1 — Install system dependencies

Tesseract is the OCR engine used for scanned PDFs and images. Install it at the
**system level** (it's a binary, not a Python package).

```bash
sudo apt update
sudo apt install -y tesseract-ocr python3-pypdf python3-pil
