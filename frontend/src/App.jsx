import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import ParticleBackground from "./components/ParticleBackground";
import LandingPage from "./pages/LandingPage";
import Dashboard from "./pages/Dashboard";
import Footer from "./components/Footer";

export default function App() {
  return (
    <BrowserRouter>
      <div className="relative min-h-screen">
        <ParticleBackground />
        <Navbar />
        <main className="relative z-10">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/dashboard" element={<Dashboard />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </BrowserRouter>
  );
}
