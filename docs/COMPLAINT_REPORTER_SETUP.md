# Complaint Reporter Agent - Technical Documentation

## Overview

The Complaint Reporter Agent is a conversational AI component that facilitates citizen complaint collection and persistence to Azure Cosmos DB. The agent employs natural language processing to gather structured information through an interactive dialogue, ensuring data completeness while maintaining user experience quality.

## Architecture

### Core Components

```
User Input → Complaint Handler → Complaint Reporter Agent → Cosmos DB
                                        ↓
                                  AI Extraction
                                        ↓
                                  Structured Data
```

### Data Flow

1. **Intake**: User initiates complaint through natural language
2. **Extraction**: Agent identifies required fields through conversation
3. **Validation**: System ensures data completeness and format compliance
4. **Persistence**: Structured complaint stored in Cosmos DB
5. **Confirmation**: User receives tracking identifier

## Technical Requirements

### Azure Cosmos DB Configuration

**API Type**: NoSQL (Core SQL)  
**Partition Strategy**: `/location/city`  
**Throughput**: Minimum 400 RU/s (adjustable based on load)

### Environment Configuration

```bash
# Azure Cosmos DB Connection
COSMOS_DB_ENDPOINT=https://<account-name>.documents.azure.com:443/
COSMOS_DB_DATABASE_NAME=<database-name>
COSMOS_DB_CONTAINER_NAME=complaints
COSMOS_DB_MEMORY_CONTAINER_NAME=user_memory

# Authentication (choose one)
# Option 1: Azure CLI (recommended for development)
# Requires: az login

# Option 2: Connection Key
COSMOS_DB_KEY=<primary-key>
```

## Database Schema

### Complaint Document Structure

```json
{
  "id": "uuid",
  "timestamp": "ISO-8601",
  "criticidad": "baja|media|alta",
  "location": {
    "city": "string",
    "address": "string",
    "lat": "number (optional)",
    "lon": "number (optional)"
  },
  "contenido": "string",
  "origen": "texto|voz|web",
  "estado": "en evaluación|en proceso|resuelto|cerrado",
  "usuarioId": "string|null",
  "metadata": {
    "categoria": "string",
    "etiquetas": ["string"]
  },
  "_ts": "unix-timestamp"
}
```

### Partition Key Strategy

The partition key `/location/city` enables:
- Efficient geographic queries
- Scalable data distribution
- City-specific analytics
- Regional compliance requirements

## Infrastructure Setup

### Azure CLI Deployment

```bash
# Create database
az cosmosdb sql database create \
  --account-name <account-name> \
  --resource-group <resource-group> \
  --name civic-complaints

# Create complaints container
az cosmosdb sql container create \
  --account-name <account-name> \
  --resource-group <resource-group> \
  --database-name civic-complaints \
  --name complaints \
  --partition-key-path "/location/city" \
  --throughput 400

# Create user memory container
az cosmosdb sql container create \
  --account-name <account-name> \
  --resource-group <resource-group> \
  --database-name civic-complaints \
  --name user_memory \
  --partition-key-path "/user_id" \
  --throughput 400
```

### Authentication Methods

#### Azure CLI Credential (Recommended)

Leverages existing Azure CLI authentication for seamless development workflow.

```python
from azure.identity import AzureCliCredential
from azure.cosmos import CosmosClient

credential = AzureCliCredential()
client = CosmosClient(endpoint, credential=credential)
```

#### Connection Key

Direct authentication using primary or secondary key from Azure Portal.

```python
from azure.cosmos import CosmosClient

client = CosmosClient(endpoint, credential=key)
```

## Integration

### Agent Framework Integration

The Complaint Reporter operates as a tool within the Complaint Handler agent:

```python
from agents.complaint_reporter_agent import get_complaint_reporter_tool

# Initialize tool
complaint_tool = await get_complaint_reporter_tool()

# Integrate with Complaint Handler
complaint_handler = ChatAgent(
    name="Complaint Handler",
    instructions=COMPLAINT_HANDLER_INSTRUCTIONS,
    tools=[search_311_services, complaint_tool]
)
```

### Conversation Flow

```
User: "I want to report a pothole"
  ↓
Agent: Identifies missing information (city, address, details)
  ↓
Agent: "What city is the problem in?"
  ↓
User: "Buenos Aires, Av. Corrientes 1234"
  ↓
Agent: Collects additional details through natural dialogue
  ↓
Agent: Structures data and persists to Cosmos DB
  ↓
Agent: Returns tracking ID to user
```

