"""
NYC Services Tools - Herramientas para acceder a servicios de NYC

Estas tools proporcionan acceso a información oficial de la ciudad de Nueva York,
incluyendo lugares de votación, servicios 311, y oficinas gubernamentales.
"""

from typing import Annotated
from pydantic import Field
from agent_framework import ai_function


# ============================================================================
# POLLING LOCATION TOOLS
# ============================================================================

@ai_function(
    name="find_polling_location",
    description="Encuentra el lugar de votación asignado para una dirección en NYC"
)
def find_polling_location(
    address: Annotated[str, Field(description="Dirección completa del votante en NYC")]
) -> dict:
    """
    Busca el lugar de votación asignado para una dirección específica.
    
    En producción, esto se conectaría con la API del NYC Board of Elections.
    Por ahora, retorna datos simulados para demostración.
    
    Args:
        address: Dirección completa incluyendo calle, ciudad y código postal
    
    Returns:
        dict: Información del lugar de votación incluyendo dirección, horarios y accesibilidad
    """
    # TODO: Integrar con NYC Board of Elections API
    # URL: https://vote.nyc/page/voter-information
    
    # Datos simulados para demostración
    return {
        "status": "success",
        "polling_place": {
            "name": "PS 123 - Brooklyn Elementary School",
            "address": "456 Main Street, Brooklyn, NY 11201",
            "hours": "6:00 AM - 9:00 PM",
            "election_date": "Next scheduled election",
            "accessible": True,
            "parking_available": True,
            "public_transit": "Subway: A, C lines to Jay St-MetroTech"
        },
        "early_voting": {
            "available": True,
            "locations": [
                {
                    "name": "Brooklyn Borough Hall",
                    "address": "209 Joralemon Street, Brooklyn, NY 11201",
                    "dates": "Check vote.nyc for current early voting dates"
                }
            ]
        },
        "note": "Para información actualizada, visita vote.nyc o llama al 1-866-VOTE-NYC"
    }


@ai_function(
    name="check_voter_registration",
    description="Verifica el estado de registro de votante y proporciona información sobre cómo registrarse"
)
def check_voter_registration(
    borough: Annotated[str, Field(description="Borough de NYC: Manhattan, Brooklyn, Queens, Bronx, Staten Island")] = "Manhattan"
) -> dict:
    """
    Proporciona información sobre cómo verificar el registro de votante y cómo registrarse.
    
    Args:
        borough: Borough de NYC donde reside el votante
    
    Returns:
        dict: Información sobre registro de votantes y recursos
    """
    return {
        "status": "success",
        "registration_info": {
            "check_status": {
                "url": "https://voterlookup.elections.ny.gov/",
                "phone": "1-866-VOTE-NYC (1-866-868-3692)",
                "description": "Verifica tu estado de registro en línea o por teléfono"
            },
            "how_to_register": {
                "online": {
                    "url": "https://dmv.ny.gov/more-info/electronic-voter-registration-application",
                    "requirements": "Licencia de conducir o ID estatal de NY",
                    "deadline": "25 días antes de las elecciones"
                },
                "by_mail": {
                    "form_url": "https://www.elections.ny.gov/NYSBOE/download/voting/voteform_spanish.pdf",
                    "deadline": "Debe estar matasellado 25 días antes de las elecciones"
                },
                "in_person": {
                    "locations": [
                        "Oficinas del Board of Elections",
                        "DMV",
                        "Bibliotecas públicas",
                        "Agencias gubernamentales"
                    ]
                }
            },
            "eligibility": {
                "requirements": [
                    "Ser ciudadano de los Estados Unidos",
                    "Tener al menos 18 años el día de las elecciones",
                    "Residir en NYC al menos 30 días antes de las elecciones",
                    "No estar cumpliendo sentencia en prisión por delito grave"
                ]
            }
        },
        "borough_office": {
            "name": f"{borough} Board of Elections",
            "note": "Contacta al 311 para la dirección y horarios específicos"
        }
    }


# ============================================================================
# 311 SERVICES TOOLS
# ============================================================================

