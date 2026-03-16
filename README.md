# CineAI — Smart Movie Recommendation Platform
## Python / Flask Version

---

## How to Run (Any PC)

### Step 1 — Install Python
Download from: https://www.python.org/downloads/
✅ Make sure to check "Add Python to PATH" during install

### Step 2 — Open Terminal / Command Prompt
Navigate to this folder:
```
cd path/to/cineai
```

### Step 3 — Install Dependencies (one time only)
```
pip install -r requirements.txt
```

### Step 4 — Run the App
```
python app.py
```

### Step 5 — Open in Browser
Go to: http://localhost:5000

---

## Project Structure
```
cineai/
├── app.py              ← Main Python/Flask backend
├── requirements.txt    ← Python packages needed
├── README.md           ← This file
└── templates/
    └── index.html      ← Frontend HTML/CSS/JS (Jinja2 template)
```

---

## What Python Does (vs old HTML file)
| Feature                  | Old HTML         | New Python        |
|--------------------------|------------------|-------------------|
| TMDB API calls           | Via CORS proxies | Direct from Python (no CORS!) |
| Movie search             | In browser JS    | Python `/api/search` endpoint |
| Watch providers          | Frontend fetch   | Python fetches + passes to frontend |
| Poster fetching          | CORS proxy chain | Direct Python requests |
| Data passing             | Hardcoded JS     | Jinja2 template variables |

---

## Requirements
- Python 3.8+
- Internet connection (for TMDB API & images)
- Any modern browser
