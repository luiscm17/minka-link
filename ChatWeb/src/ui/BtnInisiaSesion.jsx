import React from "react";
import { Link } from "react-router-dom";

function BtnInisiaSesion() {
  return (
    <Link to="/signin" className="inline-block">
      <button className="px-4 py-2 bg-theme-primary text-white rounded-full text-sm font-medium hover:bg-theme-primary-hover transition cursor-pointer">
        Sign in
      </button>
    </Link>
  );
}

export default BtnInisiaSesion;
