"""Test authentication and login functionality"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.auth import WaterlooWorksAuth
from modules.config_manager import ConfigManager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def test_login():
    """Test Waterloo Works login with Duo 2FA"""
    print("\n" + "="*60)
    print("🔐 Testing Waterloo Works Authentication")
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
    
    if not username:
        print("❌ Username not configured. Update config.yaml")
        return False
    
    if not password:
        print("⚠️  No password in config - will prompt during login")
    
    print(f"\n📝 Username: {username}")
    print("🌐 Starting Chrome browser...")
    
    # Set up Chrome options
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Uncomment to run headless
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print("✅ Browser started")
        
        # Test authentication
        print("\n🔑 Attempting login...")
        print("⏳ Waiting for Duo 2FA approval...")
        print("   (Check your phone for Duo push notification)")
        
        auth = WaterlooWorksAuth(driver)
        
        if auth.login(username, password):
            print("\n✅ Login successful!")
            print("✅ Duo 2FA completed")
            
            # Verify we're logged in by checking URL
            current_url = driver.current_url
            print(f"\n📍 Current URL: {current_url}")
            
            if "waterlooworks" in current_url and "myAccount" in current_url:
                print("✅ Successfully authenticated and redirected to WaterlooWorks")
                driver.quit()
                return True
            else:
                print("⚠️  Login succeeded but unexpected redirect")
                driver.quit()
                return False
        else:
            print("\n❌ Login failed")
            driver.quit()
            return False
            
    except Exception as e:
        print(f"\n❌ Error during authentication test: {e}")
        import traceback
        traceback.print_exc()
        try:
            driver.quit()
        except:
            pass
        return False


def test_login_with_context_manager():
    """Test authentication using context manager pattern"""
    print("\n" + "="*60)
    print("🔐 Testing Auth Context Manager")
    print("="*60)
    
    try:
        config = ConfigManager()
        config.load()
        username = config.get("waterloo_works.username")
        password = config.get("waterloo_works.password")
        
        chrome_options = Options()
        driver = webdriver.Chrome(options=chrome_options)
        
        print("🔑 Testing context manager pattern...")
        with WaterlooWorksAuth(driver) as auth:
            if auth.login(username, password):
                print("✅ Context manager login successful")
                print("✅ Browser will auto-close on context exit")
                return True
            else:
                print("❌ Context manager login failed")
                return False
                
    except Exception as e:
        print(f"❌ Context manager test failed: {e}")
        return False


if __name__ == "__main__":
    print("\n🦆 Geese - Authentication Tests")
    print("="*60)
    
    # Run basic login test
    result1 = test_login()
    
    # Run context manager test
    result2 = test_login_with_context_manager()
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    print(f"Basic Login: {'✅ PASS' if result1 else '❌ FAIL'}")
    print(f"Context Manager: {'✅ PASS' if result2 else '❌ FAIL'}")
    
    if result1 and result2:
        print("\n🎉 All authentication tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed")
        sys.exit(1)
