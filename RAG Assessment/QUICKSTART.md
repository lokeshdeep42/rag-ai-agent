# Quick Start Guide - RAG AI Agent

## ✅ Step 1: Dependencies Installed

All Python packages have been successfully installed!

## 📝 Step 2: Configure Azure OpenAI Credentials

Before running the system, you need to add your Azure OpenAI credentials.

### Create `.env` file:

1. Copy the `.env.example` file to `.env`:
   ```powershell
   Copy-Item .env.example .env
   ```

2. Edit `.env` and add your Azure OpenAI credentials:
   ```env
   AZURE_OPENAI_API_KEY=your_actual_api_key_here
   AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
   AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
   ```

### Required Information:

- **API Key**: Your Azure OpenAI API key
- **Endpoint**: Your Azure OpenAI resource endpoint URL
- **Deployment Name**: Your GPT-4 deployment name (or gpt-35-turbo)
- **Embedding Deployment**: Your embedding model deployment name

## 🚀 Step 3: Initialize the System

Once you've configured `.env`, run:

```powershell
python setup.py
```

This will:
- Process the 5 sample documents
- Generate embeddings
- Create the FAISS vector index
- Save everything to `data/vector_store/`

## ▶️ Step 4: Start the Application

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then visit:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

## 🧪 Step 5: Test the API

### Test RAG Query:
```powershell
curl -X POST http://localhost:8000/api/v1/ask `
  -H "Content-Type: application/json" `
  -d '{\"query\": \"What is the company leave policy?\"}'
```

### Test Direct Answer:
```powershell
curl -X POST http://localhost:8000/api/v1/ask `
  -H "Content-Type: application/json" `
  -d '{\"query\": \"What is the capital of France?\"}'
```

---

## 📚 Sample Documents Included

1. **hr_policies.txt** - HR policies, leave, benefits
2. **product_faq.txt** - CloudSync product FAQ
3. **security_policies.txt** - IT security policies
4. **onboarding_guide.txt** - Employee onboarding
5. **api_documentation.txt** - API documentation

---

## ❓ Need Help?

- See `README.md` for complete documentation
- See `walkthrough.md` for detailed implementation guide
- Check `/docs` endpoint for interactive API documentation

---

**Ready to proceed? Add your Azure OpenAI credentials to `.env` and run `python setup.py`!**
