# 💧 Waterworks

Automate cover letter generation for Waterloo Works job applications using AI.

**Requirements:** Python 3.9+ and Google Chrome

## 🚀 Installation

**Easy Install (Recommended):**

```bash
# macOS/Linux
curl -sSL https://raw.githubusercontent.com/amanzav/waterworks/main/install.sh | bash

# Windows PowerShell
irm https://raw.githubusercontent.com/amanzav/waterworks/main/install.ps1 | iex
```

This will download files, set up a virtual environment, install dependencies, and create a `waterworks` command.

**Manual Install:**

```bash
git clone https://github.com/amanzav/waterworks.git
cd waterworks
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 📖 Getting Started

### First Time Setup

After installation, run the configuration wizard:

```bash
waterworks config
```

You'll be asked for:
- **Resume PDF path** - Location of your resume file
- **Waterloo Works credentials** - Your username/password
- **LLM provider** - OpenAI, Anthropic, Gemini, or Groq
- **API key** - [Get API keys here](https://platform.openai.com/api-keys) (OpenAI) or from your chosen provider

Config is saved to `~/.waterworks/config.yaml`

### Using Waterworks

**Step 1:** Log into Waterloo Works and save jobs to a folder

**Step 2:** Generate cover letters:

```bash
waterworks generate --folder "My Jobs"
```

That's it! Cover letters will be in `./cover_letters/`

## 💻 Common Commands

```bash
# Generate from specific folder
waterworks generate --folder "My Jobs"

# Use Employer-Student Direct board instead of WaterlooWorks
waterworks generate --folder "Jobs" --job-board direct

# Regenerate all (skip existing check)
waterworks generate --force

# Preview without creating files
waterworks generate --dry-run

# View your config
waterworks config --show

# Update a config value
waterworks config --set llm.model gpt-4o
```

## 🔧 Platform Setup

**Windows:** PDF conversion works automatically

**macOS:** `brew install libreoffice`

**Linux:** `sudo apt-get install libreoffice`

## 🐛 Troubleshooting

**"Configuration file not found"** → Run `waterworks config`

**"API key required"** → Get key from your LLM provider, add to config or environment:
```bash
export OPENAI_API_KEY="sk-..."
```

**PDF conversion fails** → Install LibreOffice (see Platform Setup)

**Duo 2FA timeout** → You have 60 seconds to approve. Re-run if needed.

## 🛠️ For Developers

### Development Setup

```bash
git clone https://github.com/amanzav/waterworks.git
cd waterworks
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Workflow

1. Create branch: `git checkout -b feature/your-feature`
2. Make changes in `modules/`
3. Test: `python tests/run_all_tests.py`
4. Commit and push
5. Open PR

### Project Structure

```
modules/
├── auth.py                     # Waterloo Works login
├── cover_letter_generator.py  # LLM integration
├── pdf_builder.py              # PDF generation
└── ...
```

### Code Guidelines

- Follow PEP 8
- Add type hints and docstrings
- Handle exceptions specifically
- Test on multiple platforms

---

**Questions?** Open an [issue](https://github.com/amanzav/waterworks/issues)
