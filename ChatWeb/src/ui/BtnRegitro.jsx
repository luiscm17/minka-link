import React from "react";
import { Link } from "react-router-dom";

function BtnRegitro() {
  return (
    <>
      <Link to="/signup" className="inline-block">
        <button className="px-4 py-2 border-2 border-theme text-theme-text rounded-full text-sm font-medium hover:bg-theme-hover transition cursor-pointer">
          Sign up
        </button>
      </Link>
    </>
  );
}

export default BtnRegitro;
