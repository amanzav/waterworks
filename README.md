# 🦆 Geese - CLI Cover Letter Generator

Automate cover letter generation for Waterloo Works job applications using AI.

## ✨ Features

- **🤖 AI-Powered**: Generate personalized cover letters using OpenAI, Anthropic, Gemini, or Groq
- **📁 Folder-Based**: Process all jobs from a Waterloo Works folder
- **⚡ Fast**: Skip already-generated cover letters, generate only what's needed
- **🔐 Secure**: Duo 2FA authentication, credentials stored locally
- **📄 PDF Output**: Professional PDF cover letters ready to upload
- **🎯 Simple CLI**: Easy-to-use command-line interface

## 📋 Prerequisites

- Python 3.9+
- University of Waterloo email and Waterloo Works access
- Duo Mobile for 2FA
- API key for your chosen LLM provider:
  - [OpenAI API Key](https://platform.openai.com/api-keys) (recommended)
  - [Anthropic API Key](https://console.anthropic.com/)
  - [Google AI Studio](https://makersuite.google.com/app/apikey)
  - [Groq API Key](https://console.groq.com/)
- Google Chrome browser

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/amanzav/geese.git
cd geese/v2
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note for Windows users**: If `docx2pdf` installation fails, you may need:
```bash
pip install pywin32
```

### 3. Run Setup Wizard

```bash
python setup.py
```

The setup wizard will guide you through:
- Providing your resume PDF
- Setting Waterloo Works credentials
- Choosing an LLM provider and model
- Configuring output directories

This creates a config file at `~/.geese/config.yaml`

### 4. Save Jobs on Waterloo Works

1. Log into [Waterloo Works](https://waterlooworks.uwaterloo.ca)
2. Browse jobs and save desired positions to a folder (e.g., "geese")

### 5. Generate Cover Letters

```bash
python geese.py generate --folder geese
```

This will:
- Log you into Waterloo Works (with Duo 2FA)
- Extract all jobs from your folder
- Generate personalized cover letters using AI
- Save PDFs in `./cover_letters/`

## 📖 Usage

### Generate Cover Letters

```bash
# Generate for default folder (from config)
python geese.py generate

# Generate for specific folder
python geese.py generate --folder my_jobs

# Force regenerate all (even if they exist)
python geese.py generate --folder my_jobs --force

# Preview what would be generated
python geese.py generate --folder my_jobs --dry-run
```

### Manage Configuration

```bash
# Show current configuration
python geese.py config --show

# Update a config value
python geese.py config --set llm.model gpt-4o
python geese.py config --set defaults.folder_name my_folder
```

### Get Help

```bash
python geese.py --help
python geese.py generate --help
python geese.py config --help
```

## ⚙️ Configuration

Your configuration is stored at `~/.geese/config.yaml`. You can edit it directly or use the `config` command.

### Key Configuration Options

```yaml
profile:
  resume_pdf: "/path/to/resume.pdf"
  resume_text: "Your resume text (auto-extracted)"
  additional_info: "Extra details not in resume"

waterloo_works:
  username: "your.email@uwaterloo.ca"
  password: ""  # Leave empty for security

llm:
  provider: "openai"  # openai | anthropic | gemini | groq
  model: "gpt-4o-mini"
  api_key: ""  # Or set environment variable

paths:
  cover_letters_dir: "./cover_letters"

defaults:
  folder_name: "geese"
```

### LLM Provider Options

| Provider | Recommended Model | Cost | Speed |
|----------|------------------|------|-------|
| OpenAI | `gpt-4o-mini` | 💰 Low | ⚡ Fast |
| Anthropic | `claude-3-5-haiku-20241022` | 💰 Medium | ⚡ Fast |
| Gemini | `gemini-1.5-flash` | 💰 Very Low/Free | ⚡ Very Fast |
| Groq | `llama-3.1-8b-instant` | 💰 Free | ⚡⚡ Blazing Fast |

### Environment Variables

For better security, use environment variables for API keys:

```bash
# Add to your .bashrc, .zshrc, or .env file
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_API_KEY="..."
export GROQ_API_KEY="gsk_..."
```

## 📂 Output

Cover letters are saved as PDFs in your configured output directory (default: `./cover_letters/`):

```
cover_letters/
├── Microsoft_Software_Engineer_Intern.pdf
├── Google_SWE_Intern.pdf
├── Amazon_Software_Development_Engineer_Intern.pdf
└── ...
```

Naming format: `{Company}_{JobTitle}.pdf`

## 🔧 Troubleshooting

### "Configuration file not found"
Run `python setup.py` to create your configuration.

### "Resume file not found"
Check that the `resume_pdf` path in your config points to a valid PDF file.

### "API key required"
Set your API key in the config file or as an environment variable for your chosen provider.

### PDF Conversion Fails (Windows)
Install Microsoft Word or ensure `pywin32` is installed:
```bash
pip install pywin32
```

### PDF Conversion Fails (Mac/Linux)
Install LibreOffice:
```bash
# Mac
brew install libreoffice

# Ubuntu/Debian
sudo apt-get install libreoffice
```

### Duo 2FA Timeout
The script waits 60 seconds for Duo approval. If you timeout, just run the command again.

### Chrome Driver Issues
Make sure Google Chrome is installed. The script will automatically download the correct ChromeDriver.

### Empty Resume Text
If PDF extraction fails during setup, manually add your resume text to `~/.geese/config.yaml` under `profile.resume_text`.

## 🎯 Tips

1. **Test with Dry Run**: Use `--dry-run` to preview before generating
2. **Start Small**: Test with a folder containing 2-3 jobs first
3. **Review Output**: Always review generated cover letters before submitting
4. **Customize Profile**: Add specific skills/interests in `additional_info`
5. **Save API Costs**: Use `--force` sparingly - it regenerates everything

## 📁 Project Structure

```
v2/
├── geese.py                    # Main CLI entry point
├── setup.py                    # Interactive setup wizard
├── requirements.txt            # Python dependencies
├── config.yaml.template        # Configuration template
├── README.md                   # This file
├── PRD.md                      # Product requirements
│
└── modules/
    ├── __init__.py
    ├── auth.py                 # Waterloo Works authentication
    ├── config_manager.py       # Configuration handling
    ├── cover_letter_generator.py  # LLM-based generation
    ├── folder_navigator.py     # Folder navigation & job extraction
    ├── job_extractor.py        # Job detail scraping
    ├── pdf_builder.py          # PDF creation
    └── utils.py                # Selenium utilities
```

## 🤝 Contributing

This is a personal project, but suggestions and bug reports are welcome! Open an issue on GitHub.

## 📄 License

MIT License - feel free to use and modify for your own job search!

## ⚠️ Disclaimer

This tool is for personal use only. Always review generated cover letters before submitting. The author is not responsible for the content of generated cover letters or any consequences of using this tool.

## 🙏 Acknowledgments

- Built for University of Waterloo co-op students
- Inspired by the tedious process of writing 50+ unique cover letters

---

**Good luck with your job search! 🦆✨**
