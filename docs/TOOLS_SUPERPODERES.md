# Agent Tools - Technical Specification

## Overview

Agent tools extend the capabilities of AI agents beyond language model inference, enabling interaction with external systems, data sources, and APIs. This document outlines the tool architecture, implementation patterns, and recommended integrations for the Minka Link multi-agent system.

## Tool Architecture

### Tool Types

**Function Tools**  
Python functions decorated with `@ai_function` that execute custom logic and return structured data.

**Agent Tools**  
Specialized agents exposed as tools to other agents, enabling hierarchical agent composition.

**Hosted Tools**  
Azure-provided capabilities including Bing Search, Code Interpreter, and File Search.

**MCP Tools**  
Model Context Protocol tools for standardized external integrations.

## Agent-Specific Tool Specifications

### Civic Router

**Purpose**: Query classification and agent routing  
**Tool Requirements**: None

The router maintains minimal overhead for optimal latency. Tool execution occurs in specialized agents post-routing.

---

### Civic Educator

**Purpose**: Civic concept explanation and democratic education

#### Knowledge Base Search

```python
@ai_function
async def search_civic_knowledge(
    query: Annotated[str, "Civic concept or topic"],
    category: Annotated[str, "Category filter"] = "general",
    language: Annotated[str, "Response language"] = "en"
) -> dict:
    """
    Retrieves verified civic information from indexed knowledge base.
    Implements semantic search over official government documents.
    
    Returns:
        dict: {
            "results": List[dict],
            "sources": List[str],
            "confidence": float
        }
    """
```

**Implementation**: Azure AI Search with vector embeddings for semantic retrieval.

#### Glossary Service

```python
@ai_function
def get_civic_term_definition(
    term: Annotated[str, "Civic terminology"],
    jurisdiction: Annotated[str, "Geographic scope"] = "federal"
) -> dict:
    """
    Provides standardized definitions for civic terminology.
    Maintains consistency across agent responses.
    
    Returns:
        dict: {
            "term": str,
            "definition": str,
            "examples": List[str],
            "related_terms": List[str]
        }
    """
```

**Implementation**: Structured database with jurisdiction-specific terminology.

---

### Citizen Guide

**Purpose**: Practical civic service information and guidance

#### Service Discovery

```python
@ai_function
async def search_government_services(
    service_type: Annotated[str, "Service category"],
    location: Annotated[str, "Geographic identifier"],
    language: Annotated[str, "Preferred language"] = "en"
) -> dict:
    """
    Queries government service directory for location-specific information.
    
    Returns:
        dict: {
            "services": List[dict],
            "locations": List[dict],
            "hours": dict,
            "contact": dict
        }
    """
```

**Data Source**: Open Data API, municipal service directories

#### Polling Location Finder

```python
@ai_function
async def find_polling_location(
    address: Annotated[str, "Voter address"],
    election_date: Annotated[str, "Election date"] = None
) -> dict:
    """
    Determines assigned polling location for voter address.
    
    Returns:
        dict: {
            "polling_place": str,
            "address": str,
            "hours": str,
            "accessibility": dict,
            "early_voting": List[dict]
        }
    """
```

**Data Source**: Board of Elections API, voter registration database

#### Document Requirements

```python
@ai_function
def get_document_requirements(
    service: Annotated[str, "Service identifier"],
    user_status: Annotated[str, "Citizenship status"] = "citizen"
) -> dict:
    """
    Enumerates required documentation for government services.
    
    Returns:
        dict: {
            "required": List[str],
            "optional": List[str],
            "alternatives": dict,
            "notes": str
        }
    """
```

**Implementation**: Structured requirements database with service-specific rules

---

### Complaint Handler

**Purpose**: Citizen complaint routing and submission

#### 311 Service Integration

```python
@ai_function
async def search_311_services(
    problem_type: Annotated[str, "Problem description"],
    category: Annotated[str, "Problem category"] = None
) -> dict:
    """
    Identifies appropriate 311 service for reported problem.
    
    Returns:
        dict: {
            "service_code": str,
            "service_name": str,
            "description": str,
            "submission_method": str,
            "expected_response_time": str
        }
    """
```

