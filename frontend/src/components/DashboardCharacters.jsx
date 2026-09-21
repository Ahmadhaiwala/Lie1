import { motion } from "framer-motion";

/**
 * DashboardCharacters.jsx
 * Animated character overlays for the dashboard with different fills and expressions.
 * Makes the dashboard feel more alive and engaging.
 */

// Character 1: Happy Data Bot (Orange fill)
export function HappyDataBot({ size = 120, delay = 0 }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.6 }}
      className="relative inline-flex items-center justify-center"
      style={{ width: size, height: size }}
    >
      <motion.div
        animate={{
          y: [0, -8, 0],
          rotate: [0, 2, -2, 0],
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        style={{ width: size, height: size }}
      >
        <svg
          viewBox="0 0 200 200"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          width="100%"
          height="100%"
        >
          {/* Head */}
          <circle cx="100" cy="80" r="45" fill="#F97316" />
          
          {/* Happy eyes */}
          <ellipse cx="85" cy="70" rx="8" ry="12" fill="white" />
          <ellipse cx="115" cy="70" rx="8" ry="12" fill="white" />
          
          {/* Pupils looking down happily */}
          <ellipse cx="85" cy="75" rx="4" ry="5" fill="#1F2937" />
          <ellipse cx="115" cy="75" rx="4" ry="5" fill="#1F2937" />
          
          {/* Big smile */}
          <path
            d="M 80 88 Q 100 100 120 88"
            stroke="#1F2937"
            strokeWidth="3"
            strokeLinecap="round"
            fill="none"
          />
          
          {/* Rosy cheeks */}
          <ellipse cx="55" cy="85" rx="12" ry="8" fill="#EC4899" opacity="0.5" />
          <ellipse cx="145" cy="85" rx="12" ry="8" fill="#EC4899" opacity="0.5" />
          
          {/* Body */}
          <rect x="70" y="120" width="60" height="50" rx="15" fill="#FFA500" opacity="0.8" />
          
          {/* Arms */}
          <circle cx="50" cy="135" r="12" fill="#F97316" />
          <circle cx="150" cy="135" r="12" fill="#F97316" />
          
          {/* Legs */}
          <rect x="80" y="165" width="12" height="25" rx="6" fill="#F97316" />
          <rect x="108" y="165" width="12" height="25" rx="6" fill="#F97316" />
        </svg>
      </motion.div>
    </motion.div>
  );
}

// Character 2: Thinking Data Explorer (Blue fill)
export function ThinkingExplorer({ size = 120, delay = 0 }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.6 }}
      className="relative inline-flex items-center justify-center"
      style={{ width: size, height: size }}
    >
      <motion.div
        animate={{
          y: [0, -6, 0],
          scale: [1, 1.02, 1],
        }}
        transition={{
          duration: 3.5,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        style={{ width: size, height: size }}
      >
        <svg
          viewBox="0 0 200 200"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          width="100%"
          height="100%"
        >
          {/* Head */}
          <circle cx="100" cy="75" r="42" fill="#3B82F6" />
          
          {/* Thinking eyes */}
          <ellipse cx="85" cy="68" rx="7" ry="10" fill="white" />
          <ellipse cx="115" cy="68" rx="7" ry="10" fill="white" />
          
          {/* Pupils looking up thinking */}
          <ellipse cx="85" cy="63" rx="3" ry="4" fill="#1F2937" />
          <ellipse cx="115" cy="63" rx="3" ry="4" fill="#1F2937" />
          
          {/* Thinking expression - puzzled mouth */}
          <path
            d="M 85 82 Q 100 88 115 82"
            stroke="#1F2937"
            strokeWidth="2.5"
            strokeLinecap="round"
            fill="none"
          />
          
          {/* Thinking bubble */}
          <motion.circle
            cx="55"
            cy="50"
            r="8"
            fill="#3B82F6"
            animate={{ scale: [1, 1.2, 1], opacity: [0.6, 1, 0.6] }}
            transition={{ duration: 2, repeat: Infinity }}
          />
          <motion.circle
            cx="45"
            cy="40"
            r="5"
            fill="#3B82F6"
            animate={{ scale: [1, 1.3, 1], opacity: [0.5, 0.9, 0.5] }}
            transition={{ duration: 2.2, repeat: Infinity, delay: 0.2 }}
          />
          
          {/* Body with lines (data vibes) */}
          <rect x="68" y="115" width="64" height="55" rx="12" fill="#60A5FA" opacity="0.7" />
          
          {/* Data lines on body */}
          <line x1="75" y1="130" x2="125" y2="130" stroke="white" strokeWidth="2" opacity="0.6" />
          <line x1="75" y1="145" x2="115" y2="145" stroke="white" strokeWidth="2" opacity="0.6" />
          <line x1="75" y1="160" x2="120" y2="160" stroke="white" strokeWidth="2" opacity="0.6" />
          
          {/* Arms holding something */}
          <rect x="45" y="125" width="10" height="40" rx="5" fill="#3B82F6" />
          <rect x="145" y="125" width="10" height="40" rx="5" fill="#3B82F6" />
        </svg>
      </motion.div>
    </motion.div>
  );
}

