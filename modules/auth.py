"""Authentication module for Waterloo Works"""

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
        driver: Optional[webdriver.Chrome] = None
    ):
        """Initialize authentication
        
        Args:
            username: Waterloo Works username (email)
            password: Waterloo Works password (will prompt if not provided)
            driver: Existing WebDriver instance (creates new one if not provided)
        """
        self.username = username
        self.password = password
        self.driver = driver
        self._owns_driver = driver is None

    def _create_driver(self) -> webdriver.Chrome:
        """Create a new Chrome WebDriver instance
        
        Returns:
            Chrome WebDriver instance
        """
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=options)
        driver.maximize_window()
        print("✅ Browser opened")
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
            
            # Enter password
            print("  → Entering password...")
            password_field = WebDriverWait(self.driver, TIMEOUT_SHORT).until(
                EC.presence_of_element_located((By.ID, "passwordInput"))
            )
            password_field.send_keys(self.password)
            self.driver.find_element(By.ID, "submitButton").click()
            
            # Wait for Duo 2FA
            print("\n⏳ Waiting for Duo 2FA (approve on your phone)...")
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
    password: Optional[str] = None
) -> Tuple[webdriver.Chrome, WaterlooWorksAuth]:
    """Create an authenticated Waterloo Works session
    
    Args:
        username: Waterloo Works username (will prompt if not provided)
        password: Waterloo Works password (will prompt if not provided)
        
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
    auth = WaterlooWorksAuth(username, password)
    driver = auth.login()
    return driver, auth
