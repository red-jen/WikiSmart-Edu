"""LLM Service for interacting with Groq and Google Gemini APIs."""

import json
from typing import Dict, Any, List
from groq import Groq
import google.generativeai as genai

from app.config import settings
from app.utils.exceptions import LLMServiceException
from app.utils.logger import logger


class LLMService:
    """Service for handling LLM operations with Groq and Gemini."""
    
    def __init__(self):
        """Initialize LLM clients with API keys from settings."""
        # Initialize Groq client for summaries
        self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
        
        # Initialize Google Gemini for translation and quiz generation
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.gemini_model = genai.GenerativeModel(settings.GEMINI_MODEL)
    
    async def generate_summary(self, content: str, summary_type: str = "medium") -> str:
        """
        Generate a summary using Groq API.
        
        Args:
            content: The article content to summarize
            summary_type: "short" or "medium"
        
        Returns:
            str: The generated summary
        """
        try:
            # Define prompt based on summary type
            if summary_type == "short":
                max_words = 150
                instruction = "Créez un résumé très concis"
            else:  # medium
                max_words = 300
                instruction = "Créez un résumé détaillé mais concis"
            
            prompt = f"""
{instruction} de l'article suivant en maximum {max_words} mots.
Le résumé doit capturer les points clés et les informations essentielles.

Article:
{content}

Résumé:
"""
            
            logger.info(f"Generating {summary_type} summary with Groq")
            
            # Call Groq API
            response = self.groq_client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "Vous êtes un assistant expert en résumé de textes académiques."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=settings.GROQ_TEMPERATURE,
                max_tokens=settings.GROQ_MAX_TOKENS
            )
            
            summary = response.choices[0].message.content.strip()
            logger.info("Summary generated successfully")
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary with Groq: {str(e)}")
            raise LLMServiceException(f"Failed to generate summary: {str(e)}")
    
    async def translate_text(self, content: str, target_language: str) -> str:
        """
        Translate text using Google Gemini API.
        
        Args:
            content: The text to translate
            target_language: Target language code (FR, EN, AR, ES)
        
        Returns:
            str: The translated text
        """
        try:
            language_names = {
                "FR": "français",
                "EN": "anglais",
                "AR": "arabe",
                "ES": "espagnol"
            }
            
            target_lang_name = language_names.get(target_language, target_language)
            
            prompt = f"""
Traduisez fidèlement le texte suivant en {target_lang_name}.
Conservez le sens original, le ton et la structure du texte.

Texte à traduire:
{content}

Traduction en {target_lang_name}:
"""
            
            logger.info(f"Translating text to {target_language} with Gemini")
            
            # Generate content with Gemini
            response = self.gemini_model.generate_content(
                prompt,
                generation_config={
                    "temperature": settings.GEMINI_TEMPERATURE,
                    "max_output_tokens": settings.GEMINI_MAX_TOKENS
                }
            )
            
            translation = response.text.strip()
            logger.info("Translation completed successfully")
            
            return translation
            
        except Exception as e:
            logger.error(f"Error translating with Gemini: {str(e)}")
            raise LLMServiceException(f"Failed to translate text: {str(e)}")
    
    async def generate_quiz(
        self,
        content: str,
        num_mcq: int = 5,
        num_open: int = 3
    ) -> Dict[str, Any]:
        """
        Generate quiz questions using Google Gemini API.
        
        Args:
            content: The article content
            num_mcq: Number of multiple choice questions
            num_open: Number of open-ended questions
        
        Returns:
            Dict containing quiz data with MCQ and open questions
        """
        try:
            prompt = f"""
Générez un quiz éducatif basé sur le contenu suivant.

Le quiz doit contenir:
1. {num_mcq} questions à choix multiples (QCM) avec 4 options chacune
2. {num_open} questions ouvertes courtes

Pour chaque QCM:
- Proposez 4 options (A, B, C, D)
- Une seule bonne réponse
- Les distracteurs doivent être plausibles

Pour les questions ouvertes:
- Questions qui nécessitent une réponse courte (1-3 phrases)

Retournez UNIQUEMENT un objet JSON valide avec cette structure exacte:
{{
  "mcq_questions": [
    {{
      "question": "Question text",
      "options": {{
        "A": "Option A",
        "B": "Option B",
        "C": "Option C",
        "D": "Option D"
      }},
      "correct_answer": "A",
      "explanation": "Brief explanation"
    }}
  ],
  "open_questions": [
    {{
      "question": "Question text",
      "suggested_answer": "Model answer"
    }}
  ]
}}

Contenu de l'article:
{content}

JSON du quiz:
"""
            
            logger.info(f"Generating quiz with {num_mcq} MCQ and {num_open} open questions")
            
            # Generate content with Gemini
            response = self.gemini_model.generate_content(
                prompt,
                generation_config={
                    "temperature": settings.GEMINI_TEMPERATURE,
                    "max_output_tokens": settings.GEMINI_MAX_TOKENS
                }
            )
            
            # Parse JSON response
            quiz_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if quiz_text.startswith("```json"):
                quiz_text = quiz_text[7:]
            if quiz_text.startswith("```"):
                quiz_text = quiz_text[3:]
            if quiz_text.endswith("```"):
                quiz_text = quiz_text[:-3]
            
            quiz_data = json.loads(quiz_text.strip())
            
            logger.info("Quiz generated successfully")
            
            return quiz_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing quiz JSON: {str(e)}")
            raise LLMServiceException(f"Failed to parse quiz response: {str(e)}")
        except Exception as e:
            logger.error(f"Error generating quiz with Gemini: {str(e)}")
            raise LLMServiceException(f"Failed to generate quiz: {str(e)}")


# Singleton instance
llm_service = LLMService()
