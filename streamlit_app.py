"""
WikiSmart-Edu - Streamlit Interface
Educational platform for autonomous learning from Wikipedia and PDF content
"""

import streamlit as st
import requests
from typing import Dict, Any, Optional
import json
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="WikiSmart-Edu",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #1f77b4;
        color: white;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user' not in st.session_state:
    st.session_state.user = None
if 'article_content' not in st.session_state:
    st.session_state.article_content = None
if 'summary' not in st.session_state:
    st.session_state.summary = None
if 'translation' not in st.session_state:
    st.session_state.translation = None
if 'quiz' not in st.session_state:
    st.session_state.quiz = None


# API Helper Functions
def api_call(method: str, endpoint: str, data: Optional[Dict] = None, 
             files: Optional[Dict] = None, use_auth: bool = False) -> Optional[Dict]:
    """Make API call to backend."""
    url = f"{API_BASE_URL}{endpoint}"
    headers = {}
    
    if use_auth and st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            if files:
                response = requests.post(url, files=files, headers=headers)
            else:
                headers["Content-Type"] = "application/json"
                response = requests.post(url, json=data, headers=headers)
        else:
            return None
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return None


def register_user(username: str, email: str, password: str) -> bool:
    """Register a new user."""
    data = {
        "username": username,
        "email": email,
        "password": password
    }
    result = api_call("POST", "/api/auth/register", data=data)
    return result is not None


def login_user(username: str, password: str) -> bool:
    """Login user and store token."""
    # OAuth2 expects form data, not JSON
    url = f"{API_BASE_URL}/api/auth/login"
    
    try:
        # Send as form data (x-www-form-urlencoded)
        response = requests.post(
            url,
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            result = response.json()
            st.session_state.token = result.get("access_token")
            st.session_state.authenticated = True
            
            # Fetch user info
            user_info = api_call("GET", "/api/auth/me", use_auth=True)
            if user_info:
                st.session_state.user = user_info
            return True
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return False


def logout_user():
    """Logout user and clear session."""
    st.session_state.authenticated = False
    st.session_state.token = None
    st.session_state.user = None
    st.session_state.article_content = None
    st.session_state.summary = None
    st.session_state.translation = None
    st.session_state.quiz = None


# Authentication Pages
def show_login_page():
    """Display login page."""
    st.markdown("<div class='main-header'>📚 WikiSmart-Edu</div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2rem;'>Plateforme éducative intelligente</p>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 Connexion", "📝 Inscription"])
    
    with tab1:
        st.subheader("Connexion")
        with st.form("login_form"):
            username = st.text_input("Nom d'utilisateur")
            password = st.text_input("Mot de passe", type="password")
            submit = st.form_submit_button("Se connecter")
            
            if submit:
                if username and password:
                    with st.spinner("Connexion en cours..."):
                        if login_user(username, password):
                            st.success("✅ Connexion réussie!")
                            st.rerun()
                        else:
                            st.error("❌ Identifiants incorrects")
                else:
                    st.warning("⚠️ Veuillez remplir tous les champs")
    
    with tab2:
        st.subheader("Créer un compte")
        with st.form("register_form"):
            new_username = st.text_input("Nom d'utilisateur")
            new_email = st.text_input("Email")
            new_password = st.text_input("Mot de passe", type="password")
            new_password_confirm = st.text_input("Confirmer le mot de passe", type="password")
            submit_register = st.form_submit_button("S'inscrire")
            
            if submit_register:
                if new_username and new_email and new_password and new_password_confirm:
                    if new_password == new_password_confirm:
                        with st.spinner("Création du compte..."):
                            if register_user(new_username, new_email, new_password):
                                st.success("✅ Compte créé avec succès! Vous pouvez maintenant vous connecter.")
                            else:
                                st.error("❌ Erreur lors de la création du compte")
                    else:
                        st.error("❌ Les mots de passe ne correspondent pas")
                else:
                    st.warning("⚠️ Veuillez remplir tous les champs")


