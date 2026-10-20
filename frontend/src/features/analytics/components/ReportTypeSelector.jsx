import React from 'react';
import PropTypes from 'prop-types';
import { motion } from 'framer-motion';
import { DollarSign, Package, Users, Activity, Target } from 'lucide-react';
import GlassCard from '@/components/ui/GlassCard';

const REPORT_TYPES = [
  { id: 'sales', label: 'Sales & Revenue', desc: 'Conversion metrics and deal flow', icon: DollarSign, color: 'from-emerald-500 to-teal-600' },
  { id: 'orders', label: 'Order Execution', desc: 'Fulfillment times and volumes', icon: Package, color: 'from-blue-500 to-sky-600' },
  { id: 'customers', label: 'Customer Retention', desc: 'Repeat buyers and sentiment', icon: Users, color: 'from-sky-500 to-indigo-600' },
  { id: 'performance', label: 'Bot Performance', desc: 'Response latency and accuracy', icon: Activity, color: 'from-amber-500 to-orange-600' },
  { id: 'roi', label: 'ROI Analytics', desc: 'Saved hours and operational costs', icon: Target, color: 'from-indigo-500 to-purple-600' }
];

/**
 * ReportTypeSelector - Card selection grid for switching between analytics reports
 */
export default function ReportTypeSelector({ selectedType, onSelect }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
      {REPORT_TYPES.map((type, index) => {
        const isSelected = selectedType === type.id;
        const Icon = type.icon;

        return (
          <motion.div
            key={type.id}
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            onClick={() => onSelect(type.id)}
            className="cursor-pointer"
          >
            <GlassCard
              className={`p-4 h-full flex flex-col justify-between transition-all ${
                isSelected
                  ? 'border-2 border-sky-500 shadow-neon bg-sky-500/10'
                  : 'hover:border-[var(--color-border-hover)]'
              }`}
            >
              <div>
                <div
                  className={`w-10 h-10 rounded-xl bg-gradient-to-br ${type.color} flex items-center justify-center text-white mb-3 shadow-sm`}
                >
                  <Icon className="w-5 h-5" />
                </div>
                <h3 className="font-semibold text-sm text-[var(--color-text-primary)] mb-1">
                  {type.label}
                </h3>
                <p className="text-xs text-[var(--color-text-muted)] leading-relaxed">
                  {type.desc}
                </p>
              </div>
            </GlassCard>
          </motion.div>
        );
      })}
    </div>
  );
}

ReportTypeSelector.propTypes = {
  selectedType: PropTypes.string.isRequired,
  onSelect: PropTypes.func.isRequired
};
