// chatService.js - Servicio para comunicarse con el backend del chatbot

// Usamos el proxy configurado en vite.config.js para evitar errores de CORS
const API_BASE_URL = "/api";
const API_CODE = "VhHt38gZleTKWSHA-zdWlRTIN-Cb9BWFZSlod18u2NWrAzFuJzF0YA==";

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

    // Construir URL con el código de autenticación
    const url = `${API_BASE_URL}/http_chat?code=${API_CODE}`;
    console.log(
      "🔵 Llamando al backend de Azure (vía Proxy):",
      url.split("?")[0]
    );
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
    console.error("URL base:", API_BASE_URL);
    throw error;
  }
};
