import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Package, Plus, Upload, Edit2, Trash2, Search,
  Filter, X, DollarSign, Check, AlertCircle
} from 'lucide-react';
import { toast } from 'sonner';
import api from '../../../services/api';
import { useProjectStore } from '../../../store/projectStore';
import ProductImageUpload from '../../../components/ProductImageUpload';
import useThemeStore from '../../../store/themeStore';
import { useTranslation } from '../../../lib/translations';
import Button from '../../../components/ui/Button';
import Input from '../../../components/ui/Input';

export default function Products() {
  const queryClient = useQueryClient();
  const { currentProject } = useProjectStore();
  const { t } = useTranslation();
  const [searchTerm, setSearchTerm] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedStorageProductId, setSelectedStorageProductId] = useState(null);

  // Fetch products
  const { data: productsResponse = {}, isLoading } = useQuery({
    queryKey: ['products', currentProject?.id],
    queryFn: async () => {
      return await api.products.list(currentProject.id);
    },
    enabled: !!currentProject,
  });

  // Extract products array from response
  const products = productsResponse.products || [];
  const productsWithStorage = products.filter((product) =>
    Boolean(
      (product.storage_locations && product.storage_locations.length) ||
      product.reorder_point ||
      product.safety_stock ||
      product.storage_notes ||
      (product.storage_attachments && product.storage_attachments.length)
    )
  );

  useEffect(() => {
    if (productsWithStorage.length === 0) {
      if (selectedStorageProductId !== null) {
        setSelectedStorageProductId(null);
      }
      return;
    }

    const hasSelection = productsWithStorage.some((product) => product.id === selectedStorageProductId);
    if (!hasSelection) {
      setSelectedStorageProductId(productsWithStorage[0].id);
    }
  }, [productsWithStorage, selectedStorageProductId]);

  const selectedStorageProduct = selectedStorageProductId
    ? productsWithStorage.find((product) => product.id === selectedStorageProductId) || null
    : null;

  // Create product mutation
  const createMutation = useMutation({
    mutationFn: (productData) => api.products.create(currentProject.id, productData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products', currentProject?.id] });
      toast.success('Product created successfully!');
      setShowAddModal(false);
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to create product');
    },
  });

  // Update product mutation
  const updateMutation = useMutation({
    mutationFn: ({ productId, data }) =>
      api.products.update(currentProject.id, productId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products', currentProject?.id] });
      toast.success('Product updated successfully!');
      setEditingProduct(null);
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to update product');
    },
  });

  // Delete product mutation
  const deleteMutation = useMutation({
    mutationFn: (productId) =>
      api.products.delete(currentProject.id, productId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products', currentProject?.id] });
      toast.success('Product deleted successfully!');
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to delete product');
    },
  });

  // Bulk upload mutation
  const uploadMutation = useMutation({
    mutationFn: (file) => api.products.bulkUpload(currentProject.id, file),
    onSuccess: (response) => {
      queryClient.invalidateQueries({ queryKey: ['products', currentProject?.id] });
      toast.success(response.data.message);
      setShowUploadModal(false);
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to upload products');
    },
  });

  const filteredProducts = products.filter(product =>
    product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    product.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    product.sku?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (!currentProject) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-yellow-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold mb-2">No Project Selected</h2>
          <p className="text-gray-400">Please select a project to manage products</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-4xl font-bold mb-2">{t('products.title')}</h1>
          <p className="text-gray-400">{t('products.subtitle')}</p>
        </div>
        <div className="flex gap-3">
          <Button
            onClick={() => setShowUploadModal(true)}
            variant="secondary"
            leftIcon={Upload}
          >
            {t('products.buttons.bulk_upload')}
          </Button>
          <Button
            onClick={() => setShowAddModal(true)}
            variant="primary"
            leftIcon={Plus}
          >
            {t('products.buttons.add_product')}
          </Button>
        </div>
      </div>

      {/* Search */}
      <div className="glass-panel p-4 rounded-xl mb-6">
        <Input
          icon={Search}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder={t('products.search_placeholder')}
          containerClassName="w-full"
        />
      </div>

      {/* Products Grid */}
      {isLoading ? (
        <div className="text-center py-20">
          <div className="loading-spinner mx-auto mb-4"></div>
          <p className="text-gray-400">Loading products...</p>
        </div>
      ) : filteredProducts.length === 0 ? (
        <div className="text-center py-20">
          <Package className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-xl font-semibold mb-2">{t('products.empty.title')}</h3>
          <p className="text-gray-400 mb-6">
            {searchTerm ? t('products.empty.desc_search') : t('products.empty.desc_empty')}
          </p>
          {!searchTerm && (
            <button
              onClick={() => setShowAddModal(true)}
              className="btn-neon"
            >
              {t('products.buttons.add_first')}
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProducts.map((product) => (
            <ProductCard
              key={product.id}
              product={product}
              onEdit={() => setEditingProduct(product)}
              onDelete={() => {
                if (confirm('Are you sure you want to delete this product?')) {
                  deleteMutation.mutate(product.id);
                }
              }}
              onViewStorage={() => setSelectedStorageProductId(product.id)}
              isSelected={selectedStorageProductId === product.id}
            />
          ))}
        </div>
      )}

      {/* Always show Storage Section - even if no products have storage yet */}
      <StorageSection
        products={productsWithStorage.length > 0 ? productsWithStorage : products}
        selectedProduct={selectedStorageProduct || (products.length > 0 ? products[0] : null)}
        onSelect={setSelectedStorageProductId}
        allProducts={products}
      />

      {/* Add/Edit Product Modal */}
      <ProductModal
        show={showAddModal || editingProduct}
        product={editingProduct}
        onClose={() => {
          setShowAddModal(false);
          setEditingProduct(null);
        }}
        onSave={(data) => {
          if (editingProduct) {
            updateMutation.mutate({ productId: editingProduct.id, data });
          } else {
            createMutation.mutate(data);
          }
        }}
      />

      {/* Upload CSV Modal */}
      <UploadModal
        show={showUploadModal}
        onClose={() => setShowUploadModal(false)}
        onUpload={(file) => uploadMutation.mutate(file)}
      />
    </div>
  );
}

