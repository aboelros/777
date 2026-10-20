import { useTranslation } from '@/lib/translations';
import Badge from '@/components/ui/Badge';

export default function StorageDetails({ product }) {
  const { t } = useTranslation();
  const locations = Array.isArray(product.storage_locations) ? product.storage_locations : [];
  const attachments = Array.isArray(product.storage_attachments) ? product.storage_attachments : [];

  return (
    <div className="space-y-5">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-3 border-b border-border">
        <div>
          <h3 className="text-lg font-bold text-text-primary">{product.name}</h3>
          {product.sku && <p className="text-xs font-mono text-text-muted">SKU: {product.sku}</p>}
        </div>
        <Badge variant={product.in_stock ? 'success' : 'danger'} withDot>
          {product.in_stock ? t('products.card.in_stock') : t('products.card.out_of_stock')}
        </Badge>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="rounded-xl border border-border bg-surface-subtle p-3.5">
          <p className="text-[11px] text-text-muted uppercase tracking-wider font-semibold mb-1">
            {t('products.storage.current_qty')}
          </p>
          <p className="text-xl font-bold font-mono text-text-primary">{product.stock_quantity ?? 0}</p>
        </div>
        <div className="rounded-xl border border-border bg-surface-subtle p-3.5">
          <p className="text-[11px] text-text-muted uppercase tracking-wider font-semibold mb-1">
            {t('products.storage.reorder_point')}
          </p>
          <p className="text-xl font-bold font-mono text-text-primary">{product.reorder_point ?? 0}</p>
        </div>
        <div className="rounded-xl border border-border bg-surface-subtle p-3.5">
          <p className="text-[11px] text-text-muted uppercase tracking-wider font-semibold mb-1">
            {t('products.storage.safety_stock')}
          </p>
          <p className="text-xl font-bold font-mono text-text-primary">{product.safety_stock ?? 0}</p>
        </div>
      </div>

      {locations.length > 0 && (
        <div>
          <p className="text-xs uppercase tracking-wider font-semibold text-text-muted mb-2">
            {t('products.storage.locations')}
          </p>
          <div className="flex flex-wrap gap-2">
            {locations.map((loc, idx) => (
              <span key={idx} className="px-2.5 py-1 rounded-lg text-xs bg-surface border border-border text-text-secondary">
                {typeof loc === 'string' ? loc : loc?.name || JSON.stringify(loc)}
              </span>
            ))}
          </div>
        </div>
      )}

      {product.storage_notes && (
        <div className="rounded-xl border border-border bg-surface-subtle p-3.5">
          <p className="text-xs uppercase tracking-wider font-semibold text-text-muted mb-1.5">
            {t('products.storage.notes')}
          </p>
          <p className="text-sm text-text-secondary whitespace-pre-line leading-relaxed">{product.storage_notes}</p>
        </div>
      )}

      {attachments.length > 0 && (
        <div>
          <p className="text-xs uppercase tracking-wider font-semibold text-text-muted mb-2">
            {t('products.storage.attachments')}
          </p>
          <div className="flex flex-wrap gap-2">
            {attachments.map((attachment, idx) => (
              <a
                key={idx}
                href={attachment}
                target="_blank"
                rel="noopener noreferrer"
                className="px-3 py-1 rounded-lg text-xs bg-brand-primary/10 border border-brand-primary/20 text-brand-primary hover:bg-brand-primary/20 transition-colors"
              >
                Attachment {idx + 1}
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
