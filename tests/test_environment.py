"""Test to verify environment setup is correct"""

import sys
import os
from pathlib import Path


def test_virtual_environment():
    """Check if running in a virtual environment"""
    print("\n" + "="*60)
    print("🔍 Virtual Environment Check")
    print("="*60)
    
    # Check if in virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if in_venv:
        print("✅ Running in virtual environment")
        print(f"   Location: {sys.prefix}")
        return True
    else:
        print("⚠️  NOT running in virtual environment")
        print("   It's recommended to use a virtual environment")
        print("   Run: python -m venv venv")
        print("   Then activate it before running tests")
        return False


def test_python_version():
    """Check Python version"""
    print("\n" + "="*60)
    print("🐍 Python Version Check")
    print("="*60)
    
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 9:
        print("✅ Python version is compatible (3.9+)")
        return True
    else:
        print("❌ Python 3.9+ required")
        return False


def test_dependencies():
    """Check if all dependencies are installed"""
    print("\n" + "="*60)
    print("📦 Dependencies Check")
    print("="*60)
    
    dependencies = [
        ("selenium", "selenium"),
        ("docx", "python-docx"),
        ("yaml", "PyYAML"),
        ("click", "click"),
        ("openai", "openai"),
        ("anthropic", "anthropic"),
        ("google.generativeai", "google-generativeai"),
        ("groq", "groq"),
    ]
    
    all_installed = True
    
    for module_name, package_name in dependencies:
        try:
            __import__(module_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name} - NOT INSTALLED")
            all_installed = False
    
    # Check optional dependencies
    print("\nOptional dependencies:")
    
    try:
        import pypandoc  # type: ignore
        print(f"✅ pypandoc (for PDF conversion fallback)")
    except ImportError:
        print(f"⚠️  pypandoc - not installed (optional)")
    
    # Platform-specific
    if sys.platform == "win32":
        try:
            import pythoncom
            print(f"✅ pywin32 (for Windows PDF conversion)")
        except ImportError:
            print(f"⚠️  pywin32 - not installed (needed for PDF on Windows)")
    
    return all_installed


def test_workspace_structure():
    """Check workspace structure"""
    print("\n" + "="*60)
    print("📁 Workspace Structure Check")
    print("="*60)
    
    required_files = [
        "main.py",
        "setup.py",
        "requirements.txt",
        "README.md",
        "modules/auth.py",
        "modules/config_manager.py",
        "modules/cover_letter_generator.py",
        "modules/folder_navigator.py",
        "modules/job_extractor.py",
        "modules/pdf_builder.py",
        "modules/utils.py",
    ]
    
    workspace_root = Path(__file__).parent.parent
    all_present = True
    
    for file_path in required_files:
        full_path = workspace_root / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - NOT FOUND")
            all_present = False
    
    return all_present


if __name__ == "__main__":
    print("\n💧 Waterworks - Environment Setup Verification")
    print("="*60)
    
    results = {
        "Python Version": test_python_version(),
        "Virtual Environment": test_virtual_environment(),
        "Dependencies": test_dependencies(),
        "Workspace Structure": test_workspace_structure(),
    }
    
    # Summary
    print("\n" + "="*60)
    print("📊 Summary")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 Environment setup is correct!")
        print("\nYou can now:")
        print("  1. Run: python setup.py")
        print("  2. Then: python main.py generate --folder <folder_name>")
        sys.exit(0)
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\nTips:")
        print("  • Make sure you're in the virtual environment (venv)")
        print("  • Run: pip install -r requirements.txt")
        print("  • Check you're in the correct directory")
        sys.exit(1)
