"""Cover letter generation module with multi-LLM support"""

import os
import time
from typing import Optional, Dict
from pathlib import Path

# Constants
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds between retries
RATE_LIMIT_DELAY = 0.5  # seconds between API calls to avoid rate limiting


class CoverLetterGenerator:
    """Generate cover letters using various LLM providers"""
    
    def __init__(
        self,
        provider: str,
        model: str,
        api_key: str,
        resume_text: str,
        user_profile: Optional[Dict[str, str]] = None,
        additional_info: Optional[str] = None,
        prompt_template: Optional[str] = None
    ):
        """Initialize cover letter generator
        
        Args:
            provider: LLM provider (openai, anthropic, gemini, groq)
            model: Model name
            api_key: API key for the provider
            resume_text: User's resume text
            user_profile: User profile dict with name, email, phone, etc.
            additional_info: Additional information to include
            prompt_template: Custom prompt template (uses default if None)
        """
        self.provider = provider.lower()
        self.model = model
        self.api_key = api_key
        self.resume_text = resume_text
        self.user_profile = user_profile or {}
        self.additional_info = additional_info or ""
        self.prompt_template = prompt_template
        
        # Validate API key
        if not self.api_key:
            raise ValueError(f"API key required for provider '{self.provider}'")
        
        # Initialize the appropriate client
        self._client = self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the LLM client based on provider"""
        if self.provider == "openai":
            from openai import OpenAI
            return OpenAI(api_key=self.api_key)
        
        elif self.provider == "anthropic":
            from anthropic import Anthropic
            return Anthropic(api_key=self.api_key)
        
        elif self.provider == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            return genai.GenerativeModel(self.model)
        
        elif self.provider == "groq":
            from groq import Groq
            return Groq(api_key=self.api_key)
        
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    def generate(
        self,
        company: str,
        job_title: str,
        job_description: str,
        max_retries: int = MAX_RETRIES
    ) -> Optional[str]:
        """Generate a cover letter for a job
        
        Args:
            company: Company name
            job_title: Job title
            job_description: Full job description
            max_retries: Maximum number of retry attempts
            
        Returns:
            Generated cover letter text or None if failed
        """
        # Build the prompt
        prompt = self._build_prompt(company, job_title, job_description)
        
        # Try generation with retries
        for attempt in range(max_retries):
            try:
                if self.provider == "openai":
                    body_text = self._generate_openai(prompt)
                elif self.provider == "anthropic":
                    body_text = self._generate_anthropic(prompt)
                elif self.provider == "gemini":
                    body_text = self._generate_gemini(prompt)
                elif self.provider == "groq":
                    body_text = self._generate_groq(prompt)
                else:
                    return None
                
                # Add header if profile info available
                return self._add_header(body_text)
                
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"      ⚠️  Attempt {attempt + 1} failed: {e}. Retrying in {RETRY_DELAY}s...")
                    time.sleep(RETRY_DELAY)
                else:
                    print(f"      ✗ All {max_retries} attempts failed: {e}")
                    return None
        
        return None
    
    def _add_header(self, body_text: str) -> str:
        """Add contact header to cover letter if profile info available
        
        Args:
            body_text: Generated cover letter body
            
        Returns:
            Full text with header prepended
        """
        if not self.user_profile:
            return body_text
        
        # Build header lines
        header_lines = []
        
        # Name
        if self.user_profile.get("name"):
            header_lines.append(self.user_profile["name"])
        
        # Contact line: email | phone
        contact_parts = []
        if self.user_profile.get("email"):
            contact_parts.append(self.user_profile["email"])
        if self.user_profile.get("phone"):
            contact_parts.append(self.user_profile["phone"])
        if contact_parts:
            header_lines.append(" | ".join(contact_parts))
        
        # Links line: LinkedIn | GitHub | Website
        links_parts = []
        if self.user_profile.get("linkedin"):
            links_parts.append(self.user_profile["linkedin"])
        if self.user_profile.get("github"):
            links_parts.append(self.user_profile["github"])
        if self.user_profile.get("website"):
            links_parts.append(self.user_profile["website"])
        if links_parts:
            header_lines.append(" | ".join(links_parts))
        
        # Combine header and body
        if header_lines:
            header = "\n".join(header_lines)
            return f"{header}\n\n{body_text}"
        
        return body_text
    
    def _build_prompt(self, company: str, job_title: str, job_description: str) -> str:
        """Build the prompt for cover letter generation
        
        Args:
            company: Company name
            job_title: Job title
            job_description: Job description
            
        Returns:
            Complete prompt string
        """
        profile_info = f"{self.resume_text}\n\n{self.additional_info}".strip()
        
        # Use custom template if provided, otherwise use default
        if self.prompt_template:
            prompt = self.prompt_template.format(
                company=company,
                job_title=job_title,
                job_description=job_description,
                profile_info=profile_info
            )
        else:
            # Default prompt
            prompt = f"""You are an expert cover letter writer. Write a professional, enthusiastic cover letter for the following job application.

