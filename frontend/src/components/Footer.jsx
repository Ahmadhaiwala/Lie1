import { Zap, Mail, GitBranch } from "lucide-react";
import { motion } from "framer-motion";

const GithubIcon = () => (
  <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
    <path d="M12 2C6.477 2 2 6.477 2 12c0 4.418 2.865 8.166 6.839 9.489.5.092.682-.217.682-.482 0-.237-.008-.868-.013-1.703-2.782.604-3.369-1.342-3.369-1.342-.454-1.155-1.11-1.462-1.11-1.462-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.578 9.578 0 0112 6.836c.85.004 1.705.115 2.504.337 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.202 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C19.138 20.163 22 16.418 22 12c0-5.523-4.477-10-10-10z"/>
  </svg>
);
const TwitterIcon = () => (
  <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
  </svg>
);
const LinkedinIcon = () => (
  <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
  </svg>
);

export default function Footer() {
  const year = new Date().getFullYear();
  const socials = [
    { icon: GithubIcon,   href: "https://github.com/Ahmadhaiwala/Lie1", label: "GitHub"   },
    { icon: TwitterIcon,  href: "#",                                     label: "Twitter"  },
    { icon: LinkedinIcon, href: "#",                                     label: "LinkedIn" },
    { icon: Mail,         href: "mailto:hello@youragency.com",           label: "Email"    },
  ];

  return (
    <footer className="relative z-10 border-t border-white/8 bg-black/60 backdrop-blur-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-10">

          {/* Brand */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-orange-500 flex items-center justify-center">
                <Zap className="w-4 h-4 text-black fill-black" />
              </div>
              <span className="font-display font-bold text-xl text-white">
                Lead<span className="text-orange-400">Bot</span> AI
              </span>
            </div>
            <p className="text-zinc-500 text-sm leading-relaxed">
              AI-powered lead generation for Website Development,
              WhatsApp Bots, and SEO — on autopilot.
            </p>
          </div>

          {/* Quick links */}
          <div className="space-y-3">
            <p className="font-semibold text-white text-sm">Quick Links</p>
            {[
              { label: "Home",         href: "/" },
              { label: "Services",     href: "/#services" },
              { label: "How It Works", href: "/#how-it-works" },
              { label: "Dashboard",    href: "/dashboard" },
              { label: "Run Jobs",     href: "/run" },
              { label: "Contact",      href: "/#contact" },
            ].map(({ label, href }) => (
              <a key={label} href={href}
                className="block text-zinc-500 hover:text-orange-400 transition-colors text-sm">
                {label}
              </a>
            ))}
          </div>

          {/* Services */}
          <div className="space-y-3">
            <p className="font-semibold text-white text-sm">Services</p>
            {["Website Development", "WhatsApp Bot Automation", "SEO & Search Visibility"].map((s) => (
              <span key={s} className="block text-zinc-500 text-sm">{s}</span>
            ))}
            <div className="pt-2 flex items-center gap-2 text-zinc-600 text-xs">
              <GitBranch className="w-3.5 h-3.5" />
              <a href="https://github.com/Ahmadhaiwala/Lie1" target="_blank" rel="noopener noreferrer"
                className="hover:text-orange-400 transition-colors">
                github.com/Ahmadhaiwala/Lie1
              </a>
            </div>
          </div>
        </div>

        {/* Bottom */}
        <div className="mt-10 pt-6 border-t border-white/8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-zinc-600 text-sm">© {year} LeadBot AI. All rights reserved.</p>
          <div className="flex items-center gap-3">
            {socials.map(({ icon: Icon, href, label }) => (
              <motion.a
                key={label}
                href={href}
                target={href.startsWith("http") ? "_blank" : undefined}
                rel="noopener noreferrer"
                whileHover={{ scale: 1.15, y: -2 }}
                aria-label={label}
                className="w-8 h-8 rounded-lg bg-white/5 border border-white/8 flex items-center justify-center text-zinc-500 hover:text-orange-400 hover:border-orange-500/30 transition-all"
              >
                <Icon />
              </motion.a>
            ))}
          </div>
        </div>
      </div>
    </footer>
  );
}