def show_main_app():
    """Display main application interface."""
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/000000/book.png", width=80)
        st.title("WikiSmart-Edu")
        
        if st.session_state.user:
            st.markdown(f"**👤 {st.session_state.user.get('username', 'User')}**")
            st.markdown(f"📧 {st.session_state.user.get('email', '')}")
            user_role = st.session_state.user.get('role', 'user')
        else:
            user_role = 'user'
        
        st.divider()
        
        # Navigation - add admin if user is admin
        nav_options = ["🏠 Accueil", "📖 Wikipedia", "📄 PDF", "📊 Résumé", "🌍 Traduction", "❓ Quiz", "📚 Historique", "📝 Export"]
        if user_role == "admin":
            nav_options.append("👑 Admin")
        
        page = st.radio(
            "Navigation",
            nav_options,
            label_visibility="collapsed"
        )
        
        st.divider()
        
        if st.button("🚪 Déconnexion"):
            logout_user()
            st.rerun()
    
    # Main content
    if page == "🏠 Accueil":
        show_home_page()
    elif page == "📖 Wikipedia":
        show_wikipedia_page()
    elif page == "📄 PDF":
        show_pdf_page()
    elif page == "📊 Résumé":
        show_summary_page()
    elif page == "🌍 Traduction":
        show_translation_page()
    elif page == "❓ Quiz":
        show_quiz_page()
    elif page == "📚 Historique":
        show_history_page()
    elif page == "📝 Export":
        show_export_page()
    elif page == "👑 Admin":
        show_admin_page()


def show_home_page():
    """Display home page."""
    st.markdown("<div class='main-header'>Bienvenue sur WikiSmart-Edu</div>", unsafe_allow_html=True)
    
    st.markdown("""
    ### 🎯 Fonctionnalités principales
    
    Cette plateforme vous permet d'optimiser votre apprentissage autonome avec :
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        #### 📚 Contenu
        - Articles Wikipedia
        - Documents PDF
        - Extraction automatique
        """)
    
    with col2:
        st.markdown("""
        #### 🤖 IA
        - Résumés intelligents
        - Traduction multilingue
        - Quiz personnalisés
        """)
    
    with col3:
        st.markdown("""
        #### 💾 Export
        - Format PDF
        - Format TXT
        - Sauvegarde locale
        """)
    
    st.divider()
    
    st.markdown("""
    ### 🚀 Comment commencer ?
    
    1. **Choisissez votre source** : Wikipedia ou PDF
    2. **Générez un résumé** : Court ou moyen
    3. **Traduisez** : FR, EN, AR, ES
    4. **Testez vos connaissances** : Quiz QCM
    5. **Exportez** : Sauvegardez vos notes
    """)


