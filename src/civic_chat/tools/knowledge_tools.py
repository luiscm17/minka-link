from typing import Annotated
from pydantic import Field
from agent_framework import ai_function
from dotenv import load_dotenv

load_dotenv()

@ai_function(
    name="get_civic_knowledge",
    description="Provides information about civic processes and requirements"
)
async def get_civic_knowledge(
    query: Annotated[str, Field(description="The user's question about civic processes")],
    language: Annotated[str, Field(description="Language code (e.g., 'es', 'en')")] = "en"
) -> str:
    """Get information about civic processes based on the query and language."""
    knowledge_base = {
        "voting_requirements": {
            "en": "To vote in most U.S. elections, you must be a U.S. citizen, at least 18 years old, and registered to vote in your state.",
            "es": "Para votar en la mayoría de las elecciones en EE. UU., debe ser ciudadano estadounidense, tener al menos 18 años y estar registrado para votar en su estado."
        },
        "registration": {
            "en": "Voter registration deadlines vary by state. Check your state's election website for specific dates.",
            "es": "Los plazos de registro de votantes varían según el estado. Consulte el sitio web electoral de su estado para conocer las fechas específicas."
        },
        "election_dates": {
            "en": "Election dates vary by location. Check your local election office for the most accurate information.",
            "es": "Las fechas de las elecciones varían según la ubicación. Consulte la oficina electoral local para obtener la información más precisa."
        }
    }

    # Simple keyword matching (in a real app, you'd use a more sophisticated approach)
    query_lower = query.lower()
    lang = language.split("-")[0].lower()  # Handle language codes like 'en-US'
    
    if "vote" in query_lower or "votar" in query_lower:
        return knowledge_base["voting_requirements"].get(lang, knowledge_base["voting_requirements"]["en"])
    elif "register" in query_lower or "registr" in query_lower:
        return knowledge_base["registration"].get(lang, knowledge_base["registration"]["en"])
    elif "election" in query_lower or "elección" in query_lower or "elecciones" in query_lower:
        return knowledge_base["election_dates"].get(lang, knowledge_base["election_dates"]["en"])
    
    return knowledge_base["voting_requirements"].get(lang, knowledge_base["voting_requirements"]["en"])
