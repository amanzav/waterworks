# Product Requirements Document (PRD)
## Geese - CLI Cover Letter Generator

**Version:** 1.0  
**Date:** November 16, 2025  
**Status:** Proposal - Pending Approval  
**Author:** Aman Zaveri

---

## Executive Summary

Geese is a streamlined command-line tool that automates cover letter generation for Waterloo Works job applications. It focuses on delivering a single, polished feature: generating personalized cover letters from saved job folders using AI.

**Key Features:**
- CLI-only (no web frontend)
- Focus on cover letter generation only
- GitHub-based distribution (no pip installation)
- Built with proven scraping and generation techniques

---

## Problem Statement

Students applying to co-op jobs through Waterloo Works face two key challenges:
1. **Volume**: Applying to 50-100+ jobs requires unique cover letters for each
2. **Quality**: Generic cover letters hurt application success rates

Geese focuses exclusively on the cover letter generation workflow, keeping the tool simple and effective.

---

## Target Users

- **Primary**: University of Waterloo co-op students
- **Secondary**: Other students with access to job posting systems
- **Skill Level**: Basic command-line familiarity required
- **Distribution**: Open-source GitHub repository

---

## User Workflow

### Prerequisites
1. User has a Waterloo Works account
2. User has saved jobs to a specific folder in Waterloo Works
3. User has their resume and additional profile information ready
4. User has an OpenAI/Anthropic/Gemini API key

### Core Flow
1. **Setup** (one-time):
   ```bash
   git clone https://github.com/amanzav/geese.git
   cd geese
   python setup.py  # Interactive setup wizard
   ```
   - Setup wizard collects:
     - Resume PDF path
     - Additional profile information (text file or interactive input)
     - Waterloo Works credentials (optional - can be stored in config.yaml)
     - LLM API key and model preference
     - Default folder name for jobs
     - Output folder for cover letters

2. **Save Jobs** (on Waterloo Works):
   - User browses Waterloo Works and saves desired jobs to a folder (e.g., "geese_jobs")

3. **Generate Cover Letters**:
   ```bash
   python geese.py generate --folder "geese_jobs"
   ```
   - Script logs into Waterloo Works (with Duo Mobile 2FA prompt)
   - Navigates to specified folder
   - Extracts all job postings from folder (handles pagination)
   - For each job:
     - Extracts job description
     - Generates personalized cover letter using LLM
     - Saves as PDF in `cover_letters/` folder
   - Skips jobs where cover letters already exist

4. **Review & Use**:
   - User reviews generated cover letters in `cover_letters/` folder
   - User can manually edit if needed
   - User uploads to Waterloo Works or uses for applications

---

## Technical Architecture

### Technology Stack
- **Language**: Python 3.9+
- **Key Dependencies**:
  - `selenium` - Browser automation for Waterloo Works navigation
  - `python-docx` - DOCX generation
  - `docx2pdf` - PDF conversion
  - `openai`/`anthropic`/`google-generativeai` - LLM integration
  - `pyyaml` - Configuration management
  - `click` - CLI framework

### Configuration File Structure
**~/.geese/config.yaml**:
```yaml
# User Profile
profile:
  resume_pdf: "/path/to/resume.pdf"
  resume_text: "Extracted/cached resume text..."
  additional_info: |
    Additional information about yourself that you want 
    included in cover letters but isn't in your resume...

# Waterloo Works Credentials (optional - will prompt if not set)
waterloo_works:
  username: "your.email@uwaterloo.ca"
  password: ""  # Leave empty to be prompted securely

# LLM Configuration
llm:
  provider: "openai"  # openai | anthropic | gemini | groq
  model: "gpt-4o-mini"  # Default model
  api_key: "sk-..."  # Or use environment variable
  
  # Model options per provider
  models:
    openai: ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]
    anthropic: ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"]
    gemini: ["gemini-1.5-flash", "gemini-1.5-pro"]
    groq: ["llama-3.1-70b-versatile", "llama-3.1-8b-instant"]

# Paths
paths:
  cover_letters_dir: "./cover_letters"
  cache_dir: "~/.geese/cache"

# Defaults
defaults:
  folder_name: "geese"  # Default Waterloo Works folder to use
```