**Data Source**: NYC 311 API, municipal service request systems

#### Complaint Classification

```python
@ai_function
def classify_complaint_type(
    description: Annotated[str, "Problem description"],
    location: Annotated[str, "Problem location"] = None
) -> dict:
    """
    Categorizes complaint for appropriate departmental routing.
    
    Returns:
        dict: {
            "category": str,
            "subcategory": str,
            "department": str,
            "priority": str,
            "evidence_requirements": List[str]
        }
    """
```

**Implementation**: ML-based classification with rule-based fallback

#### Status Tracking

```python
@ai_function
async def track_complaint_status(
    complaint_id: Annotated[str, "Complaint identifier"]
) -> dict:
    """
    Retrieves current status of submitted complaint.
    
    Returns:
        dict: {
            "status": str,
            "last_updated": str,
            "assigned_to": str,
            "estimated_resolution": str,
            "updates": List[dict]
        }
    """
```

**Data Source**: 311 tracking API, internal complaint database

---

### Fact Checker

**Purpose**: Information verification against official sources

#### Official Source Search

```python
@ai_function
async def search_official_sources(
    query: Annotated[str, "Information to verify"],
    source_types: Annotated[List[str], "Source categories"] = ["gov"],
    jurisdiction: Annotated[str, "Geographic scope"] = "federal"
) -> dict:
    """
    Searches government and official sources for verification.
    Restricted to .gov, .gob, and verified official domains.
    
    Returns:
        dict: {
            "results": List[dict],
            "sources": List[str],
            "verification_status": str,
            "confidence": float
        }
    """
```

**Implementation**: Bing Custom Search with domain restrictions

#### Legal Reference Lookup

```python
@ai_function
async def lookup_regulation(
    topic: Annotated[str, "Legal topic"],
    jurisdiction: Annotated[str, "Legal jurisdiction"],
    effective_date: Annotated[str, "Date of interest"] = None
) -> dict:
    """
    Retrieves relevant laws and regulations.
    
    Returns:
        dict: {
            "regulations": List[dict],
            "citations": List[str],
            "effective_dates": dict,
            "amendments": List[dict]
        }
    """
```

**Data Source**: Legal databases, municipal code repositories

#### Census Data Access

```python
@ai_function
async def get_census_data(
    metric: Annotated[str, "Statistical metric"],
    location: Annotated[str, "Geographic area"],
    year: Annotated[int, "Census year"] = None
) -> dict:
    """
    Retrieves official census statistics.
    
    Returns:
        dict: {
            "value": float,
            "margin_of_error": float,
            "year": int,
            "source": str,
            "methodology": str
        }
    """
```

**Data Source**: US Census Bureau API

## Implementation Patterns

### Error Handling

```python
@ai_function
async def resilient_api_call(query: str) -> dict:
    """Implements retry logic and graceful degradation."""
    try:
        response = await external_api.call(query)
        return response
    except APIError as e:
        logger.error(f"API call failed: {e}")
        return {
            "error": True,
            "message": "Service temporarily unavailable",
            "fallback": "Contact service directly at [contact]"
        }
    except Exception as e:
        logger.exception("Unexpected error in tool execution")
        return {"error": True, "message": "Internal error occurred"}
```

### Caching Strategy

```python
from functools import lru_cache
from datetime import datetime, timedelta

class CachedTool:
    def __init__(self, ttl_minutes: int = 60):
        self.cache = {}
        self.ttl = timedelta(minutes=ttl_minutes)
    
    def get(self, key: str):
        if key in self.cache:
            value, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.ttl:
                return value
        return None
    
    def set(self, key: str, value: any):
        self.cache[key] = (value, datetime.now())

@ai_function
async def cached_office_hours(office_type: str) -> dict:
    """Caches office hours for 24 hours."""
    cache_key = f"hours:{office_type}"
    cached = tool_cache.get(cache_key)
    if cached:
        return cached
    
    result = await fetch_office_hours(office_type)
    tool_cache.set(cache_key, result)
    return result
```

