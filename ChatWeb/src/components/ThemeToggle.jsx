// ThemeToggle.jsx - Botón para cambiar entre temas
import { useTheme } from "../contexts/ThemeContext";

function ThemeToggle() {
  const { theme, setSpecificTheme } = useTheme();

  const themes = [
    {
      id: "light",
      label: "Claro",
      icon: "☀️",
      description: "Tema claro",
    },
    {
      id: "dark",
      label: "Oscuro",
      icon: "🌙",
      description: "Tema oscuro",
    },
    {
      id: "colorblind",
      label: "Accesible",
      icon: "👁️",
      description: "Modo para daltonismo",
    },
  ];

  return (
    <div className="flex items-center gap-2 bg-theme-surface rounded-lg p-1 shadow-sm">
      {themes.map((t) => (
        <button
          key={t.id}
          onClick={() => setSpecificTheme(t.id)}
          className={`
            px-3 py-2 rounded-md text-sm font-medium transition-all
            ${
              theme === t.id
                ? "bg-theme-primary text-white shadow-md"
                : "text-theme-text hover:bg-theme-hover"
            }
          `}
          title={t.description}
          aria-label={t.description}
        >
          <span className="mr-1">{t.icon}</span>
          <span className="hidden sm:inline">{t.label}</span>
        </button>
      ))}
    </div>
  );
}

export default ThemeToggle;
