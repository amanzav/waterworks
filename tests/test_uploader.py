"""Tests for cover letter uploader functionality"""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.cover_letter_uploader import CoverLetterUploader


class TestCoverLetterUploader:
    """Test suite for CoverLetterUploader"""
    
    def setup_method(self):
        """Setup test fixtures"""
        # Create temporary directories
        self.temp_dir = tempfile.mkdtemp()
        self.cover_letters_dir = Path(self.temp_dir) / "cover_letters"
        self.data_dir = Path(self.temp_dir) / "data"
        
        self.cover_letters_dir.mkdir(parents=True)
        self.data_dir.mkdir(parents=True)
        
        # Create mock driver
        self.mock_driver = Mock()
        
        # Create uploader instance
        self.uploader = CoverLetterUploader(
            driver=self.mock_driver,
            cover_letters_dir=self.cover_letters_dir,
            data_dir=self.data_dir
        )
    
    def teardown_method(self):
        """Cleanup test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test uploader initializes correctly"""
        assert self.uploader.driver == self.mock_driver
        assert self.uploader.cover_letters_dir == self.cover_letters_dir
        assert self.uploader.data_dir == self.data_dir
        assert self.uploader.upload_log_path == self.data_dir / "uploaded_cover_letters.json"
    
    def test_load_uploaded_files_empty(self):
        """Test loading uploaded files when none exist"""
        uploaded = self.uploader.load_uploaded_files()
        assert uploaded == set()
    
    def test_save_and_load_uploaded_files(self):
        """Test saving and loading uploaded files"""
        # Save a file
        self.uploader.save_uploaded_file("test1.pdf")
        
        # Load and verify
        uploaded = self.uploader.load_uploaded_files()
        assert "test1.pdf" in uploaded
        
        # Save another file
        self.uploader.save_uploaded_file("test2.pdf")
        
        # Load and verify both
        uploaded = self.uploader.load_uploaded_files()
        assert "test1.pdf" in uploaded
        assert "test2.pdf" in uploaded
        assert len(uploaded) == 2
    
    def test_save_uploaded_file_no_duplicates(self):
        """Test that saving same file twice doesn't create duplicates"""
        self.uploader.save_uploaded_file("test.pdf")
        self.uploader.save_uploaded_file("test.pdf")
        
        uploaded = self.uploader.load_uploaded_files()
        assert len(uploaded) == 1
        assert "test.pdf" in uploaded
    
    def test_reset_upload_tracking(self):
        """Test resetting upload tracking"""
        # Save some files
        self.uploader.save_uploaded_file("test1.pdf")
        self.uploader.save_uploaded_file("test2.pdf")
        
        # Verify they exist
        uploaded = self.uploader.load_uploaded_files()
        assert len(uploaded) == 2
        
        # Reset
        self.uploader.reset_upload_tracking()
        
        # Verify empty
        uploaded = self.uploader.load_uploaded_files()
        assert len(uploaded) == 0
    
    def test_get_upload_stats(self):
        """Test upload statistics calculation"""
        # Create some PDF files
        (self.cover_letters_dir / "test1.pdf").touch()
        (self.cover_letters_dir / "test2.pdf").touch()
        (self.cover_letters_dir / "test3.pdf").touch()
        
        # Mark one as uploaded
        self.uploader.save_uploaded_file("test1.pdf")
        
        # Get stats
        stats = self.uploader.get_upload_stats()
        
        assert stats["total_pdfs"] == 3
        assert stats["uploaded_count"] == 1
        assert stats["pending_count"] == 2
    
    def test_load_corrupted_json(self):
        """Test handling of corrupted upload log"""
        # Write corrupted JSON
        with open(self.uploader.upload_log_path, 'w') as f:
            f.write("{ invalid json }")
        
        # Should return empty set without crashing
        uploaded = self.uploader.load_uploaded_files()
        assert uploaded == set()
    
    def test_upload_log_persistence(self):
        """Test that upload log persists correctly"""
        # Save files
        self.uploader.save_uploaded_file("test1.pdf")
        self.uploader.save_uploaded_file("test2.pdf")
        
        # Read JSON directly
        with open(self.uploader.upload_log_path, 'r') as f:
            data = json.load(f)
        
        assert "uploaded_files" in data
        assert set(data["uploaded_files"]) == {"test1.pdf", "test2.pdf"}
        # Files should be sorted
        assert data["uploaded_files"] == sorted(["test1.pdf", "test2.pdf"])


def run_uploader_tests():
    """Run all uploader tests"""
    print("\n" + "=" * 60)
    print("🧪 Running Cover Letter Uploader Tests")
    print("=" * 60)
    
    test_suite = TestCoverLetterUploader()
    tests = [
        ("Initialization", test_suite.test_initialization),
        ("Load Empty Files", test_suite.test_load_uploaded_files_empty),
        ("Save and Load Files", test_suite.test_save_and_load_uploaded_files),
        ("No Duplicates", test_suite.test_save_uploaded_file_no_duplicates),
        ("Reset Tracking", test_suite.test_reset_upload_tracking),
        ("Upload Stats", test_suite.test_get_upload_stats),
        ("Corrupted JSON", test_suite.test_load_corrupted_json),
        ("Log Persistence", test_suite.test_upload_log_persistence),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_suite.setup_method()
            test_func()
            test_suite.teardown_method()
            print(f"✅ {test_name}")
            passed += 1
        except Exception as e:
            print(f"❌ {test_name}: {e}")
            failed += 1
            test_suite.teardown_method()
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_uploader_tests()
    sys.exit(0 if success else 1)
