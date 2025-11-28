import React, { useState } from "react";
import { Link } from "react-router-dom";
import mayor from "../assets/mayor.svg";
import menorAriba from "../assets/menor ariba.svg";
import menorBajo from "../assets/menorbajo.svg";
import abajo from "../assets/abajo.svg";

function SignIn() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Login", { username, password });
  };

  return (
    <div className="min-h-dvh bg-theme-bg w-full font-sans overflow-x-hidden flex flex-col md:block">
      <div className="w-full min-h-dvh grid grid-cols-1 md:grid-cols-2 relative">
        {/* Left decorative area using provided SVGs */}
        <div className="relative hidden md:block w-full h-full bg-theme-bg overflow-hidden min-h-[500px]">
          {/* Main large shape (Mayor) - Top Left */}
          <img
            src={mayor}
            alt="Decorative shape"
            className="absolute -top-[21%] -left-[20%] w-[96%] max-w-11/12 z-10 select-none pointer-events-none"
          />
          {/* Top Right Shape (Menor Arriba) */}
          <img
            src={menorAriba}
            alt="Decorative shape"
            className="absolute -top-[5%] right-20 w-[50%] z-0 opacity-90 select-none pointer-events-none"
          />
          {/* Bottom Left Shape (Menor Bajo) */}
          <img
            src={menorBajo}
            alt="Decorative shape"
            className="absolute bottom-[1%] -left-[10%] w-[30%] z-20 opacity-95 select-none pointer-events-none"
          />
        </div>
        {/* Bottom Right Shape */}
        <img
          src={abajo}
          alt="Decorative shape"
          className="hidden md:block absolute -bottom-3 right-80 w-[40%] z-40 opacity-95 select-none pointer-events-none"
        />

        {/* Right form area */}
        <div className="flex items-center justify-center px-6 sm:px-8 md:px-20 py-8 md:py-12 z-30 bg-theme-bg h-full w-full">
          <div className="w-full max-w-md">
            <h2 className="text-3xl md:text-5xl font-extrabold text-theme-text mb-8 md:mb-12 text-center tracking-tight">
              Sign in
            </h2>

            <form onSubmit={handleSubmit} className="space-y-4 md:space-y-6">
              <div className="relative">
                <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
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
                      d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                    />
                  </svg>
                </span>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Username"
                  className="w-full pl-14 pr-4 py-3 md:py-4 bg-theme-surface rounded-lg border border-theme text-theme-text placeholder-theme-secondary text-base md:text-lg font-medium focus:outline-none focus:ring-2 focus:ring-theme-primary transition"
                />
              </div>

              <div className="relative">
                <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
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
                      d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                    />
                  </svg>
                </span>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Password"
                  className="w-full pl-14 pr-4 py-3 md:py-4 bg-theme-surface rounded-lg border border-theme text-theme-text placeholder-theme-secondary text-base md:text-lg font-medium focus:outline-none focus:ring-2 focus:ring-theme-primary transition"
                />
              </div>

              <div className="flex justify-center pt-2">
                <button
                  type="submit"
                  className="cursor-pointer w-full sm:w-64 py-3 rounded-full text-white font-semibold text-base md:text-lg bg-linear-to-r from-[#14b8a6] to-[#0f172a] hover:opacity-95 transition-shadow shadow-lg active:scale-95"
                >
                  Login
                </button>
              </div>

              <div className="text-center pt-3">
                <a
                  href="#"
                  className="text-theme-secondary hover:text-theme-text text-sm"
                >
                  forget your password
                </a>
              </div>
            </form>

            <div className="mt-8 md:mt-12 text-center">
              <Link
                to="/signup"
                className="text-theme-secondary hover:text-theme-text font-medium text-base inline-flex items-center gap-2 transition-colors p-2"
              >
                Create an account
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-4 w-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M17 8l4 4m0 0l-4 4m4-4H3"
                  />
                </svg>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SignIn;
