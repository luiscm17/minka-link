// Test directo de la conexión al backend
const testBackend = async () => {
  const url =
    "https://backend-chat-fhdme0fqcye3fedq.brazilsouth-01.azurewebsites.net/api/http_chat?code=VhHt38gZleTKWSHA-zdWlRTIN-Cb9BWFZSlod18u2NWrAzFuJzF0YA==";

  console.log("🧪 Probando conexión al backend...");
  console.log("URL:", url.split("?")[0]);

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message: "Hola, esto es una prueba",
        channel: "web",
        language: "es",
      }),
    });

    console.log("Status:", response.status);
    console.log("Status Text:", response.statusText);

    const data = await response.json();
    console.log("✅ Respuesta:", data);
  } catch (error) {
    console.error("❌ Error:", error);
  }
};

// Ejecutar test
testBackend();
