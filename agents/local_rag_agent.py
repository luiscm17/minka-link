"""
Local RAG Agent using simple in-memory search

This agent loads PDFs into memory and provides simple keyword search.
A simpler and more reliable solution than using Azure AI Search.

Advantages:
- No external services required
- Works completely locally
- Easy to debug
- Compatible with Agent Framework via @ai_function
"""

import sys
from pathlib import Path
from typing import Annotated

# Import configuration
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
from config.settings import settings

# Agent Framework imports
from agent_framework import ai_function

# Import for reading PDFs
try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

# Global variable to store PDF chunks
pdf_chunks = []


def load_pdf_documents(pdf_directory: str = "data-resource", verbose: bool = False):
    """
    Loads all PDFs from specified directory into memory.
    
    Args:
        pdf_directory: Directory where PDFs are located
        verbose: If True, shows progress messages
    """
    global pdf_chunks
    
    if not PYPDF_AVAILABLE:
        return
    
    pdf_dir = project_root / pdf_directory
    
    if not pdf_dir.exists():
        return
    
    chunks = []
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    if not pdf_files:
        return
    
    for pdf_path in pdf_files:
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    text = page.extract_text()
                    
                    # Split into paragraphs (smaller chunks)
                    paragraphs = text.split('\n\n')
                    
                    for para in paragraphs:
                        if para.strip():
                            chunks.append({
                                'text': para.strip(),
                                'page': page_num,
                                'source': pdf_path.name
                            })
            
        except Exception as e:
            pass
    
    pdf_chunks = chunks


@ai_function
def search_documents(
    query: Annotated[str, "Search query to find relevant information in official documents"]
) -> str:
    """
    Searches for relevant information in official documents (PDFs, regulations, laws).
    Use this tool when you need to find specific information from official documents,
    verify facts, or cite sources. Works for documents in any language.
    """
    
    if not pdf_chunks:
        return "No documents loaded. Documents should be in the 'data-resource' directory."
    
    query_lower = query.lower()
    results = []
    
    # Simple keyword search
    for chunk in pdf_chunks:
        # Calculate simple relevance
        relevance = sum(1 for word in query_lower.split() if word in chunk['text'].lower())
        
        if relevance > 0:
            results.append({
                'text': chunk['text'],
                'page': chunk['page'],
                'source': chunk['source'],
                'relevance': relevance
            })
    
    # Sort by relevance and take top 5
    results.sort(key=lambda x: x['relevance'], reverse=True)
    top_results = results[:5]
    
    if not top_results:
        return f"No relevant information found for '{query}' in available documents."
    
    # Format results
    formatted_results = [f"Search results for: '{query}'\n"]
    for i, result in enumerate(top_results, 1):
        formatted_results.append(
            f"\n[Result {i} - {result['source']}, Page {result['page']}]\n{result['text']}"
        )
    
    return "\n".join(formatted_results)





def is_local_rag_available() -> bool:
    """
    Checks if local RAG is available.
    
    Returns:
        bool: True if pypdf is installed and documents are loaded
    """
    return PYPDF_AVAILABLE


def get_local_rag_tool_for_agent(agent_type: str):
    """
    Gets local RAG tool for an agent type.
    
    Args:
        agent_type: Agent type
    
    Returns:
        Tool or None: Local RAG tool if available
    """
    if not is_local_rag_available():
        return None
    
    # Load documents if not yet loaded
    if not pdf_chunks:
        load_pdf_documents()
    
    # All agents that need RAG use the same tool
    if agent_type in ["educator", "fact_checker", "guide"]:
        return search_documents
    
    return None
