# ATS Analyzer – Resume vs Job Description Matcher

![ATS Analyzer Dashboard](https://via.placeholder.com/1200x400?text=ATS+Analyzer+Dashboard)

A lightweight, self-hosted web application that analyzes your resume against a job description and provides actionable insights to improve your ATS (Applicant Tracking System) match score.

---

## 🎯 Features

- **ATS Match Score** (0–100): Get an overall compatibility score
- **Keyword Analysis**: Identify missing and weak keywords in your resume
- **Responsibility Matching**: Compare your experience against job requirements
- **Skill Gap Analysis**: Understand what skills you need to highlight
- **Smart Recommendations**: Get actionable tips to increase your ATS score
- **Resume Rewriting**: 
  - Rewritten summary section
  - Improved bullet point suggestions
  - ATS-optimized resume preview
- **Optional LLM Enhancement**: Use OpenAI to generate higher-quality bullet points (optional)
- **JSON API**: Programmatic access for automation

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+ installed

### Installation & Run

```powershell
# Clone the repository
git clone https://github.com/namann5/ats-checker.git
cd ats-checker

# Create a virtual environment
python -m venv .venv

# Activate it (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --port 8000
```

Open **http://127.0.0.1:8000** in your browser.

---

## 📝 How to Use

### Web Interface

1. **Paste Job Description**: Enter the full job posting text
2. **Paste Your Resume**: Enter your resume (plain text or formatted)
3. **Click Analyze**: Get instant feedback with:
   - ATS match percentage
   - Missing and weak keywords
   - Personalized recommendations
   - Optimized resume preview

### JSON API

For programmatic access:

```powershell
$body = @{
    job_description = "Software Engineer role..."
    resume = "Your resume text..."
} | ConvertTo-Json

curl -X POST http://127.0.0.1:8000/api/analyze `
  -H "Content-Type: application/json" `
  -d $body
```

**Python example:**

```python
import requests

jd = open('job_description.txt').read()
resume = open('resume.txt').read()

response = requests.post(
    'http://127.0.0.1:8000/api/analyze',
    json={'job_description': jd, 'resume': resume}
)

result = response.json()
print(f"Match Score: {result['match_score']}")
print(f"Missing Keywords: {result['missing_keywords']}")
```

---

## ⚙️ Configuration

### Environment Variables

Create a `back4app.env` file in the project root (template: `back4app.env.example`):

```
APPLICATION_ID=<your_back4app_app_id>
MASTER_KEY=<your_back4app_master_key>
OPENAI_API_KEY=<your_openai_api_key_optional>
```

**⚠️ Security Note**: 
- Never commit `back4app.env` to version control (it's in `.gitignore`)
- Keep your API keys confidential
- Use environment variables in production, not .env files

### Optional: OpenAI Integration

To enable AI-powered bullet rewriting:

1. Get an OpenAI API key from https://platform.openai.com/account/api-keys
2. Add `OPENAI_API_KEY` to your `back4app.env`
3. The app will automatically use OpenAI for enhanced bullet generation
4. If no key is provided, the app falls back to heuristic-based suggestions

---

## 🔧 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Main web interface |
| `/analyze` | POST | Web form analysis |
| `/api/analyze` | POST | JSON API analysis |
| `/api/app-id` | GET | Get configured Back4App App ID |
| `/api/validate-back4app` | GET | Validate Back4App credentials |
| `/api/rewrite-bullets` | POST | AI-enhanced bullet rewriting (requires OpenAI key) |
| `/admin` | GET | Admin panel for Back4App operations |
| `/api/create-class` | POST | Create a Parse class (admin) |
| `/api/upload-file` | POST | Upload a file to Back4App (admin) |

---

## 🧪 Testing

Run the test suite:

```powershell
pytest -v
```

Run with coverage report:

```powershell
pytest --cov=app --cov-report=html
```

---

## 📊 CI/CD Pipeline

The project includes a GitHub Actions workflow that:

- ✅ Runs linting (ruff)
- ✅ Executes unit tests
- ✅ Measures code coverage
- ✅ Uploads coverage to Codecov
- ✅ Enforces 70% coverage threshold

Every push to `main` triggers the CI pipeline automatically.

---

## 📁 Project Structure

```
ats-checker/
├── app/
│   ├── main.py                 # FastAPI server, ATS logic, endpoints
│   ├── templates/
│   │   ├── index.html          # Main UI
│   │   └── admin.html          # Admin panel
│   └── static/
│       └── styles.css          # Styling
├── tests/
│   ├── test_analysis.py        # Core analysis tests
│   ├── test_admin_endpoints.py # Admin endpoint tests
│   └── test_rewrite_llm.py     # LLM integration tests
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI config
├── requirements.txt            # Python dependencies
├── back4app.env.example        # Environment template
└── README.md                   # This file
```

---

## 🛠️ Technical Stack

| Component | Technology |
|-----------|-----------|
| **Web Framework** | FastAPI + Jinja2 |
| **NLP/ML** | scikit-learn (TF-IDF, cosine similarity) |
| **LLM** | OpenAI API (optional) |
| **Testing** | pytest, pytest-cov |
| **Linting** | ruff |
| **CI/CD** | GitHub Actions |
| **Backend** | Parse Server (Back4App) compatible |

---

## 💡 How It Works

### 1. **Keyword Extraction** (TF-IDF)
Extracts the most important terms from the job description using TF-IDF (Term Frequency-Inverse Document Frequency).

### 2. **Resume Analysis**
Compares your resume against extracted keywords to calculate:
- **Overlap Score**: How many important keywords appear in your resume
- **Semantic Similarity**: Using cosine similarity on TF-IDF vectors
- **Responsibility Match**: Checks for alignment of job duties

### 3. **Gap Analysis**
Identifies:
- **Missing Keywords**: Critical terms not in your resume
- **Weak Keywords**: Terms present but appearing infrequently
- **Skill Gaps**: Required skills that need emphasis

### 4. **Smart Recommendations**
Suggests:
- Which keywords to add
- How to reframe your experience
- Where to highlight metrics and achievements

### 5. **Resume Optimization** (Optional LLM)
- **Heuristic Mode** (default): Uses pattern matching to detect metrics (percentages, $, growth multipliers)
- **AI Mode** (with OpenAI key): Generates professional, achievement-focused bullet points using GPT

---

## 📈 Limitations & Future Enhancements

**Current Limitations:**
- Heuristic bullet generation works best with quantifiable achievements
- Does not validate job requirements against actual qualifications
- Single-pass analysis (no iterative feedback loops)

**Planned Enhancements:**
- Multi-format resume support (PDF, DOCX parsing)
- Interactive resume editor with live ATS scoring
- Job application tracking integration
- Resume templates by industry
- Batch analysis of multiple job postings

---

## 🔐 Privacy & Security

- **No Data Storage**: This app does not persist your resume or job description
- **Local Processing**: Analysis runs on your machine (unless using OpenAI API)
- **No Tracking**: No analytics or telemetry
- **Open Source**: Full source code available for inspection

---

## 📜 License

This project is provided as-is for educational and personal use. See the repository for any additional licensing info.

---

## 🤝 Contributing

Found a bug or have a feature request? Open an issue or pull request on GitHub!

---

## 📧 Support

For questions or issues, please visit: https://github.com/namann5/ats-checker/issues

---

**Made with ❤️ to help you land your next opportunity.**
