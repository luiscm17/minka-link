import React from "react";
import { Link } from "react-router-dom";

function BtnRegitro() {
  return (
    <>
      <Link to="/signup" className="inline-block">
        <button className="px-4 py-2 border border-slate-400 text-slate-700 rounded-full text-sm font-medium hover:bg-white transition cursor-pointer">
          Sign up
        </button>
      </Link>
    </>
  );
}

export default BtnRegitro;
