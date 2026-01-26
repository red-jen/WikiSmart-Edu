# WikiSmart-Edu Startup Script
# This script helps you start both the backend and frontend

Write-Host "🚀 WikiSmart-Edu Startup" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host ""

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  Fichier .env non trouvé!" -ForegroundColor Yellow
    Write-Host "Veuillez créer un fichier .env avec vos clés API" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Exemple de contenu .env:" -ForegroundColor Cyan
    Write-Host "DATABASE_URL=postgresql+asyncpg://user:password@localhost/wikismart" -ForegroundColor Gray
    Write-Host "SECRET_KEY=your-secret-key-here" -ForegroundColor Gray
    Write-Host "GROQ_API_KEY=your-groq-api-key" -ForegroundColor Gray
    Write-Host "GEMINI_API_KEY=your-gemini-api-key" -ForegroundColor Gray
    Write-Host ""
    exit 1
}

Write-Host "Options de démarrage:" -ForegroundColor Green
Write-Host "1. Démarrer le backend FastAPI uniquement" -ForegroundColor White
Write-Host "2. Démarrer l'interface Streamlit uniquement" -ForegroundColor White
Write-Host "3. Démarrer les deux (backend + frontend)" -ForegroundColor White
Write-Host "4. Démarrer avec Docker Compose" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Choisissez une option (1-4)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "🔧 Démarrage du backend FastAPI..." -ForegroundColor Cyan
        Write-Host "API sera disponible sur: http://localhost:8000" -ForegroundColor Green
        Write-Host "Documentation: http://localhost:8000/docs" -ForegroundColor Green
        Write-Host ""
        uvicorn app.main:app --reload
    }
    "2" {
        Write-Host ""
        Write-Host "⚠️  Assurez-vous que le backend est démarré sur http://localhost:8000" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "🎨 Démarrage de l'interface Streamlit..." -ForegroundColor Cyan
        Write-Host "Interface sera disponible sur: http://localhost:8501" -ForegroundColor Green
        Write-Host ""
        streamlit run streamlit_app.py
    }
    "3" {
        Write-Host ""
        Write-Host "🔧 Démarrage du backend FastAPI..." -ForegroundColor Cyan
        Write-Host "API: http://localhost:8000" -ForegroundColor Green
        Write-Host ""
        
        # Start backend in background
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "uvicorn app.main:app --reload"
        
        Write-Host "⏳ Attente de 5 secondes pour le démarrage du backend..." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
        
        Write-Host ""
        Write-Host "🎨 Démarrage de l'interface Streamlit..." -ForegroundColor Cyan
        Write-Host "Interface: http://localhost:8501" -ForegroundColor Green
        Write-Host ""
        
        streamlit run streamlit_app.py
    }
    "4" {
        Write-Host ""
        Write-Host "🐳 Démarrage avec Docker Compose..." -ForegroundColor Cyan
        Write-Host ""
        docker-compose up -d
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✅ Services démarrés avec succès!" -ForegroundColor Green
            Write-Host "API: http://localhost:8000" -ForegroundColor Green
            Write-Host "Documentation: http://localhost:8000/docs" -ForegroundColor Green
            Write-Host ""
            Write-Host "Pour voir les logs:" -ForegroundColor Cyan
            Write-Host "docker-compose logs -f" -ForegroundColor Gray
            Write-Host ""
            Write-Host "Pour arrêter:" -ForegroundColor Cyan
            Write-Host "docker-compose down" -ForegroundColor Gray
        }
    }
    default {
        Write-Host ""
        Write-Host "❌ Option invalide" -ForegroundColor Red
        exit 1
    }
}