function ProductCard({ product, onEdit, onDelete, onViewStorage, isSelected }) {
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
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card p-6 rounded-xl hover:bg-white/5 transition-all"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-xl font-semibold mb-1">{product.name}</h3>
          {product.sku && (
            <p className="text-sm text-gray-400">SKU: {product.sku}</p>
          )}
        </div>
        <div className={`px-3 py-1 rounded-full text-xs font-medium ${product.in_stock ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
          }`}>
          {product.in_stock ? t('products.card.in_stock') : t('products.card.out_of_stock')}
        </div>
      </div>

      <p className="text-gray-400 text-sm mb-4 line-clamp-3">
        {product.description || 'No description'}
      </p>

      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <DollarSign className="w-5 h-5 text-green-400" />
          <span className="text-2xl font-bold">
            {product.price ? `${product.price} ${product.currency}` : 'N/A'}
          </span>
        </div>
        {product.stock_quantity !== null && (
          <span className="text-sm text-gray-400">
            {t('products.card.qty')}: {product.stock_quantity}
          </span>
        )}
      </div>

      {product.tags && product.tags.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4">
          {product.tags.slice(0, 3).map((tag, i) => (
            <span
              key={i}
              className="px-2 py-1 bg-sky-500/20 text-sky-300 rounded-lg text-xs"
            >
              {tag}
            </span>
          ))}
          {product.tags.length > 3 && (
            <span className="px-2 py-1 bg-gray-500/20 text-gray-400 rounded-lg text-xs">
              +{product.tags.length - 3} {t('products.card.more')}
            </span>
          )}
        </div>
      )}

      {hasStorageInfo && (
        <button
          type="button"
          onClick={onViewStorage}
          className={`mb-4 w-full glass-card px-4 py-2 rounded-lg transition-colors text-sm font-medium text-left ${isSelected ? 'bg-white/10 text-white' : 'hover:bg-white/10'
            }`}
        >
          {isSelected ? t('products.card.viewing_storage') : t('products.card.view_storage')}
        </button>
      )}

      <div className="flex gap-2">
        <Button
          onClick={onEdit}
          variant="secondary"
          className="flex-1"
          leftIcon={Edit2}
        >
          {t('products.card.edit')}
        </Button>
        <Button
          onClick={onDelete}
          variant="secondary"
          className="hover:bg-red-500/20 hover:border-red-500/30"
        >
          <Trash2 className="w-4 h-4 text-red-400" />
        </Button>
      </div>
    </motion.div>
  );
}

