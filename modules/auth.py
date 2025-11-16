"""Authentication module for Waterloo Works"""

import time
import getpass
from typing import Optional, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# Timeout constants
TIMEOUT_SHORT = 10
TIMEOUT_MEDIUM = 30
TIMEOUT_LONG = 60


class WaterlooWorksAuth:
    """Handle authentication for Waterloo Works"""

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        driver: Optional[webdriver.Chrome] = None,
        headless: bool = False
    ):
        """Initialize authentication
        
        Args:
            username: Waterloo Works username (email)
            password: Waterloo Works password (will prompt if not provided)
            driver: Existing WebDriver instance (creates new one if not provided)
            headless: Run browser in headless mode (default: False)
        """
        self.username = username
        self.password = password
        self.driver = driver
        self.headless = headless
        self._owns_driver = driver is None

    def _create_driver(self) -> webdriver.Chrome:
        """Create a new Chrome WebDriver instance
        
        Returns:
            Chrome WebDriver instance
        """
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        if self.headless:
            options.add_argument("--headless=new")
            options.add_argument("--window-size=1920,1080")
            print("✅ Browser opened (headless mode)")
        else:
            print("✅ Browser opened (visible mode)")

        driver = webdriver.Chrome(options=options)
        
        if not self.headless:
            driver.maximize_window()
        
        return driver
        
    def login(self) -> webdriver.Chrome:
        """Log in to Waterloo Works
        
        Returns:
            WebDriver instance with authenticated session
            
        Raises:
            Exception: If login fails
        """
        # Create driver if not provided
        if not self.driver:
            self.driver = self._create_driver()
        
        # Prompt for credentials if not provided
        if not self.username:
            self.username = input("Waterloo Works username (email): ").strip()
        
        if not self.password:
            self.password = getpass.getpass("Password: ")
        
        try:
            print("🔑 Logging in to Waterloo Works...")
            
            # Go to login page
            self.driver.get("https://waterlooworks.uwaterloo.ca/waterloo.htm?action=login")
            
            # Enter email
            print("  → Entering email...")
            email_field = WebDriverWait(self.driver, TIMEOUT_SHORT).until(
                EC.presence_of_element_located((By.ID, "userNameInput"))
            )
            email_field.send_keys(self.username)
            self.driver.find_element(By.ID, "nextButton").click()
            
            # Enter password with retry on incorrect password
            password_correct = False
            max_password_attempts = 3
            attempt = 0
            
            while not password_correct and attempt < max_password_attempts:
                attempt += 1
                
                # Prompt for password if needed
                if attempt > 1 or not self.password:
                    if attempt > 1:
                        print(f"  ❌ Incorrect password. Please try again (attempt {attempt}/{max_password_attempts})")
                    self.password = getpass.getpass("Password: ")
                
                print(f"  → Entering password...")
                password_field = WebDriverWait(self.driver, TIMEOUT_SHORT).until(
                    EC.presence_of_element_located((By.ID, "passwordInput"))
                )
                password_field.clear()
                password_field.send_keys(self.password)
                self.driver.find_element(By.ID, "submitButton").click()
                
                # Wait a moment for the page to process
                time.sleep(2)
                
                # Check if password is correct by looking for verification-code div
                try:
                    verification_div = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "verification-code"))
                    )
                    password_correct = True
                    
                    # Display Duo verification code to user
                    try:
                        duo_code = verification_div.text.strip()
                        if duo_code:
                            print(f"\n🔐 Duo Verification Code: {duo_code}")
                            print("   Please enter this code in your Duo Mobile app\n")
                    except Exception:
                        pass
                    
                except Exception:
                    # verification-code div not found, check if we're back at email/password page
                    try:
                        # Check if we're back at the email input (password was wrong)
                        email_input = self.driver.find_element(By.ID, "userNameInput")
                        # We're back at email page, need to click next again
                        self.driver.find_element(By.ID, "nextButton").click()
                        password_correct = False
                    except Exception:
                        # Not at email page, might be at password page or somewhere else
                        try:
                            # Check if still at password page
                            self.driver.find_element(By.ID, "passwordInput")
                            password_correct = False
                        except Exception:
                            # Not sure where we are, assume password worked
                            password_correct = True
            
            if not password_correct:
                raise Exception(f"Failed to login after {max_password_attempts} password attempts")
            
            # Wait for Duo 2FA
            print("⏳ Waiting for Duo 2FA approval...")
            trust_button = WebDriverWait(self.driver, TIMEOUT_LONG).until(
                EC.presence_of_element_located((By.ID, "trust-browser-button"))
            )
            trust_button.click()
            
            # Wait for Waterloo Works to load
            try:
                WebDriverWait(self.driver, TIMEOUT_MEDIUM).until(
                    EC.presence_of_element_located((By.XPATH, '//h1[text()="WaterlooWorks"]'))
                )
            except Exception:
                # Check if we're on an error page or still on login
                current_url = self.driver.current_url
                if "login" in current_url.lower() or "error" in current_url.lower():
                    raise Exception(
                        "Login failed. Please check your credentials and ensure 2FA was approved."
                    )
                # If we're somewhere else, assume it worked
                pass
            
            print("✅ Login successful!\n")
            return self.driver
            
        except Exception as e:
            print(f"❌ Login failed: {e}")
            # Clean up driver on login failure
            if self._owns_driver and self.driver:
                try:
                    self.driver.quit()
                except Exception:
                    pass
                self.driver = None
            raise
    
    def close(self) -> None:
        """Close the browser if owned by this instance"""
        if not self.driver:
            return

        if self._owns_driver:
            try:
                self.driver.quit()
                print("🔒 Browser closed")
            except Exception as e:
                print(f"⚠️  Warning: Error closing browser: {e}")
                try:
                    self.driver.service.process.kill()
                except Exception:
                    pass

        self.driver = None

    def __enter__(self) -> "WaterlooWorksAuth":
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        """Context manager exit"""
        self.close()


def create_authenticated_session(
    username: Optional[str] = None,
    password: Optional[str] = None,
    headless: bool = False
) -> Tuple[webdriver.Chrome, WaterlooWorksAuth]:
    """Create an authenticated Waterloo Works session
    
    Args:
        username: Waterloo Works username (will prompt if not provided)
        password: Waterloo Works password (will prompt if not provided)
        headless: Run browser in headless mode (default: False)
        
    Returns:
        Tuple of (driver, auth) where driver is the authenticated WebDriver
        
    Example:
        driver, auth = create_authenticated_session()
        try:
            # Use driver for scraping
            ...
        finally:
            auth.close()
    """
    auth = WaterlooWorksAuth(username, password, headless=headless)
    driver = auth.login()
    return driver, auth
