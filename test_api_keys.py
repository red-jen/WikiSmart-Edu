"""Test script to verify API keys are working."""

import asyncio
import sys
from app.config import settings
from app.services.llm_service import LLMService
from app.utils.logger import logger


async def test_groq_api():
    """Test Groq API connection and summarization."""
    print("\n🔍 Testing Groq API...")
    print(f"   API Key: {settings.GROQ_API_KEY[:10]}...{settings.GROQ_API_KEY[-4:]}")
    print(f"   Model: {settings.GROQ_MODEL}")
    
    try:
        llm_service = LLMService()
        test_content = """
        Artificial Intelligence (AI) refers to the simulation of human intelligence 
        in machines that are programmed to think and learn. AI systems can perform 
        tasks that typically require human intelligence, such as visual perception, 
        speech recognition, decision-making, and language translation.
        """
        
        summary = await llm_service.generate_summary(test_content, "short")
        print("   ✅ Groq API is working!")
        print(f"   Summary: {summary[:100]}...")
        return True
    except Exception as e:
        print(f"   ❌ Groq API Error: {str(e)}")
        return False


async def test_gemini_api():
    """Test Gemini API connection and translation."""
    print("\n🔍 Testing Gemini API...")
    print(f"   API Key: {settings.GEMINI_API_KEY[:10]}...{settings.GEMINI_API_KEY[-4:]}")
    print(f"   Model: {settings.GEMINI_MODEL}")
    
    try:
        llm_service = LLMService()
        test_text = "Hello, this is a test message to verify the translation service is working correctly."
        
        translation = await llm_service.translate_text(test_text, "FR")
        print("   ✅ Gemini API is working!")
        print(f"   Translation: {translation[:100]}...")
        return True
    except Exception as e:
        print(f"   ❌ Gemini API Error: {str(e)}")
        return False


async def test_gemini_quiz():
    """Test Gemini API quiz generation."""
    print("\n🔍 Testing Gemini Quiz Generation...")
    
    try:
        llm_service = LLMService()
        test_content = """
        Python is a high-level programming language. It was created by Guido van Rossum 
        and first released in 1991. Python emphasizes code readability and uses significant 
        indentation. It supports multiple programming paradigms including procedural, 
        object-oriented, and functional programming.
        """
        
        quiz = await llm_service.generate_quiz(test_content)
        print("   ✅ Gemini Quiz Generation is working!")
        print(f"   Quiz has {len(quiz.get('questions', []))} questions")
        return True
    except Exception as e:
        print(f"   ❌ Gemini Quiz Error: {str(e)}")
        return False


async def main():
    """Run all API tests."""
    print("=" * 60)
    print("🔑 WikiSmart-Edu API Key Verification")
    print("=" * 60)
    
    # Test configuration
    print("\n📋 Configuration:")
    print(f"   App Name: {settings.APP_NAME}")
    print(f"   Debug Mode: {settings.DEBUG}")
    
    # Run tests
    results = []
    results.append(await test_groq_api())
    results.append(await test_gemini_api())
    results.append(await test_gemini_quiz())
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n   Passed: {passed}/{total}")
    
    if passed == total:
        print("\n   ✅ All API keys are working correctly!")
        print("   🚀 Your application is ready to use!")
        return 0
    else:
        print("\n   ⚠️  Some API keys are not working.")
        print("   Please check your .env file configuration.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        sys.exit(1)
