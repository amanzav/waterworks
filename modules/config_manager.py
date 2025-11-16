"""Configuration Manager for Waterworks CLI"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """Handle loading, validation, and access to Waterworks configuration"""
    
    DEFAULT_CONFIG_PATH = Path.home() / ".waterworks" / "config.yaml"
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize config manager
        
        Args:
            config_path: Path to config file (defaults to ~/.waterworks/config.yaml)
        """
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.config: Dict[str, Any] = {}
        
    def load(self) -> Dict[str, Any]:
        """Load configuration from file
        
        Returns:
            Dictionary containing configuration
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is invalid
        """
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found at {self.config_path}\n"
                f"Run 'python setup.py' to create your configuration."
            )
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f) or {}
        
        return self.config
    
    def save(self, config: Dict[str, Any]) -> None:
        """Save configuration to file
        
        Args:
            config: Configuration dictionary to save
        """
        # Ensure directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        
        self.config = config
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation
        
        Args:
            key_path: Path to config value (e.g., "llm.provider")
            default: Default value if key doesn't exist
            
        Returns:
            Configuration value or default
            
        Example:
            config.get("llm.provider", "openai")
            config.get("profile.resume_pdf")
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any) -> None:
        """Set a configuration value using dot notation
        
        Args:
            key_path: Path to config value (e.g., "llm.provider")
            value: Value to set
            
        Example:
            config.set("llm.provider", "anthropic")
        """
        keys = key_path.split('.')
        config = self.config
        
        # Navigate to parent
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # Set final value
        config[keys[-1]] = value
    
    def validate(self) -> tuple[bool, list[str]]:
        """Validate configuration has required fields
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required profile fields
        if not self.get("profile.resume_pdf"):
            errors.append("profile.resume_pdf is required")
        
        # Check resume file exists
        resume_path = self.get("profile.resume_pdf")
        if resume_path and not Path(resume_path).exists():
            errors.append(f"Resume file not found: {resume_path}")
        
        # Check Waterloo Works username
        if not self.get("waterloo_works.username"):
            errors.append("waterloo_works.username is required")
        
        # Check LLM configuration
        if not self.get("llm.provider"):
            errors.append("llm.provider is required")
        
        if not self.get("llm.model"):
            errors.append("llm.model is required")
        
        # Check API key (either in config or environment)
        provider = self.get("llm.provider", "").lower()
        
        # Try both old location (llm.api_key) and new location (llm.api_keys.{provider})
        api_key = self.get("llm.api_key") or self.get(f"llm.api_keys.{provider}")
        
        env_key_map = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "gemini": "GOOGLE_API_KEY",
            "groq": "GROQ_API_KEY"
        }
        
        env_var = env_key_map.get(provider)
        if not api_key and not (env_var and os.getenv(env_var)):
            errors.append(
                f"API key required for {provider}. "
                f"Set llm.api_keys.{provider} in config or {env_var} environment variable"
            )
        
        return (len(errors) == 0, errors)
    
    def get_api_key(self, provider: Optional[str] = None) -> Optional[str]:
        """Get API key for specified provider
        
        Args:
            provider: LLM provider name (defaults to config provider)
            
        Returns:
            API key from config or environment variable
        """
        if provider is None:
            provider = self.get("llm.provider", "").lower()
        
        # Check new location first: llm.api_keys.{provider}
        api_key = self.get(f"llm.api_keys.{provider}")
        if api_key:
            return api_key
        
        # Check old location for backwards compatibility: llm.api_key
        api_key = self.get("llm.api_key")
        if api_key:
            return api_key
        
        # Check environment variables
        env_key_map = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "gemini": "GOOGLE_API_KEY",
            "groq": "GROQ_API_KEY"
        }
        
        env_var = env_key_map.get(provider)
        if env_var:
            return os.getenv(env_var)
        
        return None
    
    def get_credentials(self) -> tuple[str, Optional[str]]:
        """Get Waterloo Works credentials
        
        Returns:
            Tuple of (username, password or None)
        """
        username = self.get("waterloo_works.username", "")
        password = self.get("waterloo_works.password", "")
        
        return (username, password if password else None)
    
    def get_cover_letters_dir(self) -> Path:
        """Get cover letters directory path
        
        Returns:
            Path object for cover letters directory
        """
        dir_path = self.get("paths.cover_letters_dir", "./cover_letters")
        path = Path(dir_path).expanduser()
        
        # Create directory if it doesn't exist
        path.mkdir(parents=True, exist_ok=True)
        
        return path
    
    def get_default_folder(self) -> str:
        """Get default Waterloo Works folder name
        
        Returns:
            Default folder name
        """
        return self.get("defaults.folder_name", "waterworks")
    
    def get_default_job_board(self) -> str:
        """Get default job board type from config
        
        Returns:
            Default job board type ('full' or 'direct')
        """
        return self.get("defaults.job_board", "full")
    
    def get_signature(self) -> Optional[str]:
        """Get signature for cover letters
        
        Returns:
            Signature string or None if not set
        """
        return self.get("profile.signature", None)
    
    def get_headless(self) -> bool:
        """Get browser headless mode setting
        
        Returns:
            True if headless mode enabled, False otherwise
        """
        return self.get("browser.headless", False)
    
    def get_user_profile(self) -> Dict[str, str]:
        """Get user profile information for cover letter headers
        
        Returns:
            Dictionary containing user profile data
        """
        return {
            "name": self.get("profile.name", ""),
            "email": self.get("profile.email", ""),
            "phone": self.get("profile.phone", ""),
            "linkedin": self.get("profile.linkedin", ""),
            "github": self.get("profile.github", ""),
            "website": self.get("profile.website", ""),
        }
    
    def get_template_path(self) -> Optional[Path]:
        """Get path to user's cover letter template
        
        Returns:
            Path to template DOCX file, or None if not set
        """
        template = self.get("profile.cover_letter_template")
        if template:
            path = Path(template).expanduser()
            if path.exists():
                return path
        
        # Fall back to default template if it exists
        default_template = Path(__file__).parent.parent / "templates" / "template.docx"
        if default_template.exists():
            return default_template
        
        return None
