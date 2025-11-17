"""Geese - CLI Cover Letter Generator for Waterloo Works"""

__version__ = "1.0.0"

# Export main classes for easy importing
from .auth import WaterlooWorksAuth
from .config_manager import ConfigManager
from .cover_letter_generator import CoverLetterGenerator, CoverLetterManager
from .cover_letter_uploader import CoverLetterUploader
from .folder_navigator import FolderNavigator
from .job_extractor import JobExtractor
from .pdf_builder import PDFBuilder

__all__ = [
    "WaterlooWorksAuth",
    "ConfigManager",
    "CoverLetterGenerator",
    "CoverLetterManager",
    "CoverLetterUploader",
    "FolderNavigator",
    "JobExtractor",
    "PDFBuilder",
]
