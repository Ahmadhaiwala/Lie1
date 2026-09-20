/**
 * Mascot.jsx
 * Cute plant-pot mascot with a glowing orange ring.
 * Matches the 3D plant pot character provided — cream pot, green sprout,
 * big eyes, rosy cheeks, holding a green checkmark card.
 *
 * Props:
 *   size     — number (px), default 180
 *   animate  — bool, enables float animation, default true
 *   ring     — bool, shows orange glow ring, default true
 *   className — extra classes
 */

import { motion } from "framer-motion";

export default function Mascot({ size = 180, animate = true, ring = true, className = "" }) {
  const Wrapper = animate ? motion.div : "div";
  const wrapProps = animate
    ? {
        animate: { y: [0, -14, 0] },
        transition: { duration: 4, repeat: Infinity, ease: "easeInOut" },
      }
    : {};

  return (
    <div className={`relative inline-flex items-center justify-center ${className}`}
         style={{ width: size, height: size }}>

      {/* Outer glow ring */}
      {ring && (
        <>
          <motion.div
            animate={{ scale: [1, 1.08, 1], opacity: [0.4, 0.7, 0.4] }}
            transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
            className="absolute inset-0 rounded-full bg-orange-500/20 blur-xl"
          />
          <motion.div
            animate={{ scale: [1, 1.05, 1], opacity: [0.6, 1, 0.6] }}
            transition={{ duration: 3, repeat: Infinity, ease: "easeInOut", delay: 0.3 }}
            style={{ inset: size * 0.07 }}
            className="absolute rounded-full border-2 border-orange-500/50"
          />
        </>
      )}

      {/* Mascot SVG — plant pot character */}
      <Wrapper {...wrapProps} style={{ width: size * 0.8, height: size * 0.8 }}>
        <svg
          viewBox="0 0 200 230"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          width="100%"
          height="100%"
        >
          {/* Soil */}
          <ellipse cx="100" cy="88" rx="52" ry="12" fill="#8B5E3C" />

          {/* Pot body */}
          <rect x="48" y="88" width="104" height="108" rx="28" fill="#F5F0E8" />
          {/* Pot rim */}
          <rect x="44" y="82" width="112" height="22" rx="11" fill="#EDE8DC" />

          {/* Pot shadow/depth */}
          <ellipse cx="100" cy="196" rx="52" ry="8" fill="#DDD8CC" opacity="0.6" />

          {/* Stem */}
          <line x1="100" y1="88" x2="100" y2="38" stroke="#4A8B3F" strokeWidth="7" strokeLinecap="round" />

          {/* Left leaf */}
          <ellipse cx="78" cy="30" rx="22" ry="13" fill="#5CB85C" transform="rotate(-30 78 30)" />
          <line x1="78" y1="30" x2="95" y2="42" stroke="#4A8B3F" strokeWidth="2" strokeLinecap="round" />

          {/* Right leaf */}
          <ellipse cx="122" cy="26" rx="22" ry="13" fill="#4CAF50" transform="rotate(25 122 26)" />
          <line x1="122" y1="26" x2="105" y2="40" stroke="#4A8B3F" strokeWidth="2" strokeLinecap="round" />

          {/* Left eyebrow */}
          <path d="M 78 112 Q 85 107 92 112" stroke="#3D2B1F" strokeWidth="3" strokeLinecap="round" fill="none" />
          {/* Right eyebrow */}
          <path d="M 108 112 Q 115 107 122 112" stroke="#3D2B1F" strokeWidth="3" strokeLinecap="round" fill="none" />

          {/* Left eye white */}
          <ellipse cx="85" cy="124" rx="13" ry="14" fill="white" />
          {/* Right eye white */}
          <ellipse cx="115" cy="124" rx="13" ry="14" fill="white" />

          {/* Left pupil */}
          <ellipse cx="87" cy="126" rx="7" ry="8" fill="#2C1A10" />
          {/* Right pupil */}
          <ellipse cx="117" cy="126" rx="7" ry="8" fill="#2C1A10" />

          {/* Eye shine left */}
          <ellipse cx="90" cy="122" rx="2.5" ry="3" fill="white" opacity="0.9" />
          {/* Eye shine right */}
          <ellipse cx="120" cy="122" rx="2.5" ry="3" fill="white" opacity="0.9" />

          {/* Smile */}
          <path d="M 88 142 Q 100 152 112 142" stroke="#3D2B1F" strokeWidth="3" strokeLinecap="round" fill="none" />

          {/* Left cheek blush */}
          <ellipse cx="72" cy="140" rx="10" ry="6" fill="#F4A7B9" opacity="0.6" />
          {/* Right cheek blush */}
          <ellipse cx="128" cy="140" rx="10" ry="6" fill="#F4A7B9" opacity="0.6" />

          {/* Left arm */}
          <path d="M 60 155 Q 45 148 38 162" stroke="#EDE8DC" strokeWidth="12" strokeLinecap="round" fill="none" />
          {/* Right arm */}
          <path d="M 140 155 Q 155 148 162 162" stroke="#EDE8DC" strokeWidth="12" strokeLinecap="round" fill="none" />

          {/* Green card held by mascot */}
          <rect x="68" y="155" width="64" height="52" rx="12" fill="#4CAF50" />
          {/* Checkmark on card */}
          <path d="M 83 181 L 94 192 L 117 169" stroke="white" strokeWidth="5" strokeLinecap="round" strokeLinejoin="round" fill="none" />
        </svg>
      </Wrapper>
    </div>
  );
}
