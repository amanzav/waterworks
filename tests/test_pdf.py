"""Test PDF generation"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.pdf_builder import PDFBuilder, sanitize_filename, get_document_name


def test_filename_sanitization():
    """Test filename sanitization"""
    print("\n" + "="*60)
    print("🧹 Testing Filename Sanitization")
    print("="*60)
    
    test_cases = [
        ("Google Inc.", "Google_Inc"),
        ("Software Engineer (Backend)", "Software_Engineer_Backend"),
        ("Jr. Developer / Intern", "Jr_Developer_Intern"),
        ("Full-Stack Developer", "Full-Stack_Developer"),
        ("Test: Special*Characters?", "Test_SpecialCharacters"),
    ]
    
    all_passed = True
    for input_text, expected in test_cases:
        result = sanitize_filename(input_text)
        passed = result == expected
        all_passed = all_passed and passed
        
        emoji = "✅" if passed else "❌"
        print(f"{emoji} '{input_text}' → '{result}' {'✓' if passed else f'(expected: {expected})'}")
    
    return all_passed


def test_document_naming():
    """Test document name generation"""
    print("\n" + "="*60)
    print("📝 Testing Document Naming")
    print("="*60)
    
    company = "Google Inc."
    job_title = "Software Engineer (Backend)"
    
    doc_name = get_document_name(company, job_title)
    expected = "Google_Inc_Software_Engineer_Backend"
    
    passed = doc_name == expected
    emoji = "✅" if passed else "❌"
    print(f"{emoji} Document name: {doc_name}")
    
    if not passed:
        print(f"   Expected: {expected}")
    
    return passed


def test_pdf_generation():
    """Test creating a PDF cover letter"""
    print("\n" + "="*60)
    print("📄 Testing PDF Generation")
    print("="*60)
    
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    
    test_cover_letter = """Dear Hiring Manager,

I am writing to express my strong interest in the Software Engineer position at Test Company. As a Computer Science student at the University of Waterloo, I am excited about this opportunity.

With my experience in full-stack development and passion for building scalable applications, I believe I would be a great fit for this role. I have worked with React, Node.js, and Python during my previous internships.

Thank you for considering my application.

Sincerely,
Test User"""
    
    try:
        builder = PDFBuilder(output_dir=output_dir)
        print("✅ PDFBuilder initialized")
        
        print("\n📝 Creating cover letter PDF...")
        pdf_path = builder.create_cover_letter(
            company="Test Company",
            job_title="Software Engineer",
            cover_text=test_cover_letter,
            signature="Test User"
        )
        
        if pdf_path and pdf_path.exists():
            file_size = pdf_path.stat().st_size
            print(f"✅ PDF created: {pdf_path.name}")
            print(f"✅ File size: {file_size:,} bytes")
            
            if file_size > 1000:  # Should be at least 1KB
                print("✅ PDF size looks reasonable")
                return True
            else:
                print("⚠️  PDF seems too small")
                return False
        else:
            print("❌ PDF file not created")
            return False
            
    except Exception as e:
        print(f"❌ Error creating PDF: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_pdfs():
    """Test creating multiple PDFs"""
    print("\n" + "="*60)
    print("📚 Testing Multiple PDF Generation")
    print("="*60)
    
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    
    test_cases = [
        ("Google", "Software Engineer"),
        ("Microsoft", "Backend Developer"),
        ("Amazon", "Full Stack Developer"),
    ]
    
    builder = PDFBuilder(output_dir=output_dir)
    created_pdfs = []
    
    for company, job_title in test_cases:
        cover_letter = f"Dear {company} Hiring Manager,\n\nI am interested in the {job_title} position.\n\nSincerely,\nTest User"
        
        try:
            pdf_path = builder.create_cover_letter(
                company=company,
                job_title=job_title,
                cover_text=cover_letter
            )
            
            if pdf_path and pdf_path.exists():
                created_pdfs.append(pdf_path)
                print(f"✅ Created: {pdf_path.name}")
            else:
                print(f"❌ Failed to create PDF for {company}")
                
        except Exception as e:
            print(f"❌ Error creating PDF for {company}: {e}")
    
    success = len(created_pdfs) == len(test_cases)
    print(f"\n{'✅' if success else '❌'} Created {len(created_pdfs)}/{len(test_cases)} PDFs")
    
    return success


def cleanup_test_files():
    """Clean up test output files"""
    print("\n" + "="*60)
    print("🧹 Cleaning Up Test Files")
    print("="*60)
    
    output_dir = Path("test_output")
    if output_dir.exists():
        count = 0
        for pdf_file in output_dir.glob("*.pdf"):
            pdf_file.unlink()
            count += 1
        
        for docx_file in output_dir.glob("*.docx"):
            docx_file.unlink()
            count += 1
        
        print(f"✅ Cleaned up {count} test files")
    else:
        print("⏭️  No test files to clean up")


if __name__ == "__main__":
    print("\n🦆 Geese - PDF Generation Tests")
    print("="*60)
    
    # Run tests
    result1 = test_filename_sanitization()
    result2 = test_document_naming()
    result3 = test_pdf_generation()
    result4 = test_multiple_pdfs()
    
    # Cleanup
    cleanup_test_files()
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    print(f"Filename Sanitization: {'✅ PASS' if result1 else '❌ FAIL'}")
    print(f"Document Naming: {'✅ PASS' if result2 else '❌ FAIL'}")
    print(f"PDF Generation: {'✅ PASS' if result3 else '❌ FAIL'}")
    print(f"Multiple PDFs: {'✅ PASS' if result4 else '❌ FAIL'}")
    
    if all([result1, result2, result3, result4]):
        print("\n🎉 All PDF tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed")
        sys.exit(1)
