#!/bin/bash

# Azure Deployment Script for RAG AI Agent
# This script automates the deployment to Azure App Service

set -e

echo "=========================================="
echo "RAG AI Agent - Azure Deployment"
echo "=========================================="

# Configuration
RESOURCE_GROUP="rag-ai-agent-rg"
LOCATION="eastus"
APP_SERVICE_PLAN="rag-ai-agent-plan"
WEB_APP_NAME="rag-ai-agent-app"
CONTAINER_REGISTRY="ragaiagentacr"
IMAGE_NAME="rag-ai-agent"
IMAGE_TAG="latest"

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed"
    echo "Please install from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

echo "✓ Azure CLI found"

# Login to Azure
echo ""
echo "Step 1: Azure Login"
echo "-------------------"
az login

# Create Resource Group
echo ""
echo "Step 2: Creating Resource Group"
echo "--------------------------------"
az group create \
    --name $RESOURCE_GROUP \
    --location $LOCATION

echo "✓ Resource group created: $RESOURCE_GROUP"

# Create Container Registry
echo ""
echo "Step 3: Creating Container Registry"
echo "------------------------------------"
az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $CONTAINER_REGISTRY \
    --sku Basic \
    --admin-enabled true

echo "✓ Container registry created: $CONTAINER_REGISTRY"

# Build and push Docker image
echo ""
echo "Step 4: Building and Pushing Docker Image"
echo "------------------------------------------"

# Login to ACR
az acr login --name $CONTAINER_REGISTRY

# Build image
docker build -t $IMAGE_NAME:$IMAGE_TAG -f deployment/Dockerfile .

# Tag image for ACR
ACR_LOGIN_SERVER=$(az acr show --name $CONTAINER_REGISTRY --query loginServer --output tsv)
docker tag $IMAGE_NAME:$IMAGE_TAG $ACR_LOGIN_SERVER/$IMAGE_NAME:$IMAGE_TAG

# Push to ACR
docker push $ACR_LOGIN_SERVER/$IMAGE_NAME:$IMAGE_TAG

echo "✓ Docker image pushed to ACR"

# Create App Service Plan
echo ""
echo "Step 5: Creating App Service Plan"
echo "----------------------------------"
az appservice plan create \
    --name $APP_SERVICE_PLAN \
    --resource-group $RESOURCE_GROUP \
    --is-linux \
    --sku B1

echo "✓ App Service Plan created: $APP_SERVICE_PLAN"

# Create Web App
echo ""
echo "Step 6: Creating Web App"
echo "------------------------"
az webapp create \
    --resource-group $RESOURCE_GROUP \
    --plan $APP_SERVICE_PLAN \
    --name $WEB_APP_NAME \
    --deployment-container-image-name $ACR_LOGIN_SERVER/$IMAGE_NAME:$IMAGE_TAG

echo "✓ Web App created: $WEB_APP_NAME"

# Configure Container Registry credentials
echo ""
echo "Step 7: Configuring Container Registry"
echo "---------------------------------------"
ACR_USERNAME=$(az acr credential show --name $CONTAINER_REGISTRY --query username --output tsv)
ACR_PASSWORD=$(az acr credential show --name $CONTAINER_REGISTRY --query passwords[0].value --output tsv)

az webapp config container set \
    --name $WEB_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --docker-custom-image-name $ACR_LOGIN_SERVER/$IMAGE_NAME:$IMAGE_TAG \
    --docker-registry-server-url https://$ACR_LOGIN_SERVER \
    --docker-registry-server-user $ACR_USERNAME \
    --docker-registry-server-password $ACR_PASSWORD

echo "✓ Container registry configured"

# Configure Environment Variables
echo ""
echo "Step 8: Configuring Environment Variables"
echo "------------------------------------------"
echo "Please enter your Azure OpenAI credentials:"

read -p "Azure OpenAI API Key: " OPENAI_KEY
read -p "Azure OpenAI Endpoint: " OPENAI_ENDPOINT
read -p "Azure OpenAI Deployment Name (default: gpt-4): " DEPLOYMENT_NAME
DEPLOYMENT_NAME=${DEPLOYMENT_NAME:-gpt-4}
read -p "Azure OpenAI Embedding Deployment (default: text-embedding-ada-002): " EMBEDDING_DEPLOYMENT
EMBEDDING_DEPLOYMENT=${EMBEDDING_DEPLOYMENT:-text-embedding-ada-002}

az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $WEB_APP_NAME \
    --settings \
        AZURE_OPENAI_API_KEY="$OPENAI_KEY" \
        AZURE_OPENAI_ENDPOINT="$OPENAI_ENDPOINT" \
        AZURE_OPENAI_DEPLOYMENT_NAME="$DEPLOYMENT_NAME" \
        AZURE_OPENAI_EMBEDDING_DEPLOYMENT="$EMBEDDING_DEPLOYMENT" \
        AZURE_OPENAI_API_VERSION="2024-02-15-preview" \
        VECTOR_STORE_TYPE="faiss" \
        LOG_LEVEL="INFO" \
        WEBSITES_PORT="8000"

echo "✓ Environment variables configured"

# Configure Health Check
echo ""
echo "Step 9: Configuring Health Check"
echo "---------------------------------"
az webapp config set \
    --resource-group $RESOURCE_GROUP \
    --name $WEB_APP_NAME \
    --health-check-path "/api/v1/health"

echo "✓ Health check configured"

# Restart Web App
echo ""
echo "Step 10: Restarting Web App"
echo "----------------------------"
az webapp restart \
    --resource-group $RESOURCE_GROUP \
    --name $WEB_APP_NAME

echo "✓ Web App restarted"

# Get Web App URL
WEB_APP_URL=$(az webapp show --resource-group $RESOURCE_GROUP --name $WEB_APP_NAME --query defaultHostName --output tsv)

echo ""
echo "=========================================="
echo "✓ Deployment Completed Successfully!"
echo "=========================================="
echo ""
echo "Your RAG AI Agent is now deployed at:"
echo "https://$WEB_APP_URL"
echo ""
echo "API Documentation:"
echo "https://$WEB_APP_URL/docs"
echo ""
echo "Health Check:"
echo "https://$WEB_APP_URL/api/v1/health"
echo ""
echo "Resource Group: $RESOURCE_GROUP"
echo "Web App Name: $WEB_APP_NAME"
echo "Container Registry: $CONTAINER_REGISTRY"
echo ""
echo "To update the deployment, run:"
echo "./deployment/update-deployment.sh"
echo "=========================================="
