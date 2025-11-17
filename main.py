#!/usr/bin/env python3
"""
Waterworks - CLI Cover Letter Generator for Waterloo Works

Usage:
    python main.py generate --folder <folder_name>
    python main.py generate --folder <folder_name> --force
    python main.py generate --dry-run
    python main.py upload
    python main.py upload --stats --list
    python main.py upload --force
    python main.py config --show
"""

__version__ = "1.0.0"

import sys
import click
from pathlib import Path

from modules.config_manager import ConfigManager
from modules.auth import WaterlooWorksAuth
from modules.folder_navigator import FolderNavigator
from modules.job_extractor import JobExtractor
from modules.cover_letter_generator import CoverLetterGenerator, CoverLetterManager
from modules.cover_letter_uploader import CoverLetterUploader


@click.group()
def cli():
    """💧 Waterworks - CLI Cover Letter Generator for Waterloo Works"""
    pass


@cli.command()
@click.option(
    "--folder",
    "-f",
    default=None,
    help="Waterloo Works folder name (uses config default if not specified)"
)
@click.option(
    "--job-board",
    "-b",
    type=click.Choice(["full", "direct"], case_sensitive=False),
    default="full",
    help="Job board type: 'full' for Full-Cycle Service (default) or 'direct' for Employer-Student Direct"
)
@click.option(
    "--force",
    is_flag=True,
    help="Force regenerate cover letters even if they already exist"
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Preview what would be generated without actually generating"
)
def generate(folder, job_board, force, dry_run):
    """Generate cover letters for jobs in a Waterloo Works folder"""
    
    try:
        # Load configuration
        print("📋 Loading configuration...")
        config = ConfigManager()
        config.load()
        
        # Validate configuration
        is_valid, errors = config.validate()
        if not is_valid:
            print("\n❌ Configuration errors:")
            for error in errors:
                print(f"  • {error}")
            print(f"\nEdit your config at: {config.config_path}")
            sys.exit(1)
        
        # Additional validation: Check resume file exists
        resume_path = Path(config.get("profile.resume_pdf", ""))
        if not resume_path.exists():
            print(f"\n❌ Resume file not found: {resume_path}")
            print("Please update the path in your config file.")
            sys.exit(1)
        
        print("✅ Configuration loaded\n")
        
        # Get folder name
        if not folder:
            folder = config.get_default_folder()
            print(f"ℹ️  Using default folder: {folder}")
        
        # Use default job board if not specified via command line
        if job_board == "full":  # Check if it's the default value
            configured_board = config.get_default_job_board()
            if configured_board != "full":
                job_board = configured_board
                print(f"ℹ️  Using configured job board: {configured_board}")
        
        # Get credentials
        username, password = config.get_credentials()
        headless = config.get_headless()
        
        # Authenticate and login
        print("\n" + "=" * 60)
        print("🔐 Authentication")
        print("=" * 60)
        
        auth = WaterlooWorksAuth(username, password, headless=headless)
        driver = auth.login()
        
        try:
            # Navigate to folder and extract jobs
            print("\n" + "=" * 60)
            print("📁 Extracting Jobs from Folder")
            print("=" * 60)
            
            board_name = "Full-Cycle Service" if job_board == "full" else "Employer-Student Direct"
            print(f"📋 Job Board: {board_name}")
            
            navigator = FolderNavigator(driver, job_board=job_board)
            all_jobs = navigator.extract_all_jobs_from_folder(folder)
            
            if not all_jobs:
                print("\n❌ No jobs found in folder. Exiting.")
                return
            
            # Dry run - just show what would be done
            if dry_run:
                print("\n" + "=" * 60)
                print("🔍 Dry Run - Preview")
                print("=" * 60)
                print(f"\nFound {len(all_jobs)} jobs:")
                for idx, job in enumerate(all_jobs, 1):
                    print(f"  {idx}. {job['company']} - {job['job_title']}")
                print(f"\n📂 Cover letters would be saved to: {config.get_cover_letters_dir()}")
                print("\nRun without --dry-run to generate cover letters.")
                return
            
            # Initialize cover letter generator
            print("\n" + "=" * 60)
            print("🤖 Initializing Cover Letter Generator")
            print("=" * 60)
            
            provider = config.get("llm.provider")
            model = config.get("llm.model")
            api_key = config.get_api_key()
            resume_text = config.get("profile.resume_text", "")
            additional_info = config.get("profile.additional_info", "")
            signature = config.get_signature()
            user_profile = config.get_user_profile()
            template_path = config.get_template_path()
            prompt_template = config.get("cover_letter.prompt")
            
            if not resume_text:
                print("⚠️  Warning: Resume text is empty. Cover letters may be generic.")
            
            print(f"Provider: {provider}")
            print(f"Model: {model}")
            if template_path:
                print(f"Template: {template_path.name}")
            
            generator = CoverLetterGenerator(
                provider=provider,
                model=model,
                api_key=api_key,
                resume_text=resume_text,
                user_profile=user_profile,
                additional_info=additional_info,
                prompt_template=prompt_template
            )
            
            manager = CoverLetterManager(
                generator=generator,
                output_dir=config.get_cover_letters_dir(),
                template_path=template_path,
                signature=signature
            )
            
            # Extract job details and generate cover letters
            print("\n" + "=" * 60)
            print("📝 Generating Cover Letters")
            print("=" * 60)
            
            extractor = JobExtractor(driver)
            
            stats = {
                "total": len(all_jobs),
                "generated": 0,
                "skipped": 0,
                "failed": 0
            }
            
            for idx, job_basic in enumerate(all_jobs, 1):
                company = job_basic["company"]
                job_title = job_basic["job_title"]
                
                print(f"\n[{idx}/{len(all_jobs)}] {company} - {job_title}")
                
                # Check if already exists (unless force)
                if not force and manager.cover_letter_exists(company, job_title):
                    print(f"      ⏭️  Cover letter already exists, skipping")
                    stats["skipped"] += 1
                    continue
                
                # Extract job details
                print(f"      📄 Extracting job details...")
                job_details = extractor.extract_job_details(job_basic)
                
                if not job_details:
                    print(f"      ✗ Failed to extract job details")
                    stats["failed"] += 1
                    continue
                
                # Check if we have a good description
                description = job_details.get("description", "")
                if not description or len(description) < 50:
                    print(f"      ⏭️  Skipping (description too short or missing)")
                    stats["failed"] += 1
                    continue
                
                # Generate and save cover letter
                success = manager.generate_and_save(
                    company=company,
                    job_title=job_title,
                    job_description=description,
                    force=force
                )
                
                if success:
                    stats["generated"] += 1
                else:
                    stats["failed"] += 1
            
            # Print summary
            print("\n" + "=" * 60)
            print("✅ Summary")
            print("=" * 60)
            print(f"Total jobs: {stats['total']}")
            print(f"Generated: {stats['generated']}")
            print(f"Skipped (already exist): {stats['skipped']}")
            print(f"Failed: {stats['failed']}")
            print(f"\n📂 Cover letters saved to: {config.get_cover_letters_dir()}")
            print()
            
        finally:
            # Close browser - ensure cleanup happens even if there are errors
            if 'auth' in locals():
                try:
                    auth.close()
                except Exception as e:
                    print(f"⚠️  Warning: Error during cleanup: {e}")
        
    except FileNotFoundError as e:
        print(f"\n❌ {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user. Cleaning up...")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.option(
    "--force",
    is_flag=True,
    help="Re-upload all files, ignoring tracking"
)
@click.option(
    "--list",
    "list_files",
    is_flag=True,
    help="List uploaded and pending files"
)
@click.option(
    "--reset",
    is_flag=True,
    help="Reset upload tracking (clear history)"
)
@click.option(
    "--stats",
    is_flag=True,
    help="Show upload statistics"
)
def upload(force, list_files, reset, stats):
    """Upload cover letters to Waterloo Works"""
    
    try:
        # Load configuration
        print("📋 Loading configuration...")
        config = ConfigManager()
        config.load()
        
        # Validate configuration
        is_valid, errors = config.validate()
        if not is_valid:
            print("\n❌ Configuration errors:")
            for error in errors:
                print(f"  • {error}")
            print(f"\nEdit your config at: {config.config_path}")
            sys.exit(1)
        
        print("✅ Configuration loaded\n")
        
        # Get credentials
        username, password = config.get_credentials()
        headless = config.get_headless()
        
        # Handle non-upload commands (don't require authentication)
        cover_letters_dir = config.get_cover_letters_dir()
        data_dir = config.get_data_dir()
        
        if reset:
            # Reset upload tracking
            uploader = CoverLetterUploader(
                driver=None,  # Not needed for reset
                cover_letters_dir=cover_letters_dir,
                data_dir=data_dir
            )
            uploader.reset_upload_tracking()
            return
        
        if stats or list_files:
            # Show stats/list without authentication
            uploader = CoverLetterUploader(
                driver=None,  # Not needed for stats
                cover_letters_dir=cover_letters_dir,
                data_dir=data_dir
            )
            
            if stats:
                upload_stats = uploader.get_upload_stats()
                print("\n📊 Upload Statistics")
                print("=" * 60)
                print(f"Total PDFs: {upload_stats['total_pdfs']}")
                print(f"Uploaded: {upload_stats['uploaded_count']}")
                print(f"Pending: {upload_stats['pending_count']}")
                print()
            
            if list_files:
                uploader.list_uploaded_files()
                uploader.list_pending_files()
            
            return
        
        # Authenticate and login for upload
        print("=" * 60)
        print("🔐 Authentication")
        print("=" * 60)
        
        auth = WaterlooWorksAuth(username, password, headless=headless)
        driver = auth.login()
        
        try:
            # Initialize uploader
            print("\n" + "=" * 60)
            print("📤 Cover Letter Upload")
            print("=" * 60)
            
            uploader = CoverLetterUploader(
                driver=driver,
                cover_letters_dir=cover_letters_dir,
                data_dir=data_dir
            )
            
            # Upload all cover letters
            uploader.upload_all_cover_letters(force=force)
            
        finally:
            # Close browser - ensure cleanup happens even if there are errors
            if 'auth' in locals():
                try:
                    auth.close()
                except Exception as e:
                    print(f"⚠️  Warning: Error during cleanup: {e}")
        
    except FileNotFoundError as e:
        print(f"\n❌ {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user. Cleaning up...")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.option(
    "--show",
    is_flag=True,
    help="Show current configuration"
)
@click.option(
    "--edit",
    is_flag=True,
    help="Open configuration file in default editor"
)
@click.option(
    "--set",
    nargs=2,
    type=str,
    metavar="KEY VALUE",
    help="Set a configuration value (e.g., --set llm.model gpt-4o)"
)
def config(show, edit, set):
    """Manage Waterworks configuration"""
    
    try:
        config_mgr = ConfigManager()
        
        if show:
            # Show configuration
            try:
                config_mgr.load()
                print("\n📋 Current Configuration")
                print("=" * 60)
                print(f"Config file: {config_mgr.config_path}")
                print()
                
                # Profile section
                print(f"Profile:")
                print(f"  Name: {config_mgr.get('profile.name', '(not set)')}")
                print(f"  Email: {config_mgr.get('profile.email', '(not set)')}")
                print(f"  Phone: {config_mgr.get('profile.phone', '(not set)')}")
                print(f"  LinkedIn: {config_mgr.get('profile.linkedin', '(not set)')}")
                print(f"  GitHub: {config_mgr.get('profile.github', '(not set)')}")
                print(f"  Website: {config_mgr.get('profile.website', '(not set)')}")
                print(f"  Resume PDF: {config_mgr.get('profile.resume_pdf', '(not set)')}")
                resume_text = config_mgr.get('profile.resume_text', '')
                if resume_text:
                    print(f"  Resume text: {len(resume_text)} chars")
                else:
                    print(f"  Resume text: (not set)")
                additional_info = config_mgr.get('profile.additional_info', '')
                if additional_info:
                    print(f"  Additional info: {len(additional_info)} chars")
                else:
                    print(f"  Additional info: (not set)")
                signature = config_mgr.get('profile.signature', '')
                if signature:
                    print(f"  Signature: {len(signature)} chars")
                else:
                    print(f"  Signature: (not set)")
                template = config_mgr.get('profile.cover_letter_template', '')
                if template:
                    print(f"  Cover letter template: {template}")
                else:
                    print(f"  Cover letter template: (using default)")
                print()
                
                # Waterloo Works section
                print(f"Waterloo Works:")
                print(f"  Username: {config_mgr.get('waterloo_works.username', '(not set)')}")
                password = config_mgr.get('waterloo_works.password', '')
                if password:
                    print(f"  Password: ***")
                else:
                    print(f"  Password: (not set - will prompt)")
                print()
                
                # LLM section
                print(f"LLM:")
                print(f"  Provider: {config_mgr.get('llm.provider', '(not set)')}")
                print(f"  Model: {config_mgr.get('llm.model', '(not set)')}")
                api_key = config_mgr.get_api_key()
                if api_key:
                    print(f"  API Key: ***")
                else:
                    print(f"  API Key: (not set)")
                
                # Show API keys for all providers if configured
                api_keys = config_mgr.get('llm.api_keys', {})
                if api_keys:
                    print(f"  API Keys:")
                    for provider, key in api_keys.items():
                        if key:
                            print(f"    {provider}: ***")
                print()
                
                # Paths section
                print(f"Paths:")
                print(f"  Cover letters: {config_mgr.get('paths.cover_letters_dir', './cover_letters')}")
                print(f"  Data: {config_mgr.get('paths.data_dir', './data')}")
                print()
                
                # Defaults section
                print(f"Defaults:")
                print(f"  Folder name: {config_mgr.get('defaults.folder_name', 'waterworks')}")
                print(f"  Job board: {config_mgr.get('defaults.job_board', 'full')}")
                print()
                
                # Browser section
                print(f"Browser:")
                headless = config_mgr.get('browser.headless', False)
                print(f"  Headless mode: {headless}")
                print()
                
                # Cover Letter section
                print(f"Cover Letter:")
                prompt = config_mgr.get('cover_letter.prompt', '')
                if prompt:
                    print(f"  Custom prompt: {len(prompt)} chars")
                else:
                    print(f"  Custom prompt: (using default)")
                print()
                
            except FileNotFoundError:
                print(f"\n❌ Configuration file not found at {config_mgr.config_path}")
                print("Run 'python setup.py' to create your configuration.")
                sys.exit(1)
        
        elif edit:
            # Open configuration file in default editor
            import subprocess
            import platform
            
            if not config_mgr.config_path.exists():
                print(f"\n❌ Configuration file not found at {config_mgr.config_path}")
                print("Run 'python setup.py' to create your configuration.")
                sys.exit(1)
            
            try:
                system = platform.system()
                if system == "Windows":
                    # Windows: use start command
                    subprocess.run(["cmd", "/c", "start", "", str(config_mgr.config_path)], check=True)
                elif system == "Darwin":
                    # macOS: use open command
                    subprocess.run(["open", str(config_mgr.config_path)], check=True)
                else:
                    # Linux: try xdg-open
                    subprocess.run(["xdg-open", str(config_mgr.config_path)], check=True)
                
                print(f"✅ Opened config file in default editor: {config_mgr.config_path}")
            except Exception as e:
                print(f"\n⚠️  Could not open file automatically: {e}")
                print(f"Please manually open: {config_mgr.config_path}")
        
        elif set:
            # Set a configuration value
            key, value = set
            
            try:
                config_mgr.load()
                config_mgr.set(key, value)
                config_mgr.save(config_mgr.config)
                print(f"✅ Set {key} = {value}")
            except FileNotFoundError:
                print(f"\n❌ Configuration file not found at {config_mgr.config_path}")
                print("Run 'python setup.py' to create your configuration.")
                sys.exit(1)
        
        else:
            # Show help
            print("\n📋 Configuration Management")
            print("=" * 60)
            print("Usage:")
            print("  python main.py config --show              # Show current config")
            print("  python main.py config --edit              # Edit config file")
            print("  python main.py config --set KEY VALUE     # Set a config value")
            print()
            print(f"Config file location: {config_mgr.config_path}")
            print()
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
