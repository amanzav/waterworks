"""Utility functions and constants for Waterworks"""

import re
import time
from typing import Optional
from contextlib import contextmanager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Wait time constants
TIMEOUT = 10
PAGE_LOAD = 0.5


class WaitTimes:
    """Optimized wait time constants"""
    INSTANT = 0.05     # Immediate DOM updates
    FAST = 0.3         # Simple page updates
    MEDIUM = 0.8       # Modal/dialog loading
    SLOW = 1.5         # Full page loads
    USER_INPUT = 10.0  # Waiting for user action


# Common CSS selectors
SELECTORS = {
    "stat_card": ".simple--stat-card.border-radius--16.display--flex.flex--column.dist--between",
    "job_table": "table.table tbody tr",
    "pagination": ".pagination",
    "job_details_panel": ".is--long-form-reading",
    "close_panel_button": "[class='btn__default--text btn--default protip']",
    "floating_action_buttons": ".floating--action-bar.color--bg--default button",
    "question_container": ".js--question--container",
}


def get_cell_text(cell, default="N/A"):
    """Extract text from a table cell
    
    Args:
        cell: Selenium WebElement for table cell
        default: Default value if extraction fails
        
    Returns:
        Extracted text or default
    """
    try:
        elem = cell.find_element(By.CLASS_NAME, "overflow--ellipsis")
        text = elem.get_attribute("innerText")
        return text.strip() if text else default
    except Exception:
        return default


def calculate_chances(openings, applications):
    """Calculate ratio of openings to applications
    
    Args:
        openings: Number of openings (str or int)
        applications: Number of applications (str or int)
        
    Returns:
        Ratio as float, rounded to 3 decimal places
    """
    try:
        openings_int = int(openings)
        applications_int = int(applications)
        return round(openings_int / applications_int, 3) if applications_int > 0 else 0.0
    except Exception:
        return 0.0


def sanitize_filename(text: str) -> str:
    """Sanitize text for use as a filename
    
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


def navigate_to_folder(driver, folder_name: str, job_board: str = "full") -> bool:
    """Navigate to a specific folder in Waterloo Works
    
    Args:
        driver: Selenium WebDriver instance
        folder_name: Name of folder to navigate to
        job_board: Job board type - "full" for Full-Cycle or "direct" for Employer-Student Direct
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Determine which job board to navigate to
        if job_board == "direct":
            url = "https://waterlooworks.uwaterloo.ca/myAccount/co-op/direct/jobs.htm"
        else:
            url = "https://waterlooworks.uwaterloo.ca/myAccount/co-op/full/jobs.htm"
        
        driver.get(url)
        
        # Wait for stat cards to load
        if not smart_page_wait(
            driver, 
            (By.CSS_SELECTOR, SELECTORS["stat_card"]),
            max_wait=WaitTimes.SLOW
        ):
            print(f"   ✗ Page did not load properly")
            return False

        stat_cards = driver.find_elements(By.CSS_SELECTOR, SELECTORS["stat_card"])

        # Find the folder card
        target_card = None
        for card in stat_cards:
            if folder_name.lower() in card.text.lower():
                target_card = card
                break

        if not target_card:
            print(f"   ✗ Could not find '{folder_name}' folder")
            return False

        # Click the folder link
        link = target_card.find_element(By.TAG_NAME, "a")
        click_and_wait(driver, link, max_wait=WaitTimes.MEDIUM)
        return True
        
    except Exception as e:
        print(f"   ✗ Error navigating to '{folder_name}' folder: {e}")
        return False


def get_pagination_pages(driver) -> int:
    """Get number of pages in pagination
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        Number of pages (minimum 1)
    """
    try:
        pagination = WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.CLASS_NAME, "pagination"))
        )
        page_buttons = len(pagination.find_elements(By.TAG_NAME, "li")) - 4
        return max(page_buttons, 1)
    except Exception:
        return 1


