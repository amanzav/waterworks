"""Folder navigation module for Waterloo Works"""

from typing import List, Dict
from selenium import webdriver
from .utils import (
    navigate_to_folder,
    get_pagination_pages,
    go_to_next_page,
    get_jobs_from_page,
    get_cell_text
)
from selenium.webdriver.common.by import By


class FolderNavigator:
    """Navigate Waterloo Works folders and extract job information"""
    
    def __init__(self, driver: webdriver.Chrome, job_board: str = "full"):
        """Initialize navigator
        
        Args:
            driver: Authenticated Selenium WebDriver instance
            job_board: Job board type - "full" for Full-Cycle or "direct" for Employer-Student Direct
        """
        self.driver = driver
        self.job_board = job_board
    
    def navigate_to_folder(self, folder_name: str) -> bool:
        """Navigate to a specific folder
        
        Args:
            folder_name: Name of the folder to navigate to
            
        Returns:
            True if successful, False otherwise
        """
        print(f"\n📁 Navigating to '{folder_name}' folder...")
        success = navigate_to_folder(self.driver, folder_name, self.job_board)
        
        if success:
            print(f"   ✓ Successfully navigated to '{folder_name}' folder")
        
        return success
    
    def get_job_count(self) -> int:
        """Get total number of jobs across all pages
        
        Returns:
            Total job count
        """
        num_pages = get_pagination_pages(self.driver)
        current_page_jobs = len(get_jobs_from_page(self.driver))
        
        # Rough estimate (assumes all pages have similar job counts)
        return current_page_jobs * num_pages
    
    def extract_jobs_from_page(self) -> List[Dict]:
        """Extract basic job information from current page
        
        Returns:
            List of job dictionaries with basic info
        """
        jobs = []
        
        try:
            job_rows = get_jobs_from_page(self.driver)
            
            for idx, row in enumerate(job_rows, 1):
                try:
                    if self.job_board == "direct":
                        # Direct board: <a> tag is in <th>, followed by <td> cells
                        # Order: job title (th), job id, term, organization, app status, job status, 
                        #        division, location, city, opening, app deadline, app submitted on, app submitted by
                        th_elem = row.find_element(By.TAG_NAME, "th")
                        job_title_elem = th_elem.find_element(By.TAG_NAME, "a")
                        job_title = job_title_elem.text.strip()
                        href = job_title_elem.get_attribute("href")
                        job_id = href.split("=")[-1] if "=" in href else ""
                        
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if len(cells) < 3:
                            continue
                        
                        # Index 0 = job_id (redundant), Index 2 = organization
                        company = get_cell_text(cells[2])
                        
                    else:
                        # Full-Cycle board: <a> tag is in first <td>
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if len(cells) < 4:
                            continue
                        
                        job_title_elem = cells[0].find_element(By.TAG_NAME, "a")
                        job_title = job_title_elem.text.strip()
                        href = job_title_elem.get_attribute("href")
                        job_id = href.split("=")[-1] if "=" in href else ""
                        company = get_cell_text(cells[1])
                    
                    # Store job info
                    jobs.append({
                        "job_id": job_id,
                        "job_title": job_title,
                        "company": company,
                        "title_element": job_title_elem,
                        "row_index": idx
                    })
                    
                except Exception as e:
                    print(f"   ⚠️  Error extracting job {idx}: {e}")
                    continue
            
            return jobs
            
        except Exception as e:
            print(f"   ✗ Error getting jobs from page: {e}")
            return []
    
    def extract_all_jobs_from_folder(self, folder_name: str) -> List[Dict]:
        """Extract all jobs from a folder (handles pagination)
        
        Args:
            folder_name: Name of the folder
            
        Returns:
            List of all job dictionaries
        """
        # Navigate to folder
        if not self.navigate_to_folder(folder_name):
            return []
        
        # Get number of pages
        num_pages = get_pagination_pages(self.driver)
        print(f"\n📄 Found {num_pages} page(s) of jobs")
        
        all_jobs = []
        
        # Extract jobs from each page
        for page in range(1, num_pages + 1):
            print(f"\n📊 Extracting jobs from page {page}/{num_pages}...")
            
            jobs = self.extract_jobs_from_page()
            all_jobs.extend(jobs)
            
            print(f"   ✓ Extracted {len(jobs)} jobs from page {page}")
            
            # Go to next page if not the last one
            if page < num_pages:
                print(f"   ➡️  Going to page {page + 1}...")
                go_to_next_page(self.driver)
        
        print(f"\n🎯 Total jobs extracted: {len(all_jobs)}")
        return all_jobs
