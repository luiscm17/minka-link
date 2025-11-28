import React, { useState, useEffect, useRef } from "react";
import { useTheme } from "../contexts/ThemeContext";

const AccessibilityWelcome = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { setSpecificTheme } = useTheme();
  const modalRef = useRef(null);
  const yesButtonRef = useRef(null);

  useEffect(() => {
    // Verificar si ya se ha mostrado el mensaje
    // Verificar si ya se ha mostrado el mensaje
    // const hasSeenWelcome = localStorage.getItem("hasSeenAccessibilityWelcome");
    // if (!hasSeenWelcome) {
    setIsOpen(true);
    // }
  }, []);

  useEffect(() => {
    if (isOpen) {
      // Mover el foco al botón "Sí" cuando se abre el modal
      setTimeout(() => {
        yesButtonRef.current?.focus();
      }, 100);

      // Trampa de foco (Focus Trap)
      const handleTabKey = (e) => {
        if (e.key === "Tab") {
          const focusableModalElements = modalRef.current.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
          );
          const firstElement = focusableModalElements[0];
          const lastElement =
            focusableModalElements[focusableModalElements.length - 1];

          if (e.shiftKey) {
            // Shift + Tab
            if (document.activeElement === firstElement) {
              lastElement.focus();
              e.preventDefault();
            }
          } else {
            // Tab
            if (document.activeElement === lastElement) {
              firstElement.focus();
              e.preventDefault();
            }
          }
        }
      };

      const keyListener = (e) => {
        if (e.key === "Escape") {
          handleClose();
        }
        handleTabKey(e);
      };

      document.addEventListener("keydown", keyListener);
      return () => {
        document.removeEventListener("keydown", keyListener);
      };
    }
  }, [isOpen]);

  const handleClose = () => {
    setIsOpen(false);
    localStorage.setItem("hasSeenAccessibilityWelcome", "true");
  };

  const handleEnableAccessibility = () => {
    setSpecificTheme("colorblind");
    handleClose();
    // Anunciar cambio (opcional, dependiendo de si el ThemeContext ya lo hace o si el cambio visual es suficiente)
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="acc-title"
      aria-describedby="acc-desc"
    >
      <div
        ref={modalRef}
        className="bg-white dark:bg-slate-800 p-6 rounded-2xl shadow-2xl max-w-md w-full border-2 border-blue-500"
      >
        <h2
          id="acc-title"
          className="text-2xl font-bold mb-4 text-gray-900 dark:text-white"
        >
          Opciones de Accesibilidad
        </h2>

        <p
          id="acc-desc"
          className="text-lg mb-8 text-gray-700 dark:text-gray-300"
        >
          Bienvenido. ¿Deseas activar el modo de alto contraste para mejorar la
          visibilidad?
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-end">
          <button
            onClick={handleClose}
            className="px-6 py-3 rounded-lg border-2 border-gray-300 text-gray-700 font-semibold hover:bg-gray-100 focus:ring-4 focus:ring-gray-200 transition-all"
          >
            No, gracias
          </button>

          <button
            ref={yesButtonRef}
            onClick={handleEnableAccessibility}
            className="px-6 py-3 rounded-lg bg-blue-600 text-white font-bold hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 transition-all shadow-lg"
          >
            Sí, activar alto contraste
          </button>
        </div>
      </div>
    </div>
  );
};

export default AccessibilityWelcome;
