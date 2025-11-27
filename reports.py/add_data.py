import os
from azure.cosmos import CosmosClient
import uuid
from dotenv import load_dotenv

# Configuración de Cosmos DB
load_dotenv()
#endpoint = os.getenv("reports_endpoint")
#key = os.getenv("reports_key")


endpoint = "https://cdb-reports.documents.azure.com:443/"
key = "NDQMFxAi2mz7xjfUxwJEf67b1KfLITgcE42yVRO3ah599H6BvzN5vYqWTWUxgr877gWyCQbJMc99ACDbHkOoCQ=="

DATABASE_NAME = "reportsdb"
CONTAINER_NAME = "reports"


# Conexión
client = CosmosClient(endpoint, key)
database = client.get_database_client(DATABASE_NAME)
container = database.get_container_client(CONTAINER_NAME)


# Ejemplos de denuncias
denuncias = [
  {
    "id": "1",
    "timestamp": "2025-11-24T08:15:00Z",
    "criticidad": "alta",
    "location": {
      "city": "CABA",
      "address": "Av. Rivadavia 3200",
      "lat": -34.6091,
      "lon": -58.4206
    },
    "contenido": "Cables eléctricos expuestos en la vereda, riesgo de electrocución.",
    "origen": "texto",
    "estado": "pendiente",
    "usuarioId": None,
    "metadata": {
      "categoria": "infraestructura",
      "etiquetas": ["riesgo eléctrico", "urgente", "seguridad"]
    }
  },
  {
    "id": "2",
    "timestamp": "2025-11-24T22:40:00Z",
    "criticidad": "alta",
    "location": {
      "city": "CABA",
      "address": "Calle Defensa 800",
      "lat": -34.6155,
      "lon": -58.3702
    },
    "contenido": "Incendio en contenedor de basura, humo denso en la zona.",
    "origen": "texto",
    "estado": "en evaluación",
    "usuarioId": None,
    "metadata": {
      "categoria": "emergencia",
      "etiquetas": ["fuego", "contaminación", "bomberos"]
    }
  },
  {
    "id": "3",
    "timestamp": "2025-11-25T09:30:00Z",
    "criticidad": "media",
    "location": {
      "city": "CABA",
      "address": "Av. Santa Fe 2400",
      "lat": -34.5895,
      "lon": -58.3974
    },
    "contenido": "Semáforo intermitente en cruce peatonal, dificulta el tránsito.",
    "origen": "texto",
    "estado": "resuelto",
    "usuarioId": None,
    "metadata": {
      "categoria": "tránsito",
      "etiquetas": ["semáforo", "peatonal", "tránsito"]
    }
  },
  {
    "id": "4",
    "timestamp": "2025-11-25T18:05:00Z",
    "criticidad": "media",
    "location": {
      "city": "CABA",
      "address": "Av. Belgrano 1500",
      "lat": -34.6132,
      "lon": -58.3921
    },
    "contenido": "Ruidos molestos por obras en horario nocturno.",
    "origen": "texto",
    "estado": "pendiente",
    "usuarioId": None,
    "metadata": {
      "categoria": "ruido",
      "etiquetas": ["obras", "descanso", "molestia"]
    }
  },
  {
    "id": "5",
    "timestamp": "2025-11-25T11:20:00Z",
    "criticidad": "baja",
    "location": {
      "city": "CABA",
      "address": "Calle Perú 500",
      "lat": -34.6150,
      "lon": -58.3740
    },
    "contenido": "Cartel de calle con letras borradas, difícil de leer.",
    "origen": "texto",
    "estado": "resuelto",
    "usuarioId": None,
    "metadata": {
      "categoria": "señalización",
      "etiquetas": ["cartel", "visibilidad", "información"]
    }
  },
  {
    "id": "6",
    "timestamp": "2025-11-25T23:45:00Z",
    "criticidad": "baja",
    "location": {
      "city": "CABA",
      "address": "Calle Lavalle 1200",
      "lat": -34.6038,
      "lon": -58.3845
    },
    "contenido": "Banco roto en plaza pública.",
    "origen": "texto",
    "estado": "en evaluación",
    "usuarioId": None,
    "metadata": {
      "categoria": "mobiliario urbano",
      "etiquetas": ["plaza", "banco", "reparación"]
    }
  },
  {
    "id": "7",
    "timestamp": "2025-11-26T07:10:00Z",
    "criticidad": "baja",
    "location": {
      "city": "CABA",
      "address": "Av. Corrientes 1800",
      "lat": -34.6032,
      "lon": -58.3951
    },
    "contenido": "Contenedor de reciclaje lleno desde hace días.",
    "origen": "texto",
    "estado": "pendiente",
    "usuarioId": None,
    "metadata": {
      "categoria": "higiene urbana",
      "etiquetas": ["reciclaje", "basura", "contenedor"]
    }
  },
  {
    "id": "8",
    "timestamp": "2025-11-26T12:25:00Z",
    "criticidad": "baja",
    "location": {
      "city": "CABA",
      "address": "Calle Junín 900",
      "lat": -34.5981,
      "lon": -58.3959
    },
    "contenido": "Luminaria pública con luz tenue.",
    "origen": "texto",
    "estado": "resuelto",
    "usuarioId": None,
    "metadata": {
      "categoria": "iluminación",
      "etiquetas": ["farola", "luz", "calle"]
    }
  },
  {
    "id": "9",
    "timestamp": "2025-11-26T15:50:00Z",
    "criticidad": "baja",
    "location": {
      "city": "CABA",
      "address": "Calle Moreno 700",
      "lat": -34.6142,
      "lon": -58.3798
    },
    "contenido": "Grafitis en fachada de edificio público.",
    "origen": "texto",
    "estado": "en evaluación",
    "usuarioId": None,
    "metadata": {
      "categoria": "espacio público",
      "etiquetas": ["grafiti", "fachada", "limpieza"]
    }
  },
  {
    "id": "10",
    "timestamp": "2025-11-26T16:40:00Z",
    "criticidad": "baja",
    "location": {
      "city": "CABA",
      "address": "Calle Bolívar 300",
      "lat": -34.6158,
      "lon": -58.3732
    },
    "contenido": "Arbusto invadiendo vereda, dificulta el paso.",
    "origen": "texto",
    "estado": "pendiente",
    "usuarioId": None,
    "metadata": {
      "categoria": "vegetación",
      "etiquetas": ["vereda", "arbusto", "accesibilidad"]
    }
  },
  {
        "timestamp": "2025-11-26T07:15:00Z",
        "criticidad": "alta",
        "location": {
            "city": "CABA",
            "address": "Av. Corrientes 1234",
            "lat": -34.6037,
            "lon": -58.3816
        },
        "contenido": "Basura acumulada en la vía pública.",
        "origen": "texto",
        "estado": "pendiente",
        "usuarioId": None,
        "metadata": {
            "categoria": "higiene urbana",
            "etiquetas": ["basura", "urgente"]
        }
    },
    {
        "timestamp": "2025-11-26T07:20:00Z",
        "criticidad": "media",
        "location": {
            "city": "CABA",
            "address": "Calle San Martín 456",
            "lat": -32.9587,
            "lon": -60.6939
        },
        "contenido": "Ruidos molestos en la madrugada provenientes de un local nocturno.",
        "origen": "voz",
        "estado": "pendiente",
        "usuarioId": None,
        "metadata": {
            "categoria": "ruidos molestos",
            "etiquetas": ["sonido", "vecinos"]
        }
    }
]

