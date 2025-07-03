#!/bin/bash
set -e

# ASCII Logo for container startup
cat << "EOF"
    __________    __  __   ______           ____                           
   /  _/_  __/   / / / /  / ____/__  ____  / __ \____ ______________  _____
   / /  / /_____/ / / /  / / __/ _ \/ __ \/ /_/ / __ `/ ___/ ___/ _ \/ ___/
 _/ /  / /_____/ /_/ /  / /_/ /  __/ /_/ / ____/ /_/ / /  (__  )  __/ /    
/___/ /_/      \____/   \____/\___/\____/_/    \__,_/_/  /____/\___/_/     
                                                                           
                                        
        🚀 GeoParser Container Starting Up 🚀
                     Version: v1.0          

        Author: Jingyao Zhang
        Contact: jingyao.zhang@it-u.at

EOF

echo "Starting GeoParser container entrypoint..."

# Load environment variables from .env file
if [ -f "/app/.env" ]; then
    echo "Loading environment variables from .env file..."
    export $(grep -v '^#' "/app/.env" | xargs)
else
    echo "Warning: .env file not found. Using default languages."
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

# Function to create symlink if it doesn't exist
create_symlink() {
    local target=$1
    local link=$2
    
    if [ -e "$target" ]; then
        # Ensure parent directory exists
        local parent_dir=$(dirname "$link")
        mkdir -p "$parent_dir"
        
        if [ ! -L "$link" ] || [ "$(readlink "$link")" != "$target" ]; then
            echo "Creating symlink: $link -> $target"
            # Remove existing file/directory/symlink
            rm -rf "$link"
            ln -sf "$target" "$link"
        else
            echo "Symlink already exists: $link -> $target"
        fi
    else
        echo "Warning: Target does not exist: $target"
    fi
}

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p /root/.local/share

# Parse supported languages and model sizes, build model list dynamically
IFS=',' read -ra LANG_ARRAY <<< "$SUPPORTED_LANGUAGES"
IFS=',' read -ra SIZE_ARRAY <<< "$AVAILABLE_MODEL_SIZES"
SPACY_MODELS=()

echo "Building spaCy model list from supported languages and model sizes..."
for lang in "${LANG_ARRAY[@]}"; do
    # Remove whitespace
    lang=$(echo "$lang" | tr -d ' ')
    if [ -n "$lang" ]; then
        # Check for each available model size
        for size in "${SIZE_ARRAY[@]}"; do
            size=$(echo "$size" | tr -d ' ')
            if [ -n "$size" ]; then
                expected_model=$(get_expected_model_name "$lang" "$size")
                
                # Check if the model directory actually exists
                if [ -d "/app/models/spacy/$expected_model" ]; then
                    SPACY_MODELS+=("$expected_model")
                    echo "  - Found model for $lang ($size): $expected_model"
                fi
            fi
        done
    fi
done

if [ ${#SPACY_MODELS[@]} -eq 0 ]; then
    echo "Warning: No spaCy models found! Check your model setup."
else
    echo "Will create symlinks for ${#SPACY_MODELS[@]} spaCy models"
fi

# Setup spaCy model symlinks
echo "Setting up spaCy model symlinks..."
for model in "${SPACY_MODELS[@]}"; do
    # Model directory
    if [ -d "/app/models/spacy/$model" ]; then
        create_symlink "/app/models/spacy/$model" "/usr/local/lib/python3.12/site-packages/$model"
    fi
    
    # Model dist-info directory (handle version wildcards)
    dist_info_dir=$(find /app/models/spacy -maxdepth 1 -name "${model}-*.dist-info" 2>/dev/null | head -1)
    if [ -n "$dist_info_dir" ]; then
        dist_info_name=$(basename "$dist_info_dir")
        create_symlink "$dist_info_dir" "/usr/local/lib/python3.12/site-packages/$dist_info_name"
    fi
done

# Setup geoparser data symlink
echo "Setting up geoparser data symlink..."
if [ -d "/app/data/geoparser" ]; then
    create_symlink "/app/data/geoparser" "/root/.local/share/geoparser"
else
    echo "Warning: Geoparser data directory not found at /app/data/geoparser"
fi

# Verify setup
echo "Verifying setup..."
echo "Python packages directory:"
if [ ${#SPACY_MODELS[@]} -gt 0 ]; then
    # Create grep pattern from model names
    grep_pattern=$(IFS='|'; echo "${SPACY_MODELS[*]}")
    ls -la /usr/local/lib/python3.12/site-packages/ | grep -E "($grep_pattern)" || echo "No spaCy model symlinks found"
else
    echo "No spaCy models to verify"
fi

echo "Geoparser data:"
ls -la /root/.local/share/ | grep geoparser || echo "No geoparser symlink found"

echo "Entrypoint setup completed!"
echo "Active spaCy models: ${SPACY_MODELS[*]}"

# Display startup success message
cat << "EOF"
┌──────────────────────────────────────────────────────────
│                                                         
│  🎯 GeoParser Service Ready! 🎯                        
│                                                         
│  📍 Service Status: STARTING                           
│  🌐 Port: 5000                                         
│  🧠 Models: Loaded                                     
│  🗄️  Data: Ready                                        
│                                                         
│  🔗 API Endpoints:                                     
│  • Health: http://localhost:5000/api/health           
│  • Parse: http://localhost:5000/api/parse             
│                                                         
└──────────────────────────────────────────────────────────
EOF

# Start the main application
echo "Starting application: $@"
exec "$@"