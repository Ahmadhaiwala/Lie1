import { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Menu, X, Play, BarChart2 } from "lucide-react";
import Mascot from "./Mascot";

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [open,     setOpen]     = useState(false);
  const { pathname } = useLocation();

  useEffect(() => {
    const fn = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", fn);
    return () => window.removeEventListener("scroll", fn);
  }, []);

  const links = [
    { to: "/",              label: "Home",         isHash: false },
    { to: "/#services",     label: "Services",     isHash: true  },
    { to: "/#how-it-works", label: "How It Works", isHash: true  },
    { to: "/dashboard",     label: "Dashboard",    isHash: false },
    { to: "/#contact",      label: "Contact",      isHash: true  },
  ];

  return (
    <motion.header
      initial={{ y: -80, opacity: 0 }}
      animate={{ y: 0,   opacity: 1 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled ? "bg-black/85 backdrop-blur-md border-b border-white/8 shadow-lg" : "bg-transparent"
      }`}
    >
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">

        {/* Logo with mini mascot */}
        <a href="/" className="flex items-center gap-2.5 group">
          <div className="w-9 h-9 relative">
            <Mascot size={36} animate={false} ring={false} />
          </div>
          <span className="font-display font-bold text-xl text-white leading-none">
            Lead<span className="text-orange-400">Bot</span>
            <span className="text-orange-500 text-sm font-semibold ml-0.5">AI</span>
          </span>
        </a>

        {/* Desktop links */}
        <div className="hidden md:flex items-center gap-0.5">
          {links.map(({ to, label, isHash }) => (
            <a
              key={label}
              href={to}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                !isHash && pathname === to
                  ? "text-white bg-orange-500/15 border border-orange-500/30"
                  : "text-zinc-300 hover:text-white hover:bg-white/5"
              }`}
            >
              {label}
            </a>
          ))}
        </div>

        {/* CTA buttons */}
        <div className="hidden md:flex items-center gap-3">
          <motion.a
            href="/run"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.97 }}
            className="btn-secondary text-sm py-2 px-4"
          >
            <Play className="w-4 h-4 fill-orange-400" />
            Run Jobs
          </motion.a>
          <motion.a
            href="/#contact"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.97 }}
            className="btn-primary text-sm py-2 px-5"
          >
            Get Started
          </motion.a>
        </div>

        {/* Mobile toggle */}
        <button
          className="md:hidden text-zinc-300 hover:text-white"
          onClick={() => setOpen(!open)}
          aria-label="Toggle menu"
        >
          {open ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </nav>

      {/* Mobile menu */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{   opacity: 0, height: 0 }}
            className="md:hidden bg-black/95 border-b border-white/8 backdrop-blur-md"
          >
            <div className="px-4 py-4 flex flex-col gap-1.5">
              {links.map(({ to, label }) => (
                <a
                  key={label}
                  href={to}
                  onClick={() => setOpen(false)}
                  className={`px-4 py-2.5 rounded-lg text-sm transition-all ${
                    pathname === to
                      ? "text-white bg-orange-500/15 border border-orange-500/25"
                      : "text-zinc-300 hover:text-white hover:bg-white/5"
                  }`}
                >
                  {label}
                </a>
              ))}
              <div className="flex gap-2 mt-2">
                <a href="/run"       className="btn-secondary text-sm py-2.5 flex-1 justify-center">
                  <Play className="w-4 h-4 fill-orange-400" /> Run Jobs
                </a>
                <a href="/#contact"  className="btn-primary  text-sm py-2.5 flex-1 justify-center">
                  Get Started
                </a>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.header>
  );
}
