"""
Utility functions for Streamlit app to interact with FastAPI backend
"""

import requests
from typing import Dict, Any, Optional
import streamlit as st


class APIClient:
    """Client for interacting with WikiSmart-Edu API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token = None
    
    def set_token(self, token: str):
        """Set authentication token."""
        self.token = token
    
    def _get_headers(self, use_auth: bool = False) -> Dict[str, str]:
        """Get request headers."""
        headers = {"Content-Type": "application/json"}
        if use_auth and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def _handle_response(self, response: requests.Response) -> Optional[Dict]:
        """Handle API response."""
        if response.status_code in [200, 201]:
            return response.json()
        elif response.status_code == 401:
            st.error("🔒 Session expirée. Veuillez vous reconnecter.")
            return None
        elif response.status_code == 404:
            st.error("❌ Ressource non trouvée")
            return None
        else:
            try:
                error_detail = response.json().get("detail", "Erreur inconnue")
            except:
                error_detail = response.text
            st.error(f"❌ Erreur {response.status_code}: {error_detail}")
            return None
    
    # Authentication endpoints
    def register(self, username: str, email: str, password: str) -> Optional[Dict]:
        """Register a new user."""
        url = f"{self.base_url}/api/auth/register"
        data = {
            "username": username,
            "email": email,
            "password": password
        }
        try:
            response = requests.post(url, json=data, headers=self._get_headers())
            return self._handle_response(response)
        except requests.exceptions.ConnectionError:
            st.error("🔌 Impossible de se connecter au serveur API. Assurez-vous que le backend est démarré.")
            return None
        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")
            return None
    
    def login(self, username: str, password: str) -> Optional[Dict]:
        """Login user."""
        url = f"{self.base_url}/api/auth/login"
        data = {
            "username": username,
            "password": password
        }
        try:
            response = requests.post(url, json=data, headers=self._get_headers())
            result = self._handle_response(response)
            if result and "access_token" in result:
                self.set_token(result["access_token"])
            return result
        except requests.exceptions.ConnectionError:
            st.error("🔌 Impossible de se connecter au serveur API. Assurez-vous que le backend est démarré.")
            return None
        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")
            return None
    
    def get_current_user(self) -> Optional[Dict]:
        """Get current user information."""
        url = f"{self.base_url}/api/auth/me"
        try:
            response = requests.get(url, headers=self._get_headers(use_auth=True))
            return self._handle_response(response)
        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")
            return None
    
    # Content extraction endpoints (to be implemented in backend)
    def extract_wikipedia(self, url: str, language: str = "fr") -> Optional[Dict]:
        """Extract content from Wikipedia URL."""
        endpoint = f"{self.base_url}/api/content/wikipedia"
        data = {
            "url": url,
            "language": language
        }
        try:
            response = requests.post(endpoint, json=data, headers=self._get_headers(use_auth=True))
            return self._handle_response(response)
        except requests.exceptions.ConnectionError:
            st.error("🔌 Impossible de se connecter au serveur API.")
            return None
        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")
            return None
    
    def extract_pdf(self, file_bytes: bytes, filename: str) -> Optional[Dict]:
        """Extract text from PDF file."""
        endpoint = f"{self.base_url}/api/content/pdf"
        files = {"file": (filename, file_bytes, "application/pdf")}
        try:
            headers = {}
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
            response = requests.post(endpoint, files=files, headers=headers)
            return self._handle_response(response)
        except requests.exceptions.ConnectionError:
            st.error("🔌 Impossible de se connecter au serveur API.")
            return None
        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")
            return None
    
    # LLM service endpoints
    def generate_summary(self, content: str, summary_type: str = "medium") -> Optional[Dict]:
        """Generate summary using Groq."""
        endpoint = f"{self.base_url}/api/llm/summary"
        data = {
            "content": content,
            "summary_type": summary_type
        }
        try:
            response = requests.post(endpoint, json=data, headers=self._get_headers(use_auth=True))
            return self._handle_response(response)
        except requests.exceptions.ConnectionError:
            st.error("🔌 Impossible de se connecter au serveur API.")
            return None
        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")
            return None
    
    def translate_text(self, content: str, target_language: str) -> Optional[Dict]:
        """Translate text using Google Gemini."""
        endpoint = f"{self.base_url}/api/llm/translate"
        data = {
            "content": content,
            "target_language": target_language
        }
        try:
            response = requests.post(endpoint, json=data, headers=self._get_headers(use_auth=True))
            return self._handle_response(response)
        except requests.exceptions.ConnectionError:
            st.error("🔌 Impossible de se connecter au serveur API.")
            return None
        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")
            return None
    
    def generate_quiz(self, content: str, num_questions: int = 5, 
                     difficulty: str = "medium") -> Optional[Dict]:
        """Generate quiz using Google Gemini."""
        endpoint = f"{self.base_url}/api/llm/quiz"
        data = {
            "content": content,
            "num_questions": num_questions,
            "difficulty": difficulty.lower()
        }
        try:
            response = requests.post(endpoint, json=data, headers=self._get_headers(use_auth=True))
            return self._handle_response(response)
        except requests.exceptions.ConnectionError:
            st.error("🔌 Impossible de se connecter au serveur API.")
            return None
        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")
            return None
    
    # Export endpoints
    def export_content(self, content_data: Dict, export_format: str = "pdf") -> Optional[bytes]:
        """Export content in specified format."""
        endpoint = f"{self.base_url}/api/export/{export_format.lower()}"
        try:
            response = requests.post(
                endpoint, 
                json=content_data, 
                headers=self._get_headers(use_auth=True)
            )
            if response.status_code == 200:
                return response.content
            else:
                self._handle_response(response)
                return None
        except requests.exceptions.ConnectionError:
            st.error("🔌 Impossible de se connecter au serveur API.")
            return None
        except Exception as e:
            st.error(f"❌ Erreur: {str(e)}")
            return None
    
    # Health check
    def health_check(self) -> bool:
        """Check if API is healthy."""
        url = f"{self.base_url}/health"
        try:
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except:
            return False


# Formatting utilities
def format_datetime(iso_string: str) -> str:
    """Format ISO datetime string to readable format."""
    from datetime import datetime
    try:
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        return dt.strftime("%d/%m/%Y %H:%M")
    except:
        return iso_string


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def calculate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """Calculate estimated reading time in minutes."""
    word_count = len(text.split())
    return max(1, round(word_count / words_per_minute))


# Session state helpers
def init_session_state():
    """Initialize Streamlit session state variables."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'token' not in st.session_state:
        st.session_state.token = None
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'api_client' not in st.session_state:
        st.session_state.api_client = APIClient()
    if 'article_content' not in st.session_state:
        st.session_state.article_content = None
    if 'summary' not in st.session_state:
        st.session_state.summary = None
    if 'translation' not in st.session_state:
        st.session_state.translation = None
    if 'quiz' not in st.session_state:
        st.session_state.quiz = None


def clear_content_state():
    """Clear all content-related session state."""
    st.session_state.article_content = None
    st.session_state.summary = None
    st.session_state.translation = None
    st.session_state.quiz = None


def logout():
    """Logout user and clear all session state."""
    st.session_state.authenticated = False
    st.session_state.token = None
    st.session_state.user = None
    st.session_state.api_client = APIClient()
    clear_content_state()
