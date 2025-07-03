# Docker Deployment Guide for GeoParser API

## 📚 Overview

This guide covers how to deploy the GeoParser API using Docker, including building custom images and using pre-built images from Docker Hub.

## 🚀 Quick Start with Pre-built Image

### 1. Prerequisites
- Docker and Docker Compose installed
- `.env` file configured (see main README)

### 2. Download Models and Data
```bash
bash setup_models.sh
```

### 3. Run with Pre-built Image
```bash
# Using docker-compose (recommended)
docker-compose -f docker-compose.prod.yml up -d

# Or using direct Docker command
docker run -d \
  --name geoparser-api \
  -p 5000:5000 \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --env-file .env \
  realjensen/geoparser-api:latest
```

## 🔧 Development Deployment

### Build and Run Locally
```bash
# Build from source
docker-compose up -d

# View logs
docker-compose logs -f geoparser

# Stop
docker-compose down
```

## 📦 Publishing to Docker Hub

### Method 1: Automated Script (Recommended)

```bash
# Make script executable
chmod +x build_and_push.sh

# Build and push with default settings
./build_and_push.sh

# Build and push specific version
./build_and_push.sh v1.2

# Build and push with custom username
./build_and_push.sh latest your-dockerhub-username
```

### Method 2: Manual Process

```bash
# 1. Login to Docker Hub
docker login

# 2. Build production image
docker build -f Dockerfile.prod -t your-username/geoparser-api:latest .

# 3. Test the image
docker run -d --rm -p 5001:5000 --name test-geoparser your-username/geoparser-api:latest
# Wait a moment, then check
curl http://localhost:5001/api/health
docker stop test-geoparser

# 4. Push to Docker Hub
docker push your-username/geoparser-api:latest

# 5. Optional: Tag and push specific versions
docker tag your-username/geoparser-api:latest your-username/geoparser-api:v1.0
docker push your-username/geoparser-api:v1.0
```

## 📁 File Structure for Docker Deployment

```
GeoParser-API/
├── Dockerfile                 # Development Dockerfile
├── Dockerfile.prod           # Production-optimized Dockerfile
├── docker-compose.yml        # Development compose file
├── docker-compose.prod.yml   # Production compose file
├── build_and_push.sh        # Automated build and push script
├── requirements.txt          # Python dependencies
├── entrypoint.sh            # Container entrypoint script
├── .env                     # Environment configuration
├── app/                     # Application source code
├── models/                  # SpaCy models (created by setup_models.sh)
├── data/                    # GeoNames data (created by setup_models.sh)
└── logs/                    # Application logs
```

## 🔍 Configuration Files Explained

### `Dockerfile` vs `Dockerfile.prod`
- **Dockerfile**: Development build, includes build tools
- **Dockerfile.prod**: Multi-stage build for smaller production image with security optimizations

### `docker-compose.yml` vs `docker-compose.prod.yml`
- **docker-compose.yml**: Local development, builds from source
- **docker-compose.prod.yml**: Production deployment, uses pre-built image from Docker Hub

## 🏷️ Tagging Strategy

### Recommended Tags
- `latest`: Most recent stable version
- `v1.0`, `v1.1`, etc.: Semantic versioning
- `dev`: Development/testing versions

### Example Tagging Commands
```bash
# Tag current build as version 1.0
docker tag realjensen/geoparser-api:latest realjensen/geoparser-api:v1.0

# Push both tags
docker push realjensen/geoparser-api:latest
docker push realjensen/geoparser-api:v1.0
```

## 🔒 Security Considerations

### Image Security
- Production image runs as non-root user
- Minimal base image (python:3.12-slim)
- No unnecessary packages in final image

### Runtime Security
```bash
# Run with limited capabilities
docker run --cap-drop=ALL --cap-add=NET_BIND_SERVICE \
  -p 5000:5000 realjensen/geoparser-api:latest

# Use read-only root filesystem
docker run --read-only \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -v /tmp:/tmp \
  realjensen/geoparser-api:latest
```

## 🐛 Troubleshooting

### Common Issues

1. **Permission Denied on Models/Data Directories**
   ```bash
   sudo chown -R $(whoami):$(whoami) models/ data/ logs/
   ```

2. **Out of Memory During Build**
   ```bash
   # Increase Docker memory limit or use smaller model sizes
   # Edit .env: AVAILABLE_MODEL_SIZES=sm,md (remove lg)
   ```

3. **GPU Support Not Working**
   ```bash
   # Check NVIDIA runtime
   docker info | grep nvidia
   
   # Install NVIDIA Container Toolkit if missing
   ```

4. **Image Pull Fails**
   ```bash
   # Check internet connection and Docker Hub status
   docker pull hello-world
   
   # Try different tag
   docker pull realjensen/geoparser-api:v1.0
   ```

### Debugging Commands

```bash
# Check running containers
docker ps

# Inspect container logs
docker logs geoparser-api

# Execute commands in running container
docker exec -it geoparser-api bash

# Check container resource usage
docker stats geoparser-api

# Inspect image layers
docker history realjensen/geoparser-api:latest
```

## 📊 Performance Optimization

### Multi-stage Build Benefits
- Reduced image size (removes build dependencies)
- Faster deployment and downloads
- Better security (fewer packages)

### Runtime Optimization
```yaml
# In docker-compose.prod.yml
deploy:
  resources:
    limits:
      memory: 8G      # Adjust based on model size
      cpus: '2.0'     # Adjust based on workload
    reservations:
      memory: 4G
      cpus: '1.0'
```

## 🌐 Production Deployment Tips

1. **Use specific version tags** in production, not `latest`
2. **Set up health checks** and monitoring
3. **Configure log rotation** to prevent disk space issues
4. **Use secrets management** for sensitive environment variables
5. **Set up automated backups** for model and data directories

## 📞 Support

If you encounter issues:
1. Check this troubleshooting guide
2. Review container logs
3. Consult the main README.md
4. Open an issue on GitHub

---

**Happy Dockerizing! 🐳** 