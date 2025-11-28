import asyncio
import os
from pathlib import Path
from typing import Annotated
from dotenv import load_dotenv
from agent_framework.azure import AzureOpenAIChatClient
from agent_framework import ai_function
from azure.identity import AzureCliCredential
import pypdf

# Cargar variables de entorno
load_dotenv()

# Variable global para almacenar los chunks del PDF
pdf_chunks = []

def load_pdf(pdf_path: str):
    """Carga y divide el PDF en chunks"""
    global pdf_chunks
    chunks = []
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                text = page.extract_text()
                
                # Dividir en párrafos (chunks más pequeños)
                paragraphs = text.split('\n\n')
                
                for para in paragraphs:
                    if para.strip():
                        chunks.append({
                            'text': para.strip(),
                            'page': page_num,
                            'source': Path(pdf_path).name
                        })
        
        pdf_chunks = chunks
        print(f"✓ PDF cargado: {len(chunks)} chunks extraídos")
        
    except Exception as e:
        print(f"✗ Error al cargar PDF: {e}")
    
    return chunks

@ai_function
def search_document(
    query: Annotated[str, "La consulta de búsqueda para encontrar información relevante en el documento"]
) -> str:
    """Busca información relevante en el documento PDF sobre los tribunales."""
    
    query_lower = query.lower()
    results = []
    
    # Búsqueda simple por palabras clave
    for chunk in pdf_chunks:
        # Calcular relevancia simple
        relevance = sum(1 for word in query_lower.split() if word in chunk['text'].lower())
        
        if relevance > 0:
            results.append({
                'text': chunk['text'],
                'page': chunk['page'],
                'source': chunk['source'],
                'relevance': relevance
            })
    
    # Ordenar por relevancia y tomar los top 3
    results.sort(key=lambda x: x['relevance'], reverse=True)
    top_results = results[:3]
    
    if not top_results:
        return "No se encontró información relevante en el documento."
    
    # Formatear resultados
    formatted_results = []
    for i, result in enumerate(top_results, 1):
        formatted_results.append(
            f"[Resultado {i} - Página {result['page']}]\n{result['text']}\n"
        )
    
    return "\n".join(formatted_results)


async def main():
    # Configuración
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment_name = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    
    if not endpoint or not deployment_name:
        print("✗ Error: Configura las variables de entorno en el archivo .env")
        return
    
    # Ruta al PDF
    pdf_path = "data/IntroGuidetotheCourtsOct2023.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"✗ Error: No se encuentra el archivo {pdf_path}")
        return
    
    # Cargar PDF
    load_pdf(pdf_path)
    
    # Crear cliente de Azure OpenAI
    if api_key:
        # Usar API Key
        chat_client = AzureOpenAIChatClient(
            endpoint=endpoint,
            deployment_name=deployment_name,
            api_key=api_key
        )
    else:
        # Usar Azure CLI Credential
        chat_client = AzureOpenAIChatClient(
            endpoint=endpoint,
            deployment_name=deployment_name,
            credential=AzureCliCredential()
        )
    
    # Crear agente con función de búsqueda como tool
    agent = chat_client.create_agent(
        instructions="Eres un asistente especializado en información sobre los tribunales. "
                    "Usa la función search_document para buscar información relevante en el documento antes de responder. "
                    "Siempre cita la página de donde obtuviste la información. "
                    "Si la información no está en el documento, indícalo claramente.",
        name="CourtsGuideAgent",
        tools=[search_document]
    )
    
    print("\n" + "="*60)
    print("🤖 Agente RAG con Microsoft Agent Framework")
    print("="*60)
    print(f"📄 Documento: {pdf_path}")
    print("💬 Escribe 'salir' para terminar\n")
    
    # Loop de conversación
    while True:
        try:
            user_input = input("Tú: ").strip()
            
            if user_input.lower() in ['salir', 'exit', 'quit']:
                print("\n👋 ¡Hasta luego!")
                break
            
            if not user_input:
                continue
            
            print("\n🤔 Pensando...\n")
            
            # Ejecutar agente
            result = await agent.run(user_input)
            print(f"Agente: {result.text}\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n✗ Error: {e}\n")


if __name__ == "__main__":
    asyncio.run(main())
