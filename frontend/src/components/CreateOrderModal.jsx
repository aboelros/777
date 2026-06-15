import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, ShoppingCart, Plus, Minus } from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../services/api';
import { useProjectStore } from '../store/projectStore';
import { toast } from 'sonner';

export default function CreateOrderModal({ isOpen, onClose, customer }) {
    const { currentProject } = useProjectStore();
    const queryClient = useQueryClient();
    const [selectedProducts, setSelectedProducts] = useState([]);
    const [quantities, setQuantities] = useState({});

    // Fetch products
    const { data: products } = useQuery({
        queryKey: ['products', currentProject?.id],
        queryFn: () => api.products.list(currentProject.id),
        enabled: !!currentProject?.id && isOpen,
    });

    // Create order mutation
    const createOrderMutation = useMutation({
        mutationFn: (orderData) => api.orders.create(currentProject.id, orderData),
        onSuccess: () => {
            toast.success('Order created successfully!');
            queryClient.invalidateQueries(['orders']);
            onClose();
        },
        onError: (error) => {
            toast.error(`Failed to create order: ${error.message}`);
        },
    });

    const toggleProduct = (productId) => {
        if (selectedProducts.includes(productId)) {
            setSelectedProducts(selectedProducts.filter(id => id !== productId));
            const newQuantities = { ...quantities };
            delete newQuantities[productId];
            setQuantities(newQuantities);
        } else {
            setSelectedProducts([...selectedProducts, productId]);
            setQuantities({ ...quantities, [productId]: 1 });
        }
    };

    const updateQuantity = (productId, delta) => {
        const newQty = (quantities[productId] || 1) + delta;
        if (newQty > 0) {
            setQuantities({ ...quantities, [productId]: newQty });
        }
    };

    const calculateTotal = () => {
        return selectedProducts.reduce((total, productId) => {
            const product = products?.find(p => p.id === productId);
            return total + (product?.price || 0) * (quantities[productId] || 1);
        }, 0);
    };

    const handleCreateOrder = () => {
        const orderItems = selectedProducts.map(productId => {
            const product = products?.find(p => p.id === productId);
            return {
                product_id: productId,
                quantity: quantities[productId] || 1,
                unit_price: product?.price || 0,
            };
        });

        createOrderMutation.mutate({
            customer_id: customer.id,
            items: orderItems,
            status: 'pending',
        });
    };

    if (!isOpen) return null;

    return (
        <AnimatePresence>
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    className="w-full max-w-2xl bg-gradient-to-br from-slate-900 to-slate-800 rounded-2xl border border-white/10 shadow-2xl overflow-hidden"
                >
                    {/* Header */}
                    <div className="p-6 border-b border-white/10 bg-white/5">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <ShoppingCart className="w-6 h-6 text-green-400" />
                                <div>
                                    <h2 className="text-2xl font-bold text-white">Create Order</h2>
                                    <p className="text-sm text-slate-400">For {customer?.name || 'Customer'}</p>
                                </div>
                            </div>
                            <button
                                onClick={onClose}
                                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                            >
                                <X className="w-5 h-5 text-slate-400" />
                            </button>
                        </div>
                    </div>

                    {/* Products List */}
                    <div className="p-6 max-h-96 overflow-y-auto">
                        <div className="space-y-3">
                            {products?.map((product) => {
                                const isSelected = selectedProducts.includes(product.id);
                                const quantity = quantities[product.id] || 1;

                                return (
                                    <motion.div
                                        key={product.id}
                                        whileHover={{ scale: 1.02 }}
                                        className={`p-4 rounded-xl border transition-all cursor-pointer ${isSelected
                                            ? 'bg-green-500/20 border-green-500/50'
                                            : 'bg-white/5 border-white/10 hover:bg-white/10'
                                            }`}
                                        onClick={() => toggleProduct(product.id)}
                                    >
                                        <div className="flex items-center justify-between">
                                            <div className="flex-1">
                                                <h3 className="font-medium text-white">{product.name}</h3>
                                                <p className="text-sm text-slate-400">{product.description}</p>
                                                <p className="text-lg font-bold text-green-400 mt-1">
                                                    ${product.price} {product.currency}
                                                </p>
                                            </div>

                                            {isSelected && (
                                                <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
                                                    <button
                                                        onClick={() => updateQuantity(product.id, -1)}
                                                        className="p-1 bg-white/10 rounded hover:bg-white/20 transition-colors"
                                                    >
                                                        <Minus className="w-4 h-4 text-white" />
                                                    </button>
                                                    <span className="text-white font-medium w-8 text-center">{quantity}</span>
                                                    <button
                                                        onClick={() => updateQuantity(product.id, 1)}
                                                        className="p-1 bg-white/10 rounded hover:bg-white/20 transition-colors"
                                                    >
                                                        <Plus className="w-4 h-4 text-white" />
                                                    </button>
                                                </div>
                                            )}
                                        </div>
                                    </motion.div>
                                );
                            })}
                        </div>
                    </div>

                    {/* Footer */}
                    <div className="p-6 border-t border-white/10 bg-white/5">
                        <div className="flex items-center justify-between mb-4">
                            <span className="text-slate-400">Total:</span>
                            <span className="text-2xl font-bold text-white">${calculateTotal().toFixed(2)}</span>
                        </div>
                        <div className="flex gap-3">
                            <button
                                onClick={onClose}
                                className="flex-1 px-4 py-3 bg-white/10 text-white rounded-xl hover:bg-white/20 transition-all font-medium"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleCreateOrder}
                                disabled={selectedProducts.length === 0 || createOrderMutation.isLoading}
                                className="flex-1 px-4 py-3 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-xl hover:shadow-lg hover:shadow-green-500/50 transition-all font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {createOrderMutation.isLoading ? 'Creating...' : 'Create Order'}
                            </button>
                        </div>
                    </div>
                </motion.div>
            </div>
        </AnimatePresence>
    );
}