### Rate Limiting

```python
import asyncio
from collections import defaultdict
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, calls_per_minute: int = 60):
        self.limit = calls_per_minute
        self.calls = defaultdict(list)
    
    async def acquire(self, key: str):
        now = datetime.now()
        window_start = now - timedelta(minutes=1)
        
        # Remove old calls
        self.calls[key] = [
            t for t in self.calls[key] 
            if t > window_start
        ]
        
        # Check limit
        if len(self.calls[key]) >= self.limit:
            sleep_time = (self.calls[key][0] - window_start).total_seconds()
            await asyncio.sleep(sleep_time)
        
        self.calls[key].append(now)

rate_limiter = RateLimiter(calls_per_minute=60)

@ai_function
async def rate_limited_api_call(query: str) -> dict:
    """Implements rate limiting for external API."""
    await rate_limiter.acquire("external_api")
    return await external_api.call(query)
```

## External Service Integration

### NYC Open Data

**Endpoint**: `https://data.cityofnewyork.us/`  
**Authentication**: API Token (optional, increases rate limits)  
**Rate Limit**: 1000 requests/hour (unauthenticated)

### NYC 311 API

**Endpoint**: `https://api.nyc.gov/`  
**Authentication**: API Key (required)  
**Rate Limit**: Varies by endpoint

### US Census Bureau

**Endpoint**: `https://api.census.gov/data/`  
**Authentication**: API Key (required)  
**Rate Limit**: 500 requests/day (free tier)

### Bing Custom Search

**Endpoint**: Azure Cognitive Services  
**Authentication**: Subscription Key  
**Rate Limit**: Based on pricing tier

## Performance Considerations

### Tool Selection Criteria

- **Latency**: Target <500ms for synchronous tools
- **Reliability**: Minimum 99.9% uptime for critical tools
- **Cost**: Monitor API usage and optimize call patterns
- **Accuracy**: Validate tool outputs against known test cases

### Optimization Strategies

1. **Parallel Execution**: Execute independent tools concurrently
2. **Result Caching**: Cache stable data (office hours, definitions)
3. **Lazy Loading**: Initialize tools on first use
4. **Connection Pooling**: Reuse HTTP connections for API calls

## Security

### API Key Management

- Store keys in Azure Key Vault
- Rotate keys quarterly
- Use managed identities where possible
- Never commit keys to version control

### Data Validation

- Sanitize user inputs before API calls
- Validate API responses against schemas
- Implement output filtering for PII
- Log security-relevant events

## Monitoring

### Key Metrics

- **Tool Invocation Rate**: Calls per minute/hour
- **Success Rate**: Successful vs failed executions
- **Latency Distribution**: P50, P95, P99 response times
- **Error Types**: Categorized failure modes

### Alerting Thresholds

- Error rate >5% over 5 minutes
- Latency P95 >2 seconds
- Rate limit approaching (>80% of quota)
- External service downtime

## Testing

### Unit Tests

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_polling_location_finder():
    with patch('external_api.call') as mock_call:
        mock_call.return_value = {
            "polling_place": "Test Location",
            "address": "123 Test St"
        }
        
        result = await find_polling_location("123 Main St")
        
        assert result["polling_place"] == "Test Location"
        mock_call.assert_called_once()
```

### Integration Tests

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_311_service_integration():
    """Test against actual 311 API (requires credentials)."""
    result = await search_311_services("pothole")
    
    assert "service_code" in result
    assert result["service_code"] is not None
```

## References

- [Microsoft Agent Framework - Function Tools](https://learn.microsoft.com/en-us/agent-framework/tutorials/agents/function-tools)
- [Azure AI Search Documentation](https://learn.microsoft.com/en-us/azure/search/)
- [NYC Open Data API](https://dev.socrata.com/foundry/data.cityofnewyork.us/)
- [US Census Bureau API](https://www.census.gov/data/developers/guidance.html)

---

**Version**: 1.0  
**Maintained By**: Minka Link Development Team