def go_to_next_page(driver):
    """Navigate to next page in pagination
    
    Args:
        driver: Selenium WebDriver instance
    """
    try:
        pagination = fast_presence_check(driver, ".pagination", by=By.CLASS_NAME, timeout=TIMEOUT)
        if not pagination:
            print("   ⚠️  Pagination not found")
            return
        
        # Click the second-to-last li (next button)
        next_button_li = pagination.find_elements(By.TAG_NAME, "li")[-2]
        next_link = next_button_li.find_element(By.TAG_NAME, "a")
        
        click_and_wait(
            driver, 
            next_link,
            wait_for=(By.CSS_SELECTOR, SELECTORS["job_table"]),
            max_wait=WaitTimes.MEDIUM
        )
    except Exception as e:
        print(f"   ⚠️  Error going to next page: {e}")


def close_job_details_panel(driver) -> bool:
    """Close the job details side panel
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        True if closed successfully
    """
    try:
        close_buttons = driver.find_elements(By.CSS_SELECTOR, SELECTORS["close_panel_button"])
        if close_buttons:
            close_buttons[-1].click()
            time.sleep(WaitTimes.FAST)
            return True
        return False
    except Exception:
        return False


def get_jobs_from_page(driver):
    """Get all job rows from current page
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        List of job row WebElements
    """
    try:
        time.sleep(PAGE_LOAD)
        job_rows = WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, SELECTORS["job_table"]))
        )
        return job_rows
    except Exception as e:
        print(f"   ✗ Error reading jobs on page: {e}")
        return []


# ============================================
# SMART WAIT HELPERS
# ============================================

def smart_page_wait(driver, expected_element=None, max_wait=None, poll=0.1):
    """Wait for page to load with smart polling
    
    Args:
        driver: Selenium WebDriver instance
        expected_element: Tuple of (By, selector) to wait for
        max_wait: Maximum wait time in seconds
        poll: Polling frequency in seconds
        
    Returns:
        True if element found or page ready
    """
    if max_wait is None:
        max_wait = WaitTimes.SLOW
        
    try:
        if expected_element:
            WebDriverWait(driver, max_wait, poll_frequency=poll).until(
                EC.presence_of_element_located(expected_element)
            )
        else:
            WebDriverWait(driver, max_wait, poll_frequency=poll).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        return True
    except Exception:
        return False


def click_and_wait(driver, element, wait_for=None, max_wait=None):
    """Click element and wait for result
    
    Args:
        driver: Selenium WebDriver instance
        element: Element to click
        wait_for: Optional tuple of (By, selector) to wait for after click
        max_wait: Maximum wait time
        
    Returns:
        True if successful
    """
    if max_wait is None:
        max_wait = WaitTimes.FAST
        
    try:
        driver.execute_script("arguments[0].click();", element)
        
        if wait_for:
            return smart_page_wait(driver, wait_for, max_wait)
        else:
            time.sleep(WaitTimes.INSTANT)
        
        return True
    except Exception as e:
        print(f"   ⚠️  Click failed: {e}")
        return False


def smart_element_click(driver, element, scroll_first=True):
    """Click element with smart scrolling and waiting
    
    Args:
        driver: Selenium WebDriver instance
        element: Element to click
        scroll_first: Whether to scroll to element first
        
    Returns:
        True if successful
    """
    try:
        if scroll_first:
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center', behavior: 'instant'});",
                element
            )
        
        WebDriverWait(driver, 2, poll_frequency=0.05).until(
            EC.element_to_be_clickable(element)
        )
        
        driver.execute_script("arguments[0].click();", element)
        time.sleep(WaitTimes.INSTANT)
        
        return True
    except Exception as e:
        print(f"   ⚠️  Smart click failed: {e}")
        return False


def fast_presence_check(driver, selector, by=By.CSS_SELECTOR, timeout=None):
    """Fast check for element presence
    
    Args:
        driver: Selenium WebDriver instance
        selector: CSS selector or other selector
        by: Selenium By locator type
        timeout: Max wait time
        
    Returns:
        Element if found, None otherwise
    """
    if timeout is None:
        timeout = WaitTimes.FAST
        
    try:
        return WebDriverWait(driver, timeout, poll_frequency=0.05).until(
            EC.presence_of_element_located((by, selector))
        )
    except Exception:
        return None


@contextmanager
def timer(operation_name: str):
    """Context manager for timing operations
    
    Args:
        operation_name: Name of operation being timed
        
    Yields:
        None
        
    Example:
        with timer("Scraping jobs"):
            scrape_jobs()
    """
    start = time.time()
    yield
    elapsed = time.time() - start
    print(f"⏱️  {operation_name} took {elapsed:.2f}s")
