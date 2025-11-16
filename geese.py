#!/usr/bin/env python3
"""
Geese - CLI Cover Letter Generator for Waterloo Works

Usage:
    python geese.py generate --folder <folder_name>
    python geese.py generate --folder <folder_name> --force
    python geese.py generate --dry-run
    python geese.py config --show
"""

import sys
import click
from pathlib import Path

from modules.config_manager import ConfigManager
from modules.auth import WaterlooWorksAuth
from modules.folder_navigator import FolderNavigator
from modules.job_extractor import JobExtractor
from modules.cover_letter_generator import CoverLetterGenerator, CoverLetterManager


@click.group()
def cli():
    """🦆 Geese - CLI Cover Letter Generator for Waterloo Works"""
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
        
        # Authenticate and login
        print("\n" + "=" * 60)
        print("🔐 Authentication")
        print("=" * 60)
        
        auth = WaterlooWorksAuth(username, password)
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
            
            if not resume_text:
                print("⚠️  Warning: Resume text is empty. Cover letters may be generic.")
            
            print(f"Provider: {provider}")
            print(f"Model: {model}")
            
            generator = CoverLetterGenerator(
                provider=provider,
                model=model,
                api_key=api_key,
                resume_text=resume_text,
                additional_info=additional_info
            )
            
            manager = CoverLetterManager(
                generator=generator,
                output_dir=config.get_cover_letters_dir()
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
            # Close browser
            auth.close()
        
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
    "--set",
    nargs=2,
    type=str,
    metavar="KEY VALUE",
    help="Set a configuration value (e.g., --set llm.model gpt-4o)"
)
def config(show, set):
    """Manage Geese configuration"""
    
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
                
                # Show key settings
                print(f"Profile:")
                print(f"  Resume: {config_mgr.get('profile.resume_pdf')}")
                print(f"  Resume text length: {len(config_mgr.get('profile.resume_text', ''))} chars")
                print()
                
                print(f"Waterloo Works:")
                print(f"  Username: {config_mgr.get('waterloo_works.username')}")
                print(f"  Password: {'***' if config_mgr.get('waterloo_works.password') else '(not set - will prompt)'}")
                print()
                
                print(f"LLM:")
                print(f"  Provider: {config_mgr.get('llm.provider')}")
                print(f"  Model: {config_mgr.get('llm.model')}")
                print(f"  API Key: {'***' if config_mgr.get_api_key() else '(not set)'}")
                print()
                
                print(f"Paths:")
                print(f"  Cover letters: {config_mgr.get('paths.cover_letters_dir')}")
                print()
                
                print(f"Defaults:")
                print(f"  Folder: {config_mgr.get('defaults.folder_name')}")
                print()
                
            except FileNotFoundError:
                print(f"\n❌ Configuration file not found at {config_mgr.config_path}")
                print("Run 'python setup.py' to create your configuration.")
                sys.exit(1)
        
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
            print("  python geese.py config --show              # Show current config")
            print("  python geese.py config --set KEY VALUE     # Set a config value")
            print()
            print(f"Config file location: {config_mgr.config_path}")
            print()
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