@ai_function(
    name="search_311_services",
    description="Busca servicios 311 de NYC para reportar problemas o solicitar información"
)
def search_311_services(
    problem_type: Annotated[str, Field(description="Tipo de problema: pothole, garbage, noise, graffiti, etc.")]
) -> dict:
    """
    Busca el servicio 311 apropiado para un tipo de problema específico.
    
    Args:
        problem_type: Descripción del tipo de problema a reportar
    
    Returns:
        dict: Información sobre cómo reportar el problema y qué esperar
    """
    # Mapeo de problemas comunes a servicios 311
    problem_categories = {
        "pothole": {
            "service": "Street Condition - Pothole",
            "department": "Department of Transportation (DOT)",
            "description": "Reportar baches en calles de NYC",
            "what_to_provide": [
                "Ubicación exacta (calle e intersección)",
                "Tamaño aproximado del bache",
                "Fotos si es posible"
            ],
            "response_time": "Varía según severidad, típicamente 1-7 días"
        },
        "garbage": {
            "service": "Sanitation Condition",
            "department": "Department of Sanitation (DSNY)",
            "description": "Reportar basura acumulada, contenedores desbordados",
            "what_to_provide": [
                "Ubicación exacta",
                "Tipo de basura (residencial, comercial)",
                "Fotos si es posible"
            ],
            "response_time": "1-3 días hábiles"
        },
        "noise": {
            "service": "Noise Complaint",
            "department": "NYPD o DEP (según tipo)",
            "description": "Reportar ruido excesivo",
            "what_to_provide": [
                "Dirección exacta de donde proviene el ruido",
                "Tipo de ruido (música, construcción, etc.)",
                "Horario del ruido"
            ],
            "response_time": "Varía, emergencias llamar al 911",
            "note": "Para ruido de construcción fuera de horario, contactar DEP"
        },
        "graffiti": {
            "service": "Graffiti Removal",
            "department": "Department of Sanitation (DSNY)",
            "description": "Solicitar remoción de grafiti",
            "what_to_provide": [
                "Ubicación exacta",
                "Tipo de superficie (pared, poste, etc.)",
                "Fotos"
            ],
            "response_time": "5-10 días hábiles"
        }
    }
    
    # Buscar categoría más cercana
    problem_lower = problem_type.lower()
    matched_category = None
    
    for key in problem_categories:
        if key in problem_lower:
            matched_category = problem_categories[key]
            break
    
    if not matched_category:
        # Categoría genérica
        matched_category = {
            "service": "General Inquiry",
            "department": "311 Customer Service",
            "description": "Servicio general de información y reportes",
            "what_to_provide": [
                "Descripción detallada del problema",
                "Ubicación si aplica",
                "Información de contacto"
            ],
            "response_time": "Varía según el tipo de servicio"
        }
    
    return {
        "status": "success",
        "service_info": matched_category,
        "how_to_report": {
            "phone": "311 (desde NYC) o 212-NEW-YORK desde fuera",
            "online": "https://portal.311.nyc.gov/",
            "app": "NYC 311 Mobile App (iOS y Android)",
            "hours": "24/7 disponible"
        },
        "tracking": {
            "description": "Recibirás un número de referencia para rastrear tu reporte",
            "check_status": "Usa el número de referencia en portal.311.nyc.gov o la app"
        },
        "languages": "Servicio disponible en más de 170 idiomas"
    }


# ============================================================================
# GOVERNMENT OFFICES TOOLS
# ============================================================================

