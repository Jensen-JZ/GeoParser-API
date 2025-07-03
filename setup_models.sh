#!/bin/bash

set -e  # Exit on any error

# ASCII Logo
cat << "EOF"
    __________    __  __   ______           ____                           
   /  _/_  __/   / / / /  / ____/__  ____  / __ \____ ______________  _____
   / /  / /_____/ / / /  / / __/ _ \/ __ \/ /_/ / __ `/ ___/ ___/ _ \/ ___/
 _/ /  / /_____/ /_/ /  / /_/ /  __/ /_/ / ____/ /_/ / /  (__  )  __/ /    
/___/ /_/      \____/   \____/\___/\____/_/    \__,_/_/  /____/\___/_/     
                                                                           
                                        
        🌍 GeoParser Service – Model Setup 🌍
                     Version: v1.0          

        Author: Jingyao Zhang
        Contact: jingyao.zhang@it-u.at

EOF

echo "Starting model and data setup using Docker container..."

# Get the directory where this script is located
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Project directory: $PROJECT_DIR"

# Load environment variables from .env file
if [ -f "$PROJECT_DIR/.env" ]; then
    echo "Loading environment variables from .env file..."
    export $(grep -v '^#' "$PROJECT_DIR/.env" | xargs)
else
    echo "Warning: .env file not found. Using default settings."
    SUPPORTED_LANGUAGES="en,de,fr,zh,es"
    AVAILABLE_MODEL_SIZES="sm,md,lg,trf"
fi

# Set default values if not specified
AVAILABLE_MODEL_SIZES=${AVAILABLE_MODEL_SIZES:-"sm,md,lg,trf"}

echo "Supported languages: $SUPPORTED_LANGUAGES"
echo "Available model sizes: $AVAILABLE_MODEL_SIZES"

# Get default model size (first available size)
DEFAULT_MODEL_SIZE=$(echo "$AVAILABLE_MODEL_SIZES" | cut -d',' -f1)
echo "Default model size: $DEFAULT_MODEL_SIZE"

# Create directories if they don't exist
echo "Creating local directories..."
mkdir -p "$PROJECT_DIR/models/spacy"
mkdir -p "$PROJECT_DIR/data/geoparser"

# Function to check if directory exists and is not empty
check_directory() {
    local dir=$1
    if [ -d "$dir" ] && [ "$(ls -A "$dir" 2>/dev/null)" ]; then
        return 0  # Directory exists and not empty
    else
        return 1  # Directory doesn't exist or is empty
    fi
}

# Function to get the expected model name for a language
get_expected_model_name() {
    local lang=$1
    local size=$2
    
    # Some languages use different naming patterns
    case $lang in
        "zh") echo "${lang}_core_web_${size}" ;;
        "en") echo "${lang}_core_web_${size}" ;;
        "ca"|"da"|"nl"|"fi"|"fr"|"de"|"el"|"it"|"ja"|"ko"|"lt"|"mk"|"nb"|"pl"|"pt"|"ro"|"ru"|"sl"|"es"|"sv"|"uk"|"hr") 
            echo "${lang}_core_news_${size}" ;;
        *) echo "${lang}_core_news_${size}" ;;
    esac
}

# Parse supported languages and model sizes, build model list
IFS=',' read -ra LANG_ARRAY <<< "$SUPPORTED_LANGUAGES"
IFS=',' read -ra SIZE_ARRAY <<< "$AVAILABLE_MODEL_SIZES"
MODELS_TO_CHECK=()

echo "Building model list to check for all supported sizes..."
for lang in "${LANG_ARRAY[@]}"; do
    # Remove whitespace
    lang=$(echo "$lang" | tr -d ' ')
    if [ -n "$lang" ]; then
        # Add models for each available size
        for size in "${SIZE_ARRAY[@]}"; do
            size=$(echo "$size" | tr -d ' ')
            if [ -n "$size" ]; then
                expected_model=$(get_expected_model_name "$lang" "$size")
                MODELS_TO_CHECK+=("$lang:$size:$expected_model")
                echo "  - $lang ($size) -> $expected_model"
            fi
        done
    fi
done

if [ ${#MODELS_TO_CHECK[@]} -eq 0 ]; then
    echo "Error: No valid language models found to check!"
    exit 1
fi

# Check if required models already exist
echo "Checking existing models..."
SKIP_SPACY=true
MISSING_MODELS=()

for model_spec in "${MODELS_TO_CHECK[@]}"; do
    lang=$(echo "$model_spec" | cut -d':' -f1)
    size=$(echo "$model_spec" | cut -d':' -f2)
    model=$(echo "$model_spec" | cut -d':' -f3)
    
    if [ ! -d "$PROJECT_DIR/models/spacy/$model" ]; then
        echo "Model $model not found for language $lang ($size)"
        MISSING_MODELS+=("$lang:$size:$model")
        SKIP_SPACY=false
    else
        echo "Model $model already exists for language $lang ($size)"
    fi
done

if [ "$SKIP_SPACY" = true ]; then
    echo "All required spaCy models already exist, skipping download..."
fi

# Check if geoparser data already exists
if check_directory "$PROJECT_DIR/data/geoparser" && [ -f "$PROJECT_DIR/data/geoparser/geonames/geonames.db" ]; then
    echo "Geoparser data already exists, skipping download..."
    SKIP_GEOPARSER=true
else
    echo "Geoparser data not found, will download..."
    SKIP_GEOPARSER=false
fi

# If everything exists, exit early
if [ "$SKIP_SPACY" = true ] && [ "$SKIP_GEOPARSER" = true ]; then
    echo "All models and data already exist. Setup complete!"
    exit 0
fi

# Build the image first if it doesn't exist
echo "Building Docker image..."
cd "$PROJECT_DIR"
docker build -t geoparser-setup .

echo "Starting temporary container to download models and data..."

# Build download and move commands dynamically
DOWNLOAD_COMMANDS=""
MOVE_COMMANDS=""

if [ "$SKIP_SPACY" = false ]; then
    echo "Preparing spaCy model download commands for missing models..."
    
    for model_spec in "${MISSING_MODELS[@]}"; do
        lang=$(echo "$model_spec" | cut -d':' -f1)
        size=$(echo "$model_spec" | cut -d':' -f2)
        expected_model=$(echo "$model_spec" | cut -d':' -f3)
        
        echo "Preparing download for $lang ($size) -> $expected_model..."
        
        # Generate download command with fallback logic
        DOWNLOAD_COMMANDS+="echo 'Downloading model for language: $lang (size: $size)'"$'\n            '
        DOWNLOAD_COMMANDS+="if python -m spacy download ${lang}_core_web_${size}; then"$'\n            '
        DOWNLOAD_COMMANDS+="    echo 'Successfully downloaded ${lang}_core_web_${size}'"$'\n            '
        DOWNLOAD_COMMANDS+="    DOWNLOADED_MODEL=${lang}_core_web_${size}"$'\n            '
        DOWNLOAD_COMMANDS+="elif python -m spacy download ${lang}_core_news_${size}; then"$'\n            '
        DOWNLOAD_COMMANDS+="    echo 'Successfully downloaded ${lang}_core_news_${size}'"$'\n            '
        DOWNLOAD_COMMANDS+="    DOWNLOADED_MODEL=${lang}_core_news_${size}"$'\n            '
        DOWNLOAD_COMMANDS+="else"$'\n            '
        DOWNLOAD_COMMANDS+="    echo 'Warning: Failed to download model for language $lang (size: $size)'"$'\n            '
        DOWNLOAD_COMMANDS+="    DOWNLOADED_MODEL=''"$'\n            '
        DOWNLOAD_COMMANDS+="fi"$'\n            '
        
        # Generate move commands for both possible model names
        MOVE_COMMANDS+="if [ -d /usr/local/lib/python3.12/site-packages/${lang}_core_web_${size} ]; then"$'\n            '
        MOVE_COMMANDS+="    mv /usr/local/lib/python3.12/site-packages/${lang}_core_web_${size} /app/models/spacy/"$'\n            '
        MOVE_COMMANDS+="    mv /usr/local/lib/python3.12/site-packages/${lang}_core_web_${size}-*.dist-info /app/models/spacy/ 2>/dev/null || true"$'\n            '
        MOVE_COMMANDS+="fi"$'\n            '
        MOVE_COMMANDS+="if [ -d /usr/local/lib/python3.12/site-packages/${lang}_core_news_${size} ]; then"$'\n            '
        MOVE_COMMANDS+="    mv /usr/local/lib/python3.12/site-packages/${lang}_core_news_${size} /app/models/spacy/"$'\n            '
        MOVE_COMMANDS+="    mv /usr/local/lib/python3.12/site-packages/${lang}_core_news_${size}-*.dist-info /app/models/spacy/ 2>/dev/null || true"$'\n            '
        MOVE_COMMANDS+="fi"$'\n            '
    done
fi

# Run temporary container with volume mounts
docker run --rm -it \
    -v "$PROJECT_DIR:/app" \
    -v "$PROJECT_DIR/models:/app/models" \
    -v "$PROJECT_DIR/data:/app/data" \
    -w /app \
    geoparser-setup \
    bash -c "
        set -e
        echo 'Installing Python dependencies...'
        pip install -r requirements.txt
        
        if [ '$SKIP_SPACY' = false ]; then
            echo 'Downloading spaCy models for languages: $SUPPORTED_LANGUAGES'
            echo 'Model size: $DEFAULT_MODEL_SIZE'
            $DOWNLOAD_COMMANDS
            
            echo 'Moving spaCy models to mounted directory...'
            $MOVE_COMMANDS
            echo 'spaCy models setup completed!'
        else
            echo 'Skipping spaCy models download - all required models already exist'
        fi
        
        if [ '$SKIP_GEOPARSER' = false ]; then
            echo 'Downloading geoparser data...'
            python -m geoparser download geonames
            
            echo 'Moving geoparser data to mounted directory...'
            if [ -d ~/.local/share/geoparser ]; then
                mv ~/.local/share/geoparser/* /app/data/geoparser/
                rm -rf ~/.local/share/geoparser/
            fi
            echo 'Geoparser data setup completed!'
        else
            echo 'Skipping geoparser data download - already exists'
        fi
        
        echo 'All setup operations completed successfully!'
    "

cat << EOF
┌──────────────────────────────────────────────────────────
│                                                         
│  ✅ Model and data setup completed successfully! ✅    
│                                                         
│  📋 Setup Summary:                                      
│  • Languages: $SUPPORTED_LANGUAGES                      
│  • Model Size: $DEFAULT_MODEL_SIZE                      
│  • SpaCy Models: Ready                                  
│  • GeoNames Data: Ready                                 
│                                                         
│  🚀 You can now run: docker-compose up                 
│                                                         
└──────────────────────────────────────────────────────────
EOF

echo "Models prepared for languages: $SUPPORTED_LANGUAGES (size: $DEFAULT_MODEL_SIZE)"
echo "You can now run: docker-compose up"

# Cleanup operations
echo ""
echo "🧹 Performing cleanup operations..."

# 1. Remove temporary Docker image
echo "Removing temporary Docker image 'geoparser-setup'..."
if docker image inspect geoparser-setup >/dev/null 2>&1; then
    docker rmi geoparser-setup
    echo "✅ Temporary Docker image removed successfully."
else
    echo "ℹ️  Temporary Docker image not found (already cleaned up)."
fi

# 2. Fix file permissions for directories created by Docker containers
echo "Fixing file permissions for directories..."
CURRENT_USER=$(id -u)
CURRENT_GROUP=$(id -g)

# Use Alpine Linux container to fix permissions
echo "Using lightweight Alpine container to fix permissions..."
if ! docker image inspect alpine:latest >/dev/null 2>&1; then
    echo "Pulling lightweight Alpine image (5MB)..."
fi
docker run --rm \
    -v "$PROJECT_DIR/models:/app/models" \
    -v "$PROJECT_DIR/data:/app/data" \
    -v "$PROJECT_DIR/logs:/app/logs" \
    alpine:latest \
    sh -c "chown -R $CURRENT_USER:$CURRENT_GROUP /app/models /app/data /app/logs 2>/dev/null || true"
echo "✅ File permissions fixed using Alpine container."

# 3. Remove Alpine image used for permission fix
echo "Removing Alpine image used for permission fix..."
if docker image inspect alpine:latest >/dev/null 2>&1; then
    docker rmi alpine:latest
    echo "✅ Alpine image removed successfully."
else
    echo "ℹ️  Alpine image not found (already cleaned up)."
fi

echo "🧹 Cleanup completed!"

# Celebration ASCII Logo
cat << "EOF"

    🎉 ═══════════════════════════════════════════════════════════════ 🎉
       __________    __  __  _____         ___                      
      /  _/_  __/___/ / / / / ___/__ ___  / _ \___ ________ ___ ____
     _/ /  / / /___/ /_/ / / (_ / -_) _ \/ ___/ _ `/ __(_-</ -_) __/
    /___/ /_/      \____/  \___/\__/\___/_/   \_,_/_/ /___/\__/_/   
                                                                                                           
                    🌍 Parser Setup Complete! 🌍        
                                v1.0                      
    🎊 ═══════════════════════════════════════════════════════════════ 🎊

EOF