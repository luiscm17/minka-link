import express from "express";
import cors from "cors";

const app = express();
app.use(cors());
app.use(express.json());

app.post("/api/http_chat", (req, res) => {
  const { message, threadId } = req.body;

  console.log("📨 Mensaje recibido:", message);

  // Simular un pequeño delay como si fuera una API real
  setTimeout(() => {
    // Respuestas simuladas basadas en palabras clave
    let reply = "";

    if (message.toLowerCase().includes("hola")) {
      reply =
        "¡Hola! Soy tu asistente virtual cívico. ¿En qué puedo ayudarte hoy?";
    } else if (message.toLowerCase().includes("certificado")) {
      reply =
        "Para obtener un certificado, puedes acercarte a la oficina municipal de lunes a viernes de 9:00 a 17:00, o solicitarlo en línea a través de nuestro portal web.";
    } else if (message.toLowerCase().includes("horario")) {
      reply =
        "Nuestros horarios de atención son de lunes a viernes de 9:00 a 17:00 horas.";
    } else {
      reply = `Recibí tu consulta: "${message}". Este es un servidor de prueba. En producción, aquí respondería el agente de IA de Azure.`;
    }

    res.json({
      threadId: threadId || `thread_${Date.now()}`,
      reply: reply,
    });
  }, 500); // Delay de 500ms para simular latencia de red
});

// Endpoint de salud para verificar que el servidor está corriendo
app.get("/api/health", (req, res) => {
  res.json({ status: "ok", message: "Mock server is running" });
});

const PORT = 7071;
app.listen(PORT, () => {
  console.log("🚀 Servidor de prueba corriendo en http://localhost:" + PORT);
  console.log(
    "📡 Endpoint disponible: POST http://localhost:" + PORT + "/api/http_chat"
  );
  console.log("💚 Health check: GET http://localhost:" + PORT + "/api/health");
});
