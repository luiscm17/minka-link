import React from "react";
import { Link } from "react-router-dom";

function BtnInisiaSesion() {
  return (
    <Link to="/signin" className="inline-block">
      <button className="px-4 py-2 bg-teal-500 text-white rounded-full text-sm font-medium hover:bg-teal-600 transition">
        Sign in
      </button>
    </Link>
  );
}

export default BtnInisiaSesion;
