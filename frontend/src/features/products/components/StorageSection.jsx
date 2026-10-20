import { Package } from 'lucide-react';
import { useTranslation } from '@/lib/translations';
import StorageDetails from './StorageDetails';

export default function StorageSection({ products, selectedProduct, onSelect, allProducts }) {
  const { t } = useTranslation();
  const displayProducts = products.length > 0 ? products : allProducts;

  if (!displayProducts.length) {
    return (
      <section className="mt-12">
        <h2 className="text-xl font-bold text-text-primary mb-4 flex items-center gap-2">
          <Package className="w-5 h-5 text-brand-primary" />
          {t('products.storage.title') || 'Warehouse & Inventory Intelligence'}
        </h2>
        <div className="glass-card rounded-2xl p-8 text-center border border-border">
          <p className="text-text-muted text-sm">{t('products.storage.empty_desc') || 'No inventory storage configured yet.'}</p>
        </div>
      </section>
    );
  }

  return (
    <section className="mt-12">
      <h2 className="text-xl font-bold text-text-primary mb-4 flex items-center gap-2">
        <Package className="w-5 h-5 text-brand-primary" />
        {t('products.storage.title') || 'Warehouse & Inventory Intelligence'}
      </h2>
      <div className="glass-card rounded-2xl p-6 grid gap-6 lg:grid-cols-[260px,1fr] border border-border">
        <div className="space-y-2 max-h-[420px] overflow-y-auto pr-1">
          <p className="text-xs font-semibold uppercase tracking-wider text-text-muted mb-2">
            {t('products.storage.select_product') || 'Select Item'}
          </p>
          {displayProducts.map((product) => {
            const isActive = selectedProduct?.id === product.id;
            return (
              <button
                key={product.id}
                type="button"
                onClick={() => onSelect(product.id)}
                className={`w-full text-left p-3 rounded-xl transition-all border ${
                  isActive
                    ? 'border-brand-primary bg-brand-primary/10 text-text-primary'
                    : 'border-border bg-surface-subtle text-text-secondary hover:bg-surface-hover hover:text-text-primary'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-semibold text-sm truncate">{product.name}</span>
                  <span className="text-xs font-mono text-text-muted">
                    {product.stock_quantity ?? 0}
                  </span>
                </div>
                <div className="text-[11px] text-text-muted truncate">
                  {t('products.storage.reorder_point')}: {product.reorder_point ?? 0} • {t('products.storage.safety_stock')}: {product.safety_stock ?? 0}
                </div>
              </button>
            );
          })}
        </div>

        <div className="rounded-xl border border-border bg-surface-subtle/50 p-6">
          {selectedProduct ? (
            <StorageDetails product={selectedProduct} />
          ) : (
            <div className="text-sm text-text-muted text-center py-16">
              <p>📍 {t('products.storage.select_prompt') || 'Select a product to view warehouse specifications'}</p>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
