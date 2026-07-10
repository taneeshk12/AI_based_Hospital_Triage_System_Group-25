import React from 'react';
import { motion } from 'framer-motion';
import { Activity, ShieldCheck, GitBranch, ArrowRight, Stethoscope, Brain, Users, TrendingUp, Zap } from 'lucide-react';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.12 } },
};
const itemVariants = {
  hidden: { y: 24, opacity: 0 },
  visible: { y: 0, opacity: 1, transition: { type: 'spring', stiffness: 90, damping: 16 } },
};

const features = [
  {
    icon: Activity,
    color: '#0ea5e9',
    title: 'Real-time Stratification',
    desc: 'Instant analysis of 20+ clinical parameters — vitals, labs, and symptoms — for precise risk stratification.',
  },
  {
    icon: Brain,
    color: '#8b5cf6',
    title: 'Multi-Agent AI',
    desc: 'Three specialised AI models (cardiac, respiratory, sepsis) run in parallel and vote on a unified risk verdict.',
  },
  {
    icon: GitBranch,
    color: '#14b8a6',
    title: 'What-If Simulator',
    desc: 'Dynamically adjust patient vitals to simulate clinical interventions and model expected outcomes.',
  },
  {
    icon: ShieldCheck,
    color: '#10b981',
    title: 'Safety & Registry',
    desc: 'Built-in guardrails, explainable SHAP drivers, and a comprehensive registry to track patient history securely.',
  },
];

export default function LandingPage({ setActivePage }) {
  return (
    <div className="landing-page-root">
      {/* Decorative background blobs */}
      <div className="landing-orb landing-orb-1" />
      <div className="landing-orb landing-orb-2" />
      <div className="landing-orb landing-orb-3" />

      <motion.div
        className="landing-inner"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* ── HERO ─────────────────────────────────────────────────────── */}
        <div className="landing-hero-grid">
          {/* Left: headline + CTA */}
          <div className="hero-left">
            <motion.div variants={itemVariants} className="hero-badge">
              <span className="hero-badge-dot" />
              <Stethoscope size={14} />
              Clinical AI System · v2.0
            </motion.div>

            <motion.h1 variants={itemVariants} className="hero-headline">
              Next-Generation<br />
              <span className="hero-headline-gradient">Patient Triage</span>
            </motion.h1>

            <motion.p variants={itemVariants} className="hero-sub">
              Empower clinical decisions with multimodal AI. Analyse real-time vitals,
              laboratory results, and clinical notes to accurately stratify patient risk
              in under a second.
            </motion.p>

            <motion.div variants={itemVariants} className="hero-cta-row">
              <button
                className="hero-cta-btn"
                onClick={() => setActivePage('intake')}
              >
                <Zap size={18} />
                Start Triage Assessment
                <ArrowRight size={18} />
              </button>
              <button
                className="hero-cta-btn-outline"
                onClick={() => setActivePage('registry')}
              >
                <Users size={16} />
                Patient Registry
              </button>
            </motion.div>
          </div>

          {/* Right: feature cards */}
          <div className="hero-right">
            {features.map((f, i) => (
              <motion.div
                key={f.title}
                variants={itemVariants}
                className="landing-feature-card"
                whileHover={{ y: -4, transition: { duration: 0.2 } }}
                style={{ '--fc-color': f.color }}
              >
                <div className="lfc-icon-wrap" style={{ background: `${f.color}18` }}>
                  <f.icon size={20} color={f.color} />
                </div>
                <div>
                  <h3 className="lfc-title">{f.title}</h3>
                  <p className="lfc-desc">{f.desc}</p>
                </div>
                <div className="lfc-accent-bar" style={{ background: f.color }} />
              </motion.div>
            ))}
          </div>
        </div>
      </motion.div>
    </div>
  );
}
