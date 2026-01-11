# Interactive setup script to configure Azure OpenAI credentials
# Run this with: python configure_env.py

import os
from pathlib import Path

print("=" * 60)
print("RAG AI Agent - Azure OpenAI Configuration")
print("=" * 60)
print()

# Check if .env already exists
env_file = Path(".env")
if env_file.exists():
    print("⚠️  .env file already exists!")
    overwrite = input("Do you want to overwrite it? (yes/no): ").lower()
    if overwrite != 'yes':
        print("Configuration cancelled.")
        exit(0)

print("Please enter your Azure OpenAI credentials:")
print("(You can find these in Azure Portal → Your OpenAI Resource → Keys and Endpoint)")
print()

# Get credentials from user
api_key = input("Azure OpenAI API Key: ").strip()
endpoint = input("Azure OpenAI Endpoint (e.g., https://your-resource.openai.azure.com/): ").strip()

print()
print("Which model did you deploy?")
print("  1. gpt-4o (recommended)")
print("  2. gpt-4o-mini")
print("  3. gpt-35-turbo")
print("  4. Custom (enter manually)")

choice = input("Enter choice (1-4): ").strip()

deployment_map = {
    "1": "gpt-4o",
    "2": "gpt-4o-mini",
    "3": "gpt-35-turbo"
}

if choice in deployment_map:
    deployment_name = deployment_map[choice]
else:
    deployment_name = input("Enter your deployment name: ").strip()

embedding_deployment = input("Embedding deployment name (press Enter for 'text-embedding-ada-002'): ").strip()
if not embedding_deployment:
    embedding_deployment = "text-embedding-ada-002"

# Validate inputs
if not api_key or not endpoint:
    print("\n❌ Error: API Key and Endpoint are required!")
    exit(1)

# Create .env content
env_content = f"""# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY={api_key}
AZURE_OPENAI_ENDPOINT={endpoint}
AZURE_OPENAI_DEPLOYMENT_NAME={deployment_name}
AZURE_OPENAI_EMBEDDING_DEPLOYMENT={embedding_deployment}
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Vector Store Configuration
VECTOR_STORE_TYPE=faiss
VECTOR_STORE_PATH=./data/vector_store

# Application Settings
APP_NAME=RAG AI Agent
APP_VERSION=1.0.0
LOG_LEVEL=INFO
SESSION_TIMEOUT_MINUTES=30

# API Settings
CORS_ORIGINS=["*"]
MAX_QUERY_LENGTH=2000
"""

# Write to .env file
with open(".env", "w") as f:
    f.write(env_content)

print()
print("=" * 60)
print("✅ Configuration saved to .env file!")
print("=" * 60)
print()
print("Your configuration:")
print(f"  Endpoint: {endpoint}")
print(f"  Deployment: {deployment_name}")
print(f"  Embedding: {embedding_deployment}")
print()
print("Next steps:")
print("  1. Run: python setup.py")
print("  2. Run: uvicorn app.main:app --reload")
print()
print("=" * 60)
