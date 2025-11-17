"""Cover Letter Uploader for Waterloo Works"""

import json
import time
from pathlib import Path
from typing import Optional, Dict, Set
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from .utils import WaitTimes


# Wait timeout for upload operations
UPLOAD_TIMEOUT = 15


class CoverLetterUploader:
    """Upload cover letters to Waterloo Works with duplicate tracking"""
    
    def __init__(
        self,
        driver: webdriver.Chrome,
        cover_letters_dir: Optional[Path] = None,
        data_dir: Optional[Path] = None
    ):
        """Initialize cover letter uploader
        
        Args:
            driver: Selenium WebDriver instance (must be authenticated)
            cover_letters_dir: Directory containing cover letter PDFs
            data_dir: Directory for storing upload tracking data
        """
        self.driver = driver
        
        # Set cover letters directory
        if cover_letters_dir is None:
            from .config_manager import ConfigManager
            config = ConfigManager()
            config.load()
            cover_letters_dir = config.get_cover_letters_dir()
        
        self.cover_letters_dir = Path(cover_letters_dir)
        
        # Set data directory for tracking
        if data_dir is None:
            from .config_manager import ConfigManager
            config = ConfigManager()
            config.load()
            data_dir = config.get_data_dir()
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Upload tracking file
        self.upload_log_path = self.data_dir / "uploaded_cover_letters.json"
    
    def navigate_to_upload_menu(self) -> bool:
        """Navigate to the document upload page
        
        Returns:
            True if navigation successful, False otherwise
        """
        try:
            print("📤 Navigating to upload menu...")
            
            # Go to home page
            home_button = WebDriverWait(self.driver, UPLOAD_TIMEOUT).until(
                EC.element_to_be_clickable((By.ID, "outerTemplateTabs_overview"))
            )
            home_button.click()
            time.sleep(WaitTimes.MEDIUM)
            
            # Click upload documents button
            upload_button = WebDriverWait(self.driver, UPLOAD_TIMEOUT).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "[data-pt-classes='tip--default']")
                )
            )
            upload_button.click()
            time.sleep(WaitTimes.FAST)
            
            # Click internal upload button
            upload_buttons = WebDriverWait(self.driver, UPLOAD_TIMEOUT).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "[class='btn__default--text btn--info  display--flex align--middle']")
                )
            )
            
            if not upload_buttons:
                print("   ✗ Upload button not found")
                return False
            
            upload_buttons[0].click()
            time.sleep(WaitTimes.FAST)
            
            print("   ✓ Navigated to upload menu")
            return True
            
        except Exception as e:
            print(f"   ✗ Error navigating to upload menu: {e}")
            return False
    
    def upload_file(self, pdf_filename: str) -> bool:
        """Upload a single PDF file
        
        Args:
            pdf_filename: Name of the PDF file to upload
            
        Returns:
            True if upload successful, False otherwise
        """
        try:
            # Extract document name (without .pdf extension)
            doc_name = pdf_filename.replace(".pdf", "")
            
            # Enter document name
            name_input = WebDriverWait(self.driver, UPLOAD_TIMEOUT).until(
                EC.presence_of_element_located((By.ID, "docName"))
            )
            name_input.clear()
            name_input.send_keys(doc_name)
            
            # Select document type (66 = Cover Letter)
            select_element = self.driver.find_element(By.ID, "docType")
            select = Select(select_element)
            select.select_by_value("66")
            
            # Get absolute file path
            file_path = (self.cover_letters_dir / pdf_filename).resolve()
            
            if not file_path.exists():
                print(f"      ✗ File not found: {file_path}")
                return False
            
            # Upload file
            file_input = WebDriverWait(self.driver, UPLOAD_TIMEOUT).until(
                EC.presence_of_element_located((By.ID, "fileUpload_docUpload"))
            )
            file_input.send_keys(str(file_path))
            time.sleep(WaitTimes.SLOW)  # Wait for file to upload
            
            # Submit
            submit_button = WebDriverWait(self.driver, UPLOAD_TIMEOUT).until(
                EC.element_to_be_clickable((By.ID, "submitFileUploadFormBtn"))
            )
            submit_button.click()
            time.sleep(WaitTimes.MEDIUM)
            
            print(f"      ✓ Uploaded: {doc_name}")
            return True
            
        except Exception as e:
            print(f"      ✗ Error uploading {pdf_filename}: {e}")
            return False
    
    def load_uploaded_files(self) -> Set[str]:
        """Load set of already uploaded filenames
        
        Returns:
            Set of filenames that have been uploaded
        """
        if not self.upload_log_path.exists():
            return set()
        
        try:
            with open(self.upload_log_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data.get("uploaded_files", []))
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️  Warning: Could not read upload log: {e}")
            return set()
    
    def save_uploaded_file(self, filename: str) -> None:
        """Mark a file as uploaded
        
        Args:
            filename: Name of the file that was uploaded
        """
        # Load existing uploaded files
        uploaded = self.load_uploaded_files()
        uploaded.add(filename)
        
        # Save updated list
        try:
            with open(self.upload_log_path, 'w', encoding='utf-8') as f:
                json.dump(
                    {"uploaded_files": sorted(list(uploaded))},
                    f,
                    indent=2,
                    ensure_ascii=False
                )
        except IOError as e:
            print(f"⚠️  Warning: Could not save upload log: {e}")
    
    def reset_upload_tracking(self) -> None:
        """Clear the upload tracking log (useful for testing or re-upload)"""
        if self.upload_log_path.exists():
            self.upload_log_path.unlink()
            print("✅ Upload tracking reset")
    
    def get_upload_stats(self) -> Dict[str, int]:
        """Get statistics about uploaded files
        
        Returns:
            Dictionary with upload statistics
        """
        uploaded_files = self.load_uploaded_files()
        all_pdfs = list(self.cover_letters_dir.glob("*.pdf"))
        
        return {
            "total_pdfs": len(all_pdfs),
            "uploaded_count": len(uploaded_files),
            "pending_count": len(all_pdfs) - len([f for f in all_pdfs if f.name in uploaded_files])
        }
    
    def upload_all_cover_letters(self, force: bool = False) -> Dict[str, int]:
        """Upload all cover letters from the directory
        
        Args:
            force: If True, re-upload all files ignoring tracking
            
        Returns:
            Dictionary with upload statistics
        """
        stats = {
            "total_files": 0,
            "uploaded": 0,
            "skipped_existing": 0,
            "failed": 0
        }
        
        # Get all PDF files
        pdf_files = sorted(self.cover_letters_dir.glob("*.pdf"))
        stats["total_files"] = len(pdf_files)
        
        if not pdf_files:
            print("📭 No cover letters found to upload")
            print(f"   Looking in: {self.cover_letters_dir}")
            return stats
        
        # Load already uploaded files (unless forcing)
        uploaded_files = set() if force else self.load_uploaded_files()
        
        if force and uploaded_files:
            print("⚠️  Force mode: Re-uploading all files")
        
        # Filter out already uploaded files
        files_to_upload = [
            f for f in pdf_files
            if force or f.name not in uploaded_files
        ]
        stats["skipped_existing"] = len(pdf_files) - len(files_to_upload)
        
        print(f"\n📤 Upload Summary")
        print(f"   Total cover letters: {len(pdf_files)}")
        if stats["skipped_existing"] > 0:
            print(f"   Already uploaded: {stats['skipped_existing']}")
        print(f"   To upload: {len(files_to_upload)}")
        
        if not files_to_upload:
            print("\n✅ All cover letters already uploaded!")
            return stats
        
        print()  # Blank line before starting uploads
        
        # Navigate to upload menu once
        if not self.navigate_to_upload_menu():
            print("\n❌ Failed to navigate to upload menu")
            return stats
        
        # Upload each file
        for idx, pdf_path in enumerate(files_to_upload, 1):
            print(f"\n[{idx}/{len(files_to_upload)}] {pdf_path.name}")
            
            if self.upload_file(pdf_path.name):
                stats["uploaded"] += 1
                # Mark as uploaded
                if not force:  # Only track if not forcing re-uploads
                    self.save_uploaded_file(pdf_path.name)
                
                # Navigate back to upload page for next file (except last one)
                if idx < len(files_to_upload):
                    time.sleep(WaitTimes.FAST)
                    if not self.navigate_to_upload_menu():
                        print("\n⚠️  Could not navigate back to upload menu")
                        break
            else:
                stats["failed"] += 1
        
        # Print final summary
        print("\n" + "=" * 60)
        print("📊 Upload Complete")
        print("=" * 60)
        print(f"Total files: {stats['total_files']}")
        print(f"✅ Uploaded: {stats['uploaded']}")
        if stats["skipped_existing"] > 0:
            print(f"⏭️  Skipped (already uploaded): {stats['skipped_existing']}")
        if stats["failed"] > 0:
            print(f"❌ Failed: {stats['failed']}")
        print()
        
        return stats
    
    def list_uploaded_files(self) -> None:
        """Display list of uploaded files"""
        uploaded = self.load_uploaded_files()
        
        if not uploaded:
            print("No uploaded files tracked")
            return
        
        print(f"\n📋 Uploaded Files ({len(uploaded)})")
        print("=" * 60)
        for filename in sorted(uploaded):
            print(f"  ✓ {filename}")
        print()
    
    def list_pending_files(self) -> None:
        """Display list of files pending upload"""
        uploaded = self.load_uploaded_files()
        all_pdfs = sorted(self.cover_letters_dir.glob("*.pdf"))
        pending = [f for f in all_pdfs if f.name not in uploaded]
        
        if not pending:
            print("No pending files to upload")
            return
        
        print(f"\n📋 Pending Upload ({len(pending)})")
        print("=" * 60)
        for pdf_path in pending:
            print(f"  ⏳ {pdf_path.name}")
        print()
