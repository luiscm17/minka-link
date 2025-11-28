// ThemeContext.jsx - Contexto para manejar el tema de la aplicación
import { createContext, useContext, useState, useEffect } from "react";

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme debe usarse dentro de ThemeProvider");
  }
  return context;
};

export function ThemeProvider({ children }) {
  // Obtener tema guardado o usar 'light' por defecto
  const [theme, setTheme] = useState(() => {
    const savedTheme = localStorage.getItem("theme");
    return savedTheme || "light";
  });

  // Aplicar tema al documento cuando cambie
  useEffect(() => {
    const root = document.documentElement;

    // Remover todas las clases de tema
    root.classList.remove("light", "dark", "colorblind");

    // Agregar la clase del tema actual
    root.classList.add(theme);

    // Guardar en localStorage
    localStorage.setItem("theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prevTheme) => {
      // Ciclo: light → dark → colorblind → light
      if (prevTheme === "light") return "dark";
      if (prevTheme === "dark") return "colorblind";
      return "light";
    });
  };

  const setSpecificTheme = (newTheme) => {
    if (["light", "dark", "colorblind"].includes(newTheme)) {
      setTheme(newTheme);
    }
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme, setSpecificTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}
