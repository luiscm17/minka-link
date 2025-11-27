"""Validation constants and helpers for neutrality enforcement."""

import logging
from typing import Dict

logger = logging.getLogger(__name__)

# Prohibited bias keywords that indicate political bias
BIAS_KEYWORDS = [
    # English voting recommendations
    "should vote for",
    "you should vote",
    "recommend voting for",
    "recommend you vote for",
    "suggest voting for",
    "suggest you vote for",
    
    # English candidate/party preferences
    "best candidate",
    "better candidate",
    "superior candidate",
    "best party",
    "better party",
    "superior party",
    "more trustworthy",
    "more qualified",
    "more experienced than",
    
    # English policy opinions
    "superior policy",
    "better policy",
    "best policy",
    "right choice",
    "wrong choice",
    "smart choice",
    "foolish choice",
    
    # English endorsements
    "support this candidate",
    "support this party",
    "endorse",
    "back this candidate",
    
    # Spanish voting recommendations
    "deberías votar por",
    "debe votar por",
    "recomiendo votar",
    "sugiero votar",
    
    # Spanish candidate/party preferences
    "mejor candidato",
    "mejor partido",
    "candidato superior",
    "partido superior",
    "más confiable",
    "más calificado",
    
    # Spanish policy opinions
    "mejor política",
    "política superior",
    "elección correcta",
    "elección incorrecta",
    
    # Spanish endorsements
    "apoyar este candidato",
    "apoyar este partido",
    "respaldar",
]

# Azure Content Safety severity threshold
# Severity levels: 0 (safe) to 6 (high severity)
# We reject anything with severity >= 2
CONTENT_SAFETY_THRESHOLD = 2

# Violation tracking threshold
# Alert after this many violations
VIOLATION_THRESHOLD = 10


def get_generic_neutral_response(language: str = "en") -> str:
    """Get a generic neutral response when validation fails.
    
    This response is used as a fallback when all regeneration attempts
    fail and we need to provide a safe, neutral response to the user.
    
    Args:
        language: Language code for the response (en or es)
    
    Returns:
        Generic neutral response in the specified language
    """
    responses: Dict[str, str] = {
        "en": (
            "I apologize, but I'm unable to provide a complete answer to your question "
            "while maintaining strict political neutrality. However, I can help you with:\n\n"
            "- General information about government structure and processes\n"
            "- Voting requirements and registration procedures\n"
            "- Election dates and civic participation\n"
            "- Official government resources and websites\n\n"
            "Please visit https://www.usa.gov for comprehensive, official information, "
            "or feel free to rephrase your question."
        ),
        "es": (
            "Disculpe, pero no puedo proporcionar una respuesta completa a su pregunta "
            "mientras mantengo estricta neutralidad política. Sin embargo, puedo ayudarle con:\n\n"
            "- Información general sobre la estructura y procesos del gobierno\n"
            "- Requisitos y procedimientos de registro para votar\n"
            "- Fechas de elecciones y participación cívica\n"
            "- Recursos y sitios web oficiales del gobierno\n\n"
            "Por favor visite https://www.usa.gov/espanol para información oficial completa, "
            "o siéntase libre de reformular su pregunta."
        )
    }
    
    return responses.get(language, responses["en"])