// Character 3: Excited Lead Finder (Green fill)
export function ExcitedLeadFinder({ size = 120, delay = 0 }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.6 }}
      className="relative inline-flex items-center justify-center"
      style={{ width: size, height: size }}
    >
      <motion.div
        animate={{
          y: [0, -12, 0],
          rotate: [-1, 1, -1],
        }}
        transition={{
          duration: 2.5,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        style={{ width: size, height: size }}
      >
        <svg
          viewBox="0 0 200 200"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          width="100%"
          height="100%"
        >
          {/* Head */}
          <circle cx="100" cy="80" r="44" fill="#10B981" />
          
          {/* Excited eyes wide */}
          <circle cx="82" cy="70" r="10" fill="white" />
          <circle cx="118" cy="70" r="10" fill="white" />
          
          {/* Big excited pupils */}
          <circle cx="82" cy="72" r="5" fill="#1F2937" />
          <circle cx="118" cy="72" r="5" fill="#1F2937" />
          
          {/* Eye shine big */}
          <circle cx="85" cy="68" r="2.5" fill="white" />
          <circle cx="121" cy="68" r="2.5" fill="white" />
          
          {/* Big excited smile */}
          <path
            d="M 78 90 Q 100 104 122 90"
            stroke="#1F2937"
            strokeWidth="3"
            strokeLinecap="round"
            fill="none"
          />
          
          {/* Happy cheeks */}
          <ellipse cx="50" cy="85" rx="14" ry="10" fill="#34D399" opacity="0.6" />
          <ellipse cx="150" cy="85" rx="14" ry="10" fill="#34D399" opacity="0.6" />
          
          {/* Body jumping */}
          <rect x="68" y="120" width="64" height="50" rx="12" fill="#34D399" />
          
          {/* Jumping arms raised */}
          <path d="M 60 130 L 40 100" stroke="#10B981" strokeWidth="12" strokeLinecap="round" />
          <path d="M 140 130 L 160 100" stroke="#10B981" strokeWidth="12" strokeLinecap="round" />
          
          {/* Legs */}
          <rect x="78" y="165" width="10" height="28" rx="5" fill="#10B981" />
          <rect x="112" y="165" width="10" height="28" rx="5" fill="#10B981" />
          
          {/* Star of excitement */}
          <motion.g
            animate={{ scale: [0, 1, 0], rotate: [0, 180, 360] }}
            transition={{ duration: 1.5, repeat: Infinity }}
            opacity="0.7"
          >
            <circle cx="140" cy="40" r="3" fill="#FBBF24" />
            <circle cx="155" cy="50" r="2.5" fill="#FBBF24" />
            <circle cx="145" cy="55" r="2" fill="#FBBF24" />
          </motion.g>
        </svg>
      </motion.div>
    </motion.div>
  );
}

// Character 4: Confident Results Master (Purple fill)
export function ConfidentMaster({ size = 120, delay = 0 }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.6 }}
      className="relative inline-flex items-center justify-center"
      style={{ width: size, height: size }}
    >
      <motion.div
        animate={{
          y: [0, -4, 0],
        }}
        transition={{
          duration: 4,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        style={{ width: size, height: size }}
      >
        <svg
          viewBox="0 0 200 200"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          width="100%"
          height="100%"
        >
          {/* Head */}
          <circle cx="100" cy="75" r="43" fill="#8B5CF6" />
          
          {/* Confident eyes - cool */}
          <ellipse cx="83" cy="68" rx="8" ry="11" fill="white" />
          <ellipse cx="117" cy="68" rx="8" ry="11" fill="white" />
          
          {/* Cool pupils */}
          <ellipse cx="83" cy="72" rx="4" ry="5" fill="#1F2937" />
          <ellipse cx="117" cy="72" rx="4" ry="5" fill="#1F2937" />
          
          {/* Cool eyebrows */}
          <path
            d="M 75 60 Q 83 57 91 60"
            stroke="#1F2937"
            strokeWidth="2.5"
            strokeLinecap="round"
            fill="none"
          />
          <path
            d="M 109 60 Q 117 57 125 60"
            stroke="#1F2937"
            strokeWidth="2.5"
            strokeLinecap="round"
            fill="none"
          />
          
          {/* Confident slight smile */}
          <path
            d="M 82 85 Q 100 92 118 85"
            stroke="#1F2937"
            strokeWidth="2.5"
            strokeLinecap="round"
            fill="none"
          />
          
          {/* Cape/cloak effect */}
          <path
            d="M 60 110 Q 60 140 100 160 Q 140 140 140 110"
            fill="#7C3AED"
            opacity="0.6"
          />
          
          {/* Body strong */}
          <rect x="70" y="115" width="60" height="45" rx="10" fill="#A78BFA" opacity="0.8" />
          
          {/* Strong arms */}
          <circle cx="48" cy="132" r="14" fill="#8B5CF6" />
          <circle cx="152" cy="132" r="14" fill="#8B5CF6" />
          
          {/* Checkmark on chest */}
          <path
            d="M 88 130 L 96 138 L 112 122"
            stroke="white"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
            fill="none"
            opacity="0.8"
          />
        </svg>
      </motion.div>
    </motion.div>
  );
}

// Wrapper component to display all characters
export function DashboardCharactersDisplay() {
  return (
    <div className="flex flex-wrap items-center justify-center gap-8 opacity-20 pointer-events-none select-none">
      <HappyDataBot size={100} delay={0} />
      <ThinkingExplorer size={100} delay={0.2} />
      <ExcitedLeadFinder size={100} delay={0.4} />
      <ConfidentMaster size={100} delay={0.6} />
    </div>
  );
}
