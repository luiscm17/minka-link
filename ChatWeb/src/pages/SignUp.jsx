import React, { useState } from "react";
import regAbajo from "../assets/registro abajo.svg";
import regAribaAriba from "../assets/registro ariba ariba.svg";
import regAriba from "../assets/registro ariba.svg";
import regMedio from "../assets/registro medio.svg";

function SignUp() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [mesNacimiento, setMesNacimiento] = useState("");
  const [diaNacimiento, setDiaNacimiento] = useState("");
  const [anoNacimiento, setAnoNacimiento] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Register", {
      name,
      email,
      password,
      mesNacimiento,
      diaNacimiento,
      anoNacimiento,
    });
  };

  return (
    <div className="min-h-dvh bg-theme-bg w-full font-sans overflow-x-hidden">
      <div className="w-full min-h-dvh grid grid-cols-1 md:grid-cols-2 relative">
        {/* Left: form */}
        <div className="flex items-start md:items-center justify-center px-6 sm:px-8 md:px-24 py-8 md:py-0 w-full">
          <div className="w-full max-w-sm">
            <h2 className="text-3xl md:text-5xl font-extrabold text-theme-text mb-6 md:mb-8 text-center md:text-left">
              Register
            </h2>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-theme-secondary">
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
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Name"
                  className="w-full pl-12 pr-4 py-3 bg-theme-surface rounded-lg text-theme-text placeholder-theme-secondary text-base font-medium focus:outline-none border border-theme"
                />
              </div>

              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-theme-secondary">
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
                      d="M16 12H8m0 0l4-4m-4 4l4 4"
                    />
                  </svg>
                </span>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Email Address"
                  className="w-full pl-12 pr-4 py-3 bg-theme-surface rounded-lg text-theme-text placeholder-theme-secondary text-base font-medium focus:outline-none border border-theme"
                />
              </div>

              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-theme-secondary">
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
                  placeholder="Passsword"
                  className="w-full pl-12 pr-4 py-3 bg-theme-surface rounded-lg text-theme-text placeholder-theme-secondary text-base font-medium focus:outline-none border border-theme"
                />
              </div>

              {/* Fecha de Nacimiento - Grid con 3 selectores */}
              <div>
                <span className="text-sm text-theme-secondary font-medium mb-2 block">
                  Fecha de nacimiento
                </span>
                <div className="grid grid-cols-3 gap-2 md:gap-3">
                  {/* Mes */}
                  <div className="relative">
                    <select
                      value={mesNacimiento}
                      onChange={(e) => setMesNacimiento(e.target.value)}
                      className="w-full px-2 md:px-3 py-3 bg-theme-surface rounded-lg text-theme-text text-sm font-medium focus:outline-none appearance-none cursor-pointer border border-theme"
                    >
                      <option value="">Mes</option>
                      <option value="01">Enero</option>
                      <option value="02">Febrero</option>
                      <option value="03">Marzo</option>
                      <option value="04">Abril</option>
                      <option value="05">Mayo</option>
                      <option value="06">Junio</option>
                      <option value="07">Julio</option>
                      <option value="08">Agosto</option>
                      <option value="09">Septiembre</option>
                      <option value="10">Octubre</option>
                      <option value="11">Noviembre</option>
                      <option value="12">Diciembre</option>
                    </select>
                  </div>

                  {/* Día */}
                  <div className="relative">
                    <select
                      value={diaNacimiento}
                      onChange={(e) => setDiaNacimiento(e.target.value)}
                      className="w-full px-2 md:px-3 py-3 bg-theme-surface rounded-lg text-theme-text text-sm font-medium focus:outline-none appearance-none cursor-pointer border border-theme"
                    >
                      <option value="">Día</option>
                      {Array.from({ length: 31 }, (_, i) => i + 1).map(
                        (day) => (
                          <option
                            key={day}
                            value={day.toString().padStart(2, "0")}
                          >
                            {day}
                          </option>
                        )
                      )}
                    </select>
                  </div>

                  {/* Año */}
                  <div className="relative">
                    <select
                      value={anoNacimiento}
                      onChange={(e) => setAnoNacimiento(e.target.value)}
                      className="w-full px-2 md:px-3 py-3 bg-theme-surface rounded-lg text-theme-text text-sm font-medium focus:outline-none appearance-none cursor-pointer border border-theme"
                    >
                      <option value="">Año</option>
                      {Array.from(
                        { length: 100 },
                        (_, i) => new Date().getFullYear() - i
                      ).map((year) => (
                        <option key={year} value={year}>
                          {year}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              <div className="pt-4 flex justify-center md:justify-start">
                <button
                  type="submit"
                  className="w-full sm:w-56 py-3 rounded-full text-white font-semibold bg-theme-primary hover:bg-theme-primary-hover transition-all shadow-md cursor-pointer bg-linear-to-r from-[#14b8a6] to-[#0f172a] active:scale-95"
                >
                  Registrarse
                </button>
              </div>
            </form>
          </div>
        </div>

        {/* Right: decorative SVGs (registro assets) */}
        <div className="relative hidden md:block w-full h-full bg-theme-bg overflow-visible">
          {/* Big rounded shape bottom-right */}
          <img
            src={regMedio}
            alt="registro medio"
            className="absolute right-0 -bottom-12 w-[85%] max-w-none z-10 select-none pointer-events-none transform-gpu"
          />

          {/* Top-right elongated shape */}
          <img
            src={regAriba}
            alt="registro ariba"
            className="absolute top-4 right-0  w-[25%] z-20 select-none pointer-events-none transform-gpu "
          />

          {/* Small top-left accent (overlapping) */}

          {/* Small bottom accent */}
          <img
            src={regAbajo}
            alt="registro abajo"
            className="absolute right-60 -bottom-6 w-[70%] z-40 select-none pointer-events-none transform-gpu"
          />
        </div>
        <img
          src={regAribaAriba}
          alt="registro ariba ariba"
          className="absolute left-100 w-[22%] z-30 select-none pointer-events-none transform-gpu"
        />
      </div>
    </div>
  );
}

export default SignUp;
