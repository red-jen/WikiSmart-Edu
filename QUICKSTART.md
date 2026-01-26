# 🚀 Quick Start Guide - WikiSmart-Edu

## Prerequisites
- Python 3.10+
- PostgreSQL (or use Docker)
- Groq API Key (for summaries)
- Google Gemini API Key (for translation & quiz)

## Installation Steps

### 1. Clone and Setup

```bash
cd WikiSmart-Edu
```

### 2. Create Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory:

```env
# Application
APP_NAME=WikiSmart-Edu
APP_VERSION=1.0.0

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/wikismart_db

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Keys
GROQ_API_KEY=your-groq-api-key
GEMINI_API_KEY=your-gemini-api-key

# Models
GROQ_MODEL=mixtral-8x7b-32768
GEMINI_MODEL=gemini-pro
```

### 5. Setup Database

#### Option A: Using Docker
```bash
docker-compose up -d postgres
```

#### Option B: Local PostgreSQL
```bash
# Create database
createdb wikismart_db

# Run migrations (when alembic is set up)
alembic upgrade head
```

### 6. Start the Application

#### Option 1: Use the Startup Script (Easiest)
```bash
.\start.ps1
```
Then choose option 3 to start both backend and frontend.

#### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
uvicorn app.main:app --reload
```
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Terminal 2 - Frontend:**
```bash
streamlit run streamlit_app.py
```
- Interface: http://localhost:8501

#### Option 3: Docker Compose (All Services)
```bash
docker-compose up -d
```

## Using the Application

### 1. **Register/Login**
   - Open http://localhost:8501
   - Create an account or login

### 2. **Extract Content**
   - **Wikipedia**: Paste a Wikipedia URL
   - **PDF**: Upload a PDF file

### 3. **Generate Summary**
   - Choose summary type (short/medium)
   - Click generate

### 4. **Translate**
   - Select target language (FR/EN/AR/ES)
   - Generate translation

### 5. **Create Quiz**
   - Set number of questions
   - Select difficulty
   - Generate and answer quiz

### 6. **Export**
   - Choose content to export
   - Select format (PDF/TXT/JSON)
   - Download

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user

### Content (To be implemented)
- `POST /api/content/wikipedia` - Extract Wikipedia article
- `POST /api/content/pdf` - Extract PDF text

### LLM Services (To be implemented)
- `POST /api/llm/summary` - Generate summary
- `POST /api/llm/translate` - Translate text
- `POST /api/llm/quiz` - Generate quiz

### Export (To be implemented)
- `POST /api/export/pdf` - Export to PDF
- `POST /api/export/txt` - Export to TXT
- `POST /api/export/json` - Export to JSON

## Troubleshooting

### Backend won't start
- Check if PostgreSQL is running
- Verify DATABASE_URL in `.env`
- Check if port 8000 is available

### Streamlit connection error
- Ensure backend is running on http://localhost:8000
- Check API_BASE_URL in streamlit_app.py

### API Key errors
- Verify GROQ_API_KEY is valid
- Verify GEMINI_API_KEY is valid
- Check API key format in `.env`

### Database connection error
- Ensure PostgreSQL is running
- Check database credentials
- Verify database exists

## Next Steps

### Backend Endpoints to Implement
The Streamlit interface is ready, but you need to create these API endpoints in your FastAPI backend:

1. **Content Router** (`app/routers/content.py`):
   - Wikipedia extraction endpoint
   - PDF upload and extraction endpoint

2. **LLM Router** (`app/routers/llm.py`):
   - Summary generation endpoint
   - Translation endpoint
   - Quiz generation endpoint

3. **Export Router** (`app/routers/export.py`):
   - PDF export endpoint
   - TXT export endpoint
   - JSON export endpoint

### Testing
```bash
# Run tests
pytest

# With coverage
pytest --cov=app --cov-report=html
```

## Support

For issues or questions, please check:
- API Documentation: http://localhost:8000/docs
- Application logs
- Environment configuration

## Project Structure
```
WikiSmart-Edu/
├── app/                  # FastAPI backend
├── streamlit_app.py      # Streamlit frontend
├── streamlit_utils.py    # API client utilities
├── requirements.txt      # Dependencies
├── start.ps1            # Startup script
├── .env                 # Environment config
└── README.md            # Documentation
```
