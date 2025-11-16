"""Test LLM providers and cover letter generation"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.cover_letter_generator import CoverLetterGenerator
from modules.config_manager import ConfigManager


def test_llm_connection():
    """Test connection to configured LLM provider"""
    print("\n" + "="*60)
    print("🤖 Testing LLM Connection")
    print("="*60)
    
    # Load config
    try:
        config = ConfigManager()
        config.load()
    except FileNotFoundError:
        print("❌ Config file not found. Run setup.py first.")
        return False
    
    provider = config.get("llm.provider")
    model = config.get("llm.model")
    
    print(f"\n📋 Provider: {provider}")
    print(f"📋 Model: {model}")
    
    # Check API key
    try:
        api_key = config.get_api_key(provider)
        if not api_key:
            print(f"❌ No API key configured for {provider}")
            print(f"   Set it with: python main.py config --set llm.api_keys.{provider} YOUR_KEY")
            return False
        print(f"✅ API key found for {provider}")
    except ValueError as e:
        print(f"❌ {e}")
        return False
    
    # Test simple generation
    print("\n🧪 Testing simple generation...")
    
    test_prompt = "Write a one-sentence test message to confirm the API is working."
    
    generator = CoverLetterGenerator(config)
    
    try:
        if provider == "openai":
            result = generator._generate_openai(test_prompt)
        elif provider == "anthropic":
            result = generator._generate_anthropic(test_prompt)
        elif provider == "gemini":
            result = generator._generate_gemini(test_prompt)
        elif provider == "groq":
            result = generator._generate_groq(test_prompt)
        else:
            print(f"❌ Unsupported provider: {provider}")
            return False
        
        if result:
            print(f"\n✅ {provider.upper()} API is working!")
            print(f"\n📝 Response: {result[:200]}...")
            return True
        else:
            print(f"\n❌ No response from {provider}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error testing {provider}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cover_letter_generation():
    """Test full cover letter generation"""
    print("\n" + "="*60)
    print("📝 Testing Cover Letter Generation")
    print("="*60)
    
    # Load config
    try:
        config = ConfigManager()
        config.load()
    except FileNotFoundError:
        print("❌ Config file not found. Run setup.py first.")
        return False
    
    provider = config.get("llm.provider")
    resume_text = config.get("profile.resume_text", "")
    additional_info = config.get("profile.additional_info", "")
    
    if not resume_text:
        print("❌ No resume text in config")
        return False
    
    print(f"\n📋 Provider: {provider}")
    print(f"📋 Resume length: {len(resume_text)} characters")
    
    # Mock job details
    job_details = {
        "title": "Software Engineer",
        "company": "Test Company Inc.",
        "location": "Waterloo, ON",
        "full_description": """
        We are seeking a talented Software Engineer to join our team.
        
        Responsibilities:
        - Develop and maintain web applications
        - Write clean, maintainable code
        - Collaborate with cross-functional teams
        
        Required Skills:
        - Python, JavaScript
        - React, Node.js
        - Git, Agile methodologies
        """
    }
    
    print(f"\n🧪 Generating cover letter for: {job_details['title']} at {job_details['company']}")
    
    generator = CoverLetterGenerator(config)
    
    try:
        cover_letter = generator.generate(
            resume_text=resume_text,
            job_details=job_details,
            additional_info=additional_info
        )
        
        if cover_letter and len(cover_letter) > 100:
            print(f"\n✅ Cover letter generated successfully!")
            print(f"📏 Length: {len(cover_letter)} characters")
            print(f"\n📄 Preview:")
            print("-" * 60)
            print(cover_letter[:500])
            if len(cover_letter) > 500:
                print(f"\n... ({len(cover_letter) - 500} more characters)")
            print("-" * 60)
            return True
        else:
            print(f"\n❌ Cover letter generation failed or too short")
            return False
            
    except Exception as e:
        print(f"\n❌ Error generating cover letter: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_all_providers():
    """Test all configured LLM providers"""
    print("\n" + "="*60)
    print("🤖 Testing All LLM Providers")
    print("="*60)
    
    try:
        config = ConfigManager()
        config.load()
    except FileNotFoundError:
        print("❌ Config file not found. Run setup.py first.")
        return False
    
    api_keys = config.get("llm.api_keys", {})
    
    results = {}
    test_prompt = "Say 'Hello' to confirm the API is working."
    
    for provider in ["openai", "anthropic", "gemini", "groq"]:
        print(f"\n🧪 Testing {provider.upper()}...")
        
        if not api_keys.get(provider):
            print(f"   ⏭️  Skipped (no API key)")
            results[provider] = "skipped"
            continue
        
        generator = CoverLetterGenerator(config)
        
        try:
            if provider == "openai":
                result = generator._generate_openai(test_prompt)
            elif provider == "anthropic":
                result = generator._generate_anthropic(test_prompt)
            elif provider == "gemini":
                result = generator._generate_gemini(test_prompt)
            elif provider == "groq":
                result = generator._generate_groq(test_prompt)
            
            if result:
                print(f"   ✅ {provider.upper()} working!")
                results[provider] = "pass"
            else:
                print(f"   ❌ {provider.upper()} failed")
                results[provider] = "fail"
                
        except Exception as e:
            print(f"   ❌ {provider.upper()} error: {str(e)[:100]}")
            results[provider] = "error"
    
    # Summary
    print("\n" + "="*60)
    print("📊 Provider Summary")
    print("="*60)
    for provider, status in results.items():
        emoji = "✅" if status == "pass" else "⏭️" if status == "skipped" else "❌"
        print(f"{emoji} {provider.upper()}: {status}")
    
    # Return True if at least one provider passed
    return any(status == "pass" for status in results.values())


if __name__ == "__main__":
    print("\n💧 Waterworks - LLM Tests")
    print("="*60)
    
    # Run LLM connection test
    result1 = test_llm_connection()
    
    # Run cover letter generation test
    result2 = test_cover_letter_generation()
    
    # Run all providers test
    result3 = test_all_providers()
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    print(f"LLM Connection: {'✅ PASS' if result1 else '❌ FAIL'}")
    print(f"Cover Letter Generation: {'✅ PASS' if result2 else '❌ FAIL'}")
    print(f"All Providers: {'✅ PASS' if result3 else '❌ FAIL'}")
    
    if result1 and result2:
        print("\n🎉 All LLM tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed")
        sys.exit(1)
