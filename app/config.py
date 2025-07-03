import os
import logging
from typing import List
from dataclasses import dataclass

@dataclass
class GeoParserConfig:
    """ GeoParser Configuration """
    # Model configurations
    transformer_model: str = "dguzh/geo-all-MiniLM-L6-v2"
    gazetteer: str = "geonames"
    available_model_sizes: List[str] = None

    # Supported languages
    supported_languages: List[str] = None

    # Model paths
    spacy_model_path: str = "/app/models/spacy"
    transformers_model_path: str = "/app/models/transformers"
    geonames_data_path: str = "/app/data/geonames"

    # API configurations
    max_text_length: int = 10000
    timeout: int = 30  # seconds
    enable_cache: bool = True
    max_batch_size: int = 100

    # Logging configurations
    log_level: str = "INFO"

    # Server configurations
    host: str = "0.0.0.0"
    port: int = 5000
    debug: bool = False

    def __post_init__(self):
        if self.supported_languages is None:
            self.supported_languages = ["en", "de", "fr", "zh", "es"]
        if self.available_model_sizes is None:
            self.available_model_sizes = ["sm", "md", "lg", "trf"]
    
    @property
    def default_model_size(self) -> str:
        """Get default model size (first available model size)"""
        return self.available_model_sizes[0] if self.available_model_sizes else "sm"

    def _validate_config(self):
        """ Validate configuration values """
        if self.max_text_length <= 0:
            raise ValueError("max_text_length must be positive")
        
        if self.max_batch_size <= 0:
            raise ValueError("max_batch_size must be positive")
        
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")
        
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level not in valid_log_levels:
            raise ValueError(f"log_level must be one of {valid_log_levels}")


def load_config() -> GeoParserConfig:
    """ Load configuration from environment or defaults """
    try:
        # Safe conversion of environment variables to integers
        def safe_int(value: str, default: int) -> int:
            try:
                return int(value)
            except (ValueError, TypeError):
                logging.warning(f"Invalid integer value for {value}, using default {default}")
                return default
            
        # Safe conversion of environment variables to boolean
        def safe_bool(value: str, default: bool) -> bool:
            if isinstance(value, str):
                return value.lower() in ("true", "1", "yes", "on")
            return default

        return GeoParserConfig(
            transformer_model=os.getenv("TRANSFORMER_MODEL", "dguzh/geo-all-MiniLM-L6-v2"),
            gazetteer=os.getenv("GAZETTEER", "geonames"),
            available_model_sizes=os.getenv("AVAILABLE_MODEL_SIZES", "sm,md,lg,trf").split(","),
            supported_languages=os.getenv("SUPPORTED_LANGUAGES", "en,de,fr,zh,es").split(","),
            spacy_model_path=os.getenv("SPACY_MODEL_PATH", "/app/models/spacy"),
            transformers_model_path=os.getenv("TRANSFORMERS_MODEL_PATH", "/app/models/transformers"),
            geonames_data_path=os.getenv("GEONAMES_DATA_PATH", "/app/data/geonames"),
            max_text_length=safe_int(os.getenv("MAX_TEXT_LENGTH", "10000"), 10000),
            timeout=safe_int(os.getenv("TIMEOUT", "30"), 30),
            enable_cache=safe_bool(os.getenv("ENABLE_CACHE", "true"), True),
            max_batch_size=safe_int(os.getenv("MAX_BATCH_SIZE", "100"), 100),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            host=os.getenv("HOST", "0.0.0.0"),
            port=safe_int(os.getenv("PORT", "5000"), 5000),
            debug=safe_bool(os.getenv("DEBUG", "false"), False)
        )
    
    except Exception as e:
        logging.error(f"Error loading configuration: {e}")
        return GeoParserConfig()  # Return default config on error