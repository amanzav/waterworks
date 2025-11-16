"""Interactive Setup Wizard for Waterworks CLI"""

import os
import sys
import getpass
from pathlib import Path
from typing import Optional
import yaml

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None


def print_header():
    """Print welcome header"""
    print("\n" + "=" * 60)
    print("💧 Waterworks - Cover Letter Generator Setup Wizard")
    print("=" * 60)
    print("\nThis wizard will help you set up Waterworks for the first time.")
    print("You can always edit ~/.waterworks/config.yaml later.\n")


def prompt_with_default(prompt: str, default: str = "") -> str:
    """Prompt user with a default value
    
    Args:
        prompt: Prompt message
        default: Default value
        
    Returns:
        User input or default
    """
    if default:
        response = input(f"{prompt} [{default}]: ").strip()
        return response if response else default
    else:
        response = input(f"{prompt}: ").strip()
        while not response:
            print("  ⚠️  This field is required.")
            response = input(f"{prompt}: ").strip()
        return response


def extract_text_from_pdf(pdf_path: Path) -> Optional[str]:
    """Extract text from PDF file
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Extracted text or None if failed
    """
    if not PdfReader:
        print("  ⚠️  PyPDF2 not installed. Install with: pip install PyPDF2")
        return None
    
    try:
        reader = PdfReader(str(pdf_path))
        text_parts = []
        
        for page in reader.pages:
            text_parts.append(page.extract_text())
        
        text = "\n".join(text_parts)
        print(f"  ✅ Extracted {len(text)} characters from resume")
        return text
    except Exception as e:
        print(f"  ⚠️  Error extracting PDF text: {e}")
        return None


def setup_profile() -> dict:
    """Set up user profile information
    
    Returns:
        Profile configuration dictionary
    """
    print("\n📋 STEP 1: Profile Information")
    print("-" * 60)
    
    # Get resume path
    while True:
        resume_path = prompt_with_default(
            "Path to your resume PDF",
            ""
        )
        resume_path = Path(resume_path).expanduser()
        
        if resume_path.exists():
            print(f"  ✅ Found resume at {resume_path}")
            break
        else:
            print(f"  ❌ File not found: {resume_path}")
    
    # Extract resume text
    print("\n  Extracting text from resume...")
    resume_text = extract_text_from_pdf(resume_path)
    
    if not resume_text:
        print("  ⚠️  Couldn't extract text automatically.")
        print("  You can manually add it to config.yaml later.")
        resume_text = ""
    
    # Get additional info
    print("\n  Do you have additional information to include in cover letters")
    print("  that isn't in your resume? (e.g., specific interests, projects)")
    has_additional = input("  Add additional info? (y/n) [n]: ").strip().lower()
    
    additional_info = ""
    if has_additional == 'y':
        print("\n  Choose how to provide additional information:")
        print("    1. Type it now")
        print("    2. Provide a text file path")
        choice = input("  Choice (1/2) [1]: ").strip() or "1"
        
        if choice == "1":
            print("\n  Enter your additional information (press Ctrl+D when done on Unix, Ctrl+Z on Windows):")
            print("  " + "-" * 56)
            lines = []
            try:
                while True:
                    line = input()
                    lines.append(line)
            except EOFError:
                pass
            additional_info = "\n".join(lines)
        else:
            info_path = input("  Path to text file: ").strip()
            info_path = Path(info_path).expanduser()
            if info_path.exists():
                with open(info_path, 'r', encoding='utf-8') as f:
                    additional_info = f.read()
                print(f"  ✅ Loaded {len(additional_info)} characters")
            else:
                print(f"  ⚠️  File not found: {info_path}")
    
    # Get signature
    print("\n  What signature would you like to use for your cover letters?")
    signature = prompt_with_default(
        "Signature (e.g., your full name)",
        ""
    )
    
    return {
        "resume_pdf": str(resume_path),
        "resume_text": resume_text,
        "additional_info": additional_info,
        "signature": signature if signature else None
    }


def setup_waterloo_works() -> dict:
    """Set up Waterloo Works credentials
    
    Returns:
        Waterloo Works configuration dictionary
    """
    print("\n🔑 STEP 2: Waterloo Works Credentials")
    print("-" * 60)
    
    # Get and validate username (email)
    while True:
        username = prompt_with_default(
            "Waterloo Works username (email)",
            ""
        )
        
        # Basic email validation
        if "@" in username and "." in username:
            break
        else:
            print("  ⚠️  Please enter a valid email address")
    
    print("\n  For security, password will be prompted each time you run Waterworks.")
    print("  You can optionally save it in config.yaml (not recommended).")
    save_password = input("  Save password in config? (y/n) [n]: ").strip().lower()
    
    password = ""
    if save_password == 'y':
        password = getpass.getpass("  Password: ")
    
    return {
        "username": username,
        "password": password
    }


