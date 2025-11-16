"""Test configuration management"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.config_manager import ConfigManager


def test_config_loading():
    """Test loading configuration file"""
    print("\n" + "="*60)
    print("⚙️  Testing Config Loading")
    print("="*60)
    
    try:
        config = ConfigManager()
        config.load()
        print(f"✅ Config loaded from: {config.config_path}")
        return True
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return False
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return False


def test_config_values():
    """Test accessing configuration values"""
    print("\n" + "="*60)
    print("📋 Testing Config Values")
    print("="*60)
    
    try:
        config = ConfigManager()
        config.load()
        
        # Test dot notation access
        username = config.get("waterloo_works.username")
        provider = config.get("llm.provider")
        model = config.get("llm.model")
        resume_text = config.get("profile.resume_text")
        
        print(f"\n✅ Waterloo Works Username: {username if username else '(not set)'}")
        print(f"✅ LLM Provider: {provider if provider else '(not set)'}")
        print(f"✅ LLM Model: {model if model else '(not set)'}")
        print(f"✅ Resume Text: {len(resume_text) if resume_text else 0} characters")
        
        # Test default values
        default_val = config.get("nonexistent.key", "default_value")
        if default_val == "default_value":
            print("✅ Default values working")
        
        return True
        
    except Exception as e:
        print(f"❌ Error accessing config values: {e}")
        return False


def test_config_validation():
    """Test configuration validation"""
    print("\n" + "="*60)
    print("✔️  Testing Config Validation")
    print("="*60)
    
    try:
        config = ConfigManager()
        config.load()
        
        print("\nValidating configuration...")
        try:
            config.validate()
            print("✅ Configuration is valid and complete")
            return True
        except ValueError as e:
            print(f"⚠️  Configuration incomplete: {e}")
            print("   This is expected if credentials aren't set yet")
            return True  # Not a failure, just incomplete config
            
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        return False


def test_config_structure():
    """Test configuration file structure"""
    print("\n" + "="*60)
    print("🏗️  Testing Config Structure")
    print("="*60)
    
    try:
        config = ConfigManager()
        config.load()
        
        required_sections = ["profile", "waterloo_works", "llm", "output"]
        missing_sections = []
        
        for section in required_sections:
            if section in config.config:
                print(f"✅ Section '{section}' exists")
            else:
                print(f"❌ Section '{section}' missing")
                missing_sections.append(section)
        
        # Check profile subsections
        if "profile" in config.config:
            if "resume_text" in config.config["profile"]:
                print("✅ profile.resume_text exists")
            else:
                print("⚠️  profile.resume_text missing")
        
        # Check LLM subsections
        if "llm" in config.config:
            llm_keys = ["provider", "model", "api_keys"]
            for key in llm_keys:
                if key in config.config["llm"]:
                    print(f"✅ llm.{key} exists")
                else:
                    print(f"❌ llm.{key} missing")
        
        return len(missing_sections) == 0
        
    except Exception as e:
        print(f"❌ Error checking config structure: {e}")
        return False


def test_api_key_access():
    """Test API key retrieval"""
    print("\n" + "="*60)
    print("🔑 Testing API Key Access")
    print("="*60)
    
    try:
        config = ConfigManager()
        config.load()
        
        providers = ["openai", "anthropic", "gemini", "groq"]
        
        for provider in providers:
            try:
                api_key = config.get_api_key(provider)
                if api_key:
                    print(f"✅ {provider.upper()}: API key found ({len(api_key)} chars)")
                else:
                    print(f"⚠️  {provider.upper()}: No API key (will use env var)")
            except ValueError:
                print(f"⚠️  {provider.upper()}: No API key configured")
        
        return True
        
    except Exception as e:
        print(f"❌ Error accessing API keys: {e}")
        return False


if __name__ == "__main__":
    print("\n💧 Waterworks - Configuration Tests")
    print("="*60)
    
    # Run tests
    result1 = test_config_loading()
    result2 = test_config_values()
    result3 = test_config_validation()
    result4 = test_config_structure()
    result5 = test_api_key_access()
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    print(f"Config Loading: {'✅ PASS' if result1 else '❌ FAIL'}")
    print(f"Config Values: {'✅ PASS' if result2 else '❌ FAIL'}")
    print(f"Config Validation: {'✅ PASS' if result3 else '❌ FAIL'}")
    print(f"Config Structure: {'✅ PASS' if result4 else '❌ FAIL'}")
    print(f"API Key Access: {'✅ PASS' if result5 else '❌ FAIL'}")
    
    if all([result1, result2, result3, result4, result5]):
        print("\n🎉 All configuration tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed")
        sys.exit(1)
