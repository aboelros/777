import { Package, AlertCircle } from 'lucide-react';
import GlassCard from '@/components/ui/GlassCard';
import { useTranslation } from '@/lib/translations';

export default function DashboardInventoryCard({ products = [], totalProducts = 0 }) {
  const { t } = useTranslation();
  const inStockCount = products.filter((p) => p.in_stock).length;
  const outOfStockCount = products.filter((p) => !p.in_stock).length;
  const healthRate = totalProducts > 0 ? Math.round((inStockCount / totalProducts) * 100) : 0;

  return (
    <GlassCard className="p-6 rounded-2xl border border-white/10 hover:border-sky-400/40 shadow-[0_8px_32px_rgba(0,0,0,0.45)]">
      <h3 className="text-lg font-bold text-white mb-4 pb-2 border-b border-white/10">
        {t('dashboard.product_inventory') || 'Inventory Health'}
      </h3>

      <div className="space-y-4">
        <div className="flex items-center justify-between p-3.5 rounded-xl bg-white/[0.04] border border-white/10 backdrop-blur-md shadow-[inset_0_1px_1px_rgba(255,255,255,0.1)]">
          <span className="text-sm font-medium text-slate-300">{t('dashboard.products') || 'Total Catalog Items'}</span>
          <span className="text-2xl font-bold font-numeric text-white">{totalProducts}</span>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/25 shadow-[0_0_12px_rgba(16,185,129,0.15)] backdrop-blur-md">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-emerald-300 font-semibold">{t('dashboard.in_stock') || 'In Stock'}</span>
              <Package className="w-4 h-4 text-emerald-400" />
            </div>
            <span className="text-2xl font-bold font-numeric text-emerald-400">{inStockCount}</span>
          </div>

          <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/25 shadow-[0_0_12px_rgba(244,63,94,0.15)] backdrop-blur-md">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-rose-300 font-semibold">{t('dashboard.out_of_stock') || 'Out of Stock'}</span>
              <AlertCircle className="w-4 h-4 text-rose-400" />
            </div>
            <span className="text-2xl font-bold font-numeric text-rose-400">{outOfStockCount}</span>
          </div>
        </div>

        <div className="pt-2">
          <div className="flex justify-between text-xs text-slate-400 mb-1.5 font-numeric">
            <span>Availability Index</span>
            <span className="font-bold text-white">{healthRate}%</span>
          </div>
          <div className="h-2 bg-slate-900/80 rounded-full overflow-hidden border border-white/10">
            <div
              className="h-full bg-gradient-to-r from-emerald-500 to-teal-400 shadow-[0_0_10px_rgba(16,185,129,0.6)] transition-all duration-500 rounded-full"
              style={{ width: `${healthRate}%` }}
            />
          </div>
        </div>
      </div>
    </GlassCard>
  );
}
