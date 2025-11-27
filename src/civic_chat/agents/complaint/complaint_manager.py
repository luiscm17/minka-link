import os
import json
import uuid
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Any, Optional
from agent_framework import ContextProvider, Context
from openai import AsyncAzureOpenAI

class ComplaintData:
    """Data structure for a citizen complaint following the specified schema."""
    
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        self.criticidad: Optional[str] = None  # alta, media, baja
        self.location: Dict[str, Any] = {
            "city": None,
            "address": None,
            "lat": None,
            "lon": None
        }
        self.contenido: Optional[str] = None
        self.origen: str = "texto"  # texto or voz
        self.estado: str = "pendiente"  # pendiente, en_revision, resuelto
        self.usuarioId: Optional[str] = None
        self.metadata: Dict[str, Any] = {
            "categoria": None,
            "etiquetas": []
        }
        self.entidad_responsable: Optional[str] = None  # Entity responsible for handling
    
    def to_dict(self) -> Dict[str, Any]:
        """Converts the complaint to dictionary following the exact schema."""
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "criticidad": self.criticidad,
            "location": self.location,
            "contenido": self.contenido,
            "origen": self.origen,
            "estado": self.estado,
            "usuarioId": self.usuarioId,
            "metadata": self.metadata,
            "entidad_responsable": self.entidad_responsable
        }
    
    def determine_responsible_entity(self) -> str:
        """Determines the responsible entity based on complaint category."""
        categoria = self.metadata.get('categoria', '').lower()
        
        # Map categories to responsible entities
        entity_mapping = {
            'seguridad': 'policia',
            'servicios': 'municipio',
            'infraestructura': 'municipio',
            'corrupcion': 'procuraduria',
            'otro': 'municipio'
        }
        
        return entity_mapping.get(categoria, 'municipio')
    
    def get_entity_email(self) -> str:
        """Gets the email address for the responsible entity (fictitious for now)."""
        entity = self.entidad_responsable or self.determine_responsible_entity()
        
        # Fictitious email addresses for each entity
        email_mapping = {
            'policia': 'denuncias@policia.gob.ficticio',
            'municipio': 'quejas@municipio.gob.ficticio',
            'procuraduria': 'corrupcion@procuraduria.gob.ficticio',
            'gobernador': 'atencion@gobernador.gob.ficticio'
        }
        
        return email_mapping.get(entity, 'general@gobierno.gob.ficticio')
    
    def to_json(self) -> str:
        """Converts the complaint to JSON."""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
    
    def save_to_file(self, directory: str = "complaints_data"):
        """Saves the complaint to a JSON file."""
        os.makedirs(directory, exist_ok=True)
        
        filename = f"{directory}/complaint_{self.id}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(self.to_json())
        
        return filename


