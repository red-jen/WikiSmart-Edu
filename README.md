# WikiSmart-Edu

EduSmart est une plateforme éducative intelligente qui permet d'optimiser l'apprentissage autonome à partir de contenus Wikipedia et PDF.

## 🚀 Fonctionnalités

- **Ingestion de contenu** : Via URL Wikipedia ou téléchargement PDF
- **Résumé intelligent** : Généré via Groq (court/moyen)
- **Traduction** : Vers FR, EN, AR, ES via Google Gemini
- **Génération de quiz** : QCM et questions ouvertes au format JSON
- **Export** : PDF et TXT
- **Suivi personnalisé** : Historique et scores

## 🛠️ Technologies

### Backend
- **Framework** : FastAPI
- **Base de données** : PostgreSQL
- **ORM** : SQLAlchemy
- **Authentification** : OAuth 2.0 + JWT
- **Validation** : Pydantic
- **LLMs** : Groq (résumés), Google Gemini (traduction & quiz)

### Containerisation
- Docker
- Docker Compose

### Tests
- pytest
- pytest-asyncio
- pytest-cov

## 📦 Installation

### Prérequis
- Python 3.10+
- Docker & Docker Compose
- PostgreSQL

### Configuration

1. Cloner le dépôt :
```bash
git clone <repository-url>
cd WikiSmart-Edu
```

2. Créer un fichier `.env` basé sur `.env.example` :
```bash
cp .env.example .env
```

3. Configurer les variables d'environnement dans `.env`

4. Lancer avec Docker :
```bash
docker-compose up -d
```

Ou installer localement :
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Interface Streamlit

1. Assurez-vous que le backend FastAPI est en cours d'exécution sur `http://localhost:8000`

2. Dans un nouveau terminal, lancez l'interface Streamlit :
```bash
streamlit run streamlit_app.py
```

3. Accédez à l'interface dans votre navigateur : `http://localhost:8501`

**Fonctionnalités de l'interface :**
- 🔐 Authentification (connexion/inscription)
- 📖 Extraction de contenu Wikipedia
- 📄 Upload et extraction de PDF
- 📊 Génération de résumés intelligents
- 🌍 Traduction multilingue (FR, EN, AR, ES)
- ❓ Génération et passage de quiz
- 📝 Export en PDF/TXT/JSON

## 📁 Structure du projet

```
WikiSmart-Edu/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── articles.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_service.py
│   │   └── wikipedia_service.py
│   └── utils/
│       ├── __init__.py
│       ├── security.py
│       └── exceptions.py
├── tests/
├── alembic/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🧪 Tests

Exécuter les tests :
```bash
pytest
```

Avec couverture :
```bash
pytest --cov=app --cov-report=html
```

## 📊 Base de données

### Tables principales :
- **users** : Gestion des utilisateurs
- **articles** : Historique des articles traités
- **quizattempts** : Scores et tentatives de quiz

## 🔐 Sécurité

- Authentification OAuth 2.0 avec JWT
- Hashage des mots de passe avec bcrypt
- Validation des entrées avec Pydantic
- Gestion centralisée des exceptions

## 📝 License

MIT

## 👤 Auteur

EduSmart Team
