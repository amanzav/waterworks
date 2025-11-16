"""Job detail extraction module"""

import time
from typing import Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from .utils import WaitTimes, SELECTORS


class JobExtractor:
    """Extract detailed job information from Waterloo Works"""
    
    def __init__(self, driver: webdriver.Chrome):
        """Initialize extractor
        
        Args:
            driver: Authenticated Selenium WebDriver instance
        """
        self.driver = driver
    
    def extract_job_details(self, job_basic: Dict) -> Optional[Dict]:
        """Extract detailed information for a job
        
        Args:
            job_basic: Basic job info dict with job_id, job_title, company, title_element
            
        Returns:
            Dictionary with full job details or None if failed
        """
        job_id = job_basic.get("job_id")
        job_title = job_basic.get("job_title", "Unknown")
        company = job_basic.get("company", "Unknown")
        
        try:
            # Click job title to open details panel
            title_element = job_basic.get("title_element")
            if not title_element:
                print(f"   ⚠️  No title element for job {job_id}")
                return None
            
            # Scroll and click
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center', behavior: 'instant'});",
                title_element
            )
            time.sleep(WaitTimes.INSTANT)
            self.driver.execute_script("arguments[0].click();", title_element)
            
            # Wait for job details panel to load
            WebDriverWait(self.driver, WaitTimes.SLOW, poll_frequency=0.05).until(
                EC.presence_of_element_located((By.CLASS_NAME, "is--long-form-reading"))
            )
            
            # Wait for question containers
            WebDriverWait(self.driver, WaitTimes.SLOW, poll_frequency=0.05).until(
                EC.presence_of_element_located((By.CLASS_NAME, "js--question--container"))
            )
            
            time.sleep(WaitTimes.FAST)
            
            # Extract job description sections
            job_info = self.driver.find_element(By.CLASS_NAME, "is--long-form-reading")
            job_divs = job_info.find_elements(By.CLASS_NAME, "js--question--container")
            
            # Section mappings
            SECTION_MAPPINGS = {
                "Job Summary:": "summary",
                "Job Responsibilities:": "responsibilities",
                "Required Skills:": "skills",
                "Additional Application Information:": "additional_info",
                "Employment Location Arrangement:": "employment_location_arrangement",
                "Work Term Duration:": "work_term_duration",
                "Compensation and Benefits:": "compensation_info",
            }
            
            sections = {key: "N/A" for key in SECTION_MAPPINGS.values()}
            
            for div in job_divs:
                text = div.get_attribute("innerText").strip()
                
                for prefix, section_key in SECTION_MAPPINGS.items():
                    if text.startswith(prefix):
                        content = text.replace(prefix, "", 1).strip()
                        sections[section_key] = content
                        break
            
            # Build description from key sections
            desc_parts = []
            if sections["summary"] and sections["summary"] != "N/A":
                desc_parts.append(f"Job Summary:\n{sections['summary']}")
            if sections["responsibilities"] and sections["responsibilities"] != "N/A":
                desc_parts.append(f"\nResponsibilities:\n{sections['responsibilities']}")
            if sections["skills"] and sections["skills"] != "N/A":
                desc_parts.append(f"\nRequired Skills:\n{sections['skills']}")
            if sections["additional_info"] and sections["additional_info"] != "N/A":
                desc_parts.append(f"\nAdditional Info:\n{sections['additional_info']}")
            
            description = "\n".join(desc_parts)
            
            # Close the details panel
            self._close_panel()
            
            return {
                "job_id": job_id,
                "job_title": job_title,
                "company": company,
                "description": description,
                **sections  # Include all individual sections
            }
            
        except TimeoutException as e:
            print(f"   ✗ Timeout extracting details for job {job_id}: Panel did not load")
            self._close_panel()
            return None
        except (NoSuchElementException, WebDriverException) as e:
            print(f"   ✗ Error extracting details for job {job_id}: {e}")
            self._close_panel()
            return None
        except Exception as e:
            print(f"   ✗ Unexpected error extracting details for job {job_id}: {e}")
            # Try to close panel even on error
            self._close_panel()
            return None
    
    def _close_panel(self):
        """Close the job details panel"""
        try:
            close_buttons = self.driver.find_elements(
                By.CSS_SELECTOR,
                SELECTORS["close_panel_button"]
            )
            if close_buttons:
                self.driver.execute_script("arguments[0].click();", close_buttons[-1])
                time.sleep(WaitTimes.INSTANT)
        except Exception:
            pass
    
    def extract_job_by_url(self, job_id: str) -> Optional[Dict]:
        """Extract job details by navigating directly to job URL
        
        Args:
            job_id: Waterloo Works job ID
            
        Returns:
            Dictionary with job details or None if failed
        """
        try:
            job_url = f"https://waterlooworks.uwaterloo.ca/myAccount/co-op/coop-postings.htm?ck_jobid={job_id}"
            self.driver.get(job_url)
            
            # Wait for job details to load
            WebDriverWait(self.driver, WaitTimes.SLOW, poll_frequency=0.05).until(
                EC.presence_of_element_located((By.CLASS_NAME, "is--long-form-reading"))
            )
            
            time.sleep(WaitTimes.FAST)
            
            # Extract similar to above
            job_info = self.driver.find_element(By.CLASS_NAME, "is--long-form-reading")
            
            # Try to get title and company from page
            try:
                title_elem = job_info.find_element(By.TAG_NAME, "h1")
                job_title = title_elem.text.strip()
            except:
                job_title = "Unknown"
            
            company = "Unknown"  # Would need to extract from page if available
            
            # Extract sections (same as above)
            job_divs = job_info.find_elements(By.CLASS_NAME, "js--question--container")
            
            SECTION_MAPPINGS = {
                "Job Summary:": "summary",
                "Job Responsibilities:": "responsibilities",
                "Required Skills:": "skills",
                "Additional Application Information:": "additional_info",
            }
            
            sections = {key: "N/A" for key in SECTION_MAPPINGS.values()}
            
            for div in job_divs:
                text = div.get_attribute("innerText").strip()
                
                for prefix, section_key in SECTION_MAPPINGS.items():
                    if text.startswith(prefix):
                        content = text.replace(prefix, "", 1).strip()
                        sections[section_key] = content
                        break
            
            # Build description
            desc_parts = []
            for section_key in ["summary", "responsibilities", "skills", "additional_info"]:
                if sections[section_key] != "N/A":
                    desc_parts.append(sections[section_key])
            
            description = "\n\n".join(desc_parts)
            
            return {
                "job_id": job_id,
                "job_title": job_title,
                "company": company,
                "description": description,
                **sections
            }
            
        except Exception as e:
            print(f"   ✗ Error extracting job {job_id} by URL: {e}")
            return None
