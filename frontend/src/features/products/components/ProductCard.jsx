import { motion } from 'framer-motion';
import { DollarSign, Edit2, Trash2 } from 'lucide-react';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import { useTranslation } from '@/lib/translations';

export default function ProductCard({ product, onEdit, onDelete, onViewStorage, isSelected }) {
  const { t } = useTranslation();
  const hasStorageInfo = Boolean(
    (product.storage_locations && product.storage_locations.length) ||
    product.reorder_point ||
    product.safety_stock ||
    product.storage_notes ||
    (product.storage_attachments && product.storage_attachments.length)
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card p-6 rounded-2xl border border-border hover:border-brand-primary/30 transition-all flex flex-col justify-between"
    >
      <div>
        <div className="flex items-start justify-between mb-3 gap-2">
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-semibold text-text-primary truncate">{product.name}</h3>
            {product.sku && (
              <p className="text-xs font-mono text-text-muted mt-0.5">SKU: {product.sku}</p>
            )}
          </div>
          <Badge variant={product.in_stock ? 'success' : 'danger'} withDot>
            {product.in_stock ? t('products.card.in_stock') : t('products.card.out_of_stock')}
          </Badge>
        </div>

        <p className="text-text-secondary text-sm mb-4 line-clamp-2 min-h-[2.5rem]">
          {product.description || t('products.empty.no_description') || 'No description provided'}
        </p>

        <div className="flex items-center justify-between mb-4 py-2 border-y border-border/50">
          <div className="flex items-center gap-1.5">
            <DollarSign className="w-4 h-4 text-emerald-400" />
            <span className="text-xl font-bold font-mono text-text-primary">
              {product.price ? `${product.price} ${product.currency || 'USD'}` : 'N/A'}
            </span>
          </div>
          {product.stock_quantity !== null && (
            <span className="text-xs font-medium text-text-secondary">
              {t('products.card.qty')}: <strong className="text-text-primary">{product.stock_quantity}</strong>
            </span>
          )}
        </div>

        {product.tags && product.tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mb-4">
            {product.tags.slice(0, 3).map((tag, i) => (
              <span
                key={i}
                className="px-2 py-0.5 bg-brand-primary/10 text-brand-primary text-xs rounded-md font-medium"
              >
                {tag}
              </span>
            ))}
            {product.tags.length > 3 && (
              <span className="px-1.5 py-0.5 bg-surface-subtle text-text-muted text-xs rounded-md">
                +{product.tags.length - 3}
              </span>
            )}
          </div>
        )}

        {hasStorageInfo && (
          <button
            type="button"
            onClick={onViewStorage}
            className={`mb-4 w-full px-3 py-1.5 rounded-lg border text-xs font-medium text-left transition-colors ${
              isSelected
                ? 'bg-brand-primary/15 border-brand-primary text-brand-primary'
                : 'bg-surface-subtle border-border text-text-secondary hover:text-text-primary'
            }`}
          >
            {isSelected ? t('products.card.viewing_storage') : t('products.card.view_storage')}
          </button>
        )}
      </div>

      <div className="flex gap-2 pt-2">
        <Button
          onClick={onEdit}
          variant="secondary"
          size="sm"
          className="flex-1"
          leftIcon={Edit2}
        >
          {t('products.card.edit')}
        </Button>
        <Button
          onClick={onDelete}
          variant="outline"
          size="sm"
          className="text-red-400 hover:bg-red-500/10 hover:border-red-500/30 px-3"
          aria-label="Delete product"
        >
          <Trash2 className="w-4 h-4" />
        </Button>
      </div>
    </motion.div>
  );
}
