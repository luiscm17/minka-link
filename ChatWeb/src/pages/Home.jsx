import React, { useRef, useEffect } from "react";
import { useState } from "react";
import logoChatImg from "../assets/logochat.png";
import BtnInisiaSesion from "../ui/BtnInisiaSesion";
import BtnRegitro from "../ui/BtnRegitro";
import BtnEstado from "../ui/BtnEstado";
import BtnBuscado from "../ui/BtnBuscado";

function Home() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = () => {
    if (input.trim()) {
      setMessages([...messages, { text: input, sender: "user" }]);
      setInput("");
      setTimeout(() => {
        setMessages((prev) => [
          ...prev,
          { text: "Procesando tu pregunta...", sender: "bot" },
        ]);
      }, 1000);
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
                Su guía de IA para el gobierno
              </h1>
              <p className="text-2xl font-light text-slate-400 mt-2">
                de tu ciudad
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
                placeholder="Pregunta lo que quieras"
                className="flex-1 outline-none text-slate-700 placeholder-slate-400 text-sm"
                autoFocus
              />
              <button
                onClick={handleSend}
                className="p-2 text-teal-500 hover:text-teal-600 transition"
              >
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
