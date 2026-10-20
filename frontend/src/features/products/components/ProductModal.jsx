import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { X } from 'lucide-react';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import ProductImageUpload from '@/components/ProductImageUpload';
import { useTranslation } from '@/lib/translations';

export default function ProductModal({ show, product, onClose, onSave }) {
  const { t } = useTranslation();
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    sku: '',
    price: '',
    currency: 'USD',
    stock_quantity: 0,
    in_stock: true,
    category: '',
    tags: '',
    keywords: '',
    storage_locations: '',
    reorder_point: '',
    safety_stock: '',
    storage_notes: '',
    storage_attachments: '',
    images: [],
  });

  useEffect(() => {
    if (product) {
      setFormData({
        name: product.name || '',
        description: product.description || '',
        sku: product.sku || '',
        price: product.price || '',
        currency: product.currency || 'USD',
        stock_quantity: product.stock_quantity || 0,
        in_stock: product.in_stock ?? true,
        category: product.category || '',
        tags: (product.tags || []).join(', '),
        keywords: (product.keywords || []).join(', '),
        storage_locations: Array.isArray(product.storage_locations)
          ? product.storage_locations
            .map((loc) => (typeof loc === 'string' ? loc : loc?.name || ''))
            .filter(Boolean)
            .join(' | ')
          : '',
        reorder_point: product.reorder_point ?? '',
        safety_stock: product.safety_stock ?? '',
        storage_notes: product.storage_notes || '',
        storage_attachments: (product.storage_attachments || []).join(', '),
        images: product.images || [],
      });
    } else {
      setFormData({
        name: '',
        description: '',
        sku: '',
        price: '',
        currency: 'USD',
        stock_quantity: 0,
        in_stock: true,
        category: '',
        tags: '',
        keywords: '',
        storage_locations: '',
        reorder_point: '',
        safety_stock: '',
        storage_notes: '',
        storage_attachments: '',
        images: [],
      });
    }
  }, [product, show]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave({
      ...formData,
      price: formData.price ? parseFloat(formData.price) : null,
      stock_quantity: parseInt(formData.stock_quantity, 10) || 0,
      tags: formData.tags.split(',').map(t => t.trim()).filter(Boolean),
      keywords: formData.keywords.split(',').map(k => k.trim()).filter(Boolean),
      storage_locations: formData.storage_locations
        ? formData.storage_locations.split('|').map(loc => loc.trim()).filter(Boolean)
        : [],
      reorder_point: formData.reorder_point ? parseInt(formData.reorder_point, 10) : 0,
      safety_stock: formData.safety_stock ? parseInt(formData.safety_stock, 10) : 0,
      storage_notes: formData.storage_notes || null,
      storage_attachments: formData.storage_attachments
        ? formData.storage_attachments.split(',').map(att => att.trim()).filter(Boolean)
        : [],
      images: formData.images,
    });
  };

  if (!show) return null;

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-md flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        className="glass-card p-6 sm:p-8 max-w-2xl w-full rounded-2xl max-h-[90vh] overflow-y-auto border border-border"
      >
        <div className="flex items-center justify-between mb-6 pb-4 border-b border-border">
          <h2 className="text-xl font-bold text-text-primary">
            {product ? t('products.modal.edit_title') : t('products.modal.add_title')}
          </h2>
          <button
            onClick={onClose}
            className="p-2 rounded-xl text-text-muted hover:text-text-primary hover:bg-surface-subtle transition-colors"
            aria-label="Close modal"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="rounded-xl border border-border p-3 bg-surface-subtle">
            <ProductImageUpload
              productId={product?.id}
              images={formData.images}
              onImagesChange={(newImages) => setFormData(prev => ({ ...prev, images: newImages }))}
            />
          </div>

          <Input
            label={`${t('products.modal.fields.name') || 'Product Name'} *`}
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
            placeholder="e.g. Smart Watch Pro"
          />

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-text-secondary mb-1.5">
              {t('products.modal.fields.description') || 'Description'}
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              rows={3}
              className="input-fluid w-full resize-y text-sm"
              placeholder="Product technical details and sales copy..."
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label={t('products.modal.fields.sku') || 'SKU'}
              value={formData.sku}
              onChange={(e) => setFormData({ ...formData, sku: e.target.value })}
              placeholder="PROD-001"
            />
            <Input
              label={t('products.modal.fields.category') || 'Category'}
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              placeholder="Electronics"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <Input
              label={t('products.modal.fields.price') || 'Price'}
              type="number"
              step="0.01"
              value={formData.price}
              onChange={(e) => setFormData({ ...formData, price: e.target.value })}
              placeholder="99.99"
            />
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-text-secondary mb-1.5">
                {t('products.modal.fields.currency') || 'Currency'}
              </label>
              <select
                value={formData.currency}
                onChange={(e) => setFormData({ ...formData, currency: e.target.value })}
                className="input-fluid w-full text-sm py-2.5"
              >
                <option value="USD">USD ($)</option>
                <option value="EUR">EUR (€)</option>
                <option value="GBP">GBP (£)</option>
                <option value="EGP">EGP (E£)</option>
                <option value="SAR">SAR (﷼)</option>
                <option value="AED">AED (د.إ)</option>
              </select>
            </div>
            <Input
              label={t('products.modal.fields.stock') || 'Stock Qty'}
              type="number"
              value={formData.stock_quantity}
              onChange={(e) => setFormData({ ...formData, stock_quantity: e.target.value })}
              placeholder="100"
            />
          </div>

          <div className="flex items-center gap-3 p-3 rounded-xl bg-surface-subtle border border-border">
            <input
              type="checkbox"
              id="in_stock"
              checked={formData.in_stock}
              onChange={(e) => setFormData({ ...formData, in_stock: e.target.checked })}
              className="w-4 h-4 rounded text-brand-primary focus:ring-brand-primary"
            />
            <label htmlFor="in_stock" className="text-sm font-medium text-text-primary cursor-pointer select-none">
              {t('products.modal.fields.in_stock') || 'Available in stock for instant purchase'}
            </label>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label={t('products.modal.fields.tags') || 'Tags (comma-separated)'}
              value={formData.tags}
              onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
              placeholder="bestseller, wireless, audio"
            />
            <Input
              label={t('products.modal.fields.keywords') || 'AI Search Keywords'}
              value={formData.keywords}
              onChange={(e) => setFormData({ ...formData, keywords: e.target.value })}
              placeholder="earbuds, headphone, bluetooth"
            />
          </div>

          <div className="flex gap-3 pt-4 border-t border-border">
            <Button
              type="button"
              onClick={onClose}
              variant="secondary"
              className="flex-1"
            >
              {t('products.buttons.cancel') || 'Cancel'}
            </Button>
            <Button
              type="submit"
              variant="primary"
              className="flex-1"
            >
              {product ? (t('products.buttons.update') || 'Update Product') : (t('products.buttons.save') || 'Save Product')}
            </Button>
          </div>
        </form>
      </motion.div>
    </div>
  );
}
