import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(env_path)

# Configuración de Azure OpenAI
class AzureOpenAIConfig:
    ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
    API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION', '2024-10-21')
    DEPLOYMENT = os.getenv('AZURE_OPENAI_CHAT_DEPLOYMENT_NAME')

# Configuración de Azure AI Project (Foundry)
class AzureAIProjectConfig:
    ENDPOINT = os.getenv('AZURE_AI_PROJECT_ENDPOINT')
    VECTOR_STORE_ID = os.getenv('AZURE_AI_VECTOR_STORE_ID')  # ID del vector store con documentos
    SEARCH_INDEX_NAME = os.getenv('AZURE_AI_SEARCH_INDEX_NAME', 'civic-bot-rag')  # Nombre del índice de AI Search

# Configuración de Bing Search
class BingSearchConfig:
    CONNECTION_ID = os.getenv('BING_CONNECTION_ID')

# Configuración de Azure AI Search (para RAG local)
class AzureSearchConfig:
    ENDPOINT = os.getenv('AZURE_SEARCH_ENDPOINT')
    KEY = os.getenv('AZURE_SEARCH_KEY')  # Opcional si usas Azure CLI auth
    INDEX_NAME = os.getenv('AZURE_SEARCH_INDEX_NAME', 'civic-bot-rag')

# Configuración de Cosmos DB (para almacenar denuncias)
class CosmosDBConfig:
    ENDPOINT = os.getenv('COSMOS_DB_ENDPOINT')
    KEY = os.getenv('COSMOS_DB_KEY')  # Opcional si usas Azure CLI auth
    DATABASE_NAME = os.getenv('COSMOS_DB_DATABASE_NAME')
    CONTAINER_NAME = os.getenv('COSMOS_DB_CONTAINER_NAME', 'complaints')
    # Container para memoria de usuario
    MEMORY_CONTAINER_NAME = os.getenv('COSMOS_DB_MEMORY_CONTAINER_NAME', 'user_memory')


# Configuración de la aplicación
class Settings:
    AZURE_OPENAI = AzureOpenAIConfig()
    AZURE_AI_PROJECT = AzureAIProjectConfig()
    BING_SEARCH = BingSearchConfig()
    AZURE_SEARCH = AzureSearchConfig()
    COSMOS_DB = CosmosDBConfig()
    
    @classmethod
    def validate(cls):
        """Valida la configuración mínima requerida."""
        if not cls.AZURE_OPENAI.ENDPOINT:
            raise ValueError("AZURE_OPENAI_ENDPOINT es requerido en .env")
        if not cls.AZURE_OPENAI.DEPLOYMENT:
            raise ValueError("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME es requerido en .env")
    
    @classmethod
    def validate_cosmos_db(cls):
        """Valida la configuración de Cosmos DB para denuncias."""
        if not cls.COSMOS_DB.ENDPOINT:
            raise ValueError("COSMOS_DB_ENDPOINT no está configurado en .env")
        if not cls.COSMOS_DB.DATABASE_NAME:
            raise ValueError("COSMOS_DB_DATABASE_NAME no está configurado en .env")
        if not cls.COSMOS_DB.CONTAINER_NAME:
            raise ValueError("COSMOS_DB_CONTAINER_NAME no está configurado en .env")
    
    @classmethod
    def validate_cosmos_db_memory(cls):
        """Valida la configuración de Cosmos DB para memoria de usuario."""
        if not cls.COSMOS_DB.ENDPOINT:
            raise ValueError("COSMOS_DB_ENDPOINT no está configurado en .env")
        if not cls.COSMOS_DB.DATABASE_NAME:
            raise ValueError("COSMOS_DB_DATABASE_NAME no está configurado en .env")
        if not cls.COSMOS_DB.MEMORY_CONTAINER_NAME:
            raise ValueError("COSMOS_DB_MEMORY_CONTAINER_NAME no está configurado en .env")
    
    @classmethod
    def is_bing_configured(cls) -> bool:
        """Verifica si Bing Search está configurado."""
        return bool(cls.BING_SEARCH.CONNECTION_ID)
    
    @classmethod
    def is_foundry_configured(cls) -> bool:
        """Verifica si Azure AI Foundry está configurado."""
        return bool(cls.AZURE_AI_PROJECT.ENDPOINT)
    
    @classmethod
    def is_azure_search_configured(cls) -> bool:
        """Verifica si Azure AI Search está configurado."""
        return bool(cls.AZURE_SEARCH.ENDPOINT and cls.AZURE_SEARCH.INDEX_NAME)
    
    @classmethod
    def is_cosmos_db_configured(cls) -> bool:
        """Verifica si Cosmos DB está configurado."""
        return bool(
            cls.COSMOS_DB.ENDPOINT and
            cls.COSMOS_DB.DATABASE_NAME and
            cls.COSMOS_DB.CONTAINER_NAME
        )

# Instancia de configuración
settings = Settings()
settings.validate()