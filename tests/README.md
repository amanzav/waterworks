# Waterworks CLI - Test Suite

This directory contains automated tests for the Waterworks CLI tool to help diagnose issues and verify functionality.

## 🧪 Test Files

### `test_config.py` - Configuration Tests
Tests the configuration management system:
- Config file loading
- Dot notation access
- Config validation
- Config structure verification
- API key access

**Run:**
```bash
python tests/test_config.py
```

**Requirements:** Config file at `~/.waterworks/config.yaml`

---

### `test_auth.py` - Authentication Tests
Tests Waterloo Works login and Duo 2FA:
- Basic login flow
- Duo 2FA handling
- Context manager pattern
- Session validation

**Run:**
```bash
python tests/test_auth.py
```

**Requirements:**
- Waterloo Works credentials in config
- Duo Mobile app for 2FA
- Chrome browser

**Note:** This test will open a browser and require you to approve Duo push notification on your phone.

---

### `test_navigation.py` - Navigation & Extraction Tests
Tests folder navigation and job extraction:
- Folder navigation
- Job listing extraction
- Pagination handling
- Job detail extraction

**Run:**
```bash
python tests/test_navigation.py
```

**Requirements:**
- Waterloo Works credentials
- At least one folder with jobs
- Chrome browser

**Note:** You'll be prompted for a folder name if not configured.

---

### `test_llm.py` - LLM Provider Tests
Tests LLM API connections and cover letter generation:
- LLM connection verification
- Cover letter generation
- All provider testing (OpenAI, Anthropic, Gemini, Groq)

**Run:**
```bash
python tests/test_llm.py
```

**Requirements:**
- At least one LLM API key configured
- Internet connection

---

### `test_pdf.py` - PDF Generation Tests
Tests PDF creation and file handling:
- Filename sanitization
- Document naming
- PDF generation
- Multiple PDF creation

**Run:**
```bash
python tests/test_pdf.py
```

**Requirements:** None (standalone test)

**Note:** Creates temporary PDFs in `test_output/` directory and cleans them up automatically.

---

### `run_all_tests.py` - Complete Test Suite
Runs all tests in sequence with user prompts:

**Run:**
```bash
python tests/run_all_tests.py
```

This will:
1. Run config tests (required)
2. Run PDF tests (required)
3. Ask if you want to run LLM tests
4. Ask if you want to run auth tests
5. Ask if you want to run navigation tests
6. Show final summary

---

## 📋 Quick Start

### 1. Run Non-Interactive Tests
Tests that don't require credentials or browser:
```bash
python tests/test_config.py
python tests/test_pdf.py
```

### 2. Run LLM Tests
Requires API key:
```bash
python tests/test_llm.py
```

### 3. Run Full Browser Tests
Requires Waterloo Works credentials:
```bash
python tests/test_auth.py
python tests/test_navigation.py
```

### 4. Run Everything
```bash
python tests/run_all_tests.py
```

---

## 🔧 Troubleshooting

### Tests Fail with "Config file not found"
**Solution:** Run setup first:
```bash
python setup.py
```

### Auth Tests Fail
**Possible causes:**
- Incorrect username/password in config
- Duo 2FA not approved
- Chrome driver issues

**Check:**
```bash
python main.py config --show
```

### LLM Tests Fail
**Possible causes:**
- No API key configured
- Invalid API key
- Rate limiting
- Network issues

**Check:**
```bash
python main.py config --show
```

### Navigation Tests Fail
**Possible causes:**
- Folder doesn't exist
- Folder is empty
- Waterloo Works changed their HTML structure

**Debug:** Run with a known folder that has jobs

### PDF Tests Fail
**Possible causes:**
- Missing docx2pdf dependency
- Permission issues with test_output directory
- COM initialization issues (Windows)

**Check:**
```bash
pip install -r requirements.txt
```

---

## 🎯 Test Coverage

| Component | Test File | Coverage |
|-----------|-----------|----------|
| Config Management | `test_config.py` | ✅ Complete |
| Authentication | `test_auth.py` | ✅ Complete |
| Folder Navigation | `test_navigation.py` | ✅ Complete |
| Job Extraction | `test_navigation.py` | ✅ Complete |
| LLM Generation | `test_llm.py` | ✅ Complete |
| PDF Creation | `test_pdf.py` | ✅ Complete |

---

## 💡 Tips

1. **Run config tests first** - They're fast and don't require credentials
2. **Run PDF tests second** - They're also standalone
3. **LLM tests use API credits** - Be aware of costs
4. **Auth/navigation tests are slowest** - They open browsers
5. **Use `run_all_tests.py`** for comprehensive checks
6. **Run tests after updates** - Verify nothing broke

---

## 📊 Understanding Test Output

### ✅ PASS
Everything working correctly

### ❌ FAIL
Something is broken - check error messages

### ⏭️ SKIPPED
Test was skipped (missing credentials or user choice)

### ⚠️ WARNING
Test passed but with warnings (e.g., config incomplete)

---

## 🐛 Reporting Issues

If tests fail, include:
1. Which test failed
2. Full error output
3. Your Python version: `python --version`
4. Your OS
5. Config structure (with sensitive data removed)

---

## 🔄 Continuous Testing

Recommended testing schedule:
- **After setup:** Run all tests
- **After config changes:** Run `test_config.py`
- **After updating credentials:** Run `test_auth.py`
- **Weekly:** Run `test_llm.py` to verify APIs
- **Before important use:** Run `run_all_tests.py`

---

## 📝 Adding New Tests

To add a new test:
1. Create `test_<feature>.py` in this directory
2. Follow the existing test structure
3. Add to `run_all_tests.py`
4. Update this README
