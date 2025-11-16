"""PDF generation module for cover letters"""

import re
from pathlib import Path
from typing import Optional
from docx import Document
from docx.shared import Pt
import pythoncom


def sanitize_filename(text: str) -> str:
    """Sanitize text for use as filename
    
    Args:
        text: Text to sanitize
        
    Returns:
        Sanitized filename-safe string
    """
    # Replace special characters
    text = text.replace('/', '_')
    text = text.replace('\\', '_')
    text = text.replace(':', '_')
    text = text.replace('*', '_')
    text = text.replace('?', '_')
    text = text.replace('"', '')
    text = text.replace('<', '')
    text = text.replace('>', '')
    text = text.replace('|', '_')
    text = text.replace('(', '')
    text = text.replace(')', '')
    text = text.replace('[', '')
    text = text.replace(']', '')
    text = text.replace('{', '')
    text = text.replace('}', '')
    
    # Remove non-word characters
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip().replace(' ', '_')
    text = re.sub(r'_+', '_', text)
    
    return text.strip('_')


def get_document_name(company: str, job_title: str) -> str:
    """Get document name for a cover letter
    
    Args:
        company: Company name
        job_title: Job title
        
    Returns:
        Sanitized document name (without extension)
    """
    company_clean = sanitize_filename(company)
    title_clean = sanitize_filename(job_title)
    return f"{company_clean}_{title_clean}"


class PDFBuilder:
    """Build PDF cover letters from text"""
    
    def __init__(self, output_dir: Path, template_path: Optional[Path] = None):
        """Initialize PDF builder
        
        Args:
            output_dir: Directory to save PDFs
            template_path: Optional path to DOCX template
        """
        self.output_dir = output_dir
        self.template_path = template_path
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def create_cover_letter(
        self,
        company: str,
        job_title: str,
        cover_text: str,
        signature: Optional[str] = None
    ) -> bool:
        """Create a cover letter PDF
        
        Args:
            company: Company name
            job_title: Job title
            cover_text: Cover letter body text
            signature: Signature line (uses config or "Sincerely" if not provided)
            
        Returns:
            True if successful
        """
        doc_name = get_document_name(company, job_title)
        
        try:
            # Create or load document
            if self.template_path and self.template_path.exists():
                document = Document(str(self.template_path))
            else:
                document = Document()
            
            # Add cover letter text
            full_text = f"{cover_text}\n\n{signature}"
            
            paragraph = document.add_paragraph()
            run = paragraph.add_run(full_text)
            run.font.size = Pt(11)
            run.font.name = "Garamond"
            
            # Save as DOCX
            docx_path = self.output_dir / f"{doc_name}.docx"
            document.save(str(docx_path))
            
            # Convert to PDF
            self._convert_to_pdf(docx_path)
            
            # Remove DOCX file
            docx_path.unlink()
            
            return True
            
        except Exception as e:
            print(f"      ✗ Error creating PDF: {e}")
            return False
    
    def _convert_to_pdf(self, docx_path: Path) -> bool:
        """Convert DOCX to PDF
        
        Args:
            docx_path: Path to DOCX file
            
        Returns:
            True if successful
        """
        import platform
        
        # Check if running on Windows
        if platform.system() != "Windows":
            print(f"      ⚠️  PDF conversion only supported on Windows")
            print(f"      ℹ️  DOCX file saved at: {docx_path}")
            print(f"      💡 Tip: Use LibreOffice or similar to convert manually:")
            print(f"          libreoffice --headless --convert-to pdf '{docx_path}'")
            return False
        
        try:
            # Initialize COM for Windows
            pythoncom.CoInitialize()
            
            try:
                # Import here to avoid issues on non-Windows platforms
                from docx2pdf import convert
                
                # Convert (docx2pdf automatically uses same name with .pdf extension)
                convert(str(docx_path))
                
                return True
            finally:
                # Always uninitialize COM
                pythoncom.CoUninitialize()
            
        except ImportError as e:
            print(f"      ⚠️  PDF conversion library not available: {e}")
            print(f"      ℹ️  DOCX file saved at: {docx_path}")
            print(f"      💡 Install with: pip install docx2pdf")
            return False
        except Exception as e:
            print(f"      ⚠️  PDF conversion failed: {e}")
            print(f"      ℹ️  DOCX file saved at: {docx_path}")
            return False
