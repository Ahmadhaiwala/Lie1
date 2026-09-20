import { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Zap, Menu, X, Play } from "lucide-react";

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
    { to: "/#contact",      label: "Contact",      isHash: true  },
    { to: "/dashboard",     label: "Dashboard",    isHash: false },
  ];

  return (
    <motion.header
      initial={{ y: -80, opacity: 0 }}
      animate={{ y: 0,   opacity: 1 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled
          ? "bg-black/80 backdrop-blur-md border-b border-white/8 shadow-lg"
          : "bg-transparent"
      }`}
    >
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">

        {/* Logo */}
        <a href="/" className="flex items-center gap-2">
          <motion.div
            whileHover={{ rotate: 15, scale: 1.1 }}
            className="w-8 h-8 rounded-lg bg-orange-500 flex items-center justify-center"
          >
            <Zap className="w-4 h-4 text-black fill-black" />
          </motion.div>
          <span className="font-display font-bold text-xl text-white">
            Lead<span className="text-orange-400">Bot</span>
            <span className="text-orange-500">AI</span>
          </span>
        </a>

        {/* Desktop links */}
        <div className="hidden md:flex items-center gap-1">
          {links.map(({ to, label, isHash }) => (
            <a
              key={label}
              href={to}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                !isHash && pathname === to
                  ? "text-white bg-orange-500/15 border border-orange-500/30"
                  : "text-zinc-400 hover:text-white hover:bg-white/5"
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
            className="btn-primary text-sm py-2"
          >
            <Zap className="w-4 h-4" />
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
            className="md:hidden bg-black/90 border-b border-white/8 backdrop-blur-md"
          >
            <div className="px-4 py-4 flex flex-col gap-2">
              {links.map(({ to, label }) => (
                <a
                  key={label}
                  href={to}
                  onClick={() => setOpen(false)}
                  className="px-4 py-2.5 rounded-lg text-zinc-300 hover:text-white hover:bg-white/5 text-sm transition-all"
                >
                  {label}
                </a>
              ))}
              <a href="/run" className="btn-secondary mt-1 justify-center text-sm">
                <Play className="w-4 h-4 fill-orange-400" /> Run Jobs
              </a>
              <a href="/#contact" className="btn-primary mt-1 justify-center text-sm">
                <Zap className="w-4 h-4" /> Get Started
              </a>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.header>
  );
}
