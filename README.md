# GeoParser API

**语言 / Languages**: [English](#english) | [中文](#中文)

---

## English

# GeoParser API

## Overview

The GeoParser API is a powerful service designed to extract and disambiguate geographic entities (like cities, countries, and other locations) from text. It leverages state-of-the-art NLP models to provide accurate location recognition across multiple languages. This service is containerized using Docker for easy deployment and scalability.

## Features

*   **Named Entity Recognition (NER) for Locations:** Identifies geographic names in text.
*   **Multi-Language Support:** Configurable to support various languages (e.g., English, German, French, Chinese, Spanish).
*   **Flexible Model Selection:** Supports different SpaCy model sizes (sm, md, lg, trf) to balance performance and resource usage.
*   **Transformer-Based Models:** Utilizes transformer models for enhanced accuracy.
*   **Gazetteer Integration:** Uses GeoNames for disambiguation and rich location data.
*   **Dockerized:** Easy to deploy and manage using Docker and Docker Compose.
*   **Batch Processing:** Efficiently parse multiple texts in a single API call.
*   **Caching:** In-memory caching for frequently requested texts to improve response times.
*   **Health Check Endpoint:** Provides a health status for monitoring.
*   **GPU Support:** Can leverage NVIDIA GPUs for accelerated processing.
*   **Comprehensive Configuration:** Highly configurable via environment variables.

## Tech Stack

*   **Backend:** `Python`, `Flask`
*   **NLP Libraries:**
    *   `geoparser` (core library)
    *   `SpaCy`
    *   `Transformers` (Hugging Face)
    *   `PyTorch`
*   **Containerization:** `Docker`, `Docker Compose`
*   **WSGI Server:** `Gunicorn`

## Supported Models

The GeoParser API supports a wide range of SpaCy language models for geographic entity recognition. The service currently supports **24 languages** with different model configurations:

### Language Support Overview

| Language | Code | Model Pattern | Available Sizes | TRF Support | Notes |
|----------|------|---------------|----------------|-------------|-------|
| Catalan | `ca` | `ca_core_news_{size}` | sm, md, lg, trf | ✅ | |
| Chinese | `zh` | `zh_core_web_{size}` | sm, md, lg, trf | ✅ | Web-based model |
| Croatian | `hr` | `hr_core_news_{size}` | sm, md, lg | ❌ | |
| Danish | `da` | `da_core_news_{size}` | sm, md, lg | ❌ | |
| Dutch | `nl` | `nl_core_news_{size}` | sm, md, lg | ❌ | |
| English | `en` | `en_core_web_{size}` | sm, md, lg, trf | ✅ | Web-based model |
| Finnish | `fi` | `fi_core_news_{size}` | sm, md, lg | ❌ | |
| French | `fr` | `fr_core_news_{size}` | sm, md, lg | ⚠️ | TRF: `fr_dep_news_trf` (dependency parsing only) |
| German | `de` | `de_core_news_{size}` | sm, md, lg | ⚠️ | TRF: `de_dep_news_trf` (dependency parsing only) |
| Greek | `el` | `el_core_news_{size}` | sm, md, lg | ❌ | |
| Italian | `it` | `it_core_news_{size}` | sm, md, lg | ❌ | |
| Japanese | `ja` | `ja_core_news_{size}` | sm, md, lg, trf | ✅ | |
| Korean | `ko` | `ko_core_news_{size}` | sm, md, lg | ❌ | |
| Lithuanian | `lt` | `lt_core_news_{size}` | sm, md, lg | ❌ | |
| Macedonian | `mk` | `mk_core_news_{size}` | sm, md, lg | ❌ | |
| Norwegian | `nb` | `nb_core_news_{size}` | sm, md, lg | ❌ | |
| Polish | `pl` | `pl_core_news_{size}` | sm, md, lg | ❌ | |
| Portuguese | `pt` | `pt_core_news_{size}` | sm, md, lg | ❌ | |
| Romanian | `ro` | `ro_core_news_{size}` | sm, md, lg | ❌ | |
| Russian | `ru` | `ru_core_news_{size}` | sm, md, lg | ❌ | |
| Slovenian | `sl` | `sl_core_news_{size}` | sm, md, lg, trf | ✅ | |
| Spanish | `es` | `es_core_news_{size}` | sm, md, lg | ⚠️ | TRF: `es_dep_news_trf` (dependency parsing only) |
| Swedish | `sv` | `sv_core_news_{size}` | sm, md, lg | ❌ | |
| Ukrainian | `uk` | `uk_core_news_{size}` | sm, md, lg, trf | ✅ | |

### Model Size Recommendations

- **sm (Small)**: Fastest, minimal memory usage, good for basic NER
- **md (Medium)**: Balanced performance and accuracy - **Recommended for most use cases**
- **lg (Large)**: Higher accuracy, more memory intensive
- **trf (Transformer)**: Highest accuracy but **not recommended** for geo-parsing due to limited availability and compatibility issues

> **⚠️ Important Note**: While some languages have `trf` (transformer) models available, we **do not recommend** using the `trf` size for geographic entity recognition. Languages like German, French, and Spanish only have dependency parsing transformer models (`xx_dep_news_trf`) which cannot perform named entity recognition required for geo-parsing.

### Model Naming Convention

The service follows SpaCy's standard naming convention:
- **English & Chinese**: Use `xx_core_web_{size}` (web-trained models)
- **All other languages**: Use `xx_core_news_{size}` (news-trained models)

Where `xx` is the ISO 639-1 language code and `{size}` is one of: `sm`, `md`, `lg`, `trf`.

## Prerequisites

*   [Git](https://git-scm.com/downloads)
*   [Docker](https://docs.docker.com/get-docker/)
*   [Docker Compose](https://docs.docker.com/compose/install/) (usually included with Docker Desktop)
*   A shell environment (like Bash, Zsh, PowerShell).
*   (Optional) For GPU support:
    *   NVIDIA GPU drivers
    *   [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

## Setup and Installation

1.  **Clone the Repository:**
    ```bash
    git clone <repository-url>
    cd GeoParser-API
    ```

2.  **Configure Environment:**
    Create a `.env` file in the root of the project. You can copy the structure from the example below or from the existing `.env` file if you pulled it from a source that included it (though it's often gitignored).
    A minimal `.env.example` would look like this:
    ```env
    # GeoParser API Configuration

    # --------------------------------------------------------------------------
    # Model Configuration
    # --------------------------------------------------------------------------
    # Transformer model for embeddings (from Hugging Face Model Hub)
    TRANSFORMER_MODEL=dguzh/geo-all-MiniLM-L6-v2
    # Gazetteer to use (geonames is standard for geoparser)
    GAZETTEER=geonames
    # Available SpaCy model sizes (e.g., sm, md, lg, trf for transformer models)
    # The setup_models.sh script will try to download models for these sizes for each supported language.
    # The first size in this list will be used as the default if not specified in API calls.
    AVAILABLE_MODEL_SIZES=md,sm

    # --------------------------------------------------------------------------
    # Supported Languages
    # --------------------------------------------------------------------------
    # Comma-separated list of ISO 639-1 language codes (e.g., en, de, fr, zh, es)
    # The setup_models.sh script will download models for these languages.
    SUPPORTED_LANGUAGES=en,de

    # --------------------------------------------------------------------------
    # Model and Data Paths (within the Docker container)
    # These should generally not be changed unless you modify docker-compose.yml volume mounts.
    # --------------------------------------------------------------------------
    SPACY_MODEL_PATH=/app/models/spacy
    TRANSFORMERS_MODEL_PATH=/app/models/transformers # Currently not used for pre-downloaded custom transformers, but reserved.
    GEONAMES_DATA_PATH=/app/data/geonames

    # --------------------------------------------------------------------------
    # API Configuration
    # --------------------------------------------------------------------------
    MAX_TEXT_LENGTH=10000  # Maximum characters for input text
    TIMEOUT=30             # Request timeout in seconds
    ENABLE_CACHE=true      # Enable/disable in-memory cache
    MAX_BATCH_SIZE=100     # Maximum items in a batch request

    # --------------------------------------------------------------------------
    # Logging Configuration
    # --------------------------------------------------------------------------
    LOG_LEVEL=INFO # DEBUG, INFO, WARNING, ERROR, CRITICAL

    # --------------------------------------------------------------------------
    # Server Configuration (for Flask/Gunicorn)
    # --------------------------------------------------------------------------
    HOST=0.0.0.0
    PORT=5000
    DEBUG=false # Set to true for Flask debug mode (not recommended for Gunicorn production)

    # Gunicorn worker settings (see docker-compose.yml command for how these are used)
    WORKERS=2
    WORKER_TIMEOUT=600
    WORKER_CLASS=sync # or 'gthread', 'eventlet', 'gevent' for async workers
    MAX_REQUESTS=1000
    MAX_REQUESTS_JITTER=100

    # --------------------------------------------------------------------------
    # GPU Configuration (Informational, actual GPU allocation is via Docker)
    # --------------------------------------------------------------------------
    CUDA_VISIBLE_DEVICES=0 # Specific GPU to use, if multiple are available
    NVIDIA_VISIBLE_DEVICES=all
    NVIDIA_DRIVER_CAPABILITIES=compute,utility

    # --------------------------------------------------------------------------
    # Docker Resource Limits (Informational, actual limits are in docker-compose.yml)
    # --------------------------------------------------------------------------
    MEMORY_LIMIT=12G
    MEMORY_RESERVATION=6G
    CPU_LIMIT=2.0
    CPU_RESERVATION=1.0
    ```

    After creating/editing your `.env` file, ensure it reflects the languages and model sizes you intend to use. Key variables to customize initially:
    *   `SUPPORTED_LANGUAGES`: Comma-separated list of languages to support (e.g., `en,de,fr,zh`).
    *   `AVAILABLE_MODEL_SIZES`: Comma-separated list of SpaCy model sizes to make available (e.g., `sm,md,lg,trf`).
    *   `PORT`: Port on which the API will be accessible.
    *   `TRANSFORMER_MODEL`: The Hugging Face model to use for embeddings.
    *   Paths for models and data (ensure these match your `docker-compose.yml` volumes if you customize them).

3.  **Download Models and Data:**
    This step is crucial. It downloads the required SpaCy language models and GeoNames data that the GeoParser service needs. The script uses the settings from your `.env` file to determine which models to fetch.
    ```bash
    bash setup_models.sh
    ```
    This script will:
    *   Build a temporary Docker image.
    *   Run a container to download SpaCy models for the languages and sizes specified in `.env`.
    *   Download GeoNames data used by the `geoparser` library.
    *   Place these assets into the local `./models` and `./data` directories, which will be mounted into the main service container.
    *   Clean up the temporary Docker image.
    *   Fix potential permission issues on the created directories.

    Ensure this script completes successfully. If you change `SUPPORTED_LANGUAGES` or `AVAILABLE_MODEL_SIZES` in `.env` later, you may need to re-run this script to download any new required models.

## Running the Application

You have two options to run the GeoParser API:

### Option 1: Build from Source (Development)

Once the setup is complete, you can start the GeoParser API using Docker Compose:

```bash
docker-compose up -d
```

*   The `-d` flag runs the containers in detached mode.
*   The service will be available at `http://localhost:<PORT>` (e.g., `http://localhost:5000` if `PORT=5000`).

### Option 2: Use Pre-built Image from Docker Hub (Production)

For easier deployment, you can use the pre-built Docker image:

```bash
# Pull the latest image
docker pull realjensen/geoparser-api:latest

# Run with docker-compose using pre-built image
docker-compose -f docker-compose.prod.yml up -d
```

Or run directly with Docker:

```bash
# Create required directories
mkdir -p models data logs

# Run the container
docker run -d \
  --name geoparser-api \
  -p 5000:5000 \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --env-file .env \
  realjensen/geoparser-api:latest
```

**Note**: You still need to download models and data using `bash setup_models.sh` before running the container.

### Common Commands

To view the logs:
```bash
docker-compose logs -f geoparser
```

To stop the application:
```bash
docker-compose down
```

## Docker Hub Repository

The GeoParser API is available as a pre-built Docker image on Docker Hub:

**🐳 Docker Hub**: [realjensen/geoparser-api](https://hub.docker.com/r/realjensen/geoparser-api)

Available tags:
- `latest`: Most recent stable version
- `v1.0`: Specific version tags

### Building and Pushing to Docker Hub

If you want to build and push your own version to Docker Hub:

1. **Login to Docker Hub:**
   ```bash
   docker login
   ```

2. **Build and push using the provided script:**
   ```bash
   ./build_and_push.sh [version] [username]
   ```
   
   Examples:
   ```bash
   # Push as latest with default username
   ./build_and_push.sh
   
   # Push specific version
   ./build_and_push.sh v1.1 your-username
   ```

3. **Manual build and push:**
   ```bash
   # Build production image
   docker build -f Dockerfile.prod -t your-username/geoparser-api:latest .
   
   # Push to Docker Hub
   docker push your-username/geoparser-api:latest
   ```

## API Endpoints

The API provides several endpoints for interacting with the GeoParser service. All request and response bodies are in JSON format.

---

### 1. Parse Text

*   **Endpoint:** `POST /api/parse`
*   **Description:** Parses a single text string to extract geographic entities.
*   **Request Body:**
    ```json
    {
        "text": "I want to travel from Berlin to Paris next week.",
        "languages": ["en"], // Optional: list of language codes (e.g., "en", "de"). Uses default if not provided or model not available.
        "model_size": "md"   // Optional: "sm", "md", "lg", "trf". Uses default from .env if not provided.
    }
    ```
*   **Example Request (`curl`):**
    ```bash
    curl -X POST -H "Content-Type: application/json" \
    -d '{
        "text": "I want to travel from Berlin to Paris next week.",
        "languages": ["en"],
        "model_size": "md"
    }' \
    http://localhost:5000/api/parse
    ```
*   **Success Response (200 OK):**
    ```json
    {
        "success": true,
        "language_detected": "en",
        "model_used": "en_core_web_md",
        "text_length": 50,
        "locations_found": 2,
        "locations": [
            {
                "name": "Berlin",
                "geonameid": "2950159",
                "feature_type": "PPLC",
                "latitude": 52.52437,
                "longitude": 13.41053,
                "elevation": null,
                "population": 3426354,
                "admin2_name": null,
                "admin1_name": "Berlin",
                "country_name": "Germany"
            },
            {
                "name": "Paris",
                "geonameid": "2988507",
                "feature_type": "PPLC",
                "latitude": 48.85341,
                "longitude": 2.3488,
                "elevation": null,
                "population": 2138551,
                "admin2_name": null,
                "admin1_name": "Île-de-France",
                "country_name": "France"
            }
        ],
        "processing_time": 0.8523,
        "parse_time": 0.7998,
        "from_cache": false
    }
    ```
*   **Error Responses:**
    *   `400 Bad Request`: Invalid input (e.g., missing `text`, text too long).
        ```json
        {
            "success": false,
            "error": "Text cannot be empty",
            "locations": []
        }
        ```
    *   `503 Service Unavailable`: If the GeoParserService is not initialized.

---

### 2. Parse Batch of Texts

*   **Endpoint:** `POST /api/parse/batch`
*   **Description:** Parses a list of text strings.
*   **Request Body:**
    ```json
    {
        "texts": [
            {
                "id": "doc1", // Optional: user-defined identifier for the text
                "text": "London is the capital of the United Kingdom.",
                "languages": ["en"] // Optional: per-item language
            },
            {
                "id": "doc2",
                "text": "Ich fahre nach München.",
                "languages": ["de"]
            }
        ],
        "model_size": "md" // Optional: applies to all texts unless overridden per-item (though per-item model_size is not explicitly shown in service.py, it's good practice for future)
    }
    ```
*   **Example Request (`curl`):**
    ```bash
    curl -X POST -H "Content-Type: application/json" \
    -d '{
        "texts": [
            {"id": "doc1", "text": "London is the capital of the United Kingdom.", "languages": ["en"]},
            {"id": "doc2", "text": "Ich fahre nach München.", "languages": ["de"]}
        ],
        "model_size": "md"
    }' \
    http://localhost:5000/api/parse/batch
    ```
*   **Success Response (200 OK):**
    ```json
    {
        "success": true,
        "total_processed": 2,
        "successful_parses": 2,
        "failed_parses": 0,
        "results": [
            {
                "id": "doc1", // Included if provided in request
                "success": true,
                "language_detected": "en",
                // ... other fields similar to /api/parse response
                "locations": [ /* ... */ ]
            },
            {
                "id": "doc2",
                "success": true,
                "language_detected": "de",
                // ... other fields
                "locations": [ /* ... */ ]
            }
        ]
    }
    ```
*   **Error Responses:**
    *   `400 Bad Request`: Invalid input (e.g., `texts` not a list, batch size exceeded).

---

### 3. Get Service Information

*   **Endpoint:** `GET /api/info`
*   **Description:** Provides information about the loaded models and service configuration.
*   **Example Request (`curl`):**
    ```bash
    curl http://localhost:5000/api/info
    ```
*   **Success Response (200 OK):**
    ```json
    {
        "success": true,
        "info": {
            "loaded_models": ["en", "de"], // Actual loaded language codes
            "default_model_size": "md",
            "transformer_model": "dguzh/geo-all-MiniLM-L6-v2",
            "gazetteer": "geonames",
            "supported_languages": ["en", "de", "fr", "zh", "es"], // From .env
            "cache_enabled": true,
            "cache_size": 10,
            "max_text_length": 10000,
            "max_batch_size": 100
        }
    }
    ```
*   **Error Responses:**
    *   `503 Service Unavailable`: If the GeoParserService is not initialized.

---

### 4. Health Check

*   **Endpoint:** `GET /api/health`
*   **Description:** Checks the health of the service. Used by Docker for container health monitoring.
*   **Example Request (`curl`):**
    ```bash
    curl http://localhost:5000/api/health
    ```
*   **Success Response (200 OK):**
    ```json
    {
        "status": "healthy",
        "models_loaded": 2,
        "test_parse_success": true,
        "config_valid": true
    }
    ```
*   **Error Response (503 Service Unavailable):**
    ```json
    {
        "status": "unhealthy",
        "error": "GeoParser service is not available"
    }
    ```

---

### 5. Clear Cache

*   **Endpoint:** `POST /api/cache/clear`
*   **Description:** Clears the in-memory cache of the GeoParserService.
*   **Example Request (`curl`):**
    ```bash
    curl -X POST http://localhost:5000/api/cache/clear
    ```
*   **Success Response (200 OK):**
    ```json
    {
        "success": true,
        "message": "Cache cleared successfully. Removed 10 entries."
    }
    ```
*   **Response if caching is disabled (200 OK but indicates no action):**
    ```json
    {
        "success": false, // Or true with a different message
        "message": "Caching is not enabled. No cache to clear."
    }
    ```

---

### 6. Get Supported Languages and Models

*   **Endpoint:** `GET /api/languages`
*   **Description:** Returns the list of languages and model sizes supported by the current configuration.
*   **Example Request (`curl`):**
    ```bash
    curl http://localhost:5000/api/languages
    ```
*   **Success Response (200 OK):**
    ```json
    {
        "success": true,
        "supported_languages": ["en", "de", "fr", "zh", "es"], // From .env
        "default_model_size": "md", // From .env
        "available_model_sizes": ["sm", "md", "lg", "trf"] // From .env
    }
    ```

---

### Root Endpoint

*   **Endpoint:** `GET /`
*   **Description:** Provides basic service information and a list of available endpoints.
*   **Example Request (`curl`):**
    ```bash
    curl http://localhost:5000/
    ```
*   **Success Response (200 OK):**
    ```json
    {
        "service": "GeoParser API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "parse": "/api/parse",
            "batch_parse": "/api/parse/batch",
            "info": "/api/info",
            "health": "/api/health",
            "clear_cache": "/api/cache/clear",
            "languages": "/api/languages"
        },
        "documentation": "https://github.com/Jensen-JZ/GeoParser-API"
    }
    ```

## Configuration Options

The application is configured primarily through the `.env` file. Some key options include:

*   `TRANSFORMER_MODEL`: Specifies the Hugging Face transformer model for embeddings.
*   `GAZETTEER`: The gazetteer to use (default: `geonames`).
*   `AVAILABLE_MODEL_SIZES`: Comma-separated list of SpaCy model sizes (e.g., `sm,md,lg,trf`).
*   `SUPPORTED_LANGUAGES`: Comma-separated list of ISO language codes (e.g., `en,de,fr,zh,es`).
*   `SPACY_MODEL_PATH`, `TRANSFORMERS_MODEL_PATH`, `GEONAMES_DATA_PATH`: Paths within the container where models and data are stored. These are typically managed by `docker-compose.yml` volumes and the `setup_models.sh` script.
*   `MAX_TEXT_LENGTH`: Maximum characters allowed for input text.
*   `TIMEOUT`: Request timeout.
*   `ENABLE_CACHE`: Set to `true` to enable in-memory caching.
*   `MAX_BATCH_SIZE`: Maximum number of texts allowed in a batch request.
*   `LOG_LEVEL`: Logging level (e.g., `INFO`, `DEBUG`).
*   `HOST`, `PORT`: Server host and port.
*   `WORKERS`, `WORKER_TIMEOUT`, etc.: Gunicorn worker configuration.
*   `MEMORY_LIMIT`, `CPU_LIMIT`: Docker resource limits.

Refer to the `.env` file and `app/config.py` for a complete list of configurations.

## GPU Support

The service is configured to support NVIDIA GPUs for faster model inference.
To enable GPU support:

1.  Ensure you have NVIDIA drivers installed on the host machine.
2.  Install the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) on the host machine.
3.  The `docker-compose.yml` file includes the necessary `runtime: nvidia` configuration.
    ```yaml
    services:
      geoparser:
        # ... other configurations
        runtime: nvidia
        deploy:
          resources:
            reservations:
              devices:
                - driver: nvidia
                  count: 1 # Or 'all'
                  capabilities: [gpu]
    ```
    (Note: The `deploy.resources.reservations.devices` structure is common, but `runtime: nvidia` is the primary enabler for Docker Compose v2+).
    The `.env` file also contains GPU-related environment variables like `CUDA_VISIBLE_DEVICES`.

If the NVIDIA runtime is correctly configured, PyTorch (a dependency of Transformers) should automatically detect and use available GPUs.

## Troubleshooting

*   **Model Download Issues (`setup_models.sh`):**
    *   Ensure you have a stable internet connection.
    *   Check for typos in `SUPPORTED_LANGUAGES` or `AVAILABLE_MODEL_SIZES` in your `.env` file. SpaCy model names are specific (e.g., `en_core_web_sm`, `de_core_news_md`). The script attempts to derive these.
    *   If a specific model fails, try downloading it manually with `python -m spacy download <model_name>` inside a Python environment with `spacy` installed to see more detailed errors.
*   **Port Conflicts:** If another service is using the specified `PORT` (default 5000), change it in `.env` and restart the containers.
*   **Docker Permission Issues:**
    *   The `setup_models.sh` script attempts to fix permissions for `./models` and `./data` directories.
    *   If you encounter permission errors when Docker tries to write to mounted volumes, ensure the user running Docker has write access to these directories on the host or run `sudo chown -R $(whoami):$(whoami) models/ data/ logs/` (be cautious with `sudo`).
*   **Service Fails to Start (Check Logs):**
    *   `docker-compose logs -f geoparser`
    *   Look for errors related to model loading (e.g., "No models were successfully loaded") or Python package issues.
    *   Ensure all models listed by `SUPPORTED_LANGUAGES` and `DEFAULT_MODEL_SIZE` (first of `AVAILABLE_MODEL_SIZES`) were successfully downloaded by `setup_models.sh`.
*   **`CUDA_ERROR_NO_DEVICE` or similar GPU errors:**
    *   Verify NVIDIA drivers and NVIDIA Container Toolkit are correctly installed and configured on the host.
    *   Ensure the `runtime: nvidia` is set in `docker-compose.yml`.
    *   Check `CUDA_VISIBLE_DEVICES` in `.env`.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs, feature requests, or improvements.
(Consider adding more specific guidelines if this is an active open-source project, e.g., coding standards, testing procedures).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 中文

# GeoParser API

## 概述

GeoParser API 是一个强大的服务，旨在从文本中提取和消歧地理实体（如城市、国家和其他位置）。它利用最先进的NLP模型，在多种语言中提供准确的位置识别。此服务使用Docker进行容器化，便于部署和扩展。

## 功能特性

*   **位置命名实体识别(NER):** 识别文本中的地理名称。
*   **多语言支持:** 可配置支持多种语言（如英语、德语、法语、中文、西班牙语）。
*   **灵活的模型选择:** 支持不同的SpaCy模型大小（sm、md、lg、trf），平衡性能和资源使用。
*   **基于Transformer的模型:** 使用transformer模型提高准确性。
*   **地名词典集成:** 使用GeoNames进行消歧和丰富的位置数据。
*   **Docker化:** 使用Docker和Docker Compose轻松部署和管理。
*   **批量处理:** 在单个API调用中高效解析多个文本。
*   **缓存:** 为频繁请求的文本提供内存缓存，提高响应时间。
*   **健康检查端点:** 提供监控的健康状态。
*   **GPU支持:** 可以利用NVIDIA GPU进行加速处理。
*   **全面配置:** 通过环境变量高度可配置。

## 技术栈

*   **后端:** `Python`, `Flask`
*   **NLP库:**
    *   `geoparser`（核心库）
    *   `SpaCy`
    *   `Transformers`（Hugging Face）
    *   `PyTorch`
*   **容器化:** `Docker`, `Docker Compose`
*   **WSGI服务器:** `Gunicorn`

## 支持的模型

GeoParser API 支持广泛的 SpaCy 语言模型进行地理实体识别。该服务目前支持 **24种语言**，具有不同的模型配置：

### 语言支持概览

| 语言 | 代码 | 模型模式 | 可用大小 | TRF支持 | 备注 |
|------|------|----------|----------|---------|------|
| 加泰罗尼亚语 | `ca` | `ca_core_news_{size}` | sm, md, lg, trf | ✅ | |
| 中文 | `zh` | `zh_core_web_{size}` | sm, md, lg, trf | ✅ | 基于网络的模型 |
| 克罗地亚语 | `hr` | `hr_core_news_{size}` | sm, md, lg | ❌ | |
| 丹麦语 | `da` | `da_core_news_{size}` | sm, md, lg | ❌ | |
| 荷兰语 | `nl` | `nl_core_news_{size}` | sm, md, lg | ❌ | |
| 英语 | `en` | `en_core_web_{size}` | sm, md, lg, trf | ✅ | 基于网络的模型 |
| 芬兰语 | `fi` | `fi_core_news_{size}` | sm, md, lg | ❌ | |
| 法语 | `fr` | `fr_core_news_{size}` | sm, md, lg | ⚠️ | TRF: `fr_dep_news_trf`（仅依存句法分析） |
| 德语 | `de` | `de_core_news_{size}` | sm, md, lg | ⚠️ | TRF: `de_dep_news_trf`（仅依存句法分析） |
| 希腊语 | `el` | `el_core_news_{size}` | sm, md, lg | ❌ | |
| 意大利语 | `it` | `it_core_news_{size}` | sm, md, lg | ❌ | |
| 日语 | `ja` | `ja_core_news_{size}` | sm, md, lg, trf | ✅ | |
| 韩语 | `ko` | `ko_core_news_{size}` | sm, md, lg | ❌ | |
| 立陶宛语 | `lt` | `lt_core_news_{size}` | sm, md, lg | ❌ | |
| 马其顿语 | `mk` | `mk_core_news_{size}` | sm, md, lg | ❌ | |
| 挪威语 | `nb` | `nb_core_news_{size}` | sm, md, lg | ❌ | |
| 波兰语 | `pl` | `pl_core_news_{size}` | sm, md, lg | ❌ | |
| 葡萄牙语 | `pt` | `pt_core_news_{size}` | sm, md, lg | ❌ | |
| 罗马尼亚语 | `ro` | `ro_core_news_{size}` | sm, md, lg | ❌ | |
| 俄语 | `ru` | `ru_core_news_{size}` | sm, md, lg | ❌ | |
| 斯洛文尼亚语 | `sl` | `sl_core_news_{size}` | sm, md, lg, trf | ✅ | |
| 西班牙语 | `es` | `es_core_news_{size}` | sm, md, lg | ⚠️ | TRF: `es_dep_news_trf`（仅依存句法分析） |
| 瑞典语 | `sv` | `sv_core_news_{size}` | sm, md, lg | ❌ | |
| 乌克兰语 | `uk` | `uk_core_news_{size}` | sm, md, lg, trf | ✅ | |

### 模型大小建议

- **sm（小）**: 最快，内存使用最少，适合基本NER
- **md（中）**: 性能和准确性平衡 - **大多数情况下推荐使用**
- **lg（大）**: 更高准确性，更占内存
- **trf（Transformer）**: 最高准确性，但**不推荐**用于地理解析，因为可用性有限且存在兼容性问题

> **⚠️ 重要提示**: 虽然某些语言有 `trf`（transformer）模型可用，但我们**不建议**将 `trf` 大小用于地理实体识别。像德语、法语和西班牙语等语言只有依存句法分析的transformer模型（`xx_dep_news_trf`），无法执行地理解析所需的命名实体识别。

### 模型命名约定

该服务遵循 SpaCy 的标准命名约定：
- **英语和中文**: 使用 `xx_core_web_{size}`（基于网络训练的模型）
- **所有其他语言**: 使用 `xx_core_news_{size}`（基于新闻训练的模型）

其中 `xx` 是 ISO 639-1 语言代码，`{size}` 是以下之一：`sm`、`md`、`lg`、`trf`。

## 先决条件

*   [Git](https://git-scm.com/downloads)
*   [Docker](https://docs.docker.com/get-docker/)
*   [Docker Compose](https://docs.docker.com/compose/install/)（通常包含在Docker Desktop中）
*   Shell环境（如Bash、Zsh、PowerShell）
*   （可选）GPU支持：
    *   NVIDIA GPU驱动程序
    *   [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)

## 设置和安装

1.  **克隆仓库:**
    ```bash
    git clone <repository-url>
    cd GeoParser-API
    ```

2.  **配置环境:**
    在项目根目录下创建`.env`文件。您可以复制下面示例的结构，或从现有的`.env`文件复制（如果存在）。
    最小的`.env.example`如下所示：
    ```env
    # GeoParser API Configuration

    # --------------------------------------------------------------------------
    # Model Configuration
    # --------------------------------------------------------------------------
    # Transformer model for embeddings (from Hugging Face Model Hub)
    TRANSFORMER_MODEL=dguzh/geo-all-MiniLM-L6-v2
    # Gazetteer to use (geonames is standard for geoparser)
    GAZETTEER=geonames
    # Available SpaCy model sizes (e.g., sm, md, lg, trf for transformer models)
    # The setup_models.sh script will try to download models for these sizes for each supported language.
    # The first size in this list will be used as the default if not specified in API calls.
    AVAILABLE_MODEL_SIZES=md,sm

    # --------------------------------------------------------------------------
    # Supported Languages
    # --------------------------------------------------------------------------
    # Comma-separated list of ISO 639-1 language codes (e.g., en, de, fr, zh, es)
    # The setup_models.sh script will download models for these languages.
    SUPPORTED_LANGUAGES=en,de

    # --------------------------------------------------------------------------
    # Model and Data Paths (within the Docker container)
    # These should generally not be changed unless you modify docker-compose.yml volume mounts.
    # --------------------------------------------------------------------------
    SPACY_MODEL_PATH=/app/models/spacy
    TRANSFORMERS_MODEL_PATH=/app/models/transformers # Currently not used for pre-downloaded custom transformers, but reserved.
    GEONAMES_DATA_PATH=/app/data/geonames

    # --------------------------------------------------------------------------
    # API Configuration
    # --------------------------------------------------------------------------
    MAX_TEXT_LENGTH=10000  # Maximum characters for input text
    TIMEOUT=30             # Request timeout in seconds
    ENABLE_CACHE=true      # Enable/disable in-memory cache
    MAX_BATCH_SIZE=100     # Maximum items in a batch request

    # --------------------------------------------------------------------------
    # Logging Configuration
    # --------------------------------------------------------------------------
    LOG_LEVEL=INFO # DEBUG, INFO, WARNING, ERROR, CRITICAL

    # --------------------------------------------------------------------------
    # Server Configuration (for Flask/Gunicorn)
    # --------------------------------------------------------------------------
    HOST=0.0.0.0
    PORT=5000
    DEBUG=false # Set to true for Flask debug mode (not recommended for Gunicorn production)

    # Gunicorn worker settings (see docker-compose.yml command for how these are used)
    WORKERS=2
    WORKER_TIMEOUT=600
    WORKER_CLASS=sync # or 'gthread', 'eventlet', 'gevent' for async workers
    MAX_REQUESTS=1000
    MAX_REQUESTS_JITTER=100

    # --------------------------------------------------------------------------
    # GPU Configuration (Informational, actual GPU allocation is via Docker)
    # --------------------------------------------------------------------------
    CUDA_VISIBLE_DEVICES=0 # Specific GPU to use, if multiple are available
    NVIDIA_VISIBLE_DEVICES=all
    NVIDIA_DRIVER_CAPABILITIES=compute,utility

    # --------------------------------------------------------------------------
    # Docker Resource Limits (Informational, actual limits are in docker-compose.yml)
    # --------------------------------------------------------------------------
    MEMORY_LIMIT=12G
    MEMORY_RESERVATION=6G
    CPU_LIMIT=2.0
    CPU_RESERVATION=1.0
    ```

    创建/编辑`.env`文件后，确保它反映您打算使用的语言和模型大小。初始需要自定义的关键变量：
    *   `SUPPORTED_LANGUAGES`: 要支持的语言的逗号分隔列表（例如，`en,de,fr,zh`）。
    *   `AVAILABLE_MODEL_SIZES`: 要提供的SpaCy模型大小的逗号分隔列表（例如，`sm,md,lg,trf`）。
    *   `PORT`: API可访问的端口。
    *   `TRANSFORMER_MODEL`: 用于嵌入的Hugging Face模型。
    *   模型和数据的路径（如果您自定义，请确保这些与您的`docker-compose.yml`卷匹配）。

3.  **下载模型和数据:**
    这一步至关重要。它下载GeoParser服务所需的SpaCy语言模型和GeoNames数据。脚本使用您的`.env`文件中的设置来确定要获取哪些模型。
    ```bash
    bash setup_models.sh
    ```
    此脚本将：
    *   构建临时Docker镜像。
    *   运行容器以下载`.env`中指定的语言和大小的SpaCy模型。
    *   下载`geoparser`库使用的GeoNames数据。
    *   将这些资产放入本地的`./models`和`./data`目录中，这些目录将挂载到主服务容器中。
    *   清理临时Docker镜像。
    *   修复创建目录的潜在权限问题。

    确保此脚本成功完成。如果您稍后在`.env`中更改`SUPPORTED_LANGUAGES`或`AVAILABLE_MODEL_SIZES`，您可能需要重新运行此脚本以下载任何新的必需模型。

## 运行应用程序

您有两种选择来运行GeoParser API：

### 选项1：从源码构建（开发环境）

设置完成后，您可以使用Docker Compose启动GeoParser API：

```bash
docker-compose up -d
```

*   `-d`标志在分离模式下运行容器。
*   服务将在`http://localhost:<PORT>`（例如，如果`PORT=5000`，则为`http://localhost:5000`）可用。

### 选项2：使用Docker Hub预构建镜像（生产环境）

为了更便捷的部署，您可以使用预构建的Docker镜像：

```bash
# 拉取最新镜像
docker pull realjensen/geoparser-api:latest

# 使用预构建镜像运行docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

或直接使用Docker运行：

```bash
# 创建必需的目录
mkdir -p models data logs

# 运行容器
docker run -d \
  --name geoparser-api \
  -p 5000:5000 \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --env-file .env \
  realjensen/geoparser-api:latest
```

**注意**：您仍然需要使用`bash setup_models.sh`下载模型和数据，然后才能运行容器。

### 常用命令

查看日志：
```bash
docker-compose logs -f geoparser
```

停止应用程序：
```bash
docker-compose down
```

## Docker Hub 仓库

GeoParser API 作为预构建的Docker镜像可在Docker Hub上获得：

**🐳 Docker Hub**: [realjensen/geoparser-api](https://hub.docker.com/r/realjensen/geoparser-api)

可用标签：
- `latest`: 最新稳定版本
- `v1.0`: 特定版本标签

### 构建并推送到Docker Hub

如果您想构建并推送自己的版本到Docker Hub：

1. **登录到Docker Hub:**
   ```bash
   docker login
   ```

2. **使用提供的脚本构建和推送:**
   ```bash
   ./build_and_push.sh [版本] [用户名]
   ```
   
   示例：
   ```bash
   # 使用默认用户名推送最新版本
   ./build_and_push.sh
   
   # 推送特定版本
   ./build_and_push.sh v1.1 your-username
   ```

3. **手动构建和推送:**
   ```bash
   # 构建生产镜像
   docker build -f Dockerfile.prod -t your-username/geoparser-api:latest .
   
   # 推送到Docker Hub
   docker push your-username/geoparser-api:latest
   ```

## API端点

API提供了几个端点来与GeoParser服务交互。所有请求和响应体都是JSON格式。

---

### 1. 解析文本

*   **端点:** `POST /api/parse`
*   **描述:** 解析单个文本字符串以提取地理实体。
*   **请求体:**
    ```json
    {
        "text": "I want to travel from Berlin to Paris next week.",
        "languages": ["en"], // Optional: list of language codes (e.g., "en", "de"). Uses default if not provided or model not available.
        "model_size": "md"   // Optional: "sm", "md", "lg", "trf". Uses default from .env if not provided.
    }
    ```
*   **示例请求 (`curl`):**
    ```bash
    curl -X POST -H "Content-Type: application/json" \
    -d '{
        "text": "I want to travel from Berlin to Paris next week.",
        "languages": ["en"],
        "model_size": "md"
    }' \
    http://localhost:5000/api/parse
    ```
*   **成功响应 (200 OK):**
    ```json
    {
        "success": true,
        "language_detected": "en",
        "model_used": "en_core_web_md",
        "text_length": 50,
        "locations_found": 2,
        "locations": [
            {
                "name": "Berlin",
                "geonameid": "2950159",
                "feature_type": "PPLC",
                "latitude": 52.52437,
                "longitude": 13.41053,
                "elevation": null,
                "population": 3426354,
                "admin2_name": null,
                "admin1_name": "Berlin",
                "country_name": "Germany"
            },
            {
                "name": "Paris",
                "geonameid": "2988507",
                "feature_type": "PPLC",
                "latitude": 48.85341,
                "longitude": 2.3488,
                "elevation": null,
                "population": 2138551,
                "admin2_name": null,
                "admin1_name": "Île-de-France",
                "country_name": "France"
            }
        ],
        "processing_time": 0.8523,
        "parse_time": 0.7998,
        "from_cache": false
    }
    ```
*   **错误响应:**
    *   `400 Bad Request`: 无效输入（例如，缺少`text`，文本过长）。
        ```json
        {
            "success": false,
            "error": "Text cannot be empty",
            "locations": []
        }
        ```
    *   `503 Service Unavailable`: 如果GeoParserService未初始化。

---

### 2. 批量解析文本

*   **端点:** `POST /api/parse/batch`
*   **描述:** 解析文本字符串列表。
*   **请求体:**
    ```json
    {
        "texts": [
            {
                "id": "doc1", // Optional: user-defined identifier for the text
                "text": "London is the capital of the United Kingdom.",
                "languages": ["en"] // Optional: per-item language
            },
            {
                "id": "doc2",
                "text": "Ich fahre nach München.",
                "languages": ["de"]
            }
        ],
        "model_size": "md" // Optional: applies to all texts unless overridden per-item (though per-item model_size is not explicitly shown in service.py, it's good practice for future)
    }
    ```
*   **示例请求 (`curl`):**
    ```bash
    curl -X POST -H "Content-Type: application/json" \
    -d '{
        "texts": [
            {"id": "doc1", "text": "London is the capital of the United Kingdom.", "languages": ["en"]},
            {"id": "doc2", "text": "Ich fahre nach München.", "languages": ["de"]}
        ],
        "model_size": "md"
    }' \
    http://localhost:5000/api/parse/batch
    ```
*   **成功响应 (200 OK):**
    ```json
    {
        "success": true,
        "total_processed": 2,
        "successful_parses": 2,
        "failed_parses": 0,
        "results": [
            {
                "id": "doc1", // Included if provided in request
                "success": true,
                "language_detected": "en",
                // ... other fields similar to /api/parse response
                "locations": [ /* ... */ ]
            },
            {
                "id": "doc2",
                "success": true,
                "language_detected": "de",
                // ... other fields
                "locations": [ /* ... */ ]
            }
        ]
    }
    ```
*   **错误响应:**
    *   `400 Bad Request`: 无效输入（例如，`texts`不是列表，超过批量大小）。

---

### 3. 获取服务信息

*   **端点:** `GET /api/info`
*   **描述:** 提供有关已加载模型和服务配置的信息。
*   **示例请求 (`curl`):**
    ```bash
    curl http://localhost:5000/api/info
    ```
*   **成功响应 (200 OK):**
    ```json
    {
        "success": true,
        "info": {
            "loaded_models": ["en", "de"], // Actual loaded language codes
            "default_model_size": "md",
            "transformer_model": "dguzh/geo-all-MiniLM-L6-v2",
            "gazetteer": "geonames",
            "supported_languages": ["en", "de", "fr", "zh", "es"], // From .env
            "cache_enabled": true,
            "cache_size": 10,
            "max_text_length": 10000,
            "max_batch_size": 100
        }
    }
    ```
*   **错误响应:**
    *   `503 Service Unavailable`: 如果GeoParserService未初始化。

---

### 4. 健康检查

*   **端点:** `GET /api/health`
*   **描述:** 检查服务的健康状态。用于Docker容器健康监控。
*   **示例请求 (`curl`):**
    ```bash
    curl http://localhost:5000/api/health
    ```
*   **成功响应 (200 OK):**
    ```json
    {
        "status": "healthy",
        "models_loaded": 2,
        "test_parse_success": true,
        "config_valid": true
    }
    ```
*   **错误响应 (503 Service Unavailable):**
    ```json
    {
        "status": "unhealthy",
        "error": "GeoParser service is not available"
    }
    ```

---

### 5. 清除缓存

*   **端点:** `POST /api/cache/clear`
*   **描述:** 清除GeoParserService的内存缓存。
*   **示例请求 (`curl`):**
    ```bash
    curl -X POST http://localhost:5000/api/cache/clear
    ```
*   **成功响应 (200 OK):**
    ```json
    {
        "success": true,
        "message": "Cache cleared successfully. Removed 10 entries."
    }
    ```
*   **缓存禁用时的响应 (200 OK但表示无操作):**
    ```json
    {
        "success": false, // Or true with a different message
        "message": "Caching is not enabled. No cache to clear."
    }
    ```

---

### 6. 获取支持的语言和模型

*   **端点:** `GET /api/languages`
*   **描述:** 返回当前配置支持的语言和模型大小列表。
*   **示例请求 (`curl`):**
    ```bash
    curl http://localhost:5000/api/languages
    ```
*   **成功响应 (200 OK):**
    ```json
    {
        "success": true,
        "supported_languages": ["en", "de", "fr", "zh", "es"], // From .env
        "default_model_size": "md", // From .env
        "available_model_sizes": ["sm", "md", "lg", "trf"] // From .env
    }
    ```

---

### 根端点

*   **端点:** `GET /`
*   **描述:** 提供基本服务信息和可用端点列表。
*   **示例请求 (`curl`):**
    ```bash
    curl http://localhost:5000/
    ```
*   **成功响应 (200 OK):**
    ```json
    {
        "service": "GeoParser API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "parse": "/api/parse",
            "batch_parse": "/api/parse/batch",
            "info": "/api/info",
            "health": "/api/health",
            "clear_cache": "/api/cache/clear",
            "languages": "/api/languages"
        },
        "documentation": "https://github.com/Jensen-JZ/GeoParser-API"
    }
    ```

## 配置选项

应用程序主要通过`.env`文件进行配置。一些关键选项包括：

*   `TRANSFORMER_MODEL`: 指定用于嵌入的Hugging Face transformer模型。
*   `GAZETTEER`: 要使用的地名词典（默认：`geonames`）。
*   `AVAILABLE_MODEL_SIZES`: 以逗号分隔的SpaCy模型大小列表（例如，`sm,md,lg,trf`）。
*   `SUPPORTED_LANGUAGES`: 以逗号分隔的ISO语言代码列表（例如，`en,de,fr,zh,es`）。
*   `SPACY_MODEL_PATH`、`TRANSFORMERS_MODEL_PATH`、`GEONAMES_DATA_PATH`: 容器内存储模型和数据的路径。这些通常由`docker-compose.yml`卷和`setup_models.sh`脚本管理。
*   `MAX_TEXT_LENGTH`: 输入文本允许的最大字符数。
*   `TIMEOUT`: 请求超时。
*   `ENABLE_CACHE`: 设置为`true`以启用内存缓存。
*   `MAX_BATCH_SIZE`: 批量请求中允许的最大文本数。
*   `LOG_LEVEL`: 日志级别（例如，`INFO`、`DEBUG`）。
*   `HOST`、`PORT`: 服务器主机和端口。
*   `WORKERS`、`WORKER_TIMEOUT`等: Gunicorn工作器配置。
*   `MEMORY_LIMIT`、`CPU_LIMIT`: Docker资源限制。

请参阅`.env`文件和`app/config.py`以获取完整的配置列表。

## GPU支持

该服务配置为支持NVIDIA GPU以实现更快的模型推理。
要启用GPU支持：

1.  确保在主机上安装了NVIDIA驱动程序。
2.  在主机上安装[NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)。
3.  `docker-compose.yml`文件包含必要的`runtime: nvidia`配置。
    ```yaml
    services:
      geoparser:
        # ... other configurations
        runtime: nvidia
        deploy:
          resources:
            reservations:
              devices:
                - driver: nvidia
                  count: 1 # Or 'all'
                  capabilities: [gpu]
    ```
    （注意：`deploy.resources.reservations.devices`结构很常见，但`runtime: nvidia`是Docker Compose v2+的主要启用器）。
    `.env`文件还包含与GPU相关的环境变量，如`CUDA_VISIBLE_DEVICES`。

如果NVIDIA运行时配置正确，PyTorch（Transformers的依赖项）应该自动检测并使用可用的GPU。

## 故障排除

*   **模型下载问题 (`setup_models.sh`):**
    *   确保您有稳定的互联网连接。
    *   检查`.env`文件中`SUPPORTED_LANGUAGES`或`AVAILABLE_MODEL_SIZES`的拼写错误。SpaCy模型名称是特定的（例如，`en_core_web_sm`、`de_core_news_md`）。脚本尝试推导这些。
    *   如果特定模型失败，尝试在安装了`spacy`的Python环境中使用`python -m spacy download <model_name>`手动下载，以查看更详细的错误。
*   **端口冲突:** 如果另一个服务正在使用指定的`PORT`（默认5000），请在`.env`中更改它并重新启动容器。
*   **Docker权限问题:**
    *   `setup_models.sh`脚本尝试修复`./models`和`./data`目录的权限。
    *   如果Docker尝试写入挂载卷时遇到权限错误，请确保运行Docker的用户对主机上的这些目录有写入权限，或运行`sudo chown -R $(whoami):$(whoami) models/ data/ logs/`（谨慎使用`sudo`）。
*   **服务启动失败（检查日志）:**
    *   `docker-compose logs -f geoparser`
    *   查找与模型加载相关的错误（例如，"未成功加载模型"）或Python包问题。
    *   确保`SUPPORTED_LANGUAGES`和`DEFAULT_MODEL_SIZE`（`AVAILABLE_MODEL_SIZES`的第一个）列出的所有模型都已由`setup_models.sh`成功下载。
*   **`CUDA_ERROR_NO_DEVICE`或类似的GPU错误:**
    *   验证NVIDIA驱动程序和NVIDIA Container Toolkit在主机上正确安装和配置。
    *   确保在`docker-compose.yml`中设置了`runtime: nvidia`。
    *   检查`.env`中的`CUDA_VISIBLE_DEVICES`。

## 贡献

欢迎贡献！请随时提交拉取请求或为错误、功能请求或改进打开问题。
（如果这是一个活跃的开源项目，请考虑添加更具体的指导原则，例如，编码标准、测试程序）。

## 许可证

本项目基于MIT许可证。有关详细信息，请参阅[LICENSE](LICENSE)文件。