### Code Structure
```
geese/
├── PRD.md                          # This document
├── README.md                       # User-facing documentation
├── setup.py                        # Interactive setup wizard
├── geese.py                        # Main CLI entry point
├── config.yaml.template            # Template config file
├── requirements.txt                # Python dependencies
│
├── modules/
│   ├── __init__.py
│   ├── auth.py                    # Waterloo Works login + Duo 2FA
│   ├── folder_navigator.py        # Navigate to folders, handle pagination
│   ├── job_extractor.py           # Extract job details from pages
│   ├── cover_letter_generator.py  # LLM-based generation logic
│   ├── pdf_builder.py             # Build DOCX -> PDF pipeline
│   ├── config_manager.py          # Handle config.yaml operations
│   └── utils.py                   # Selenium helpers, selectors
│
└── tests/
    ├── test_auth.py
    ├── test_extractor.py
    └── test_generator.py
```

### Key Components

1. **Authentication (`modules/auth.py`)**:
   - Login flow, email/password handling, Duo 2FA waiting
   - Uses existing selectors and WebDriver setup
   - Credentials from config.yaml or interactive prompt

2. **Folder Navigation (`modules/folder_navigator.py`)**:
   - `navigate_to_folder()` function
   - `get_pagination_pages()` and `go_to_next_page()`
   - `get_jobs_from_page()` for extracting job links

3. **Job Detail Extraction (`modules/job_extractor.py`)**:
   - Job detail scraping logic
   - Extract: job summary, responsibilities, required skills, company info
   - Build consolidated description for LLM

4. **Cover Letter Generation (`modules/cover_letter_generator.py`)**:
   - `generate_cover_letter_text()` with agent pattern
   - `save_cover_letter()` for DOCX → PDF conversion
   - `cover_letter_exists()` to skip duplicates

5. **Utilities (`modules/utils.py`)**:
   - Selenium selectors and helper functions
   - `sanitize_filename()`, `smart_page_wait()`, etc.

---

## User Stories

### Must-Have (MVP)

**US-1: Initial Setup**
- **As a** new user
- **I want to** run an interactive setup wizard
- **So that** I can configure my profile and credentials once

**Acceptance Criteria**:
- Setup wizard prompts for all required information
- Creates `~/.geese/config.yaml` with user inputs
- Extracts text from resume PDF and caches it
- Validates API key works with chosen LLM provider
- Handles missing or invalid inputs gracefully

---

**US-2: Generate Cover Letters from Folder**
- **As a** student
- **I want to** generate cover letters for all jobs in my Waterloo Works folder
- **So that** I can save hours of manual writing

**Acceptance Criteria**:
- Command: `python geese.py generate --folder "folder_name"`
- Logs into Waterloo Works with Duo 2FA
- Navigates to specified folder
- Extracts all jobs across all pages
- Generates cover letter for each job using resume + job description
- Saves as PDF with naming: `{Company}_{JobTitle}.pdf`
- Skips jobs where cover letter already exists
- Shows progress bar/counter during generation
- Handles errors gracefully (network issues, LLM failures)

---

**US-3: Authentication with Duo 2FA**
- **As a** user
- **I want to** complete Duo Mobile authentication during login
- **So that** the tool can access my Waterloo Works account securely

**Acceptance Criteria**:
- Prompts user to approve Duo push notification
- Waits up to 60 seconds for approval
- Shows clear instructions in CLI
- Handles timeout gracefully
- Allows retry if authentication fails

---

**US-4: Profile Information Management**
- **As a** user
- **I want to** provide additional information beyond my resume
- **So that** cover letters can include relevant details not on my resume

**Acceptance Criteria**:
- Setup wizard asks: "Do you have additional information to include?"
- If yes, prompts for text file path OR allows typing directly
- Stores in config.yaml under `profile.additional_info`
- Can be edited manually in config.yaml later
- LLM uses both resume + additional info for generation

---

