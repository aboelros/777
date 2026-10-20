import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Package, Plus, Upload, Search } from 'lucide-react';
import { toast } from 'sonner';
import api from '@/services/api';
import { useProjectStore } from '@/store/projectStore';
import { useTranslation } from '@/lib/translations';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { NoProjectState, EmptyState } from '@/components/ui/EmptyState';
import SkeletonLoader from '@/components/ui/SkeletonLoader';
import ProductCard from '../components/ProductCard';
import StorageSection from '../components/StorageSection';
import ProductModal from '../components/ProductModal';
import UploadModal from '../components/UploadModal';

export default function Products() {
  const queryClient = useQueryClient();
  const { currentProject } = useProjectStore();
  const { t } = useTranslation();
  const [searchTerm, setSearchTerm] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedStorageProductId, setSelectedStorageProductId] = useState(null);

  const { data: productsResponse = {}, isLoading } = useQuery({
    queryKey: ['products', currentProject?.id],
    queryFn: () => api.products.list(currentProject.id),
    enabled: !!currentProject?.id,
  });

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
      if (selectedStorageProductId !== null) setSelectedStorageProductId(null);
      return;
    }
    const hasSelection = productsWithStorage.some((p) => p.id === selectedStorageProductId);
    if (!hasSelection) setSelectedStorageProductId(productsWithStorage[0].id);
  }, [productsWithStorage, selectedStorageProductId]);

  const selectedStorageProduct = selectedStorageProductId
    ? productsWithStorage.find((product) => product.id === selectedStorageProductId) || null
    : null;

  const createMutation = useMutation({
    mutationFn: (data) => api.products.create(currentProject.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products', currentProject?.id] });
      toast.success(t('products.created_success') || 'Product created successfully');
      setShowAddModal(false);
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to create product');
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ productId, data }) => api.products.update(currentProject.id, productId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products', currentProject?.id] });
      toast.success(t('products.updated_success') || 'Product updated successfully');
      setEditingProduct(null);
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to update product');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (productId) => api.products.delete(currentProject.id, productId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products', currentProject?.id] });
      toast.success(t('products.deleted_success') || 'Product deleted');
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to delete product');
    },
  });

  const uploadMutation = useMutation({
    mutationFn: (file) => api.products.bulkUpload(currentProject.id, file),
    onSuccess: (response) => {
      queryClient.invalidateQueries({ queryKey: ['products', currentProject?.id] });
      toast.success(response.data?.message || 'Products uploaded successfully');
      setShowUploadModal(false);
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Bulk upload failed');
    },
  });

  if (!currentProject) {
    return <NoProjectState subtitle={t('products.subtitle') || 'Select a project to manage inventory and product catalog'} />;
  }

  const filteredProducts = products.filter(product =>
    product.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    product.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    product.sku?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3 text-text-primary tracking-tight">
            <span className="p-2.5 rounded-xl bg-brand-primary/10 border border-brand-primary/20 text-brand-primary">
              <Package className="w-6 h-6" />
            </span>
            {t('products.title')}
          </h1>
          <p className="text-sm text-text-secondary mt-1">{t('products.subtitle')}</p>
        </div>
        <div className="flex items-center gap-3">
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

      {/* Search Input Bar */}
      <div className="glass-panel p-3 rounded-2xl border border-border">
        <Input
          icon={Search}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder={t('products.search_placeholder') || 'Search catalog by name, SKU, or tags...'}
          containerClassName="w-full"
        />
      </div>

      {/* Catalog Content */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <SkeletonLoader key={i} type="card" />
          ))}
        </div>
      ) : filteredProducts.length === 0 ? (
        <EmptyState
          icon={Package}
          title={searchTerm ? 'No Matching Products' : (t('products.empty.title') || 'Product Catalog is Empty')}
          description={searchTerm ? `No products found for "${searchTerm}"` : (t('products.empty.desc_empty') || 'Add items to your catalog so the AI agent can sell them across messaging channels.')}
          actionLabel={searchTerm ? 'Clear Search' : t('products.buttons.add_product')}
          onAction={searchTerm ? () => setSearchTerm('') : () => setShowAddModal(true)}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProducts.map((product) => (
            <ProductCard
              key={product.id}
              product={product}
              onEdit={() => setEditingProduct(product)}
              onDelete={() => {
                if (window.confirm('Are you sure you want to delete this product?')) {
                  deleteMutation.mutate(product.id);
                }
              }}
              onViewStorage={() => setSelectedStorageProductId(product.id)}
              isSelected={selectedStorageProductId === product.id}
            />
          ))}
        </div>
      )}

      {/* Storage & Inventory Tracking */}
      <StorageSection
        products={productsWithStorage.length > 0 ? productsWithStorage : products}
        selectedProduct={selectedStorageProduct || (products.length > 0 ? products[0] : null)}
        onSelect={setSelectedStorageProductId}
        allProducts={products}
      />

      {/* Add / Edit Modal */}
      <ProductModal
        show={showAddModal || Boolean(editingProduct)}
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

      {/* Bulk Upload Modal */}
      <UploadModal
        show={showUploadModal}
        onClose={() => setShowUploadModal(false)}
        onUpload={(file) => uploadMutation.mutate(file)}
      />
    </div>
  );
}
