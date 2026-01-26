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
    data = {
        "username": username,
        "password": password
    }
    result = api_call("POST", "/api/auth/login", data=data)
    
    if result:
        st.session_state.token = result.get("access_token")
        st.session_state.authenticated = True
        
        # Fetch user info
        user_info = api_call("GET", "/api/auth/me", use_auth=True)
        if user_info:
            st.session_state.user = user_info
        return True
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
        
        st.divider()
        
        # Navigation
        page = st.radio(
            "Navigation",
            ["🏠 Accueil", "📖 Wikipedia", "📄 PDF", "📊 Résumé", "🌍 Traduction", "❓ Quiz", "📝 Export"],
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
    elif page == "📝 Export":
        show_export_page()


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
                # Note: This endpoint needs to be created in the backend
                # For now, we'll show a placeholder
                st.info("⚠️ Cette fonctionnalité nécessite un endpoint API backend. Veuillez créer `/api/content/wikipedia` dans votre backend.")
                
                # Placeholder for future implementation
                st.session_state.article_content = {
                    "title": "Article Wikipedia",
                    "url": wiki_url,
                    "language": language,
                    "content": "Contenu extrait de l'article..."
                }
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
                # Note: This endpoint needs to be created in the backend
                st.info("⚠️ Cette fonctionnalité nécessite un endpoint API backend. Veuillez créer `/api/content/pdf` dans votre backend.")
                
                # Placeholder for future implementation
                st.session_state.article_content = {
                    "title": uploaded_file.name,
                    "source": "PDF",
                    "content": f"Texte extrait du fichier {uploaded_file.name}..."
                }
                
                st.success(f"✅ Texte extrait de {uploaded_file.name}")


def show_summary_page():
    """Display summary generation page."""
    st.title("📊 Génération de Résumé")
    
    if not st.session_state.article_content:
        st.warning("⚠️ Veuillez d'abord extraire du contenu depuis Wikipedia ou PDF")
        return
    
    st.markdown(f"**Source:** {st.session_state.article_content.get('title', 'N/A')}")
    
    summary_type = st.radio(
        "Type de résumé",
        ["Court (150 mots)", "Moyen (300 mots)"],
        horizontal=True
    )
    
    if st.button("✨ Générer le résumé", type="primary"):
        summary_mode = "short" if "Court" in summary_type else "medium"
        
        with st.spinner("Génération du résumé avec Groq..."):
            # Note: This endpoint needs to be created in the backend
            st.info("⚠️ Cette fonctionnalité nécessite un endpoint API backend. Veuillez créer `/api/llm/summary` dans votre backend.")
            
            # Placeholder
            st.session_state.summary = {
                "type": summary_mode,
                "content": f"Résumé {summary_mode} de l'article...",
                "generated_at": datetime.now().isoformat()
            }
    
    if st.session_state.summary:
        st.success("✅ Résumé généré avec succès!")
        
        st.subheader("📝 Résumé")
        st.markdown(f"**Type:** {st.session_state.summary.get('type', 'N/A').capitalize()}")
        
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
    
    target_lang = st.selectbox(
        "Langue cible",
        ["FR - Français", "EN - Anglais", "AR - Arabe", "ES - Espagnol"]
    )
    
    if st.button("🌐 Traduire", type="primary"):
        lang_code = target_lang.split(" - ")[0]
        
        with st.spinner(f"Traduction en {target_lang.split(' - ')[1]} avec Google Gemini..."):
            # Note: This endpoint needs to be created in the backend
            st.info("⚠️ Cette fonctionnalité nécessite un endpoint API backend. Veuillez créer `/api/llm/translate` dans votre backend.")
            
            # Placeholder
            st.session_state.translation = {
                "target_language": lang_code,
                "content": f"Texte traduit en {lang_code}...",
                "generated_at": datetime.now().isoformat()
            }
    
    if st.session_state.translation:
        st.success(f"✅ Traduction en {st.session_state.translation.get('target_language', 'N/A')} réussie!")
        
        st.subheader("📝 Traduction")
        
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
        
        col1, col2 = st.columns(2)
        with col1:
            num_questions = st.number_input("Nombre de questions", min_value=3, max_value=20, value=5)
        with col2:
            difficulty = st.select_slider("Difficulté", options=["Facile", "Moyen", "Difficile"])
        
        if st.button("🎲 Générer le quiz", type="primary"):
            with st.spinner("Génération du quiz avec Google Gemini..."):
                # Note: This endpoint needs to be created in the backend
                st.info("⚠️ Cette fonctionnalité nécessite un endpoint API backend. Veuillez créer `/api/llm/quiz` dans votre backend.")
                
                # Placeholder quiz
                st.session_state.quiz = {
                    "questions": [
                        {
                            "id": 1,
                            "question": "Question 1?",
                            "options": ["Option A", "Option B", "Option C", "Option D"],
                            "correct_answer": 0,
                            "user_answer": None
                        },
                        {
                            "id": 2,
                            "question": "Question 2?",
                            "options": ["Option A", "Option B", "Option C", "Option D"],
                            "correct_answer": 1,
                            "user_answer": None
                        }
                    ],
                    "difficulty": difficulty,
                    "num_questions": num_questions,
                    "generated_at": datetime.now().isoformat()
                }
                
                st.success("✅ Quiz généré avec succès!")
    
    with tab2:
        if not st.session_state.quiz:
            st.info("ℹ️ Générez d'abord un quiz dans l'onglet précédent")
        else:
            st.subheader("Répondez aux questions")
            
            questions = st.session_state.quiz.get('questions', [])
            
            for idx, q in enumerate(questions):
                st.markdown(f"**Question {idx + 1}:** {q['question']}")
                
                user_choice = st.radio(
                    f"Choisissez votre réponse",
                    q['options'],
                    key=f"q_{idx}",
                    label_visibility="collapsed"
                )
                
                # Store user answer
                q['user_answer'] = q['options'].index(user_choice)
                
                st.divider()
            
            if st.button("📊 Soumettre et voir les résultats", type="primary"):
                correct_count = sum(1 for q in questions if q['user_answer'] == q['correct_answer'])
                total_questions = len(questions)
                score = (correct_count / total_questions) * 100
                
                st.success(f"✅ Quiz terminé! Score: {correct_count}/{total_questions} ({score:.1f}%)")
                
                # Show detailed results
                st.subheader("📋 Résultats détaillés")
                for idx, q in enumerate(questions):
                    is_correct = q['user_answer'] == q['correct_answer']
                    status = "✅" if is_correct else "❌"
                    
                    st.markdown(f"{status} **Question {idx + 1}:** {q['question']}")
                    st.markdown(f"Votre réponse: {q['options'][q['user_answer']]}")
                    if not is_correct:
                        st.markdown(f"✓ Bonne réponse: {q['options'][q['correct_answer']]}")
                    st.divider()


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
        ["PDF", "TXT", "JSON"],
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
                # Note: This endpoint needs to be created in the backend
                st.info(f"⚠️ Cette fonctionnalité nécessite un endpoint API backend. Veuillez créer `/api/export/{export_format.lower()}` dans votre backend.")
                
                st.success(f"✅ Export {export_format} généré avec succès!")
                
                # Placeholder download button
                st.download_button(
                    label=f"📥 Télécharger ({export_format})",
                    data="Contenu exporté...",
                    file_name=f"wikismart_export.{export_format.lower()}",
                    mime="application/octet-stream"
                )
        else:
            st.warning("⚠️ Veuillez sélectionner au moins un élément à exporter")


# Main application logic
def main():
    """Main application entry point."""
    if not st.session_state.authenticated:
        show_login_page()
    else:
        show_main_app()


if __name__ == "__main__":
    main()
