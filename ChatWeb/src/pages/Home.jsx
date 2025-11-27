import React, { useRef, useEffect } from "react";
import { useState } from "react";
import logoChatImg from "../assets/logochat.png";
import BtnInisiaSesion from "../ui/BtnInisiaSesion";
import BtnRegitro from "../ui/BtnRegitro";
import BtnEstado from "../ui/BtnEstado";
import BtnBuscado from "../ui/BtnBuscado";
import { sendMessage } from "../services/chatService";

function Home() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [threadId, setThreadId] = useState(null);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

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
    <div className="h-screen flex flex-col bg-white">
      {/* Header fijo */}
      <div className="border-b border-slate-200 px-8 py-4 flex justify-between items-center bg-white">
        <div className="">
          <img src={logoChatImg} alt="Logo Chat" className="h-12" />
        </div>
        <div className="flex gap-2">
          <BtnInisiaSesion />
          <BtnRegitro />
        </div>
      </div>

      {/* Área de mensajes o bienvenida - scrollable */}
      <div className="flex-1 overflow-y-auto">
        {!hasMessages ? (
          // Pantalla de bienvenida (centrada)
          <div className="h-full flex flex-col items-center justify-center px-4">
            <div className="text-center mb-12">
              <h1 className="text-4xl font-light text-slate-400 leading-tight">
                Your AI Guide for Government
              </h1>
              <p className="text-2xl font-light text-slate-400 mt-2">
                of Your City
              </p>
            </div>
          </div>
        ) : (
          // Mensajes del chat
          <div className="max-w-2xl mx-auto w-full px-4 py-8 space-y-4">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${
                  msg.sender === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-xs lg:max-w-md px-4 py-3 rounded-lg ${
                    msg.sender === "user"
                      ? "bg-teal-500 text-white rounded-br-none"
                      : "bg-slate-200 text-slate-900 rounded-bl-none"
                  }`}
                >
                  {msg.text}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Barra de entrada fija en la parte inferior */}
      <div className="border-t border-slate-200 bg-white px-4 py-4">
        <div className="max-w-2xl mx-auto w-full">
          <div className="border-2 border-slate-300 rounded-3xl px-6 py-4 bg-white shadow-sm hover:shadow-md transition">
            <div className="flex items-center gap-3 mb-3">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleSend()}
                placeholder="Ask me anything"
                className="flex-1 outline-none text-slate-700 placeholder-slate-400 text-sm"
                autoFocus
              />
              <button
                onClick={handleSend}
                disabled={loading || !input.trim()}
                className={`p-2 transition ${
                  loading || !input.trim()
                    ? "text-slate-300 cursor-not-allowed"
                    : "text-teal-500 hover:text-teal-600"
                }`}
              >
                {loading ? (
                  <svg
                    className="w-5 h-5 animate-spin"
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
                    className="w-5 h-5"
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
              <div className="flex gap-3">
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
