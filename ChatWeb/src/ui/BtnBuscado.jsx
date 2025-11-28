import React from "react";

function BtnBuscado() {
  return (
    <>
      <button className="px-3 py-1 border border-theme rounded-full text-xs text-theme-text hover:bg-theme-hover transition flex items-center gap-1 cursor-pointer">
        <span>🔍</span> Most Searched
      </button>
    </>
  );
}

export default BtnBuscado;
