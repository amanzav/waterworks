"""Test PDF conversion on different platforms"""

import sys
import platform
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.pdf_builder import PDFBuilder


def test_pdf_conversion():
    """Test PDF conversion methods"""
    print("\n" + "="*60)
    print("🖨️  Testing PDF Conversion")
    print("="*60)
    
    # Detect platform
    system = platform.system()
    print(f"\nPlatform: {system}")
    
    # Create test directory
    test_dir = Path(__file__).parent / "test_output"
    test_dir.mkdir(exist_ok=True)
    
    # Create PDF builder
    builder = PDFBuilder(test_dir)
    
    # Test cover letter creation
    print("\nGenerating test cover letter...")
    
    test_company = "Test Company"
    test_title = "Software Engineer"
    test_content = """Dear Hiring Manager,

I am writing to express my interest in the Software Engineer position at Test Company.

With my background in computer science and experience in software development, I believe I would be a great fit for your team.

Thank you for considering my application."""
    
    try:
        success = builder.create_cover_letter(
            company=test_company,
            job_title=test_title,
            cover_text=test_content,
            signature="John Doe"
        )
        
        if success:
            print("\n✅ Cover letter generation successful!")
            
            # Check what was created
            pdf_path = test_dir / "Test_Company_Software_Engineer.pdf"
            docx_path = test_dir / "Test_Company_Software_Engineer.docx"
            
            if pdf_path.exists():
                print(f"✅ PDF created: {pdf_path}")
                print(f"   Size: {pdf_path.stat().st_size} bytes")
            elif docx_path.exists():
                print(f"⚠️  DOCX created (manual conversion needed): {docx_path}")
                print(f"   Size: {docx_path.stat().st_size} bytes")
            else:
                print("❌ No output file found")
                return False
            
            # Platform-specific advice
            print("\n📋 Platform-specific notes:")
            if system == "Windows":
                print("   • Windows: Should use docx2pdf with COM automation")
                print("   • Requires: Microsoft Word or pip install docx2pdf")
            elif system == "Darwin":  # macOS
                print("   • macOS: Uses LibreOffice if installed")
                print("   • Install: brew install libreoffice")
            elif system == "Linux":
                print("   • Linux: Uses LibreOffice if installed")
                print("   • Install: sudo apt-get install libreoffice")
            
            return True
        else:
            print("\n❌ Cover letter generation failed")
            return False
            
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_conversion_tools():
    """Check what PDF conversion tools are available"""
    print("\n" + "="*60)
    print("🔍 Checking Available Conversion Tools")
    print("="*60)
    
    system = platform.system()
    
    # Check docx2pdf (Windows)
    if system == "Windows":
        try:
            import docx2pdf
            print("✅ docx2pdf: Available")
        except ImportError:
            print("❌ docx2pdf: Not installed")
            print("   Install: pip install docx2pdf")
    
    # Check LibreOffice
    import subprocess
    libreoffice_found = False
    for cmd in ['libreoffice', 'soffice']:
        try:
            result = subprocess.run([cmd, '--version'], capture_output=True, timeout=5)
            if result.returncode == 0:
                version = result.stdout.decode().strip().split('\n')[0]
                print(f"✅ LibreOffice: {version}")
                libreoffice_found = True
                break
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    
    if not libreoffice_found:
        print("❌ LibreOffice: Not found")
        if system == "Darwin":
            print("   Install: brew install libreoffice")
        elif system == "Linux":
            print("   Install: sudo apt-get install libreoffice")
    
    # Check pypandoc
    try:
        import pypandoc
        print("✅ pypandoc: Available")
    except ImportError:
        print("⚠️  pypandoc: Not installed (optional fallback)")
        print("   Install: pip install pypandoc")
    
    print()


if __name__ == "__main__":
    print("\n💧 Waterworks - PDF Conversion Tests")
    print("="*60)
    
    # Check tools
    check_conversion_tools()
    
    # Run test
    result = test_pdf_conversion()
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    print(f"PDF Conversion Test: {'✅ PASS' if result else '❌ FAIL'}")
    
    if result:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed")
        sys.exit(1)
