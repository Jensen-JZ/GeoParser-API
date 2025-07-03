import os 
import io
import logging
import time
from contextlib import redirect_stdout, redirect_stderr
from typing import Dict, List, Optional, Union
from geoparser import Geoparser
import numpy as np

from .utils import map_to_spacy_model, extract_location_data
from .config import GeoParserConfig

logger = logging.getLogger(__name__)

class GeoParserService:
    """
    GeoParser Service for parsing geographic information from text.
    """
    def __init__(self, config: GeoParserConfig):
        """
        Initialize the GeoParserService with configuration.

        Parameters:
        - config: GeoParserConfig object containing configuration settings.
        """
        self.config = config
        self.nlp_models: Dict[str, Geoparser] = {}
        self._cache: Dict[str, Dict] = {} if config.enable_cache else None

        # Pre-load models if necessary
        self._load_models()

    def _load_models(self):
        """
        Pre-load Spacy and Transformer models based on the configuration.
        """
        logger.info("Start to pre-load spaCy models...")

        successful_models = 0
        failed_models = []

        for lang in self.config.supported_languages:
            try:
                lang_code, model_name = map_to_spacy_model(
                    [lang],
                    model_size=self.config.default_model_size
                )

                logger.info(f"Loading model for language '{lang_code}' with model name '{model_name}'")

                # Load the model without timeout control (signal doesn't work in Flask threads)
                self.nlp_models[lang_code] = Geoparser(
                    spacy_model=model_name,
                    transformer_model=self.config.transformer_model,
                    gazetteer=self.config.gazetteer
                )
                successful_models += 1
                logger.info(f"Model for language '{lang_code}' loaded successfully.")

                logger.info(f"Successfully loaded model for language '{lang_code}'")
            
            except Exception as e:
                logger.error(f"Failed to load model for language '{lang}': {e}")
                failed_models.append(lang)
                continue

        logger.info(f"Finished pre-loading spaCy models, successful: {successful_models}/{len(self.config.supported_languages)} languages: {list(self.nlp_models.keys())}")

        if successful_models == 0:
            raise RuntimeError("No models were successfully loaded. Please check your configuration and model paths.")
        
        if failed_models:
            logger.warning(f"Failed to load models for the following languages: {', '.join(failed_models)}. Please check your model paths and configurations.")

    def _get_cache_key(self, text:str, lang_code: str, model_size: str) -> str:
        """
        Generate a cache key based on the input text, language code, and model size.
        """
        import hashlib
        key_string = f"{text}_{lang_code}_{model_size}"
        return hashlib.md5(key_string.encode()).hexdigest()

    def _validate_input(self, text: str, languages: Optional[Union[List[str], str]], model_size: str) -> Dict:
        """
        Validate the input parameters and return a dictionary with validated values.
        Note: model_size validation is now handled in parse_text method before calling this.
        """
        if not text or not text.strip():
            return {
                "valid": False,
                "error": "Input text is empty or invalid."
            }
        
        if len(text) > self.config.max_text_length:
            return {
                "valid": False,
                "error": f"Input text exceeds maximum length of {self.config.max_text_length} characters."
            }
        
        return {"valid": True}

    def parse_text(
            self,
            text: str, 
            languages: Optional[Union[List[str], str]] = None, 
            model_size: Optional[str] = None,
    ) -> Dict:
        """
        Parse geographic information from the input text.

        Parameters:
        - text: The input text to parse.
        - languages: Optional list of language codes to use for parsing. If None, uses default languages.
        - model_size: Optional model size to use for parsing. If None, uses the default model size from configuration.

        Returns:
        - A dictionary containing the parsed geographic information, or an error message if parsing fails.
        """
        start_time = time.time()

        # Use default model size if not provided
        if model_size is None:
            model_size = self.config.default_model_size
        
        # Check if model_size is supported, fallback to first available if not
        if model_size not in self.config.available_model_sizes:
            fallback_model_size = self.config.available_model_sizes[0] if self.config.available_model_sizes else 'sm'
            logger.warning(f"Model size '{model_size}' not supported. Using default '{fallback_model_size}' model size.")
            model_size = fallback_model_size

        # Validate input parameters (text length check only, since model_size is already handled)
        validation = self._validate_input(text, languages, model_size)
        if not validation["valid"]:
            return {
                'success': False,
                'error': validation["error"],
                'locations': [],
                'processing_time': time.time() - start_time
            }
        
        # Determine language code
        if isinstance(languages, str):
            languages = [languages]

        lang_code, model_name = map_to_spacy_model(languages, model_size=model_size)

        # Check cache
        if self._cache is not None:
            cache_key = self._get_cache_key(text, lang_code, model_size)
            if cache_key in self._cache:
                logger.debug(f"Cache hit for key: {cache_key[:8]}...")
                cached_result = self._cache[cache_key].copy()
                cached_result['from_cache'] = True
                cached_result['processing_time'] = time.time() - start_time
                return cached_result
            
        # Check if the model is valid
        if lang_code not in self.nlp_models:
            # Use the first supported language as fallback instead of hardcoded 'en'
            fallback_lang = self.config.supported_languages[0] if self.config.supported_languages else 'en'
            logger.warning(f"Language '{lang_code}' not supported or model not loaded. Using default '{fallback_lang}' model.")
            lang_code = fallback_lang
            # Update model_name to match the fallback language
            _, model_name = map_to_spacy_model([lang_code], model_size=model_size)

            if lang_code not in self.nlp_models:
                return {
                    'success': False,
                    'error': f"No model available for language '{lang_code}'.",
                    'locations': [],
                    'processing_time': time.time() - start_time
                }
            
        try:
            # Excute parsing with context management for stdout/stderr
            parse_start = time.time()
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                doc = self.nlp_models[lang_code].parse([text])
            parse_time = time.time() - parse_start

            # Extract locations from the parsed document
            locations = []
            if doc and len(doc) > 0 and hasattr(doc[0], 'locations') and doc[0].locations:
                for location in doc[0].locations:
                    location_data = extract_location_data(location)
                    if location_data:
                        locations.append(location_data)

            result = {
                'success': True,
                'language_detected': lang_code,
                'model_used': model_name,
                'text_length': len(text),
                'locations_found': len(locations),
                'locations': locations,
                'processing_time': time.time() - start_time,
                'parse_time': parse_time,
                'from_cache': False
            }

            # Cache the result if caching is enabled
            if self._cache is not None and len(self._cache) < 1000:  # Limit cache size to 1000 entries
                cache_key = self._get_cache_key(text, lang_code, model_size)
                self._cache[cache_key] = {k: v for k, v in result.items() if k != 'processing_time'}

            return result

        except Exception as e:
            logger.error(f"Error parsing text: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'language_detected': lang_code,
                'locations': [],
                'processing_time': time.time() - start_time
            }


    def parse_batch(
        self, 
        texts: List[Dict],
        model_size: Optional[str] = None,
    ) -> List[Dict]:
        """
        Parse geographic information from a batch of input texts.

        Parameters:
        - texts: A list of input texts to parse.
        - model_size: Optional model size to use for parsing. If None, uses the default

        Returns:
        - A list of dictionaries, each containing the parsed geographic information for the corresponding text.
        """
        if len(texts) > self.config.max_batch_size:
            return [{
                'success': False,
                'error': f"Batch size exceeds maximum limit of {self.config.max_batch_size}.",
                'locations': []
            }]
        
        results = []

        for item in texts:
            if not isinstance(item, dict) or 'text' not in item:
                results.append({
                    'success': False,
                    'error': 'Invalid input format - missing text field',
                    'locations': []
                })
                continue
            
            text = item['text']
            languages = item.get('languages', None)
            item_id = item.get('id', None)
            
            result = self.parse_text(text, languages, model_size)
            
            # 添加原始 ID 信息
            if item_id is not None:
                result['id'] = item_id
            
            results.append(result)
        
        return results

    def get_model_info(self) -> Dict:
        """
        Get information about the loaded models.
        """
        return {
            'loaded_models': list(self.nlp_models.keys()),
            'default_model_size': self.config.default_model_size,
            'transformer_model': self.config.transformer_model,
            'gazetteer': self.config.gazetteer,
            'supported_languages': self.config.supported_languages,
            'cache_enabled': self.config.enable_cache,
            'cache_size': len(self._cache) if self._cache else 0,
            'max_text_length': self.config.max_text_length,
            'max_batch_size': self.config.max_batch_size
        }

    def health_check(self) -> Dict:
        """
        Health check for the GeoParser service.
        """
        try:
            # Simply check if the service is running by accessing the models
            test_result = self.parse_text("I want to travel to Beijing!", ['en'])

            return {
                'status': 'healthy',
                'models_loaded': len(self.nlp_models),
                'test_parse_success': test_result['success'],
                'config_valid': True
            }

        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'models_loaded': len(self.nlp_models),
                'config_valid': False
            }

    def clear_cache(self) -> Dict:
        """
        Clear the cache if caching is enabled.
        """
        if self._cache is not None:
            cache_size = len(self._cache)
            self._cache.clear()
            return {
                'success': True,
                'message': f"Cache cleared successfully. Removed {cache_size} entries.",
            }
        else:
            return {
                'success': False,
                'message': "Caching is not enabled. No cache to clear."
            }