def setup_llm() -> dict:
    """Set up LLM provider and API key
    
    Returns:
        LLM configuration dictionary
    """
    print("\n🤖 STEP 3: LLM Configuration")
    print("-" * 60)
    
    print("\n  Available providers:")
    print("    1. OpenAI (gpt-4o-mini - recommended, fast and cheap)")
    print("    2. Anthropic (claude-3-5-haiku - good quality)")
    print("    3. Google Gemini (gemini-1.5-flash - free tier available)")
    print("    4. Groq (llama-3.1-8b - very fast, free)")
    
    provider_map = {
        "1": "openai",
        "2": "anthropic",
        "3": "gemini",
        "4": "groq"
    }
    
    choice = input("\n  Choose provider (1-4) [1]: ").strip() or "1"
    provider = provider_map.get(choice, "openai")
    
    # Default models per provider
    default_models = {
        "openai": "gpt-4o-mini",
        "anthropic": "claude-3-5-haiku-20241022",
        "gemini": "gemini-1.5-flash",
        "groq": "llama-3.1-8b-instant"
    }
    
    model = default_models[provider]
    print(f"  ✅ Selected {provider} with model {model}")
    
    # Get API key
    env_vars = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "gemini": "GOOGLE_API_KEY",
        "groq": "GROQ_API_KEY"
    }
    
    env_var = env_vars[provider]
    existing_key = os.getenv(env_var)
    
    api_keys = {
        "openai": "",
        "anthropic": "",
        "gemini": "",
        "groq": ""
    }
    
    if existing_key:
        print(f"\n  ✅ Found {env_var} in environment")
        print("  API key will be loaded from environment variable.")
    else:
        print(f"\n  Enter your {provider.capitalize()} API key.")
        print("  (It will be saved securely in ~/.waterworks/config.yaml)")
        api_key = getpass.getpass(f"\n  {provider.capitalize()} API Key: ").strip()
        
        if api_key:
            api_keys[provider] = api_key
            print(f"  ✅ API key saved")
        else:
            print(f"  ⚠️  No API key provided. You'll need to add it later.")
    
    return {
        "provider": provider,
        "model": model,
        "temperature": 0.7,
        "max_tokens": 800,
        "api_keys": api_keys
    }


def setup_paths_and_defaults() -> tuple[dict, dict]:
    """Set up paths and default settings
    
    Returns:
        Tuple of (paths dict, defaults dict)
    """
    print("\n📁 STEP 4: Paths and Defaults")
    print("-" * 60)
    
    cover_letters_dir = prompt_with_default(
        "Cover letters output directory",
        "./cover_letters"
    )
    
    default_folder = prompt_with_default(
        "Default Waterloo Works folder name",
        "waterworks"
    )
    
    print("\n  Job board options:")
    print("    1. Full-Cycle Service (default) - Jobs aligned with work term sequences")
    print("    2. Employer-Student Direct - Apply outside hiring cycles")
    job_board_choice = input("  Default job board (1/2) [1]: ").strip() or "1"
    default_job_board = "direct" if job_board_choice == "2" else "full"
    
    print("\n  Browser mode:")
    print("    1. Visible (default) - See the browser window during scraping")
    print("    2. Headless - Run browser hidden in background (faster)")
    browser_choice = input("  Browser mode (1/2) [1]: ").strip() or "1"
    headless = browser_choice == "2"
    
    paths = {
        "cover_letters_dir": cover_letters_dir,
        "cache_dir": "~/.waterworks/cache"
    }
    
    defaults = {
        "folder_name": default_folder,
        "job_board": default_job_board
    }
    
    browser = {
        "headless": headless
    }
    
    return paths, defaults, browser


def save_config(config: dict, config_path: Path):
    """Save configuration to file
    
    Args:
        config: Configuration dictionary
        config_path: Path to save config file
    """
    # Ensure directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    print(f"\n  ✅ Configuration saved to {config_path}")


def main():
    """Main setup wizard"""
    print_header()
    
    # Run setup steps
    profile = setup_profile()
    waterloo_works = setup_waterloo_works()
    llm = setup_llm()
    paths, defaults, browser = setup_paths_and_defaults()
    
    # Build config
    config = {
        "profile": profile,
        "waterloo_works": waterloo_works,
        "llm": llm,
        "browser": browser,
        "output": {
            "directory": paths["cover_letters_dir"],
            "format": "pdf",
            "filename_template": "{company}_{position}.pdf"
        },
        "paths": paths,
        "defaults": defaults
    }
    
    # Save config
    config_path = Path.home() / ".waterworks" / "config.yaml"
    
    print("\n" + "=" * 60)
    print("💾 Saving Configuration")
    print("=" * 60)
    
    if config_path.exists():
        overwrite = input(f"\n  Config already exists at {config_path}\n  Overwrite? (y/n) [n]: ").strip().lower()
        if overwrite != 'y':
            print("\n  ❌ Setup cancelled. Existing config preserved.")
            return
    
    save_config(config, config_path)
    
    # Print success
    print("\n" + "=" * 60)
    print("✅ Setup Complete!")
    print("=" * 60)
    print(f"\nConfiguration saved to: {config_path}")
    print("\nNext steps:")
    print("  1. Save jobs to a folder in Waterloo Works")
    print("  2. Run: python main.py generate --folder <folder_name>")
    print("  3. Review generated cover letters in:", paths["cover_letters_dir"])
    print("\nFor help: python main.py --help")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
