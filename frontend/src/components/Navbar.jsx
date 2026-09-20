import { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Zap, Menu, X, LayoutDashboard, Home } from "lucide-react";

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);
  const { pathname } = useLocation();

  useEffect(() => {
    const fn = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", fn);
    return () => window.removeEventListener("scroll", fn);
  }, []);

  const links = [
    { to: "/", label: "Home", icon: Home },
    { to: "/#services", label: "Services", icon: null },
    { to: "/#how-it-works", label: "How It Works", icon: null },
    { to: "/#contact", label: "Contact", icon: null },
    { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  ];

  return (
    <motion.header
      initial={{ y: -80, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled ? "glass border-b border-white/5 shadow-xl" : "bg-transparent"
      }`}
    >
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2 group">
          <motion.div
            whileHover={{ rotate: 20, scale: 1.1 }}
            className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-500 to-neon flex items-center justify-center"
          >
            <Zap className="w-4 h-4 text-white fill-white" />
          </motion.div>
          <span className="font-display font-bold text-xl text-white">
            Lead<span className="gradient-text">Bot</span>
            <span className="text-brand-400 ml-0.5">AI</span>
          </span>
        </Link>

        {/* Desktop links */}
        <div className="hidden md:flex items-center gap-1">
          {links.map(({ to, label }) => (
            <a
              key={label}
              href={to}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                pathname === to
                  ? "text-white bg-brand-500/20"
                  : "text-slate-400 hover:text-white hover:bg-white/5"
              }`}
            >
              {label}
            </a>
          ))}
        </div>

        {/* CTA */}
        <div className="hidden md:flex items-center gap-3">
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
          className="md:hidden text-slate-300 hover:text-white"
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
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden glass border-b border-white/5"
          >
            <div className="px-4 py-4 flex flex-col gap-2">
              {links.map(({ to, label, icon: Icon }) => (
                <a
                  key={label}
                  href={to}
                  onClick={() => setOpen(false)}
                  className="flex items-center gap-2 px-4 py-2.5 rounded-lg text-slate-300 hover:text-white hover:bg-white/5 transition-all"
                >
                  {Icon && <Icon className="w-4 h-4" />}
                  {label}
                </a>
              ))}
              <a href="/#contact" className="btn-primary mt-2 justify-center text-sm">
                <Zap className="w-4 h-4" /> Get Started
              </a>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.header>
  );
}
