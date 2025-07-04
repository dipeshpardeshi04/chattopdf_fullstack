import React from "react";
import Navbar from "./scripts/navbar";
import First from "./scripts/first";
import Second from "./scripts/second";
import "./styles/App.css";
import Third from "./scripts/third";
import Footer from "./scripts/Footer";

function App() {
  return (
    <>
      <div className="App">
        <Navbar />
      </div>
      <First />
      <Second />
      <Third />
      <Footer />
    </>
  );
}

export default App;
