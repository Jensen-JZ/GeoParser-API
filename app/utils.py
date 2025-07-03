import numpy as np
import logging
from typing import Union, List, Tuple, Optional

logger = logging.getLogger(__name__)

def map_to_spacy_model(
        lang_code: Union[List, np.ndarray, None],
        model_size: str = "sm",
        default: str = "en_core_web_sm"
) -> Tuple[str, str]:
    """
    Map language codes to Spacy model names.
    """
    # Handle None, empty list or empty numpy array
    if lang_code is None or (hasattr(lang_code, '__len__') and len(lang_code) == 0):
        return 'en', '_'.join(default.split('_')[:3] + [model_size])
    
    # Convert to list if it's a numpy array
    if isinstance(lang_code, np.ndarray):
        lang_code = lang_code.tolist()

    # If not a list or already processed as a list
    if not isinstance(lang_code, list):
        return 'en', '_'.join(default.split('_')[:3] + [model_size])
    
    if len(lang_code) > 1:
        logger.warning(f"Multiple language codes provided: {lang_code}. Using the first one.")

    lang_code = lang_code[0]

    # Normalize language code
    code = lang_code.strip().lower()

    # Map language code to standard langeage code
    # Common incorrect / non-standard language codes mapping to standard ISO codes
    custom_map = {
        'jp': 'ja',
        'cn': 'zh',
        'zh-cn': 'zh', 'zh-tw': 'zh', 'zh-hk': 'zh',
        'en-us': 'en', 'en-gb': 'en', 'en-ca': 'en', 'en-au': 'en', 'en-nz': 'en',
        'fr-ca': 'fr', 'fr-be': 'fr', 'fr-fr': 'fr', 'fr-ch': 'fr',
        'de-de': 'de', 'de-ch': 'de', 'de-at': 'de',
        'es-es': 'es', 'es-mx': 'es', 'es-ar': 'es', 'es-co': 'es', 'es-pr': 'es',
        'nl-be': 'nl', 'nl-nl': 'nl',
        'pt-br': 'pt', 'pt-pt': 'pt',
        'sv-se': 'sv', 'sv-fi': 'sv',
        'it-it': 'it', 'it-ch': 'it',
        'ro-ro': 'ro', 'pl-pl': 'pl', 'da-dk': 'da',
    }

    # Apply custom mapping or extract the first part of the code
    code = custom_map.get(code, code.split('-')[0])

    # Map to Spacy model name
    spacy_models = {
        'ca': 'ca_core_news_',
        'zh': 'zh_core_web_',
        'hr': 'hr_core_news_',
        'da': 'da_core_news_',
        'nl': 'nl_core_news_',
        'en': 'en_core_web_',
        'fi': 'fi_core_news_',
        'fr': 'fr_core_news_',
        'de': 'de_core_news_',
        'el': 'el_core_news_',
        'it': 'it_core_news_',
        'ja': 'ja_core_news_',
        'ko': 'ko_core_news_',
        'lt': 'lt_core_news_',
        'mk': 'mk_core_news_',
        'nb': 'nb_core_news_',
        'pl': 'pl_core_news_',
        'pt': 'pt_core_news_',
        'ro': 'ro_core_news_',
        'ru': 'ru_core_news_',
        'sl': 'sl_core_news_',
        'es': 'es_core_news_',
        'sv': 'sv_core_news_',
        'uk': 'uk_core_news_',
    }

    # If the language code is not in the mapping, use the default model
    if code not in spacy_models:
        code = 'en'

    # Supported languages for transformer models
    trf_supported_langs = {'ca', 'zh', 'da', 'en', 'ja', 'sl', 'uk'}

    # Determine the final model size
    actual_model_size = model_size
    if model_size == 'trf' and code not in trf_supported_langs:
        logger.warning(f"Transformer model size '{model_size}' is not supported for language '{code}'. Using 'lg'.")
        actual_model_size = 'lg'

    # Construct the full model name
    model_name = spacy_models[code] + actual_model_size

    return code, model_name


def extract_location_data(location) -> Optional[dict]:
    """
    Extract geographic information from a location object.
    """
    if location is None:
        return None
    
    # Check if location is a dictionary
    if not isinstance(location, dict):
        location_dict = {}
        try:
            # Attempt to convert the location object to a dictionary
            if hasattr(location, '__dict__'):
                location_dict = location.__dict__
            # If location is an object with attributes
            elif hasattr(location, '__getitem__'):
                # Attempt to extract common geographic keys
                for key in ['name', 'geonameid', 'feature_type', 'latitude', 'longitude']:
                    try:
                        location_dict[key] = location[key]
                    except (KeyError, TypeError):
                        pass
        except Exception:
            return None
        location = location_dict
    
    # Extract standardized geographic information
    return {
        'name': location.get('name', None),
        'geonameid': location.get('geonameid', None),
        'feature_type': location.get('feature_type', None),
        'latitude': location.get('latitude', None),
        'longitude': location.get('longitude', None),
        'elevation': location.get('elevation', None),
        'population': location.get('population', None),
        'admin2_name': location.get('admin2_name', None),
        'admin1_name': location.get('admin1_name', None),
        'country_name': location.get('country_name', None)
    }