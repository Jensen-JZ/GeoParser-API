from flask import Flask, request, Response
import json
import logging
from typing import Dict, List, Any
from .service import GeoParserService
from .config import load_config

# Set up logging
logger = logging.getLogger(__name__)

app = Flask(__name__)
config = load_config()

# Initialize GeoParserService at startup
logger.info("Initializing GeoParserService...")
try:
    geo_service = GeoParserService(config)
    logger.info("GeoParserService initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize GeoParserService: {e}")
    geo_service = None

def get_geo_service():
    """Get GeoParserService instance"""
    global geo_service
    if geo_service is None:
        raise RuntimeError("GeoParserService is not available. Please check the logs for initialization errors.")
    return geo_service

def json_response(data, status_code=200):
    """Custom JSON response with forced UTF-8 and non-ASCII encoding"""
    response = Response(
        response=json.dumps(data, ensure_ascii=False, indent=2),
        status=status_code,
        mimetype='application/json; charset=utf-8'
    )
    return response

def validate_json_request(required_fields: List[str]) -> Dict:
    """ Validate JSON request data """
    if not request.is_json:
        return {'valid': False, 'error': 'Content-Type must be application/json'}
    
    data = request.get_json()
    if not data:
        return {'valid': False, 'error': 'Invalid JSON data'}
    
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return {'valid': False, 'error': f'Missing required fields: {missing_fields}'}
    
    return {'valid': True, 'data': data}

@app.route('/api/parse', methods=['POST'])
def parse_text():
    """ Parse text for geographical entities """
    try:
        # Validate the request JSON
        validation = validate_json_request(['text'])
        if not validation['valid']:
            return json_response({
                'success': False,
                'error': validation['error']
            }, 400)
        
        data = validation['data']
        text = data['text']
        languages = data.get('languages', None)
        model_size = data.get('model_size', None)
        
        # Validate that text is not empty
        if not text or not text.strip():
            return json_response({
                'success': False,
                'error': 'Text cannot be empty'
            }, 400)
        
        # Call the GeoParserService to parse the text
        service = get_geo_service()
        result = service.parse_text(
            text=text,
            languages=languages,
            model_size=model_size
        )
        
        # Return 200 if parsing was successful, otherwise 400
        status_code = 200 if result['success'] else 400
        return json_response(result, status_code)
        
    except RuntimeError as e:
        logger.error(f"Service not available: {str(e)}")
        return json_response({
            'success': False,
            'error': 'GeoParser service is not available',
            'locations': []
        }, 503)
    except Exception as e:
        logger.error(f"Error in parse_text endpoint: {str(e)}")
        return json_response({
            'success': False,
            'error': 'Internal server error',
            'locations': []
        }, 500)

@app.route('/api/parse/batch', methods=['POST'])
def parse_batch():
    """ Parse a batch of texts for geographical entities """
    try:
        # Validate the request JSON
        validation = validate_json_request(['texts'])
        if not validation['valid']:
            return json_response({
                'success': False,
                'error': validation['error']
            }, 400)
        
        data = validation['data']
        texts = data['texts']
        model_size = data.get('model_size', None)
        
        # Validate that texts is a list
        if not isinstance(texts, list):
            return json_response({
                'success': False,
                'error': 'texts must be a list'
            }, 400)
        
        # Validate that the texts list is not empty
        if not texts:
            return json_response({
                'success': False,
                'error': 'texts list cannot be empty'
            }, 400)
        
        # Validate batch size
        if len(texts) > config.max_batch_size:
            return json_response({
                'success': False,
                'error': f'Batch size too large. Maximum allowed: {config.max_batch_size}'
            }, 400)
        
        # Call the GeoParserService to parse the batch of texts
        service = get_geo_service()
        results = service.parse_batch(
            texts=texts,
            model_size=model_size
        )
        
        # Statistics for successful and failed parses
        success_count = sum(1 for result in results if result.get('success', False))
        total_count = len(results)
        
        return json_response({
            'success': True,
            'total_processed': total_count,
            'successful_parses': success_count,
            'failed_parses': total_count - success_count,
            'results': results
        }, 200)
        
    except RuntimeError as e:
        logger.error(f"Service not available: {str(e)}")
        return json_response({
            'success': False,
            'error': 'GeoParser service is not available'
        }, 503)
    except Exception as e:
        logger.error(f"Error in parse_batch endpoint: {str(e)}")
        return json_response({
            'success': False,
            'error': 'Internal server error'
        }, 500)

