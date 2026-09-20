import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { Home, ArrowLeft, Zap } from "lucide-react";
import GlowOrb from "../components/GlowOrb";
import ParticleBackground from "../components/ParticleBackground";

export default function NotFound() {
  const navigate = useNavigate();

  return (
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden">
      <GlowOrb className="w-96 h-96 -top-20 left-1/2 -translate-x-1/2 opacity-30" color="brand" />
      <GlowOrb className="w-64 h-64 bottom-20 right-10 opacity-20" color="neon" />

      <div className="relative z-10 text-center px-4 max-w-2xl mx-auto">
        {/* Animated 404 */}
        <motion.div
          initial={{ scale: 0.5, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.7, type: "spring", bounce: 0.4 }}
          className="mb-8"
        >
          <span className="font-display font-black text-[10rem] sm:text-[14rem] leading-none bg-gradient-to-br from-brand-500 via-purple-500 to-neon bg-clip-text text-transparent select-none">
            404
          </span>
        </motion.div>

        {/* Floating icon */}
        <motion.div
          animate={{ y: [0, -12, 0] }}
          transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
          className="w-20 h-20 rounded-2xl bg-gradient-to-br from-brand-500 to-neon flex items-center justify-center mx-auto mb-8 shadow-2xl shadow-brand-500/30"
        >
          <Zap className="w-10 h-10 text-white fill-white" />
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.6 }}
          className="font-display font-bold text-3xl sm:text-4xl text-white mb-4"
        >
          Page Not Found
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.6 }}
          className="text-slate-400 text-lg mb-10 leading-relaxed"
        >
          Looks like our AI crawler couldn't find this page either.
          <br />
          Let's get you back on track.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.6 }}
          className="flex flex-col sm:flex-row items-center justify-center gap-4"
        >
          <motion.button
            onClick={() => navigate(-1)}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.97 }}
            className="btn-secondary"
          >
            <ArrowLeft className="w-4 h-4" />
            Go Back
          </motion.button>
          <motion.a
            href="/"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.97 }}
            className="btn-primary"
          >
            <Home className="w-4 h-4" />
            Back to Home
          </motion.a>
        </motion.div>
      </div>
    </div>
  );
}
