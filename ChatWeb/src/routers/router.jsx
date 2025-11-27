import React from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import Home from "../pages/Home.jsx";
import Page404 from "../pages/Page404.jsx";

export const Myrouter = () => (
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<Home />} />

      <Route path="*" element={<Page404 />} />
    </Routes>
  </BrowserRouter>
);
