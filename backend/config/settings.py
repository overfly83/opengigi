import os
import dotenv
import yaml
from typing import Dict, Optional, Any

# Load environment variables
dotenv.load_dotenv()


class Settings:
    """Application settings class that loads from environment variables and YAML config"""
    
    def __init__(self):
        """Initialize settings from environment variables and YAML config"""
        # Basic settings
        self.HOST = os.getenv("HOST", "0.0.0.0")
        self.PORT = int(os.getenv("PORT", "8000"))
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "info")
        
        # Model provider settings
        self.MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "volcengine")
        
        # Load model configuration
        self.model_config = self._load_model_config()
        
        # Derive model settings from config
        self.OPENAI_API_KEY = self.model_config.get("api_key", os.getenv("OPENAI_API_KEY"))
        self.BASE_URL = self.model_config.get("base_url", os.getenv("BASE_URL"))
        self.MODEL_NAME = self.model_config.get("model_name", os.getenv("MODEL_NAME"))
        self.MODEL_TEMPERATURE = float(self.model_config.get("model_temperature", os.getenv("MODEL_TEMPERATURE", "0.3")))
        self.MODEL_TIMEOUT = int(self.model_config.get("timeout", "30"))
        self.MODEL_MAX_RETRIES = int(self.model_config.get("max_retries", "3"))
        
        # Other API keys
        self.TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    
    def _load_model_config(self) -> Dict[str, Any]:
        """Load model configuration from YAML file
        
        Returns:
            Dict[str, Any]: Model configuration dictionary
        """
        # Get config file path
        config_dir = os.path.dirname(__file__)
        config_path = os.path.join(config_dir, "model_config.yaml")
        
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                yaml_config = yaml.safe_load(f)
            
            # Get provider configuration
            provider = self.MODEL_PROVIDER
            providers = yaml_config.get("providers", {})
            
            if provider in providers:
                # Use specific provider config
                return providers[provider]
            else:
                # Use default provider
                default_provider = yaml_config.get("default_provider", "zhipu")
                if default_provider in providers:
                    return providers[default_provider]
                else:
                    # Return empty dict as last resort
                    return {}
        except Exception as e:
            # Return empty dict if config can't be loaded
            return {}


# Create global settings instance
settings = Settings()
