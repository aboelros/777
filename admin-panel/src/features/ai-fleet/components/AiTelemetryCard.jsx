/**
 * AI telemetry summary cards visualizing model latency, tokens, and active jobs.
 */

import React from 'react';
import MetricCard from '@/features/dashboard/components/MetricCard';
import { Cpu, Zap, Activity, CheckCircle2 } from 'lucide-react';

export default function AiTelemetryCard({ telemetry }) {
  const cards = [
    {
      title: 'Active Primary Engine',
      value: telemetry?.primary_model || 'gemini-2.5-flash',
      subtitle: `Fallback: ${telemetry?.fallback_model || 'gemini-2.0-flash'}`,
      icon: Cpu,
      color: '#6366F1',
      bg: 'rgba(99, 102, 241, 0.15)',
    },
    {
      title: 'Average Inference Speed',
      value: `${telemetry?.avg_latency_ms || 320} ms`,
      subtitle: 'Streaming response time',
      icon: Zap,
      color: '#F59E0B',
      bg: 'rgba(245, 158, 11, 0.15)',
    },
    {
      title: 'Estimated Token Volume',
      value: (telemetry?.estimated_token_usage_30d || 0).toLocaleString(),
      subtitle: 'Tokens processed across stores (30d)',
      icon: Activity,
      color: '#0EA5E9',
      bg: 'rgba(14, 165, 233, 0.15)',
    },
    {
      title: 'Completion Success Rate',
      value: `${telemetry?.success_rate || 99.4}%`,
      subtitle: 'Zero-downtime candidate failover',
      icon: CheckCircle2,
      color: '#10B981',
      bg: 'rgba(16, 185, 129, 0.15)',
    },
  ];

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.25rem' }}>
      {cards.map((c, idx) => (
        <MetricCard key={idx} {...c} />
      ))}
    </div>
  );
}