**US-5: Skip Existing Cover Letters**
- **As a** user
- **I want to** avoid regenerating cover letters that already exist
- **So that** I can run the tool multiple times without waste

**Acceptance Criteria**:
- Checks if `{Company}_{JobTitle}.pdf` exists before generation
- Skips generation and logs: "⏭️ Skipping {Company} - cover letter exists"
- Can force regeneration with `--force` flag

---

### Nice-to-Have (Future)

**US-6: Multiple LLM Provider Support**
- Support OpenAI, Anthropic, Gemini, Groq
- User selects provider and model in config
- Falls back to defaults if model unavailable

**US-7: Dry Run Mode**
- `python geese.py generate --folder "jobs" --dry-run`
- Shows what would be generated without actually generating
- Useful for checking job count before API costs

**US-8: Custom Templates**
- Allow users to provide custom cover letter templates
- Support variable substitution: `{company}`, `{job_title}`, `{content}`

---

## Non-Functional Requirements

### Performance
- **Login**: < 30 seconds (waiting for Duo 2FA is user-dependent)
- **Job Extraction**: < 5 seconds per page of jobs
- **Cover Letter Generation**: < 30 seconds per letter (LLM-dependent)
- **Overall**: Should handle 50 jobs in < 30 minutes

### Reliability
- **Error Handling**: Graceful failures with clear error messages
- **Resume Capability**: If a job fails, continue with remaining jobs
- **Retry Logic**: Retry LLM calls up to 3 times on failure
- **Network**: Handle temporary network issues with exponential backoff

### Security
- **Credentials**: Never log passwords
- **API Keys**: Support environment variables (`.env`)
- **Config File**: Warn users to add `config.yaml` to `.gitignore`
- **2FA**: Respect Duo timeout limits

### Usability
- **Installation**: < 5 minutes from clone to first run
- **Setup**: < 10 minutes for first-time configuration
- **Documentation**: Clear README with screenshots
- **Feedback**: Progress indicators for long operations
- **Error Messages**: Actionable ("Your API key is invalid. Check config.yaml")

### Compatibility
- **OS**: Windows, macOS, Linux
- **Python**: 3.9+
- **Browser**: Chrome/Chromium (via Selenium)

---

## Success Metrics

### Primary Metrics
1. **Adoption**: GitHub stars/forks/clones
2. **Usage**: Number of cover letters generated per user session
3. **Quality**: User feedback on cover letter relevance/quality

### Secondary Metrics
1. **Setup Time**: Time from clone to first successful generation
2. **Error Rate**: % of jobs that fail to generate cover letters
3. **User Retention**: % of users who run tool more than once

---

## Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Waterloo Works UI changes | High | Medium | Use robust selectors, version documentation, quick updates |
| LLM API cost | Medium | High | Default to cheapest models (gpt-4o-mini, flash), show cost estimates |
| Duo 2FA timeout | Medium | Medium | Clear instructions, 60s timeout, allow retry |
| PDF generation issues (Windows) | Medium | Medium | Test on all platforms, provide troubleshooting guide |
| Resume parsing failures | Medium | Low | Support manual text input as fallback |
| Rate limiting (LLM APIs) | Low | Medium | Implement exponential backoff, show progress |

---

## Out of Scope

The following features are **explicitly excluded** to maintain focus:

❌ Web frontend/dashboard  
❌ Job matching/scoring  
❌ Embeddings-based resume analysis  
❌ Auto-apply functionality  
❌ Database storage (SQLite/Supabase)  
❌ Multiple resume support  
❌ Job filtering/search  
❌ Analytics/statistics  
❌ Cover letter uploading to Waterloo Works  
❌ pip/PyPI distribution  

These may be considered for future versions.

---

## Open Questions

1. **Resume Format**: Should we support Word docs in addition to PDF?
2. **Additional Info Format**: Text file vs interactive input vs both?
3. **LLM Defaults**: Which provider/model should be the default?
4. **Error Recovery**: Should we save partial progress if script crashes?
5. **Concurrency**: Should we generate multiple cover letters in parallel?
6. **Template Customization**: How much control should users have over output format?

---