**Job Details:**
- Company: {company}
- Position: {job_title}

**Job Description:**
{job_description}

**Candidate Profile:**
{profile_info}

**Instructions:**
1. Write a compelling cover letter that highlights relevant skills and experience
2. Keep it between 200-400 words
3. Be specific about why the candidate is a good fit
4. Show enthusiasm for the role and company
5. Use a professional but friendly tone
6. Do NOT include a header/address/date (just the body text)
7. Do NOT include a signature (that will be added separately)
8. Start with "Dear Hiring Manager,"

Write only the cover letter body text, nothing else."""

        return prompt
    
    def _generate_openai(self, prompt: str) -> str:
        """Generate using OpenAI API
        
        Args:
            prompt: Generation prompt
            
        Returns:
            Generated text
        """
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert cover letter writer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content.strip()
    
    def _generate_anthropic(self, prompt: str) -> str:
        """Generate using Anthropic API
        
        Args:
            prompt: Generation prompt
            
        Returns:
            Generated text
        """
        response = self._client.messages.create(
            model=self.model,
            max_tokens=1000,
            temperature=0.7,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.content[0].text.strip()
    
    def _generate_gemini(self, prompt: str) -> str:
        """Generate using Google Gemini API
        
        Args:
            prompt: Generation prompt
            
        Returns:
            Generated text
        """
        response = self._client.generate_content(prompt)
        return response.text.strip()
    
    def _generate_groq(self, prompt: str) -> str:
        """Generate using Groq API
        
        Args:
            prompt: Generation prompt
            
        Returns:
            Generated text
        """
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert cover letter writer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content.strip()


class CoverLetterManager:
    """Manage cover letter generation and storage"""
    
    def __init__(
        self,
        generator: CoverLetterGenerator,
        output_dir: Path,
        template_path: Optional[Path] = None,
        signature: Optional[str] = None
    ):
        """Initialize manager
        
        Args:
            generator: CoverLetterGenerator instance
            output_dir: Directory to save cover letters
            template_path: Path to DOCX template file
            signature: Signature line for cover letters (optional)
        """
        self.generator = generator
        self.output_dir = output_dir
        self.template_path = template_path
        self.signature = signature
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def cover_letter_exists(self, company: str, job_title: str) -> bool:
        """Check if a cover letter already exists
        
        Args:
            company: Company name
            job_title: Job title
            
        Returns:
            True if PDF exists
        """
        from .pdf_builder import get_document_name
        
        doc_name = get_document_name(company, job_title)
        pdf_path = self.output_dir / f"{doc_name}.pdf"
        
        return pdf_path.exists()
    
    def generate_and_save(
        self,
        company: str,
        job_title: str,
        job_description: str,
        force: bool = False
    ) -> bool:
        """Generate and save a cover letter
        
        Args:
            company: Company name
            job_title: Job title
            job_description: Job description
            force: Force regeneration even if exists
            
        Returns:
            True if successful
        """
        # Check if already exists
        if not force and self.cover_letter_exists(company, job_title):
            print(f"      ⏭️  Cover letter already exists, skipping")
            return False
        
        # Generate cover letter text
        print(f"      🤖 Generating cover letter...")
        cover_text = self.generator.generate(company, job_title, job_description)
        
        if not cover_text:
            print(f"      ✗ Failed to generate cover letter")
            return False
        
        word_count = len(cover_text.split())
        print(f"      ✓ Generated {word_count} word cover letter")
        
        # Small delay to avoid rate limiting
        time.sleep(RATE_LIMIT_DELAY)
        
        # Save as PDF
        from .pdf_builder import PDFBuilder
        
        builder = PDFBuilder(self.output_dir, template_path=self.template_path)
        success = builder.create_cover_letter(company, job_title, cover_text, signature=self.signature)
        
        if success:
            print(f"      ✓ Saved cover letter")
        else:
            print(f"      ✗ Failed to save cover letter")
        
        return success