@app.route('/api/info', methods=['GET'])
def get_info():
    """ Get model information """
    try:
        service = get_geo_service()
        model_info = service.get_model_info()
        return json_response({
            'success': True,
            'info': model_info
        }, 200)
    except RuntimeError as e:
        logger.error(f"Service not available: {str(e)}")
        return json_response({
            'success': False,
            'error': 'GeoParser service is not available. Please check server logs for details.'
        }, 503)
    except Exception as e:
        logger.error(f"Error in get_info endpoint: {str(e)}")
        return json_response({
            'success': False,
            'error': 'Failed to retrieve model information'
        }, 500)

@app.route('/api/health', methods=['GET'])
def health_check():
    """ Health check endpoint """
    try:
        service = get_geo_service()
        health_status = service.health_check()
        status_code = 200 if health_status['status'] == 'healthy' else 503
        return json_response(health_status, status_code)
    except RuntimeError as e:
        logger.error(f"Service not available during health check: {str(e)}")
        return json_response({
            'status': 'unhealthy',
            'error': 'GeoParser service is not available'
        }, 503)
    except Exception as e:
        logger.error(f"Error in health_check endpoint: {str(e)}")
        return json_response({
            'status': 'unhealthy',
            'error': 'Health check failed'
        }, 503)

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """ Clear the cache of the GeoParserService """
    try:
        service = get_geo_service()
        result = service.clear_cache()
        status_code = 200 if result['success'] else 400
        return json_response(result, status_code)
    except RuntimeError as e:
        logger.error(f"Service not available: {str(e)}")
        return json_response({
            'success': False,
            'error': 'GeoParser service is not available'
        }, 503)
    except Exception as e:
        logger.error(f"Error in clear_cache endpoint: {str(e)}")
        return json_response({
            'success': False,
            'error': 'Failed to clear cache'
        }, 500)

@app.route('/api/languages', methods=['GET'])
def get_supported_languages():
    """ Get supported languages and model sizes """
    try:
        return json_response({
            'success': True,
            'supported_languages': config.supported_languages,
            'default_model_size': config.default_model_size,
            'available_model_sizes': config.available_model_sizes
        }, 200)
    except Exception as e:
        logger.error(f"Error in get_supported_languages endpoint: {str(e)}")
        return json_response({
            'success': False,
            'error': 'Failed to retrieve supported languages'
        }, 500)

@app.route('/', methods=['GET'])
def root():
    """ Root endpoint providing service information """
    return json_response({
        'service': 'GeoParser API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'parse': '/api/parse',
            'batch_parse': '/api/parse/batch',
            'info': '/api/info',
            'health': '/api/health',
            'clear_cache': '/api/cache/clear',
            'languages': '/api/languages'
        },
        'documentation': 'https://github.com/Jensen-JZ/GeoParser-API'
    }, 200)

@app.errorhandler(404)
def not_found(error):
    """ Handler for not found errors """
    return json_response({
        'success': False,
        'error': 'Endpoint not found',
        'available_endpoints': [
            '/api/parse',
            '/api/parse/batch',
            '/api/info',
            '/api/health',
            '/api/cache/clear',
            '/api/languages'
        ]
    }, 404)

@app.errorhandler(405)
def method_not_allowed(error):
    """ Handler for method not allowed errors """
    return json_response({
        'success': False,
        'error': 'Method not allowed for this endpoint'
    }, 405)

@app.errorhandler(500)
def internal_error(error):
    """ Handler for internal server errors """
    logger.error(f"Internal server error: {str(error)}")
    return json_response({
        'success': False,
        'error': 'Internal server error'
    }, 500)

# Set up logging for the application
if __name__ != '__main__':
    # Set up logging to use Gunicorn's error logger
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

if __name__ == '__main__':
    # Execute the application with Flask's built-in server
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    app.run(host=config.host, port=config.port, debug=config.debug)