def show_wikipedia_page():
    """Display Wikipedia content extraction page."""
    st.title("📖 Extraction Wikipedia")
    
    st.markdown("""
    Entrez l'URL d'un article Wikipedia pour extraire son contenu.
    """)
    
    wiki_url = st.text_input(
        "URL Wikipedia",
        placeholder="https://fr.wikipedia.org/wiki/Intelligence_artificielle"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        language = st.selectbox("Langue", ["fr", "en", "ar", "es"])
    
    if st.button("📥 Extraire le contenu", type="primary"):
        if wiki_url:
            with st.spinner("Extraction en cours..."):
                # Call the real API endpoint
                result = api_call(
                    "POST", 
                    "/api/content/wikipedia",
                    data={"url": wiki_url, "language": language},
                    use_auth=True
                )
                
                if result:
                    st.session_state.article_content = {
                        "title": result.get("title", "Article Wikipedia"),
                        "url": wiki_url,
                        "language": language,
                        "content": result.get("content", ""),
                        "source": result.get("source", "wikipedia"),
                        "character_count": result.get("character_count", 0)
                    }
                    st.success(f"✅ Article extrait: {result.get('title')}")
        else:
            st.warning("⚠️ Veuillez entrer une URL Wikipedia")
    
    # Display extracted content
    if st.session_state.article_content:
        st.success("✅ Contenu extrait avec succès!")
        
        st.subheader("📄 Article")
        st.markdown(f"**Titre:** {st.session_state.article_content.get('title', 'N/A')}")
        st.markdown(f"**URL:** {st.session_state.article_content.get('url', 'N/A')}")
        st.markdown(f"**Langue:** {st.session_state.article_content.get('language', 'N/A')}")
        
        with st.expander("📖 Voir le contenu complet"):
            st.text_area(
                "Contenu",
                st.session_state.article_content.get('content', ''),
                height=400,
                disabled=True
            )


def show_pdf_page():
    """Display PDF upload and extraction page."""
    st.title("📄 Extraction PDF")
    
    st.markdown("""
    Téléchargez un fichier PDF pour extraire son contenu texte.
    """)
    
    uploaded_file = st.file_uploader(
        "Choisir un fichier PDF",
        type=['pdf'],
        help="Formats supportés: PDF"
    )
    
    if uploaded_file is not None:
        if st.button("📥 Extraire le texte", type="primary"):
            with st.spinner("Extraction du texte..."):
                # Call the real API endpoint with file upload
                url = f"{API_BASE_URL}/api/content/pdf"
                headers = {}
                if st.session_state.token:
                    headers["Authorization"] = f"Bearer {st.session_state.token}"
                
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    response = requests.post(url, files=files, headers=headers)
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.article_content = {
                            "title": result.get("title", uploaded_file.name),
                            "source": "pdf",
                            "content": result.get("content", ""),
                            "character_count": result.get("character_count", 0)
                        }
                        st.success(f"✅ Texte extrait de {uploaded_file.name}")
                    else:
                        st.error(f"❌ Erreur: {response.text}")
                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")


def show_summary_page():
    """Display summary generation page."""
    st.title("📊 Génération de Résumé")
    
    if not st.session_state.article_content:
        st.warning("⚠️ Veuillez d'abord extraire du contenu depuis Wikipedia ou PDF")
        return
    
    st.markdown(f"**Source:** {st.session_state.article_content.get('title', 'N/A')}")
    st.markdown(f"**Caractères:** {st.session_state.article_content.get('character_count', len(st.session_state.article_content.get('content', '')))}")
    
    summary_type = st.radio(
        "Type de résumé",
        ["Court (150 mots)", "Moyen (300 mots)"],
        horizontal=True
    )
    
    if st.button("✨ Générer le résumé", type="primary"):
        summary_mode = "short" if "Court" in summary_type else "medium"
        
        with st.spinner("Génération du résumé avec Groq (Llama 3.3)..."):
            # Call the real API endpoint
            result = api_call(
                "POST",
                "/api/llm/summarize",
                data={
                    "content": st.session_state.article_content.get("content", ""),
                    "summary_type": summary_mode
                },
                use_auth=True
            )
            
            if result:
                st.session_state.summary = {
                    "type": summary_mode,
                    "content": result.get("summary", ""),
                    "word_count": result.get("word_count", 0),
                    "language": result.get("language", ""),
                    "generated_at": datetime.now().isoformat()
                }
                st.success("✅ Résumé généré avec succès!")
    
    if st.session_state.summary:
        st.subheader("📝 Résumé")
        st.markdown(f"**Type:** {st.session_state.summary.get('type', 'N/A').capitalize()}")
        st.markdown(f"**Mots:** {st.session_state.summary.get('word_count', 0)}")
        
        st.text_area(
            "Contenu du résumé",
            st.session_state.summary.get('content', ''),
            height=300,
            disabled=True
        )


def show_translation_page():
    """Display translation page."""
    st.title("🌍 Traduction")
    
    # Check if there's content to translate
    content_to_translate = None
    source_title = None
    
    if st.session_state.summary:
        content_to_translate = st.session_state.summary.get('content', '')
        source_title = "Résumé"
    elif st.session_state.article_content:
        content_to_translate = st.session_state.article_content.get('content', '')
        source_title = st.session_state.article_content.get('title', 'Article')
    
    if not content_to_translate:
        st.warning("⚠️ Veuillez d'abord extraire du contenu ou générer un résumé")
        return
    
    st.markdown(f"**Source:** {source_title}")
    st.markdown(f"**Caractères à traduire:** {len(content_to_translate)}")
    
    target_lang = st.selectbox(
        "Langue cible",
        ["FR - Français", "EN - Anglais", "AR - Arabe", "ES - Espagnol"]
    )
    
    if st.button("🌐 Traduire", type="primary"):
        lang_code = target_lang.split(" - ")[0].lower()
        lang_name = target_lang.split(" - ")[1]
        
        with st.spinner(f"Traduction en {lang_name} avec Google Gemini..."):
            # Call the real API endpoint
            result = api_call(
                "POST",
                "/api/llm/translate",
                data={
                    "content": content_to_translate,
                    "target_language": lang_code
                },
                use_auth=True
            )
            
            if result:
                st.session_state.translation = {
                    "target_language": lang_code,
                    "content": result.get("translated_text", ""),
                    "source_language": result.get("source_language", ""),
                    "generated_at": datetime.now().isoformat()
                }
                st.success(f"✅ Traduction en {lang_name} réussie!")
    
    if st.session_state.translation:
        st.subheader("📝 Traduction")
        st.markdown(f"**Langue cible:** {st.session_state.translation.get('target_language', 'N/A').upper()}")
        
        st.text_area(
            "Texte traduit",
            st.session_state.translation.get('content', ''),
            height=300,
            disabled=True
        )


def show_quiz_page():
    """Display quiz generation and taking page."""
    st.title("❓ Quiz")
    
    if not st.session_state.article_content:
        st.warning("⚠️ Veuillez d'abord extraire du contenu depuis Wikipedia ou PDF")
        return
    
    tab1, tab2 = st.tabs(["📝 Générer Quiz", "✅ Répondre au Quiz"])
    
    with tab1:
        st.subheader("Générer un nouveau quiz")
        st.markdown(f"**Source:** {st.session_state.article_content.get('title', 'N/A')}")
        
        col1, col2 = st.columns(2)
        with col1:
            num_mcq = st.number_input("Questions QCM", min_value=1, max_value=10, value=3)
        with col2:
            num_open = st.number_input("Questions ouvertes", min_value=0, max_value=5, value=2)
        
        if st.button("🎲 Générer le quiz", type="primary"):
            with st.spinner("Génération du quiz avec Google Gemini..."):
                # Call the real API endpoint
                result = api_call(
                    "POST",
                    "/api/llm/quiz/generate",
                    data={
                        "content": st.session_state.article_content.get("content", ""),
                        "num_mcq": num_mcq,
                        "num_open": num_open
                    },
                    use_auth=True
                )
                
                if result:
                    # Process API response into quiz format
                    questions = []
                    for idx, q in enumerate(result.get("questions", [])):
                        question_data = {
                            "id": idx + 1,
                            "question": q.get("question", ""),
                            "type": q.get("type", "mcq"),
                            "options": q.get("options", []),
                            "correct_answer": q.get("correct_answer", ""),
                            "user_answer": None
                        }
                        questions.append(question_data)
                    
                    st.session_state.quiz = {
                        "questions": questions,
                        "total_questions": result.get("total_questions", len(questions)),
                        "generated_at": datetime.now().isoformat()
                    }
                    st.success(f"✅ Quiz généré avec {len(questions)} questions!")
    
    with tab2:
        if not st.session_state.quiz:
            st.info("ℹ️ Générez d'abord un quiz dans l'onglet précédent")
        else:
            st.subheader("Répondez aux questions")
            
            questions = st.session_state.quiz.get('questions', [])
            user_answers = {}
            
            for idx, q in enumerate(questions):
                st.markdown(f"### Question {idx + 1}: {q['question']}")
                
                if q['type'] == 'mcq' and q.get('options'):
                    # Multiple choice question
                    user_choice = st.radio(
                        f"Choisissez votre réponse",
                        q['options'],
                        key=f"q_{idx}",
                        label_visibility="collapsed"
                    )
                    user_answers[idx] = user_choice
                else:
                    # Open-ended question
                    user_input = st.text_area(
                        "Votre réponse",
                        key=f"open_q_{idx}",
                        height=100
                    )
                    user_answers[idx] = user_input
                
                st.divider()
            
            if st.button("📊 Soumettre et voir les résultats", type="primary"):
                correct_count = 0
                total_questions = len(questions)
                
                st.subheader("📋 Résultats détaillés")
                
                for idx, q in enumerate(questions):
                    user_answer = user_answers.get(idx, "")
                    correct_answer = q.get('correct_answer', '')
                    
                    # For MCQ, compare directly
                    if q['type'] == 'mcq':
                        is_correct = user_answer == correct_answer
                    else:
                        # For open questions, do simple comparison (in real app, use AI to evaluate)
                        is_correct = user_answer.lower().strip() in correct_answer.lower()
                    
                    if is_correct:
                        correct_count += 1
                        st.markdown(f"✅ **Question {idx + 1}:** {q['question']}")
                        st.markdown(f"Votre réponse: {user_answer}")
                    else:
                        st.markdown(f"❌ **Question {idx + 1}:** {q['question']}")
                        st.markdown(f"Votre réponse: {user_answer}")
                        st.markdown(f"✓ Bonne réponse: {correct_answer}")
                    st.divider()
                
                score = (correct_count / total_questions) * 100 if total_questions > 0 else 0
                st.success(f"### 🎯 Score final: {correct_count}/{total_questions} ({score:.1f}%)")


def show_export_page():
    """Display export page."""
    st.title("📝 Export")
    
    st.markdown("""
    Exportez vos résumés, traductions et quiz dans différents formats.
    """)
    
    # Check what can be exported
    exportable_items = []
    if st.session_state.article_content:
        exportable_items.append("Article original")
    if st.session_state.summary:
        exportable_items.append("Résumé")
    if st.session_state.translation:
        exportable_items.append("Traduction")
    if st.session_state.quiz:
        exportable_items.append("Quiz")
    
    if not exportable_items:
        st.warning("⚠️ Aucun contenu à exporter. Générez d'abord du contenu.")
        return
    
    st.subheader("📦 Contenu disponible")
    for item in exportable_items:
        st.markdown(f"- ✅ {item}")
    
    st.divider()
    
    export_format = st.radio(
        "Format d'export",
        ["PDF", "TXT"],
        horizontal=True
    )
    
    items_to_export = st.multiselect(
        "Sélectionnez le contenu à exporter",
        exportable_items,
        default=exportable_items
    )
    
    if st.button("💾 Exporter", type="primary"):
        if items_to_export:
            with st.spinner(f"Génération du fichier {export_format}..."):
                # Prepare content for export
                title = st.session_state.article_content.get('title', 'WikiSmart Export') if st.session_state.article_content else 'WikiSmart Export'
                
                content_parts = []
                content_type = "summary"
                
                if "Article original" in items_to_export and st.session_state.article_content:
                    content_parts.append("=== ARTICLE ORIGINAL ===\n")
                    content_parts.append(st.session_state.article_content.get('content', ''))
                    content_parts.append("\n\n")
                
                if "Résumé" in items_to_export and st.session_state.summary:
                    content_parts.append("=== RÉSUMÉ ===\n")
                    content_parts.append(st.session_state.summary.get('content', ''))
                    content_parts.append("\n\n")
                    content_type = "summary"
                
                if "Traduction" in items_to_export and st.session_state.translation:
                    content_parts.append("=== TRADUCTION ===\n")
                    content_parts.append(st.session_state.translation.get('content', ''))
                    content_parts.append("\n\n")
                    content_type = "translation"
                
                if "Quiz" in items_to_export and st.session_state.quiz:
                    content_parts.append("=== QUIZ ===\n")
                    for q in st.session_state.quiz.get('questions', []):
                        content_parts.append(f"Q: {q['question']}\n")
                        if q.get('options'):
                            for opt in q['options']:
                                content_parts.append(f"  - {opt}\n")
                        content_parts.append(f"Réponse: {q.get('correct_answer', 'N/A')}\n\n")
                    content_type = "quiz"
                
                full_content = "".join(content_parts)
                
                # Call the real API endpoint
                endpoint = "/api/export/pdf" if export_format == "PDF" else "/api/export/txt"
                
                url = f"{API_BASE_URL}{endpoint}"
                headers = {"Content-Type": "application/json"}
                if st.session_state.token:
                    headers["Authorization"] = f"Bearer {st.session_state.token}"
                
                try:
                    response = requests.post(
                        url,
                        json={
                            "title": title,
                            "content": full_content,
                            "content_type": content_type,
                            "source_url": st.session_state.article_content.get('url', '') if st.session_state.article_content else ''
                        },
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        st.success(f"✅ Export {export_format} généré avec succès!")
                        
                        # Download button with actual content
                        file_ext = export_format.lower()
                        mime_type = "application/pdf" if export_format == "PDF" else "text/plain"
                        
                        st.download_button(
                            label=f"📥 Télécharger ({export_format})",
                            data=response.content,
                            file_name=f"wikismart_export.{file_ext}",
                            mime=mime_type
                        )
                    else:
                        st.error(f"❌ Erreur d'export: {response.text}")
                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")
        else:
            st.warning("⚠️ Veuillez sélectionner au moins un élément à exporter")


def show_history_page():
    """Display article history page."""
    st.title("📚 Historique des Articles")
    
    st.markdown("""
    Retrouvez ici tous vos articles, résumés, traductions et quiz précédents.
    """)
    
    # Fetch article history from API
    with st.spinner("Chargement de l'historique..."):
        result = api_call("GET", "/api/articles/", use_auth=True)
    
    if result:
        articles = result.get('articles', [])
        total = result.get('total', 0)
        
        st.markdown(f"**Total:** {total} article(s)")
        st.divider()
        
        if articles:
            for article in articles:
                with st.expander(f"📄 {article.get('title', 'Sans titre')} - {article.get('action', '').capitalize()}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Action:** {article.get('action', 'N/A')}")
                        st.markdown(f"**Langue:** {article.get('language', 'N/A')}")
                    with col2:
                        st.markdown(f"**Date:** {article.get('created_at', 'N/A')[:10]}")
                        if article.get('url'):
                            st.markdown(f"**URL:** [{article.get('url')[:30]}...]({article.get('url')})")
                    
                    st.markdown("---")
                    st.markdown("**Contenu:**")
                    content = article.get('content', '')
                    st.text_area("", content[:1000] + ("..." if len(content) > 1000 else ""), height=150, disabled=True, key=f"art_{article.get('id')}")
        else:
            st.info("ℹ️ Aucun article dans l'historique. Commencez par extraire un article Wikipedia ou PDF!")
    else:
        st.info("ℹ️ Aucun historique disponible ou erreur de connexion.")


def show_admin_page():
    """Display admin dashboard page."""
    st.title("👑 Tableau de Bord Admin")
    
    # Verify admin status
    if st.session_state.user and st.session_state.user.get('role') != 'admin':
        st.error("❌ Accès refusé. Privilèges admin requis.")
        return
    
    tab1, tab2 = st.tabs(["📊 Statistiques", "👥 Utilisateurs"])
    
    with tab1:
        st.subheader("📊 Statistiques Globales")
        
        with st.spinner("Chargement des statistiques..."):
            result = api_call("GET", "/api/admin/stats", use_auth=True)
        
        if result:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("👥 Utilisateurs", result.get('total_users', 0))
            with col2:
                st.metric("📄 Articles", result.get('total_articles', 0))
            with col3:
                st.metric("📊 Résumés", result.get('total_summaries', 0))
            with col4:
                st.metric("🌍 Traductions", result.get('total_translations', 0))
            
            st.divider()
            
            col5, col6, col7 = st.columns(3)
            with col5:
                st.metric("❓ Quiz Générés", result.get('total_quizzes_generated', 0))
            with col6:
                st.metric("✅ Quiz Tentatives", result.get('total_quiz_attempts', 0))
            with col7:
                avg_score = result.get('average_quiz_score', 0)
                st.metric("📈 Score Moyen", f"{avg_score:.1f}%")
        else:
            st.error("❌ Erreur lors du chargement des statistiques")
    
    with tab2:
        st.subheader("👥 Gestion des Utilisateurs")
        
        with st.spinner("Chargement des utilisateurs..."):
            result = api_call("GET", "/api/admin/users", use_auth=True)
        
        if result:
            users = result.get('users', [])
            
            if users:
                # Create a table
                for user in users:
                    with st.container():
                        col1, col2, col3, col4, col5 = st.columns([2, 3, 1, 1, 1])
                        
                        with col1:
                            st.markdown(f"**{user.get('username', 'N/A')}**")
                        with col2:
                            st.markdown(f"📧 {user.get('email', 'N/A')}")
                        with col3:
                            role = user.get('role', 'user')
                            role_badge = "👑" if role == "admin" else "👤"
                            st.markdown(f"{role_badge} {role}")
                        with col4:
                            st.markdown(f"📄 {user.get('article_count', 0)}")
                        with col5:
                            st.markdown(f"❓ {user.get('quiz_attempts', 0)}")
                        
                        st.divider()
            else:
                st.info("ℹ️ Aucun utilisateur trouvé")
        else:
            st.error("❌ Erreur lors du chargement des utilisateurs")


# Main application logic
def main():
    """Main application entry point."""
    if not st.session_state.authenticated:
        show_login_page()
    else:
        show_main_app()


if __name__ == "__main__":
    main()
