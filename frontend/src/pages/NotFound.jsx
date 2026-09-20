import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { Home, ArrowLeft, Zap } from "lucide-react";

export default function NotFound() {
  const navigate = useNavigate();
  return (
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden bg-[#111]">
      <div className="absolute inset-0 bg-radial-glow" aria-hidden="true" />

      <div className="relative z-10 text-center px-4 max-w-2xl mx-auto">
        <motion.div
          initial={{ scale: 0.5, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.7, type: "spring", bounce: 0.4 }}
          className="mb-8"
        >
          <span className="font-display font-black text-[10rem] sm:text-[14rem] leading-none bg-gradient-to-br from-orange-500 to-white bg-clip-text text-transparent select-none">
            404
          </span>
        </motion.div>

        <motion.div
          animate={{ y: [0, -12, 0] }}
          transition={{ duration: 3, repeat: Infinity }}
          className="w-20 h-20 rounded-2xl bg-orange-500 flex items-center justify-center mx-auto mb-8 shadow-2xl shadow-orange-500/30"
        >
          <Zap className="w-10 h-10 text-black fill-black" />
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="font-display font-bold text-3xl sm:text-4xl text-white mb-4"
        >
          Page Not Found
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="text-zinc-400 text-lg mb-10"
        >
          Looks like our AI crawler couldn't find this page either.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="flex flex-col sm:flex-row items-center justify-center gap-4"
        >
          <motion.button onClick={() => navigate(-1)} whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.97 }}
            className="btn-secondary">
            <ArrowLeft className="w-4 h-4" /> Go Back
          </motion.button>
          <motion.a href="/" whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.97 }} className="btn-primary">
            <Home className="w-4 h-4" /> Back to Home
          </motion.a>
        </motion.div>
      </div>
    </div>
  );
}
