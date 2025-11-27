import { useState } from "react";
import logoChatImg from "./assets/logochat.png";

function App() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);

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

  return (
    <div className="min-h-screen  flex flex-col">
      {/* Header con botones */}
      <div className="px-8 py-4 flex justify-between items-center">
        <div className="">
          <img src={logoChatImg} alt="Logo Chat" className="h-20" />
        </div>
        <div className="flex gap-2">
          <button className="px-4 py-2 bg-teal-500 text-white rounded-full text-sm font-medium hover:bg-teal-600 transition">
            Iniciar sesión
          </button>
          <button className="px-4 py-2 border border-slate-400 text-slate-700 rounded-full text-sm font-medium hover:bg-white transition">
            Registrate
          </button>
        </div>
      </div>

      {/* Contenedor principal */}
      <div className="flex-1 flex flex-col items-center justify-center px-4">
        {/* Título */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-light text-slate-400 leading-tight">
            Su guía de IA para el gobierno
          </h1>
          <p className="text-2xl font-light text-slate-400 mt-2">
            de la ciudad de Nueva York
          </p>
        </div>

        {/* Barra de búsqueda */}
        <div className="w-full max-w-2xl">
          <div className="border-2 border-slate-300 rounded-3xl px-6 py-4 bg-white shadow-sm hover:shadow-md transition">
            <div className="flex items-center gap-3">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleSend()}
                placeholder="Escribe tu pregunta aquí"
                className="w-full mt-3 outline-none text-slate-700 placeholder-slate-400 text-sm"
              />

              <div className="flex-1" />
              <button className="p-2 text-slate-400 hover:text-slate-600 transition">
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
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
              </button>
            </div>
            <div className=" flex gap-3 mt-4">
              <button className="px-3 py-1 border border-slate-300 rounded-full text-xs text-slate-600 hover:bg-slate-50 transition flex items-center gap-1">
                <span>📋</span> Estado
              </button>
              <button className="px-3 py-1 border border-slate-300 rounded-full text-xs text-slate-600 hover:bg-slate-50 transition flex items-center gap-1">
                <span>🔍</span> Lo más buscado
              </button>
            </div>
          </div>
        </div>

        {/* Área de mensajes (si hay) */}
        {messages.length > 0 && (
          <div className="w-full max-w-2xl mt-8 space-y-3">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`p-3 rounded-lg ${
                  msg.sender === "user"
                    ? "bg-teal-100 text-teal-900 ml-auto max-w-xs"
                    : "bg-slate-200 text-slate-900 mr-auto max-w-xs"
                }`}
              >
                {msg.text}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