'''
[
    {
        "timestamp": "2025-11-26T07:15:00Z",
        "criticidad": "alta",
        "location": {
            "city": "CABA",
            "address": "Av. Corrientes 1234",
            "lat": -34.6037,
            "lon": -58.3816
        },
        "contenido": "Basura acumulada en la vía pública.",
        "origen": "texto",
        "estado": "pendiente",
        "usuarioId": None,
        "metadata": {
            "categoria": "higiene urbana",
            "etiquetas": ["basura", "urgente"]
        }
    },
    {
        "timestamp": "2025-11-26T07:20:00Z",
        "criticidad": "media",
        "location": {
            "city": "CABA",
            "address": "Calle San Martín 456",
            "lat": -32.9587,
            "lon": -60.6939
        },
        "contenido": "Ruidos molestos en la madrugada provenientes de un local nocturno.",
        "origen": "voz",
        "estado": "pendiente",
        "usuarioId": None,
        "metadata": {
            "categoria": "ruidos molestos",
            "etiquetas": ["sonido", "vecinos"]
        }
    }
]
'''

# Insertar denuncias de a poco
for denuncia in denuncias:
    denuncia["id"] = str(uuid.uuid4())  # Cosmos requiere un id único
    container.create_item(body=denuncia)
    print(f"Denuncia {denuncia['id']} insertada correctamente.")
    
'''
for db in client.list_databases():
    print(db['id'])
'''