## Data Access Patterns

### Query Examples

```python
from azure.cosmos import CosmosClient
from azure.identity import AzureCliCredential

# Initialize client
credential = AzureCliCredential()
client = CosmosClient(endpoint, credential=credential)
database = client.get_database_client("civic-complaints")
container = database.get_container_client("complaints")

# Query by city (efficient - uses partition key)
query = "SELECT * FROM c WHERE c.location.city = @city"
parameters = [{"name": "@city", "value": "Buenos Aires"}]
items = container.query_items(
    query=query,
    parameters=parameters,
    enable_cross_partition_query=False
)

# Query by status across cities
query = "SELECT * FROM c WHERE c.estado = @status ORDER BY c.timestamp DESC"
parameters = [{"name": "@status", "value": "en evaluación"}]
items = container.query_items(
    query=query,
    parameters=parameters,
    enable_cross_partition_query=True
)

# Aggregate by category
query = """
    SELECT c.metadata.categoria, COUNT(1) as count
    FROM c
    GROUP BY c.metadata.categoria
"""
items = container.query_items(
    query=query,
    enable_cross_partition_query=True
)
```

## Monitoring and Observability

### Key Metrics

- **Complaint Volume**: Track complaints per city/category
- **Response Time**: Agent conversation completion time
- **Data Quality**: Completeness of required fields
- **User Satisfaction**: Tracking ID retrieval rate

### Cosmos DB Metrics

Monitor through Azure Portal:
- Request Units (RU) consumption
- Storage utilization
- Query performance
- Throttling events

## Security Considerations

### Data Protection

- **Encryption at Rest**: Enabled by default in Cosmos DB
- **Encryption in Transit**: TLS 1.2+ for all connections
- **PII Handling**: User IDs anonymized, no direct personal information stored
- **Access Control**: RBAC for database operations

### Compliance

- **Data Residency**: Configure Cosmos DB region per compliance requirements
- **Retention Policies**: Implement TTL for complaint lifecycle management
- **Audit Logging**: Enable diagnostic settings for compliance tracking

## Troubleshooting

### Common Issues

**Connection Failures**
- Verify `COSMOS_DB_ENDPOINT` format includes `https://` and port `:443/`
- Confirm Azure CLI authentication: `az account show`
- Check network connectivity and firewall rules

**Permission Errors**
- Ensure user has "Cosmos DB Built-in Data Contributor" role
- Verify resource group and subscription access
- Check key validity if using connection string authentication

**Performance Issues**
- Monitor RU consumption in Azure Portal
- Consider increasing provisioned throughput
- Optimize queries to use partition key
- Implement caching for frequent queries

## API Reference

### Complaint Reporter Tool

```python
@ai_function
def save_complaint(
    complaint_json: Annotated[str, "JSON string with complaint data"]
) -> str:
    """
    Persists structured complaint to Cosmos DB.
    
    Args:
        complaint_json: Serialized complaint object
        
    Returns:
        Success message with tracking ID or error details
    """
```

### Expected Input Format

```json
{
  "criticidad": "baja|media|alta",
  "location": {
    "city": "required",
    "address": "required",
    "lat": "optional",
    "lon": "optional"
  },
  "contenido": "required",
  "origen": "texto",
  "estado": "en evaluación",
  "usuarioId": null,
  "metadata": {
    "categoria": "inferred",
    "etiquetas": ["tag1", "tag2"]
  }
}
```

## Performance Optimization

### Indexing Strategy

Default indexing policy is sufficient for most queries. Consider custom indexing for:
- Frequent range queries on timestamp
- Geospatial queries on coordinates
- Full-text search on complaint content### Query Optimization
- Use partition key for efficient geographic queries
- Consider caching frequently accessed data
- Optimize queries to avoid full table scans

## References

- [Azure Cosmos DB Documentation](https://learn.microsoft.com/en-us/azure/cosmos-db/)
- [Python SDK Reference](https://learn.microsoft.com/en-us/python/api/overview/azure/cosmos-readme)
- [Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/)
- [Azure Identity Library](https://learn.microsoft.com/en-us/python/api/overview/azure/identity-readme)

---

**Version**: 1.0  
**Maintained By**: Minka Link Development Team
