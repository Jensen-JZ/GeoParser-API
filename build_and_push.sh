#!/bin/bash

# Build and Push Script for GeoParser API Docker Image
# Usage: ./build_and_push.sh [version] [username]

set -e

# Configuration
DEFAULT_USERNAME="realjensen"
DEFAULT_VERSION="latest"
IMAGE_NAME="geoparser-api"

# Parse arguments
VERSION=${1:-$DEFAULT_VERSION}
USERNAME=${2:-$DEFAULT_USERNAME}
FULL_IMAGE_NAME="${USERNAME}/${IMAGE_NAME}:${VERSION}"

echo "=============================================="
echo "Building and Pushing GeoParser API Docker Image"
echo "=============================================="
echo "Username: ${USERNAME}"
echo "Image: ${IMAGE_NAME}"
echo "Version: ${VERSION}"
echo "Full name: ${FULL_IMAGE_NAME}"
echo "=============================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if logged in to Docker Hub
if ! docker system info | grep -q "Username"; then
    echo "⚠️  You are not logged in to Docker Hub."
    echo "Please run: docker login"
    read -p "Press Enter after logging in..."
fi

# Build the image
echo "🔨 Building Docker image..."
docker build -t ${FULL_IMAGE_NAME} .

# Also tag as latest if not already latest
if [ "${VERSION}" != "latest" ]; then
    docker tag ${FULL_IMAGE_NAME} ${USERNAME}/${IMAGE_NAME}:latest
    echo "📦 Tagged as ${USERNAME}/${IMAGE_NAME}:latest"
fi

# Test the image (basic smoke test)
echo "🧪 Testing the built image..."
CONTAINER_ID=$(docker run -d --rm -p 5001:5000 --name geoparser-test ${FULL_IMAGE_NAME})
sleep 10

# Check if container is running
if docker ps | grep -q geoparser-test; then
    echo "✅ Image test passed - container started successfully"
    docker stop ${CONTAINER_ID}
else
    echo "❌ Error: Image test failed - container did not start properly"
    docker logs ${CONTAINER_ID} || true
    docker stop ${CONTAINER_ID} || true
    exit 1
fi

# Push to Docker Hub
echo "🚀 Pushing to Docker Hub..."
docker push ${FULL_IMAGE_NAME}

if [ "${VERSION}" != "latest" ]; then
    docker push ${USERNAME}/${IMAGE_NAME}:latest
    echo "✅ Pushed ${USERNAME}/${IMAGE_NAME}:latest"
fi

echo "✅ Pushed ${FULL_IMAGE_NAME}"

# Show image info
echo ""
echo "=============================================="
echo "🎉 Successfully pushed to Docker Hub!"
echo "=============================================="
echo "Image: ${FULL_IMAGE_NAME}"
echo "Size: $(docker images ${FULL_IMAGE_NAME} --format 'table {{.Size}}' | tail -n 1)"
echo ""
echo "To use this image:"
echo "  docker pull ${FULL_IMAGE_NAME}"
echo "  docker run -p 5000:5000 ${FULL_IMAGE_NAME}"
echo ""
echo "Docker Hub URL:"
echo "  https://hub.docker.com/r/${USERNAME}/${IMAGE_NAME}"
echo "=============================================="

# Clean up local test artifacts
echo "🧹 Cleaning up..."
docker image prune -f > /dev/null 2>&1 || true

echo "✨ Done!" 