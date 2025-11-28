import React from "react";

function BtnEstado() {
  return (
    <>
      <button className="px-3 py-1 border border-theme rounded-full text-xs text-theme-text hover:bg-theme-hover transition flex items-center gap-1 cursor-pointer">
        <span>📋</span> Status
      </button>
    </>
  );
}

export default BtnEstado;
