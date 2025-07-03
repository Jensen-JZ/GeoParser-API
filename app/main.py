import logging
from .api import app
from .config import load_config

def setup_logging(log_level: str):
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )

if __name__ == "__main__":
    config = load_config()
    setup_logging(config.log_level)
    app.run(host=config.host, port=config.port, debug=config.debug)