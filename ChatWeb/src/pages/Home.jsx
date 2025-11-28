import React, { useRef, useEffect } from "react";
import { useState } from "react";
import logoChatImg from "../assets/logochat.png";
import BtnInisiaSesion from "../ui/BtnInisiaSesion";
import BtnRegitro from "../ui/BtnRegitro";
import BtnEstado from "../ui/BtnEstado";
import BtnBuscado from "../ui/BtnBuscado";
import { sendMessage } from "../services/chatService";
import ThemeToggle from "../components/ThemeToggle";
import AccessibilityWelcome from "../components/AccessibilityWelcome";
import useSpeech from "../hooks/useSpeech";

function Home() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [threadId, setThreadId] = useState(null);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const {
    isListening,
    transcript,
    startListening,
    stopListening,
    speak,
    isSupported,
    setTranscript,
  } = useSpeech();

  // Actualizar input cuando hay transcripción de voz
  useEffect(() => {
    if (transcript) {
      setInput(transcript);
    }
  }, [transcript]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();

    // Agregar mensaje del usuario a la UI
    setMessages((prev) => [...prev, { text: userMessage, sender: "user" }]);
    setInput("");
    setLoading(true);

    try {
      // Llamar al backend con el threadId actual
      const response = await sendMessage(userMessage, threadId);

      // Guardar threadId para mantener la conversación
      if (response.threadId) {
        setThreadId(response.threadId);
      }

      // Agregar respuesta del bot a la UI
      setMessages((prev) => [
        ...prev,
        {
          text: response.reply || "Lo siento, no pude procesar tu pregunta.",
          sender: "bot",
        },
      ]);
    } catch (error) {
      console.error("Error al comunicarse con el chatbot:", error);

      // Mostrar mensaje de error al usuario
      setMessages((prev) => [
        ...prev,
        {
          text: "Lo siento, hubo un error al conectar con el servidor. Por favor intenta de nuevo.",
          sender: "bot",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const hasMessages = messages.length > 0;

  return (
    <div className="h-dvh flex flex-col bg-theme-bg transition-colors duration-300">
      <AccessibilityWelcome />

      {/* Header fijo - Responsivo */}
      <div className="border-b border-theme px-4 md:px-8 py-3 md:py-4 flex flex-col md:flex-row justify-between items-center bg-theme-surface gap-3 md:gap-0 z-10">
        <div className="w-full md:w-auto flex justify-center md:justify-start">
          <img
            src={logoChatImg}
            alt="Logo Chat"
            className="h-10 md:h-12 object-contain"
          />
        </div>
        <div className="flex gap-2 md:gap-3 items-center w-full md:w-auto justify-center md:justify-end overflow-x-auto pb-1 md:pb-0">
          <ThemeToggle />
          <BtnInisiaSesion />
          <BtnRegitro />
        </div>
      </div>

      {/* Área de mensajes o bienvenida - scrollable */}
      <div className="flex-1 overflow-y-auto scroll-smooth">
        {!hasMessages ? (
          // Pantalla de bienvenida (centrada)
          <div className="h-full flex flex-col items-center justify-center px-4">
            <div className="text-center mb-8 md:mb-12 max-w-lg mx-auto">
              <h1 className="text-3xl md:text-5xl font-light text-theme-secondary leading-tight transition-colors">
                Your AI Guide for Government
              </h1>
              <p className="text-xl md:text-2xl font-light text-theme-secondary mt-2 md:mt-4 transition-colors">
                of Your City
              </p>
            </div>
          </div>
        ) : (
          // Mensajes del chat
          <div
            className="max-w-3xl mx-auto w-full px-4 py-6 md:py-8 space-y-4 md:space-y-6"
            aria-live="polite"
            aria-relevant="additions"
          >
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${
                  msg.sender === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`flex items-end gap-2 ${
                    msg.sender === "user" ? "flex-row-reverse" : "flex-row"
                  }`}
                >
                  <div
                    className={`max-w-[85%] md:max-w-lg px-4 md:px-6 py-3 md:py-4 rounded-2xl text-sm md:text-base shadow-sm ${
                      msg.sender === "user"
                        ? "bg-theme-primary text-white rounded-br-none"
                        : "bg-theme-surface text-theme-text border border-theme rounded-bl-none"
                    }`}
                  >
                    {msg.text}
                  </div>

                  {/* Botón de leer en voz alta para mensajes del bot */}
                  {msg.sender === "bot" && (
                    <button
                      onClick={() => speak(msg.text)}
                      className="p-2 rounded-full text-theme-secondary hover:bg-theme-hover transition-colors"
                      title="Leer en voz alta"
                      aria-label="Leer respuesta en voz alta"
                    >
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className="h-5 w-5"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                        strokeWidth={2}
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"
                        />
                      </svg>
                    </button>
                  )}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Barra de entrada fija en la parte inferior */}
      <div className="border-t border-theme bg-theme-surface px-2 md:px-4 py-3 md:py-4 z-10">
        <div className="max-w-3xl mx-auto w-full">
          <div className="border-2 border-theme rounded-3xl px-4 md:px-6 py-2 md:py-4 bg-theme-bg shadow-sm hover:shadow-md transition-all">
            <div className="flex items-center gap-2 md:gap-3 mb-2 md:mb-3">
              <input
                type="text"
                value={input}
                onChange={(e) => {
                  setInput(e.target.value);
                  // Si el usuario escribe manualmente, detenemos el reconocimiento para evitar conflictos
                  if (isListening) stopListening();
                }}
                onKeyPress={(e) => e.key === "Enter" && handleSend()}
                placeholder={isListening ? "Escuchando..." : "Ask me anything"}
                className={`flex-1 outline-none text-theme-text placeholder-theme-secondary text-sm md:text-base bg-transparent min-w-0 transition-all ${
                  isListening ? "placeholder-red-500 animate-pulse" : ""
                }`}
                autoFocus
              />

              {/* Botón de Micrófono */}
              {isSupported && (
                <button
                  onClick={isListening ? stopListening : startListening}
                  className={`p-2 rounded-full transition-all ${
                    isListening
                      ? "bg-red-100 text-red-600 animate-pulse"
                      : "text-theme-secondary hover:text-theme-primary hover:bg-theme-hover"
                  }`}
                  title={
                    isListening ? "Detener grabación" : "Activar micrófono"
                  }
                  aria-label={
                    isListening ? "Detener grabación" : "Activar micrófono"
                  }
                >
                  {isListening ? (
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      className="h-5 w-5 md:h-6 md:w-6"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                    >
                      <path
                        fillRule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 002 0V8a1 1 0 00-1-1zm4 0a1 1 0 00-1 1v4a1 1 0 002 0V8a1 1 0 00-1-1z"
                        clipRule="evenodd"
                      />
                    </svg>
                  ) : (
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      className="h-5 w-5 md:h-6 md:w-6"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      strokeWidth={2}
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                      />
                    </svg>
                  )}
                </button>
              )}
              <button
                onClick={handleSend}
                disabled={loading || !input.trim()}
                className={`p-2 rounded-full transition-all ${
                  loading || !input.trim()
                    ? "text-theme-secondary opacity-50 cursor-not-allowed"
                    : "text-theme-primary hover:bg-theme-hover active:scale-95"
                }`}
                aria-label="Enviar mensaje"
              >
                {loading ? (
                  <svg
                    className="w-5 h-5 md:w-6 md:h-6 animate-spin"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                ) : (
                  <svg
                    className="w-5 h-5 md:w-6 md:h-6"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M13 5l7 7-7 7M5 5l7 7-7 7"
                    />
                  </svg>
                )}
              </button>
            </div>
            {!hasMessages && (
              <div className="flex flex-wrap gap-2 md:gap-3 justify-center md:justify-start">
                <BtnEstado />
                <BtnBuscado />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Home;
