# Generate a random 6-digit number using nanoseconds
RANDOM_NUM=$(($(date +%N) % 9000 + 1000))

# Resource names
RESOURCE_GROUP="rg-chatbot-${RANDOM_NUM}"
FOUNDRY_RESOURCE="foundry-chatbot-${RANDOM_NUM}"
FOUNDRY_PROJECT="pj-chatbot-${RANDOM_NUM}"
OPENAI_RESOURCE="openai-chatbot-${RANDOM_NUM}"
SEARCH_SERVICE="search-chatbot-${RANDOM_NUM}"
STORAGE_ACCOUNT="stchatbot${RANDOM_NUM}"
TRANSLATE_RESOURCE="translate-chatbot-${RANDOM_NUM}"
LOCATION="eastus"

# Check if Azure CLI is logged in
az account show >/dev/null 2>&1
if [ $? != 0 ]; then
    echo "Please log in to Azure CLI first using 'az login'"
    exit 1
fi

# Create resource group
echo "Creating resource group: ${RESOURCE_GROUP}"
az group create --name "${RESOURCE_GROUP}" --location "${LOCATION}"

# 1. Create AI Foundry Resource
echo "Creating AI Foundry resource: $FOUNDRY_RESOURCE"
az cognitiveservices account create \
    --name "${FOUNDRY_RESOURCE}" \
    --resource-group "${RESOURCE_GROUP}" \
    --kind AIServices \
    --location "${LOCATION}" \
    --sku S0 \
    --custom-domain "${FOUNDRY_RESOURCE}" \
    --allow-project-management

# 2. Create AI Foundry Project
echo "Creating AI Foundry project: $FOUNDRY_PROJECT"
az cognitiveservices account project create \
    --name "${FOUNDRY_RESOURCE}" \
    --resource-group "${RESOURCE_GROUP}" \
    --project-name "${FOUNDRY_PROJECT}" \
    --location "${LOCATION}"

# 3. Deploy GPT-4.1-mini model
echo "Deploying GPT-4.1-mini model"
az cognitiveservices account deployment create \
    --name "${FOUNDRY_RESOURCE}" \
    --resource-group "${RESOURCE_GROUP}" \
    --deployment-name gpt41mini-deployment \
    --model-name gpt-4.1-mini \
    --model-version "2025-04-14" \
    --model-format OpenAI \
    --sku-capacity 50 \
    --sku-name GlobalStandard

# 4. Create Azure AI Search service
echo "Creating Azure AI Search service: $SEARCH_SERVICE"
az search service create \
    --name "${SEARCH_SERVICE}" \
    --resource-group "${RESOURCE_GROUP}" \
    --location "${LOCATION}" \
    --sku basic \
    --partition-count 1 \
    --replica-count 1

# 5. Create Azure Storage Account
echo "Creating Azure Storage Account: $STORAGE_ACCOUNT"
az storage account create \
    --name "${STORAGE_ACCOUNT}" \
    --resource-group "${RESOURCE_GROUP}" \
    --location "${LOCATION}" \
    --sku Standard_LRS

# 6. Get the endpoints and deployment status
echo "Retrieving endpoints and deployment status..."
FOUNDRY_ENDPOINT=$(az cognitiveservices account show \
    --name "${FOUNDRY_RESOURCE}" \
    --resource-group "${RESOURCE_GROUP}" \
    --query "properties.endpoint" -o tsv)

# 7. Create Azure AI Translate service
az cognitiveservices account create \
    --name "${TRANSLATE_RESOURCE}" \
    --resource-group "${RESOURCE_GROUP}" \
    --kind TextTranslation \
    --sku S1 \
    --location "${LOCATION}"

TRANSLATE_ENDPOINT=$(az cognitiveservices account show \
    --name "${TRANSLATE_RESOURCE}" \
    --resource-group "${RESOURCE_GROUP}" \
    --query "properties.endpoint" -o tsv)

# Get the deployment status
DEPLOYMENT_STATUS=$(az cognitiveservices account deployment show \
    --name "${FOUNDRY_RESOURCE}" \
    --resource-group "${RESOURCE_GROUP}" \
    --deployment-name gpt41mini-deployment \
    --query "properties.provisioningState" -o tsv 2>/dev/null || echo "Not Found")

# 8. Display configuration
echo -e "\n\n=== Azure Resource Configuration ==="
echo "Resource Group: $RESOURCE_GROUP"
echo "Location: $LOCATION"
echo ""
echo "=== AI Foundry ==="
echo "Foundry Resource: $FOUNDRY_RESOURCE"
echo "Foundry Project: $FOUNDRY_PROJECT"
echo "Foundry Endpoint: $FOUNDRY_ENDPOINT"
echo "Model Deployment Status: $DEPLOYMENT_STATUS"
echo ""
echo "=== Other Services ==="
echo "AI Search Service: $SEARCH_SERVICE.search.windows.net"
echo "Storage Account: $STORAGE_ACCOUNT.blob.core.windows.net"
echo "Translate Service: $TRANSLATE_RESOURCE"
echo "Translate Endpoint: $TRANSLATE_ENDPOINT"
echo ""
echo "=== Next Steps ==="
echo "1. Update your .env file with the following values:"
echo "   AZURE_AI_ENDPOINT=${FOUNDRY_ENDPOINT}"
echo "   AZURE_AI_PROJECT_NAME=${FOUNDRY_PROJECT}"
echo "   AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt41mini-deployment"
echo "   AZURE_SEARCH_SERVICE=${SEARCH_SERVICE}.search.windows.net"
echo "   AZURE_STORAGE_ACCOUNT=${STORAGE_ACCOUNT}.blob.core.windows.net"
echo "   AZURE_TRANSLATE_ENDPOINT=${TRANSLATE_ENDPOINT}"
echo ""
echo "2. Make sure you're logged in to Azure CLI:"
echo "   az login"
echo ""
echo "3. Your application will use Azure CLI credentials automatically."