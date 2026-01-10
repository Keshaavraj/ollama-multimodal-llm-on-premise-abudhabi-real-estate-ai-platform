# 📦 Installation Guide

Complete step-by-step installation guide for all platforms.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Ollama Installation](#ollama-installation)
3. [Model Setup](#model-setup)
4. [Project Setup](#project-setup)
5. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

**Minimum:**
- CPU: 4 cores
- RAM: 8GB
- Storage: 15GB free
- OS: Linux, macOS, Windows (with WSL2)

**Recommended:**
- CPU: 8+ cores (Intel i7/AMD Ryzen 7)
- RAM: 16GB+
- GPU: NVIDIA RTX 3060+ (4GB+ VRAM) or equivalent
- Storage: 20GB+ SSD

### Software Requirements

- **Python**: 3.10 or higher
- **Node.js**: 18.0 or higher (for React version)
- **npm**: 9.0 or higher
- **Git**: Latest version

---

## Ollama Installation

### Linux / WSL2

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Verify installation
ollama --version

# Start Ollama service (usually auto-starts)
ollama serve
```

### macOS

```bash
# Download from ollama.com
# Or use Homebrew
brew install ollama

# Start service
ollama serve
```

### Windows

1. Download installer from [ollama.com/download](https://ollama.com/download)
2. Run `OllamaSetup.exe`
3. Ollama starts automatically as a service

**For WSL2 Users:**
```bash
# Inside WSL2 terminal
curl -fsSL https://ollama.com/install.sh | sh
```

---

## Model Setup

### Download AI Models

```bash
# Text model (required) - ~4.7GB, 5-10 minutes
ollama pull llama3.1:8b

# Vision model (optional) - ~4.5GB, 5-10 minutes
ollama pull llava:7b

# Verify models installed
ollama list
```

Expected output:
```
NAME            SIZE    MODIFIED
llama3.1:8b    4.7 GB  X minutes ago
llava:7b       4.5 GB  X minutes ago
```

### Test Models

```bash
# Test text model
ollama run llama3.1:8b "Hello, tell me about real estate"

# Test vision model (requires image)
ollama run llava:7b "Describe this image" --image path/to/image.jpg
```

---

## Project Setup

### 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/ollama-multimodal-llm-on-premise-real-estate-ai.git
cd ollama-multimodal-llm-on-premise-real-estate-ai
```

### 2. Choose Your Version

#### Option A: Streamlit (Quick Start)

```bash
cd streamlit-version

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app.py
```

✅ Access at: `http://localhost:8501`

#### Option B: React (Production)

**Backend Setup:**
```bash
cd react-version/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start server
python server.py
```

✅ Backend at: `http://localhost:8000`

**Frontend Setup (New Terminal):**

**IMPORTANT for WSL2 users:** Use Linux npm (not Windows npm) to avoid UNC path issues!

```bash
# First-time setup: Install nvm (Node Version Manager) in WSL2
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Load nvm
source ~/.nvm/nvm.sh

# Install Node.js LTS
nvm install --lts
nvm use node

# Verify using Linux npm (not Windows npm)
which npm  # Should output: /home/username/.nvm/versions/node/.../bin/npm
           # NOT: /mnt/c/Program Files/nodejs/npm
```

```bash
cd react-version/frontend

# Load nvm (if not already in ~/.bashrc)
source ~/.nvm/nvm.sh && nvm use node

# Clean install (if previous Windows npm was used)
rm -rf node_modules package-lock.json

# Install Node.js dependencies
npm install

# Start development server
npm run dev
```

✅ Frontend at: `http://localhost:5173`

**Pro Tip:** Add to `~/.bashrc` for auto-loading:
```bash
echo 'source ~/.nvm/nvm.sh' >> ~/.bashrc
echo 'nvm use node >/dev/null 2>&1' >> ~/.bashrc
source ~/.bashrc
```

---

## Platform-Specific Notes

### Windows (WSL2)

1. **Install WSL2:**
```powershell
wsl --install
```

2. **Update WSL:**
```powershell
wsl --update
```

3. **Install Ubuntu:**
```powershell
wsl --install -d Ubuntu-22.04
```

4. **Access project in WSL:**
```bash
cd ~
# Follow Linux installation steps
```

### macOS

**Install Homebrew (if not installed):**
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**Install Python:**
```bash
brew install python@3.11
```

**Install Node.js:**
```bash
brew install node
```

### Linux (Ubuntu/Debian)

**Update system:**
```bash
sudo apt update && sudo apt upgrade -y
```

**Install Python:**
```bash
sudo apt install python3.11 python3.11-venv python3-pip
```

**Install Node.js:**
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

---

## Troubleshooting

### Ollama Issues

**Problem: Command 'ollama' not found**
```bash
# Check if installed
which ollama

# If not found, reinstall
curl -fsSL https://ollama.com/install.sh | sh

# Add to PATH (Linux/macOS)
export PATH=$PATH:/usr/local/bin
```

**Problem: Models won't download**
```bash
# Check disk space
df -h

# Check Ollama service
ollama list

# Restart Ollama
pkill ollama
ollama serve
```

**Problem: Out of memory**
- Close other applications
- Use smaller models: `ollama pull llama3.2:3b`
- Add swap space (Linux)

### Python Issues

**Problem: ModuleNotFoundError**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Problem: Permission denied**
```bash
# Use virtual environment (recommended)
python3 -m venv venv

# Or fix permissions
chmod +x script.py
```

### Node.js Issues

**Problem: npm install fails**
```bash
# Clear cache
npm cache clean --force

# Delete node_modules
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

**Problem: Port 5173 already in use**
```bash
# Kill process on port
lsof -ti:5173 | xargs kill -9

# Or use different port
npm run dev -- --port 3000
```

### Network Issues

**Problem: CORS errors**
- Check backend CORS settings in `server.py`
- Ensure frontend uses correct API URL
- Restart both servers

**Problem: Can't access localhost**
- Check firewall settings
- Use `127.0.0.1` instead of `localhost`
- Check if ports are blocked

---

## Verification

### Check All Components

```bash
# 1. Ollama
ollama --version
ollama list

# 2. Python
python --version
pip list | grep -E "ollama|fastapi|streamlit"

# 3. Node.js (for React version)
node --version
npm --version

# 4. Git
git --version
```

### Success Indicators

✅ Ollama shows installed models
✅ Python dependencies installed without errors
✅ Node modules installed successfully
✅ Application starts without errors
✅ Can access web interface

---

## Next Steps

1. **Test the application** with sample queries
2. **Customize settings** in config files
3. **Read** [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system
4. **Explore** API documentation at `http://localhost:8000/docs`

---

## Need Help?

- 📝 Check [GitHub Issues](https://github.com/YOUR_USERNAME/ollama-multimodal-llm-on-premise-real-estate-ai/issues)
- 📧 Contact: kesavan.rasu@example.com
- 💬 Join discussions on GitHub

---

**Installation Time Estimate:**
- Ollama: 5 minutes
- Models: 10-20 minutes
- Project setup: 5-10 minutes
- **Total: 20-35 minutes**