@ai_function(
    name="find_government_office",
    description="Encuentra oficinas gubernamentales de NYC y sus horarios"
)
def find_government_office(
    office_type: Annotated[str, Field(description="Tipo de oficina: DMV, Board of Elections, Social Services, etc.")],
    borough: Annotated[str, Field(description="Borough: Manhattan, Brooklyn, Queens, Bronx, Staten Island")] = None
) -> dict:
    """
    Encuentra oficinas gubernamentales y proporciona información de contacto.
    
    Args:
        office_type: Tipo de oficina gubernamental
        borough: Borough de NYC (opcional)
    
    Returns:
        dict: Información de la oficina incluyendo dirección, horarios y contacto
    """
    # Datos simulados - en producción usar NYC Open Data API
    offices = {
        "dmv": {
            "name": "Department of Motor Vehicles (DMV)",
            "description": "Licencias de conducir, identificaciones, registros de vehículos",
            "main_office": {
                "address": "11 Greenwich Street, New York, NY 10004",
                "hours": "Lunes-Viernes: 8:30 AM - 4:00 PM",
                "phone": "1-518-486-9786",
                "appointments": "Recomendado hacer cita en dmv.ny.gov"
            },
            "services": [
                "Licencias de conducir",
                "Identificaciones estatales",
                "Registro de vehículos",
                "Renovaciones"
            ],
            "website": "https://dmv.ny.gov/"
        },
        "board of elections": {
            "name": "NYC Board of Elections",
            "description": "Registro de votantes, información electoral",
            "main_office": {
                "address": "32 Broadway, 7th Floor, New York, NY 10004",
                "hours": "Lunes-Viernes: 9:00 AM - 5:00 PM",
                "phone": "1-866-VOTE-NYC (1-866-868-3692)",
                "appointments": "No requerido para la mayoría de servicios"
            },
            "services": [
                "Registro de votantes",
                "Información sobre elecciones",
                "Boletas de voto en ausencia",
                "Verificación de registro"
            ],
            "website": "https://vote.nyc/"
        },
        "social services": {
            "name": "Department of Social Services (DSS)",
            "description": "Asistencia pública, SNAP, Medicaid",
            "contact": {
                "phone": "311",
                "hours": "Varía por centro",
                "appointments": "Llamar al 311 para ubicación más cercana"
            },
            "services": [
                "SNAP (cupones de alimentos)",
                "Medicaid",
                "Asistencia en efectivo",
                "Servicios de empleo"
            ],
            "website": "https://www1.nyc.gov/site/hra/"
        }
    }
    
    # Buscar oficina
    office_lower = office_type.lower()
    matched_office = None
    
    for key in offices:
        if key in office_lower:
            matched_office = offices[key]
            break
    
    if not matched_office:
        return {
            "status": "not_found",
            "message": f"No se encontró información específica para '{office_type}'",
            "suggestion": "Llama al 311 para información sobre oficinas gubernamentales",
            "phone": "311 o 212-NEW-YORK"
        }
    
    result = {
        "status": "success",
        "office": matched_office,
        "general_info": {
            "note": "Los horarios pueden variar. Llama antes de visitar.",
            "holidays": "Cerrado en días festivos federales y estatales",
            "accessibility": "La mayoría de oficinas son accesibles para sillas de ruedas"
        }
    }
    
    if borough:
        result["note"] = f"Mostrando información general. Para oficinas específicas en {borough}, llama al 311"
    
    return result


# ============================================================================
# DOCUMENT REQUIREMENTS TOOLS
# ============================================================================

@ai_function(
    name="get_document_requirements",
    description="Obtiene lista de documentos necesarios para trámites específicos"
)
def get_document_requirements(
    service: Annotated[str, Field(description="Servicio o trámite: voter registration, driver license, passport, etc.")]
) -> dict:
    """
    Proporciona lista de documentos necesarios para trámites comunes.
    
    Args:
        service: Tipo de servicio o trámite
    
    Returns:
        dict: Lista de documentos requeridos y opcionales
    """
    requirements = {
        "voter registration": {
            "required": [
                "Prueba de ciudadanía estadounidense",
                "Prueba de residencia en NYC (al menos 30 días antes de elecciones)"
            ],
            "accepted_documents": {
                "citizenship": [
                    "Certificado de nacimiento de EE.UU.",
                    "Pasaporte estadounidense",
                    "Certificado de naturalización"
                ],
                "residence": [
                    "Licencia de conducir de NY",
                    "Factura de servicios públicos",
                    "Estado de cuenta bancario",
                    "Contrato de alquiler"
                ]
            },
            "notes": [
                "Si te registras por correo por primera vez, puede que necesites ID adicional",
                "Puedes registrarte en línea si tienes licencia de NY o ID estatal"
            ]
        },
        "driver license": {
            "required": [
                "Prueba de identidad",
                "Prueba de fecha de nacimiento",
                "Prueba de residencia en NY",
                "Número de Seguro Social"
            ],
            "accepted_documents": {
                "identity": [
                    "Pasaporte válido",
                    "Certificado de nacimiento",
                    "Tarjeta de residencia permanente"
                ],
                "residence": [
                    "Factura de servicios (no más de 90 días)",
                    "Estado de cuenta bancario",
                    "Contrato de alquiler o escritura"
                ]
            },
            "additional": [
                "Aprobar examen de la vista",
                "Aprobar examen escrito (si es primera licencia)",
                "Aprobar examen de manejo"
            ],
            "notes": [
                "Necesitas 6 puntos de identificación",
                "Consulta dmv.ny.gov para lista completa de documentos aceptados"
            ]
        }
    }
    
    service_lower = service.lower()
    matched_service = None
    
    for key in requirements:
        if key in service_lower:
            matched_service = requirements[key]
            break
    
    if not matched_service:
        return {
            "status": "not_found",
            "message": f"No se encontró información específica para '{service}'",
            "suggestion": "Contacta a la agencia gubernamental correspondiente o llama al 311",
            "phone": "311"
        }
    
    return {
        "status": "success",
        "service": service,
        "requirements": matched_service,
        "important": "Siempre lleva documentos originales, no copias, a menos que se especifique lo contrario"
    }
