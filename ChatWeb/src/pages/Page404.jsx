import React from "react";
import logoChatImg from "../assets/logochat.png";
import { useNavigate } from "react-router-dom";

function Page404() {
  const navigate = useNavigate();

  return (
    <div className="h-screen flex flex-col bg-white">
      {/* Header */}
      <div className="border-b border-slate-200 px-8 py-4 flex justify-between items-center bg-white">
        <div className="">
          <img
            src={logoChatImg}
            alt="Logo Chat"
            className="h-12 cursor-pointer"
            onClick={() => navigate("/")}
          />
        </div>
        <div className="flex gap-2">
          <button className="px-4 py-2 bg-teal-500 text-white rounded-full text-sm font-medium hover:bg-teal-600 transition">
            Sign in
          </button>
          <button className="px-4 py-2 border border-slate-400 text-slate-700 rounded-full text-sm font-medium hover:bg-white transition">
            Sign up
          </button>
        </div>
      </div>

      {/* Contenedor principal centrado */}
      <div className="flex-1 flex flex-col items-center justify-center px-4">
        <div className="text-center">
          {/* Número 404 grande */}
          <h1 className="text-8xl font-bold text-teal-500 mb-4">404</h1>

          {/* Title */}
          <h2 className="text-4xl font-light text-slate-700 mb-2">
            Page Not Found
          </h2>

          {/* Description */}
          <p className="text-lg text-slate-500 mb-8 max-w-md mx-auto">
            Sorry, the page you're looking for doesn't exist or has been moved.
            Go back to the home page to continue exploring.
          </p>

          {/* Botón de regreso */}
          <button
            onClick={() => navigate("/")}
            className="px-8 py-3 bg-teal-500 text-white rounded-full font-medium hover:bg-teal-600 transition shadow-md hover:shadow-lg"
          >
            Back to Home
          </button>

          {/* Decoración */}
          <div className="mt-16">
            <svg
              className="w-32 h-32 mx-auto text-slate-200"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1}
                d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Page404;