class ComplaintManager(ContextProvider):
    """Manages complaint collection and storage using AI extraction."""
    
    def __init__(self, user_id: str, ai_client: AsyncAzureOpenAI):
        self.user_id = user_id
        self.ai_client = ai_client
        self.current_complaint: Optional[ComplaintData] = None
        self.complaints_dir = "complaints_data"
        self.emails_dir = "complaints_data/emails"
        os.makedirs(self.complaints_dir, exist_ok=True)
        os.makedirs(self.emails_dir, exist_ok=True)
    
    async def _extract_complaint_info(self, message: str) -> Dict[str, Any]:
        """Extracts complaint information from user message using AI."""
        if not message or len(message) < 3:
            return {}
        
        try:
            prompt = """Analyze this message and extract complaint/report information.

Extract ONLY explicitly mentioned information:
- criticidad: urgency level (alta/media/baja) - ONLY if explicitly mentioned
- city: city name - ONLY if explicitly mentioned
- address: street address or location description - ONLY if explicitly mentioned
- contenido: description of the incident - extract the main problem description
- categoria: category (infraestructura, seguridad, servicios, corrupcion, otro) - infer from context
- etiquetas: relevant tags as array - infer from context

IMPORTANT: 
- Do NOT include fields with empty values
- Only include fields that have actual information
- If a field is not mentioned or cannot be inferred, OMIT it from the JSON

Good example: {"criticidad": "alta", "city": "Miami", "address": "Calle Principal", "contenido": "Bache peligroso", "categoria": "infraestructura", "etiquetas": ["urgente"]}
Bad example: {"criticidad": "", "city": "", "address": ""}

JSON only, no explanation:"""
            
            response = await self.ai_client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": "You are an assistant that extracts structured complaint information."},
                    {"role": "user", "content": f"{prompt}\n\nMessage: {message}"}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            result = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            if "{" in result and "}" in result:
                start = result.index("{")
                end = result.rindex("}") + 1
                json_str = result[start:end]
                extracted = json.loads(json_str)
                return extracted
            
            return {}
            
        except Exception as e:
            # Silent fail
            return {}
    
    async def update_complaint(self, message: str) -> None:
        """Updates the current complaint with information from the message."""
        if not message:
            return
        
        # Extract complaint information
        extracted = await self._extract_complaint_info(message)
        print(f"🔍 Extracted from '{message[:50]}...': {extracted}")
        if not extracted:
            return
        
        # Initialize complaint if needed
        if self.current_complaint is None:
            self.current_complaint = ComplaintData()
            self.current_complaint.usuarioId = self.user_id
            print(f"📝 New complaint created: {self.current_complaint.id}")
        
        # Update complaint fields
        if extracted.get('criticidad'):
            self.current_complaint.criticidad = extracted['criticidad']
        
        if extracted.get('city'):
            self.current_complaint.location['city'] = extracted['city']
        if extracted.get('address'):
            self.current_complaint.location['address'] = extracted['address']
        if extracted.get('lat'):
            self.current_complaint.location['lat'] = extracted['lat']
        if extracted.get('lon'):
            self.current_complaint.location['lon'] = extracted['lon']
        
        if extracted.get('contenido'):
            self.current_complaint.contenido = extracted['contenido']
        
        if extracted.get('categoria'):
            self.current_complaint.metadata['categoria'] = extracted['categoria']
        if extracted.get('etiquetas'):
            self.current_complaint.metadata['etiquetas'] = extracted['etiquetas']
    
    def _send_email_notification(self, complaint: ComplaintData) -> bool:
        """Sends email notification to the responsible entity (simulated for now).
        
        In production, this would use a real SMTP server.
        For now, it saves the email content to a file.
        """
        try:
            # Determine responsible entity
            complaint.entidad_responsable = complaint.determine_responsible_entity()
            recipient_email = complaint.get_entity_email()
            
            # Create email content
            subject = f"Nueva Denuncia #{complaint.id[:8]} - {complaint.metadata.get('categoria', 'General')}"
            
            body = f"""
NUEVA DENUNCIA CIUDADANA
========================

ID de Denuncia: {complaint.id}
Fecha y Hora: {complaint.timestamp}
Criticidad: {complaint.criticidad or 'No especificada'}
Estado: {complaint.estado}

UBICACIÓN:
----------
Ciudad: {complaint.location.get('city', 'No especificada')}
Dirección: {complaint.location.get('address', 'No especificada')}

DESCRIPCIÓN:
------------
{complaint.contenido or 'Sin descripción'}

CATEGORÍA Y ETIQUETAS:
----------------------
Categoría: {complaint.metadata.get('categoria', 'No especificada')}
Etiquetas: {', '.join(complaint.metadata.get('etiquetas', [])) or 'Ninguna'}

INFORMACIÓN DEL USUARIO:
------------------------
ID de Usuario: {complaint.usuarioId}

ENTIDAD RESPONSABLE:
--------------------
{complaint.entidad_responsable}

---
Este es un mensaje automático del Sistema de Denuncias Ciudadanas.
Por favor, no responder a este correo.
"""
            
            # For now, save email to file instead of sending
            email_filename = f"{self.emails_dir}/email_{complaint.id}.txt"
            with open(email_filename, 'w', encoding='utf-8') as f:
                f.write(f"To: {recipient_email}\n")
                f.write(f"Subject: {subject}\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("\n" + "="*70 + "\n\n")
                f.write(body)
            
            return True
            
        except Exception as e:
            # Silent fail for production
            return False
    
    def save_current_complaint(self) -> Optional[Dict[str, str]]:
        """Saves the current complaint to file and sends email notification.
        
        Returns:
            Dictionary with 'json_file' and 'email_file' paths, or None if failed
        """
        if self.current_complaint and self.current_complaint.contenido:
            # Save JSON file
            json_filename = self.current_complaint.save_to_file(self.complaints_dir)
            
            # Send email notification
            email_sent = self._send_email_notification(self.current_complaint)
            
            result = {
                'json_file': json_filename,
                'email_sent': email_sent,
                'complaint_id': self.current_complaint.id,
                'entity': self.current_complaint.entidad_responsable
            }
            
            # Reset for next complaint
            self.current_complaint = None
            
            return result
        return None
    
    async def invoking(self, messages, **kwargs) -> Context:
        """Provides context to the agent before processing."""
        # No need to inject context for complaints
        return Context()
    
    async def invoked(self, request_messages, response_messages, **kwargs) -> None:
        """Processes messages after agent response to extract complaint data."""
        if not request_messages:
            return
        
        # Get the FIRST user message (original input), not the classifier output
        user_message = ""
        if isinstance(request_messages, (list, tuple)):
            for msg in request_messages:  # Don't reverse, get the first one
                if hasattr(msg, 'contents') and isinstance(msg.contents, list):
                    if len(msg.contents) > 0 and hasattr(msg.contents[0], 'text'):
                        text = str(msg.contents[0].text)
                        # Skip classifier outputs (single words like "COMPLAINT", "GENERAL", etc.)
                        if len(text) > 3 and not text.isupper():
                            user_message = text
                            break
                elif hasattr(msg, 'content') and msg.content:
                    text = str(msg.content)
                    # Skip classifier outputs
                    if len(text) > 3 and not text.isupper():
                        user_message = text
                        break
                elif hasattr(msg, 'text'):
                    text = str(msg.text)
                    # Skip classifier outputs
                    if len(text) > 3 and not text.isupper():
                        user_message = text
                        break
        
        print(f"📨 Processing user message: '{user_message}'")
        
        if user_message and len(user_message) >= 3:
            await self.update_complaint(user_message)
            
            # Auto-save if complaint has minimum required information
            if self.current_complaint and self.current_complaint.contenido:
                # Check if we have enough information to save
                has_location = (self.current_complaint.location.get('city') or 
                              self.current_complaint.location.get('address'))
                has_category = self.current_complaint.metadata.get('categoria')
                
                print(f"📝 Complaint status:")
                print(f"   - Has content: {bool(self.current_complaint.contenido)}")
                print(f"   - Has location: {has_location}")
                print(f"   - Has category: {has_category}")
                
                # Auto-save if we have content + (location OR category)
                if has_location or has_category:
                    print(f"💾 Auto-saving complaint (sufficient information)")
                    result = self.save_current_complaint()
                    if result:
                        print(f"✅ Complaint saved: {result['json_file']}")
                        print(f"📧 Email notification: {result['email_sent']}")
                        print(f"🏛️  Responsible entity: {result['entity']}")
                    else:
                        print("⚠️  Failed to save complaint")
