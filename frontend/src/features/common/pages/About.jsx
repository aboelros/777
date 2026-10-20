import { motion } from 'framer-motion';
import { Globe, Heart, Award, Zap, Shield, Target, Sparkles, Cpu, Layers } from 'lucide-react';
import GlassCard from '@/components/ui/GlassCard';
import Logo from '@/components/brand/Logo';

export default function About() {
  const pillars = [
    {
      icon: Cpu,
      title: 'Autonomous Intelligence',
      description: 'System-level reasoning engines transforming inbound sales inquiries into verified business orders.',
    },
    {
      icon: Shield,
      title: 'Enterprise Trust & Security',
      description: 'End-to-end data privacy, role-based authorization, and resilient operational infrastructure.',
    },
    {
      icon: Target,
      title: 'Precision Conversational Sales',
      description: 'Zero hallucinations. Grounded RAG knowledge bases paired with real-time inventory telemetry.',
    },
    {
      icon: Layers,
      title: 'Omnichannel Unification',
      description: 'Single command console harmonizing WhatsApp, Telegram, Instagram, and storefront operations.',
    },
  ];

  const milestones = [
    { value: 'Enterprise Grade', label: 'Architecture' },
    { value: '< 1.2s', label: 'Reasoning Latency' },
    { value: '99.9%', label: 'Uptime Reliability' },
    { value: 'Omnichannel', label: 'Ecosystem Coverage' },
  ];

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-8">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center space-y-4 py-8"
      >
        <div className="flex justify-center mb-4">
          <Logo variant="full" size="lg" />
        </div>
        <p className="text-lg text-text-secondary max-w-2xl mx-auto">
          The next-generation AI sales automation and customer communication platform engineered for modern commerce.
        </p>
      </motion.div>

      {/* Metrics Banner */}
      <GlassCard className="p-6 rounded-2xl border border-border">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          {milestones.map((milestone, idx) => (
            <div key={idx} className="space-y-1">
              <p className="text-2xl font-bold font-mono text-brand-primary">{milestone.value}</p>
              <p className="text-xs font-semibold uppercase tracking-wider text-text-muted">{milestone.label}</p>
            </div>
          ))}
        </div>
      </GlassCard>

      {/* Mission & Story */}
      <GlassCard className="p-8 rounded-2xl border border-border space-y-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-brand-primary/10 border border-brand-primary/20 text-brand-primary">
            <Globe className="w-5 h-5" />
          </div>
          <h2 className="text-2xl font-bold text-text-primary">Platform Vision & Engineering</h2>
        </div>
        <div className="space-y-3 text-text-secondary text-sm leading-relaxed">
          <p>
            Automio is engineered from the ground up to solve the operational bottleneck of modern commerce:
            delivering high-touch, deeply knowledgeable, instantaneous customer sales interactions 24/7 across every messaging channel.
          </p>
          <p>
            By coupling high-speed neural models with structured inventory synchronization, payment gateways, and autonomous follow-ups,
            Automio empowers businesses to convert casual social inquiries into fulfilled orders with zero manual friction.
          </p>
        </div>
      </GlassCard>

      {/* Platform Pillars */}
      <div className="space-y-4">
        <h2 className="text-xl font-bold text-text-primary flex items-center gap-2">
          <Award className="w-5 h-5 text-brand-primary" />
          Architectural Pillars
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {pillars.map((pillar, idx) => (
            <GlassCard key={idx} className="p-6 rounded-2xl border border-border hover:border-brand-primary/30 transition-all">
              <div className="p-2.5 w-fit rounded-xl bg-brand-primary/10 border border-brand-primary/20 text-brand-primary mb-3">
                <pillar.icon className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-text-primary mb-1.5">{pillar.title}</h3>
              <p className="text-xs text-text-secondary leading-relaxed">{pillar.description}</p>
            </GlassCard>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="text-center text-xs text-text-muted pt-6 border-t border-border/50">
        <p>Automio Platform Architecture • Engineered for Scalability & Resilience</p>
      </div>
    </div>
  );
}