## Implementation Phases

### Phase 1: Core Infrastructure (Week 1)
- [ ] Set up v2 project structure
- [ ] Copy and adapt reusable modules from v1
- [ ] Implement `config_manager.py` for YAML handling
- [ ] Build `setup.py` interactive wizard
- [ ] Test authentication flow end-to-end

### Phase 2: Job Extraction (Week 2)
- [ ] Implement folder navigation
- [ ] Handle pagination correctly
- [ ] Extract job details reliably
- [ ] Test with various folder sizes (1, 10, 50+ jobs)

### Phase 3: Cover Letter Generation (Week 3)
- [ ] Integrate LLM providers (start with OpenAI)
- [ ] Implement generation logic
- [ ] Build DOCX → PDF pipeline
- [ ] Test output quality with real jobs

### Phase 4: CLI & Polish (Week 4)
- [ ] Build CLI with `click`
- [ ] Add progress indicators
- [ ] Implement error handling
- [ ] Write comprehensive README
- [ ] Test on Windows, macOS, Linux

### Phase 5: Testing & Documentation (Week 5)
- [ ] End-to-end testing with real Waterloo Works account
- [ ] Write troubleshooting guide
- [ ] Create setup video/GIF
- [ ] Prepare for GitHub release

---

## Appendix

### A. CLI Command Reference

```bash
# Setup (one-time)
python setup.py

# Generate cover letters (default folder from config)
python geese.py generate

# Generate from specific folder
python geese.py generate --folder "urgent_jobs"

# Force regenerate all (ignore existing)
python geese.py generate --force

# Dry run (preview without generating)
python geese.py generate --dry-run

# Update configuration
python geese.py config --set llm.model="gpt-4o"

# Show current configuration
python geese.py config --show
```

### B. Example Output

```
🔑 Logging in to Waterloo Works...
  → Entering email...
  → Entering password...
  
⏳ Waiting for Duo 2FA (approve on your phone)...
✅ Login successful!

📁 Navigating to 'geese_jobs' folder...
   ✓ Successfully navigated to 'geese_jobs' folder

📄 Found 2 page(s) of jobs

🎯 Processing 23 jobs total...

[1/23] Microsoft - Software Engineer Intern
      ✓ Found job in database
      🤖 Generating cover letter...
      ✓ Generated 267 word cover letter
      ✓ Saved: Microsoft_SoftwareEngineerIntern.pdf

[2/23] Google - SWE Intern
      ⏭️ Cover letter already exists, skipping

[3/23] Amazon - Software Development Engineer Intern
      🔍 Not in database - scraping live...
      ✓ Scraped and saved job to database
      🤖 Generating cover letter...
      ✓ Generated 312 word cover letter
      ✓ Saved: Amazon_SoftwareDevelopmentEngineerIntern.pdf

...

✅ Complete! Generated 21 new cover letters (2 skipped)
📂 Cover letters saved to: ./cover_letters/
```

### C. Example config.yaml

```yaml
profile:
  resume_pdf: "/Users/aman/Documents/resume.pdf"
  resume_text: |
    Aman Zaveri
    Software Engineering Student
    University of Waterloo
    
    Experience:
    - Software Engineer Intern @ TechCorp...
    
  additional_info: |
    I'm particularly interested in backend systems and have
    built several personal projects using Python and AWS.
    I'm passionate about developer tools and automation.

waterloo_works:
  username: "a2zaveri@uwaterloo.ca"
  password: ""  # Will prompt securely

llm:
  provider: "openai"
  model: "gpt-4o-mini"
  api_key: "sk-proj-..."

paths:
  cover_letters_dir: "./cover_letters"

defaults:
  folder_name: "geese"
```

---

## Approval Sign-Off

**Stakeholders**: 
- [ ] Product Owner: Aman Zaveri
- [ ] Technical Lead: Aman Zaveri
- [ ] User Representative: _________________

**Approval Date**: _________________

**Next Steps After Approval**:
1. Create GitHub project board
2. Set up development environment
3. Begin Phase 1 implementation
4. Weekly progress reviews

---

*End of PRD*