function StorageSection({ products, selectedProduct, onSelect, allProducts }) {
  const { language } = useThemeStore();
  const { t } = useTranslation(language);
  // Always show storage section
  const displayProducts = products.length > 0 ? products : allProducts;

  if (!displayProducts.length) {
    return (
      <section className="mt-12">
        <h2 className="text-2xl font-semibold mb-4">📦 {t('products.storage.title')}</h2>
        <div className="glass-card rounded-xl p-8 text-center">
          <p className="text-gray-400">{t('products.storage.empty_desc')}</p>
        </div>
      </section>
    );
  }

  return (
    <section className="mt-12">
      <h2 className="text-2xl font-semibold mb-4">📦 {t('products.storage.title')}</h2>
      <div className="glass-card rounded-xl p-6 grid gap-6 lg:grid-cols-[240px,1fr]">
        <div className="space-y-2">
          <p className="text-sm text-gray-400 mb-2">{t('products.storage.select_product')}</p>
          {displayProducts.map((product) => {
            const isActive = selectedProduct?.id === product.id;
            return (
              <button
                key={product.id}
                type="button"
                onClick={() => onSelect(product.id)}
                className={`w-full text-left px-4 py-3 rounded-lg transition-colors border ${isActive
                  ? 'border-sky-500/70 bg-sky-500/10 text-white'
                  : 'border-white/10 bg-white/5 text-gray-300 hover:bg-white/10'
                  }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium text-sm">{product.name}</span>
                  <span className="text-xs text-gray-400">{t('products.card.qty')}: {product.stock_quantity ?? 0}</span>
                </div>
                <div className="mt-1 text-xs text-gray-500">
                  {t('products.storage.reorder_point')} @ {product.reorder_point ?? 0} • {t('products.storage.safety_stock')} {product.safety_stock ?? 0}
                </div>
              </button>
            );
          })}
        </div>

        <div className="rounded-lg border border-white/10 bg-white/5 p-6">
          {selectedProduct ? (
            <StorageDetails product={selectedProduct} />
          ) : (
            <div className="text-sm text-gray-400 text-center py-8">
              <p className="mb-2">📍 {t('products.storage.select_prompt')}</p>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

function StorageDetails({ product }) {
  const { language } = useThemeStore();
  const { t } = useTranslation(language);
  const locations = Array.isArray(product.storage_locations) ? product.storage_locations : [];
  const attachments = Array.isArray(product.storage_attachments) ? product.storage_attachments : [];

  return (
    <div className="space-y-4">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h3 className="text-xl font-semibold text-white">{product.name}</h3>
          {product.sku && <p className="text-sm text-gray-400">SKU: {product.sku}</p>}
        </div>
        <div className={`px-3 py-1 rounded-full text-xs font-medium ${product.in_stock ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
          }`}>
          {product.in_stock ? 'In Stock' : 'Out of Stock'}
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="rounded-lg border border-white/10 bg-white/5 p-4">
          <p className="text-xs text-gray-400 uppercase tracking-wide mb-1">{t('products.storage.current_qty')}</p>
          <p className="text-lg font-semibold text-white">{product.stock_quantity ?? 0}</p>
        </div>
        <div className="rounded-lg border border-white/10 bg-white/5 p-4">
          <p className="text-xs text-gray-400 uppercase tracking-wide mb-1">{t('products.storage.reorder_point')}</p>
          <p className="text-lg font-semibold text-white">{product.reorder_point ?? 0}</p>
        </div>
        <div className="rounded-lg border border-white/10 bg-white/5 p-4">
          <p className="text-xs text-gray-400 uppercase tracking-wide mb-1">{t('products.storage.safety_stock')}</p>
          <p className="text-lg font-semibold text-white">{product.safety_stock ?? 0}</p>
        </div>
      </div>

      {locations.length > 0 && (
        <div>
          <p className="text-xs uppercase tracking-wide text-gray-400 mb-2">{t('products.storage.locations')}</p>
          <div className="flex flex-wrap gap-2">
            {locations.map((loc, idx) => (
              <span key={idx} className="px-3 py-1 rounded-full text-xs bg-white/10 text-gray-200">
                {typeof loc === 'string' ? loc : loc?.name || JSON.stringify(loc)}
              </span>
            ))}
          </div>
        </div>
      )}

      {product.storage_notes && (
        <div className="rounded-lg border border-white/10 bg-white/5 p-4">
          <p className="text-xs uppercase tracking-wide text-gray-400 mb-2">{t('products.storage.notes')}</p>
          <p className="text-sm text-gray-100 whitespace-pre-line">{product.storage_notes}</p>
        </div>
      )}

      {attachments.length > 0 && (
        <div>
          <p className="text-xs uppercase tracking-wide text-gray-400 mb-2">{t('products.storage.attachments')}</p>
          <div className="flex flex-wrap gap-2">
            {attachments.map((attachment, idx) => (
              <a
                key={idx}
                href={attachment}
                target="_blank"
                rel="noopener noreferrer"
                className="px-3 py-1 rounded-full text-xs bg-sky-500/20 text-sky-200 hover:bg-sky-500/30 transition"
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

function ProductModal({ show, product, onClose, onSave }) {
  const { language } = useThemeStore();
  const { t } = useTranslation(language);
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

  useState(() => {
    if (product) {
      setFormData({
        name: product.name || '',
        description: product.description || '',
        sku: product.sku || '',
        price: product.price || '',
        currency: product.currency || 'USD',
        stock_quantity: product.stock_quantity || 0,
        in_stock: product.in_stock,
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
      // Reset form for new product
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
  }, [product]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave({
      ...formData,
      price: formData.price ? parseFloat(formData.price) : null,
      stock_quantity: parseInt(formData.stock_quantity) || 0,
      tags: formData.tags.split(',').map(t => t.trim()).filter(Boolean),
      keywords: formData.keywords.split(',').map(k => k.trim()).filter(Boolean),
      storage_locations: formData.storage_locations
        ? formData.storage_locations.split('|').map(loc => loc.trim()).filter(Boolean)
        : [],
      reorder_point: formData.reorder_point ? parseInt(formData.reorder_point) : 0,
      safety_stock: formData.safety_stock ? parseInt(formData.safety_stock) : 0,
      storage_notes: formData.storage_notes || null,
      storage_attachments: formData.storage_attachments
        ? formData.storage_attachments.split(',').map(att => att.trim()).filter(Boolean)
        : [],
      // Images are handled separately via the upload component, but we keep them in sync
      images: formData.images,
    });
  };

  if (!show) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="glass-card p-8 max-w-2xl w-full rounded-2xl max-h-[90vh] overflow-y-auto"
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold">
            {product ? t('products.modal.edit_title') : t('products.modal.add_title')}
          </h2>
          <button onClick={onClose} className="glass-card p-2 rounded-lg hover:bg-white/10">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Image Upload Section */}
          <div className="glass-panel p-4 rounded-xl border border-white/5">
            <ProductImageUpload
              productId={product?.id}
              images={formData.images}
              onImagesChange={(newImages) => setFormData(prev => ({ ...prev, images: newImages }))}
            />
          </div>

          <div className="space-y-4">
            <Input
              label={t('products.modal.fields.name') + " *"}
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
              placeholder="Premium Widget"
            />

            <div>
              <label className="block text-sm font-medium mb-2 text-gray-300">{t('products.modal.fields.description')}</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={3}
                className="input-fluid w-full resize-y"
                placeholder="Detailed product description..."
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <Input
                label={t('products.modal.fields.sku')}
                value={formData.sku}
                onChange={(e) => setFormData({ ...formData, sku: e.target.value })}
                placeholder="PROD-001"
              />
              <Input
                label={t('products.modal.fields.category')}
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                placeholder="Electronics"
              />
            </div>

            <div className="grid grid-cols-3 gap-4">
              <Input
                label={t('products.modal.fields.price')}
                type="number"
                step="0.01"
                value={formData.price}
                onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                placeholder="99.99"
              />

              <div>
                <label className="block text-sm font-medium mb-2 text-gray-300">{t('products.modal.fields.currency')}</label>
                <select
                  value={formData.currency}
                  onChange={(e) => setFormData({ ...formData, currency: e.target.value })}
                  className="input-fluid w-full"
                >
                  <option value="USD">USD</option>
                  <option value="EUR">EUR</option>
                  <option value="GBP">GBP</option>
                </select>
              </div>

              <Input
                label={t('products.modal.fields.stock')}
                type="number"
                value={formData.stock_quantity}
                onChange={(e) => setFormData({ ...formData, stock_quantity: e.target.value })}
                placeholder="100"
              />
            </div>

            <div className="flex items-center gap-3 p-3 rounded-lg bg-white/5 border border-white/5">
              <input
                type="checkbox"
                id="in_stock"
                checked={formData.in_stock}
                onChange={(e) => setFormData({ ...formData, in_stock: e.target.checked })}
                className="w-5 h-5 rounded bg-dark-800 border-white/20 text-accent-500 focus:ring-accent-500/50"
              />
              <label htmlFor="in_stock" className="text-sm font-medium text-gray-200 cursor-pointer select-none">
                {t('products.modal.fields.in_stock')}
              </label>
            </div>

            <Input
              label={t('products.modal.fields.tags')}
              value={formData.tags}
              onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
              placeholder="premium, featured, bestseller"
            />

            <Input
              label={t('products.modal.fields.keywords')}
              value={formData.keywords}
              onChange={(e) => setFormData({ ...formData, keywords: e.target.value })}
              placeholder="widget, gadget, device, tool"
            />

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2 text-gray-300">{t('products.modal.fields.storage_locations')}</label>
                <textarea
                  value={formData.storage_locations}
                  onChange={(e) => setFormData({ ...formData, storage_locations: e.target.value })}
                  rows={2}
                  className="input-fluid w-full resize-y"
                  placeholder="Main Warehouse | Shelf B3"
                />
                <p className="text-xs text-gray-500 mt-1">{t('products.modal.fields.storage_locations_hint')}</p>
              </div>
              <div className="space-y-4">
                <Input
                  label={t('products.modal.fields.reorder_point')}
                  type="number"
                  value={formData.reorder_point}
                  onChange={(e) => setFormData({ ...formData, reorder_point: e.target.value })}
                  placeholder="20"
                />
                <Input
                  label={t('products.modal.fields.safety_stock')}
                  type="number"
                  value={formData.safety_stock}
                  onChange={(e) => setFormData({ ...formData, safety_stock: e.target.value })}
                  placeholder="10"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2 text-gray-300">{t('products.modal.fields.storage_notes')}</label>
              <textarea
                value={formData.storage_notes}
                onChange={(e) => setFormData({ ...formData, storage_notes: e.target.value })}
                rows={3}
                className="input-fluid w-full resize-y"
                placeholder="Keep refrigerated. Handle with gloves."
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2 text-gray-300">{t('products.modal.fields.attachments')}</label>
              <textarea
                value={formData.storage_attachments}
                onChange={(e) => setFormData({ ...formData, storage_attachments: e.target.value })}
                rows={2}
                className="input-fluid w-full resize-y"
                placeholder="https://example.com/sds.pdf, https://cdn.com/storage-guide"
              />
            </div>
          </div>

          <div className="flex gap-3 pt-4">
            <Button
              onClick={onClose}
              variant="secondary"
              className="flex-1"
            >
              {t('products.buttons.cancel')}
            </Button>
            <Button
              type="submit"
              variant="primary"
              className="flex-1 shadow-neon"
            >
              {product ? t('products.buttons.update') : t('products.buttons.save')}
            </Button>
          </div>
        </form>
      </motion.div>
    </div>
  );
}

function UploadModal({ show, onClose, onUpload }) {
  const [file, setFile] = useState(null);

  const handleUpload = () => {
    if (file) {
      onUpload(file);
      setFile(null);
    }
  };

  if (!show) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="glass-card p-8 max-w-lg w-full rounded-2xl"
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold">Bulk Upload Products</h2>
          <button onClick={onClose} className="glass-card p-2 rounded-lg hover:bg-white/10">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="mb-6">
          <p className="text-gray-400 mb-4">
            Upload a CSV file with the following columns:
          </p>
          <code className="block bg-dark-800/50 p-4 rounded-lg text-sm mb-4">
            name, description, sku, price, currency, stock_quantity, in_stock, category, tags, keywords
          </code>
          <a
            href="/sample-products.csv"
            className="text-sky-400 hover:text-sky-300 text-sm"
          >
            Download sample CSV template
          </a>
        </div>

        <div className="mb-6">
          <input
            type="file"
            accept=".csv"
            onChange={(e) => setFile(e.target.files[0])}
            className="w-full"
          />
          {file && (
            <p className="text-sm text-green-400 mt-2">
              <Check className="w-4 h-4 inline mr-1" />
              {file.name} selected
            </p>
          )}
        </div>

        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 glass-card px-6 py-3 rounded-xl hover:bg-white/10 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleUpload}
            disabled={!file}
            className="flex-1 btn-neon disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Upload Products
          </button>
        </div>
      </motion.div>
    </div>
  );
}
