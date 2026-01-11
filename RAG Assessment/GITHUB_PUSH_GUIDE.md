# Step-by-Step Guide: Push Code to GitHub

## 📋 Prerequisites

1. **GitHub account** - Create one at https://github.com if you don't have one
2. **Git installed** - ✅ Already installed on your system

---

## 🚀 Steps to Push to GitHub

### Step 1: Create a New Repository on GitHub

1. Go to https://github.com
2. Click the **"+"** button (top right) → **"New repository"**
3. Fill in:
   - **Repository name**: `rag-ai-agent` (or any name you prefer)
   - **Description**: "RAG-based AI Agent with Azure OpenAI integration"
   - **Visibility**: Choose **Private** or **Public**
   - **DO NOT** initialize with README (we already have one)
4. Click **"Create repository"**

### Step 2: Initialize Git and Add Files

Open your terminal in the project directory and run:

```powershell
# Make sure you're in the project directory
cd "d:\Python\RAG Assessment"

# Initialize git (already done)
git init

# Add all files (respects .gitignore)
git add .

# Create first commit
git commit -m "Initial commit: RAG AI Agent with Azure OpenAI"
```

### Step 3: Connect to GitHub Repository

After creating the repository on GitHub, you'll see commands. Use these:

```powershell
# Add remote repository (replace YOUR_USERNAME and REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/rag-ai-agent.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

**Example:**
```powershell
git remote add origin https://github.com/johndoe/rag-ai-agent.git
git branch -M main
git push -u origin main
```

### Step 4: Enter GitHub Credentials

When prompted:
- **Username**: Your GitHub username
- **Password**: Use a **Personal Access Token** (not your password)

**To create a Personal Access Token:**
1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Give it a name: "RAG AI Agent"
4. Select scopes: Check **"repo"**
5. Click "Generate token"
6. **Copy the token** (you won't see it again!)
7. Use this token as your password when pushing

---

## ✅ Verify Upload

After pushing, go to your GitHub repository URL:
```
https://github.com/YOUR_USERNAME/rag-ai-agent
```

You should see all your files!

---

## 🔒 Security Check

Your `.gitignore` file already excludes:
- ✅ `.env` (API keys won't be uploaded)
- ✅ `data/vector_store/` (large files excluded)
- ✅ `__pycache__/` (Python cache excluded)
- ✅ Virtual environments

**Your API keys are safe!** ✅

---

## 📝 Quick Commands Summary

```powershell
# 1. Add all files
git add .

# 2. Commit
git commit -m "Initial commit: RAG AI Agent with Azure OpenAI"

# 3. Add remote (replace with your URL)
git remote add origin https://github.com/YOUR_USERNAME/rag-ai-agent.git

# 4. Push
git push -u origin main
```

---

## 🎯 After Pushing

Your GitHub repository will contain:
- ✅ All source code
- ✅ Documentation (README, QUICKSTART)
- ✅ Sample documents
- ✅ Deployment files
- ✅ Configuration templates
- ❌ No API keys or secrets (protected by .gitignore)

**Perfect for submission or sharing!** 🚀

---

## 🔄 Future Updates

To push changes later:
```powershell
git add .
git commit -m "Description of changes"
git push
```

---

**Ready to start? Create the GitHub repository first, then run the commands!**
