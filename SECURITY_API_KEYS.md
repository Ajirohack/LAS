# Security Best Practices - API Keys

## ⚠️ IMPORTANT: API Key Security

**NEVER commit API keys to version control!**

This document outlines how to properly handle API keys in the LAS project.

---

## 🔒 Secure API Key Management

### 1. Environment Variables (Recommended)

Store API keys in environment variables, not in code:

```bash
# Set in your shell profile (~/.bashrc, ~/.zshrc, etc.)
export OLLAMA_API_KEY="your_ollama_cloud_api_key"
export OPENROUTER_API_KEY="your_openrouter_api_key"
export GOOGLE_API_KEY="your_google_api_key"
```

### 2. .env File (Local Development)

Create a `.env` file in `las-v1/las_core/` (this file is gitignored):

```bash
# Copy the example file
cp .env.example .env

# Edit with your actual keys
nano .env
```

### 3. Docker Secrets (Production)

For production deployments, use Docker secrets or your cloud provider's secret management:

```yaml
# docker-compose.yml
services:
  backend:
    environment:
      - OLLAMA_API_KEY=${OLLAMA_API_KEY}
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
```

---

## ✅ What's Protected

### Files in .gitignore

- `.env` - Local environment variables
- `.env.local` - Local overrides
- `*.key` - Any key files
- `secrets/` - Secrets directory

### Example Files (Safe to Commit)

- `.env.example` - Template with placeholders
- Documentation with placeholder keys

---

## 🚫 What NOT to Do

❌ **DON'T** hardcode API keys in source code:

```python
# BAD - Don't do this!
api_key = "sk-or-v1-abc123..."
```

❌ **DON'T** commit .env files with real keys

❌ **DON'T** share API keys in public repositories

❌ **DON'T** include keys in Docker images

---

## ✅ What TO Do

✅ **DO** use environment variables:

```python
# GOOD
import os
api_key = os.getenv("OPENROUTER_API_KEY")
```

✅ **DO** use .env files (gitignored)

✅ **DO** provide .env.example with placeholders

✅ **DO** document required environment variables

---

## 🔑 Getting API Keys

### Ollama Cloud

1. Visit: <https://ollama.com/settings/keys>
2. Create new API key
3. Set: `export OLLAMA_API_KEY="your_key"`

### OpenRouter

1. Visit: <https://openrouter.ai/settings/keys>
2. Create new API key
3. Set: `export OPENROUTER_API_KEY="sk-or-v1-..."`

### Google Gemini

1. Visit: <https://aistudio.google.com/app/apikey>
2. Create API key
3. Set: `export GOOGLE_API_KEY="AIza..."`

---

## 🧪 Testing with API Keys

### Running Tests

```bash
# Set environment variables first
export OLLAMA_API_KEY="your_key"
export OPENROUTER_API_KEY="your_key"
export GOOGLE_API_KEY="your_key"

# Then run tests
python3 test_providers.py
```

### Docker Compose

```bash
# Create .env file with your keys
cp .env.example .env
nano .env  # Add your real keys

# Docker Compose will automatically load .env
docker-compose up -d
```

---

## 🔍 Checking for Exposed Keys

Before committing, always check:

```bash
# Search for potential API keys in staged files
git diff --cached | grep -i "api.key\|secret\|password"

# Check if .env is gitignored
git check-ignore .env  # Should output: .env
```

---

## 🚨 If You Accidentally Commit a Key

1. **Immediately revoke the key** on the provider's dashboard
2. Generate a new key
3. Remove from git history:

   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch path/to/file" \
     --prune-empty --tag-name-filter cat -- --all
   ```

4. Force push (if already pushed):

   ```bash
   git push origin --force --all
   ```

---

## 📋 Checklist

Before committing:

- [ ] No API keys in source code
- [ ] .env file is gitignored
- [ ] .env.example has placeholders only
- [ ] Documentation doesn't contain real keys
- [ ] Docker images don't contain keys
- [ ] CI/CD uses secret management

---

**Remember: Security is everyone's responsibility!**
