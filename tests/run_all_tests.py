"""Run all tests for Geese CLI"""

import sys
import subprocess
from pathlib import Path


def run_test_file(test_file: str, description: str) -> bool:
    """Run a test file and return success status"""
    print("\n" + "="*80)
    print(f"🧪 Running: {description}")
    print("="*80)
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=False,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running {test_file}: {e}")
        return False


def main():
    """Run all test suites"""
    print("\n" + "="*80)
    print("🦆 Geese - Complete Test Suite")
    print("="*80)
    print("\nThis will run all tests to verify the Geese CLI is working correctly.")
    print("Some tests require:")
    print("  - Waterloo Works credentials (for auth & navigation tests)")
    print("  - LLM API key (for LLM tests)")
    print("  - Internet connection")
    
    response = input("\nDo you want to continue? (y/n): ").strip().lower()
    if response != 'y':
        print("❌ Tests cancelled")
        return
    
    tests_dir = Path(__file__).parent
    
    # Define tests in order
    tests = [
        ("test_config.py", "Configuration Tests", True),
        ("test_pdf.py", "PDF Generation Tests", True),
        ("test_llm.py", "LLM Provider Tests", False),
        ("test_auth.py", "Authentication Tests", False),
        ("test_navigation.py", "Navigation & Extraction Tests", False),
    ]
    
    results = {}
    
    for test_file, description, required in tests:
        test_path = tests_dir / test_file
        
        if not test_path.exists():
            print(f"\n⚠️  Skipping {description}: File not found")
            results[description] = "skipped"
            continue
        
        if not required:
            response = input(f"\nRun {description}? (y/n): ").strip().lower()
            if response != 'y':
                print(f"⏭️  Skipping {description}")
                results[description] = "skipped"
                continue
        
        success = run_test_file(str(test_path), description)
        results[description] = "pass" if success else "fail"
    
    # Final Summary
    print("\n" + "="*80)
    print("📊 FINAL TEST SUMMARY")
    print("="*80)
    
    for test_name, status in results.items():
        if status == "pass":
            emoji = "✅"
        elif status == "fail":
            emoji = "❌"
        else:
            emoji = "⏭️"
        
        print(f"{emoji} {test_name}: {status.upper()}")
    
    # Calculate statistics
    passed = sum(1 for s in results.values() if s == "pass")
    failed = sum(1 for s in results.values() if s == "fail")
    skipped = sum(1 for s in results.values() if s == "skipped")
    total = len(results)
    
    print("\n" + "="*80)
    print(f"Total: {total} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}")
    print("="*80)
    
    if failed == 0 and passed > 0:
        print("\n🎉 All run tests passed!")
        sys.exit(0)
    elif failed > 0:
        print("\n⚠️  Some tests failed - check output above")
        sys.exit(1)
    else:
        print("\n⚠️  No tests were run")
        sys.exit(1)


if __name__ == "__main__":
    main()
