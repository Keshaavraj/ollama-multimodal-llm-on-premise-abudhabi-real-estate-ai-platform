# 🐳 Docker Deployment Guide

Complete guide for running the Real Estate AI Platform with Docker.

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Architecture](#architecture)
4. [Configuration](#configuration)
5. [Troubleshooting](#troubleshooting)
6. [Production Deployment](#production-deployment)

---

## Prerequisites

### Required Software
- **Docker**: 20.10 or higher
- **Docker Compose**: 2.0 or higher
- **Ollama**: Running on host machine

### Install Docker

**Linux:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

**macOS:**
```bash
brew install docker docker-compose
```

**Windows:**
Download Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop)

---

## Quick Start

### 1. Ensure Ollama is Running

```bash
# Check Ollama is running on host
ollama list

# If not running, start it
ollama serve
```

### 2. Pull AI Models

```bash
ollama pull llama3.1:8b
ollama pull llava:7b  # Optional for image analysis
```

### 3. Choose Your Version

#### Streamlit Version (Simple)

```bash
cd streamlit-version
docker-compose up
```

Access at: **http://localhost:8501**

#### React Version (Production)

```bash
cd react-version
docker-compose up
```

Access at: **http://localhost:5173**
Backend API: **http://localhost:8000**

### 4. Stop Services

```bash
# Press Ctrl+C, then:
docker-compose down

# To remove volumes as well:
docker-compose down -v
```

---

## Architecture

### React Version

```
┌─────────────────────────────────────────┐
│         Docker Compose                   │
│  ┌────────────┐      ┌────────────┐    │
│  │  Frontend  │      │  Backend   │    │
│  │  (Nginx)   │◄────►│  (FastAPI) │    │
│  │  Port 5173 │      │  Port 8000 │    │
│  └────────────┘      └──────┬─────┘    │
└──────────────────────────────┼──────────┘
                               │
                    ┌──────────▼────────┐
                    │   Ollama (Host)   │
                    │   Port 11434      │
                    └───────────────────┘
```

### Streamlit Version

```
┌────────────────────────────┐
│     Docker Container       │
│  ┌──────────────────┐     │
│  │   Streamlit App  │     │
│  │   Port 8501      │     │
│  └────────┬─────────┘     │
└───────────┼────────────────┘
            │
    ┌───────▼──────┐
    │ Ollama (Host)│
    │ Port 11434   │
    └──────────────┘
```

---

## Configuration

### Environment Variables

Create `.env` file in project root:

```bash
# Backend
OLLAMA_HOST=http://host.docker.internal:11434
BACKEND_PORT=8000

# Frontend
FRONTEND_PORT=5173
VITE_API_URL=http://localhost:8000

# Streamlit
STREAMLIT_PORT=8501
```

### Custom Ports

Edit `docker-compose.yml`:

```yaml
services:
  frontend:
    ports:
      - "3000:80"  # Change 3000 to your preferred port

  backend:
    ports:
      - "9000:8000"  # Change 9000 to your preferred port
```

### Ollama on Remote Host

If Ollama is running on a different machine:

```yaml
services:
  backend:
    environment:
      - OLLAMA_HOST=http://192.168.1.100:11434  # Your Ollama server IP
```

---

## Docker Commands

### Build and Run

```bash
# Build images
docker-compose build

# Run in foreground
docker-compose up

# Run in background (detached)
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
```

### Manage Containers

```bash
# List running containers
docker-compose ps

# Stop services
docker-compose stop

# Start services
docker-compose start

# Restart services
docker-compose restart

# Remove containers
docker-compose down

# Remove containers and volumes
docker-compose down -v
```

### Rebuild After Changes

```bash
# Rebuild specific service
docker-compose build backend

# Rebuild all services
docker-compose build --no-cache

# Rebuild and restart
docker-compose up --build
```

---

## Troubleshooting

### Problem: "Cannot connect to Ollama"

**Solution:**
```bash
# 1. Check Ollama is running on host
ollama list

# 2. Verify host.docker.internal works
docker run --rm alpine ping -c 1 host.docker.internal

# 3. Linux users: Use host IP instead
docker-compose exec backend ping host.docker.internal
# If fails, replace host.docker.internal with your machine IP
```

### Problem: "Port already in use"

**Solution:**
```bash
# Find process using port
sudo lsof -i :8000
# Or
sudo netstat -tulpn | grep 8000

# Kill the process
kill -9 <PID>

# Or change port in docker-compose.yml
```

### Problem: "Frontend can't reach backend"

**Solution:**
```bash
# 1. Check both containers are running
docker-compose ps

# 2. Verify backend is healthy
curl http://localhost:8000/docs

# 3. Check container network
docker network ls
docker network inspect react-version_real-estate-network
```

### Problem: "Models not found"

**Solution:**
```bash
# Ensure models are pulled on HOST machine
ollama list

# Pull models
ollama pull llama3.1:8b
ollama pull llava:7b
```

### Problem: "Build fails on frontend"

**Solution:**
```bash
# Clear npm cache
docker-compose run --rm frontend npm cache clean --force

# Rebuild without cache
docker-compose build --no-cache frontend
```

---

## Production Deployment

### 1. Use Production Compose File

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: always
    environment:
      - OLLAMA_HOST=${OLLAMA_HOST}
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    restart: always
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
```

Run with:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 2. Add Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5173;
    }

    location /api {
        proxy_pass http://localhost:8000;
    }
}
```

### 3. Enable HTTPS with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 4. Set Up Monitoring

```bash
# View resource usage
docker stats

# Setup logging
docker-compose logs -f > app.log

# Health checks (already configured in docker-compose.yml)
docker inspect --format='{{.State.Health.Status}}' <container-id>
```

---

## Best Practices

### Security
- ✅ Don't expose Ollama port publicly
- ✅ Use environment variables for secrets
- ✅ Keep Docker images updated
- ✅ Run containers as non-root user

### Performance
- ✅ Use multi-stage builds (already implemented)
- ✅ Optimize image layers
- ✅ Set resource limits in production
- ✅ Use Docker volumes for persistent data

### Development
- ✅ Use bind mounts for live code reloading
- ✅ Keep development and production configs separate
- ✅ Use `.dockerignore` to reduce build context

---

## Advanced Usage

### Development Mode with Hot Reload

```yaml
# docker-compose.dev.yml
services:
  backend:
    volumes:
      - ./backend:/app
    command: uvicorn server:app --reload --host 0.0.0.0

  frontend:
    volumes:
      - ./frontend/src:/app/src
    command: npm run dev
```

### Multi-Environment Setup

```bash
# Development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## Cleanup

```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune -a

# Remove all unused data
docker system prune -a --volumes

# Nuclear option - remove everything
docker system prune -a --volumes --force
```

---

## Need Help?

- 📖 [Docker Documentation](https://docs.docker.com/)
- 📖 [Docker Compose Docs](https://docs.docker.com/compose/)
- 🐛 [Report Issues](https://github.com/YOUR_USERNAME/REPO_NAME/issues)

---

**Docker setup by Kesavan Rasu**
