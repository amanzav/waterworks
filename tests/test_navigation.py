"""Test folder navigation and job extraction"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.auth import WaterlooWorksAuth
from modules.folder_navigator import FolderNavigator
from modules.job_extractor import JobExtractor
from modules.config_manager import ConfigManager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def test_folder_navigation():
    """Test navigating to a Waterloo Works folder and extracting jobs"""
    print("\n" + "="*60)
    print("📁 Testing Folder Navigation")
    print("="*60)
    
    # Load config
    try:
        config = ConfigManager()
        config.load()
    except FileNotFoundError:
        print("❌ Config file not found. Run setup.py first.")
        return False
    
    username = config.get("waterloo_works.username")
    password = config.get("waterloo_works.password")
    
    # Get folder name from config or prompt
    folder_name = config.get("defaults.folder")
    if not folder_name:
        folder_name = input("\n📋 Enter a Waterloo Works folder name to test: ").strip()
        if not folder_name:
            print("❌ No folder name provided")
            return False
    
    print(f"\n📂 Testing folder: {folder_name}")
    
    chrome_options = Options()
    driver = None
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print("✅ Browser started")
        
        # Login
        print("\n🔑 Logging in...")
        auth = WaterlooWorksAuth(driver)
        if not auth.login(username, password):
            print("❌ Login failed")
            return False
        print("✅ Login successful")
        
        # Navigate to folder
        print(f"\n📁 Navigating to folder: {folder_name}")
        navigator = FolderNavigator(driver)
        
        jobs = navigator.extract_all_jobs_from_folder(folder_name)
        
        if jobs:
            print(f"\n✅ Found {len(jobs)} jobs in folder '{folder_name}'")
            print("\n📋 Jobs extracted:")
            for i, job in enumerate(jobs[:5], 1):  # Show first 5
                print(f"\n  {i}. {job.get('title', 'N/A')}")
                print(f"     Company: {job.get('company', 'N/A')}")
                print(f"     Location: {job.get('location', 'N/A')}")
                print(f"     Job ID: {job.get('job_id', 'N/A')}")
            
            if len(jobs) > 5:
                print(f"\n  ... and {len(jobs) - 5} more jobs")
            
            driver.quit()
            return True
        else:
            print(f"\n⚠️  No jobs found in folder '{folder_name}'")
            print("   This might be expected if the folder is empty")
            driver.quit()
            return False
            
    except Exception as e:
        print(f"\n❌ Error during navigation test: {e}")
        import traceback
        traceback.print_exc()
        if driver:
            driver.quit()
        return False


def test_job_extraction():
    """Test extracting detailed job information"""
    print("\n" + "="*60)
    print("📄 Testing Job Detail Extraction")
    print("="*60)
    
    # Load config
    try:
        config = ConfigManager()
        config.load()
    except FileNotFoundError:
        print("❌ Config file not found. Run setup.py first.")
        return False
    
    username = config.get("waterloo_works.username")
    password = config.get("waterloo_works.password")
    
    folder_name = config.get("defaults.folder")
    if not folder_name:
        folder_name = input("\n📋 Enter a Waterloo Works folder name to test: ").strip()
        if not folder_name:
            print("❌ No folder name provided")
            return False
    
    chrome_options = Options()
    driver = None
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print("✅ Browser started")
        
        # Login
        print("\n🔑 Logging in...")
        auth = WaterlooWorksAuth(driver)
        if not auth.login(username, password):
            print("❌ Login failed")
            return False
        print("✅ Login successful")
        
        # Navigate and get jobs
        print(f"\n📁 Getting jobs from folder: {folder_name}")
        navigator = FolderNavigator(driver)
        jobs = navigator.extract_all_jobs_from_folder(folder_name)
        
        if not jobs:
            print(f"⚠️  No jobs found in folder '{folder_name}'")
            driver.quit()
            return False
        
        # Extract details from first job
        print(f"\n📄 Extracting details from first job...")
        extractor = JobExtractor(driver)
        
        first_job = jobs[0]
        print(f"\nJob: {first_job.get('title', 'N/A')}")
        print(f"Company: {first_job.get('company', 'N/A')}")
        
        details = extractor.extract_job_details(first_job)
        
        if details:
            print("\n✅ Job details extracted successfully:")
            print(f"\n  Title: {details.get('title', 'N/A')}")
            print(f"  Company: {details.get('company', 'N/A')}")
            print(f"  Location: {details.get('location', 'N/A')}")
            
            summary = details.get('job_summary', '')
            if summary:
                print(f"\n  Summary: {summary[:200]}...")
            
            responsibilities = details.get('job_responsibilities', '')
            if responsibilities:
                print(f"\n  Responsibilities: {responsibilities[:200]}...")
            
            required_skills = details.get('required_skills', '')
            if required_skills:
                print(f"\n  Skills: {required_skills[:200]}...")
            
            description = details.get('full_description', '')
            print(f"\n  Full Description Length: {len(description)} characters")
            
            driver.quit()
            return True
        else:
            print("\n❌ Failed to extract job details")
            driver.quit()
            return False
            
    except Exception as e:
        print(f"\n❌ Error during job extraction test: {e}")
        import traceback
        traceback.print_exc()
        if driver:
            driver.quit()
        return False


if __name__ == "__main__":
    print("\n🦆 Geese - Navigation & Extraction Tests")
    print("="*60)
    
    # Run navigation test
    result1 = test_folder_navigation()
    
    # Run job extraction test
    result2 = test_job_extraction()
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    print(f"Folder Navigation: {'✅ PASS' if result1 else '❌ FAIL'}")
    print(f"Job Extraction: {'✅ PASS' if result2 else '❌ FAIL'}")
    
    if result1 and result2:
        print("\n🎉 All navigation tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed")
        sys.exit(1)
