// chatService.js - Servicio para comunicarse con el backend del chatbot

const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://localhost:7071/api";
const API_KEY = import.meta.env.VITE_API_KEY;

/**
 * Envía un mensaje al chatbot y recibe una respuesta
 * @param {string} message - Mensaje del usuario
 * @param {string|null} threadId - ID del hilo de conversación (opcional)
 * @param {object} context - Contexto adicional (comunaId, channel, language)
 * @returns {Promise<{threadId: string, reply: string}>}
 */
export const sendMessage = async (message, threadId = null, context = {}) => {
  try {
    const headers = {
      "Content-Type": "application/json",
    };

    // Agregar API key si está disponible
    if (API_KEY) {
      headers["x-functions-key"] = API_KEY;
    }

    const url = `${API_BASE_URL}/http_chat`;
    console.log("🔵 Llamando al backend:", url);
    console.log("📤 Enviando mensaje:", message);

    const response = await fetch(url, {
      method: "POST",
      headers,
      body: JSON.stringify({
        message,
        threadId,
        comunaId: context.comunaId,
        channel: context.channel || "web",
        language: context.language || "es",
      }),
    });

    console.log(
      "📥 Respuesta del servidor:",
      response.status,
      response.statusText
    );

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      console.error("❌ Error del servidor:", error);
      throw new Error(error.error || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log("✅ Respuesta exitosa:", data);
    return data;
  } catch (error) {
    console.error("❌ Error completo:", error);
    console.error("URL intentada:", `${API_BASE_URL}/http_chat`);
    throw error;
  }
};
