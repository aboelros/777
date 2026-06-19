import { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, X, Image as ImageIcon, Trash2, MoveUp, MoveDown, Edit2, Save } from 'lucide-react';
import { toast } from 'sonner';
import api from '../services/api';
import { useProjectStore } from '../store/projectStore';

export default function ProductImageUpload({ productId, images = [], onImagesChange }) {
    const { currentProject } = useProjectStore();
    const [uploading, setUploading] = useState(false);
    const [editingIndex, setEditingIndex] = useState(null);
    const [editDescription, setEditDescription] = useState('');
    const fileInputRef = useRef(null);

    const handleFileSelect = async (e) => {
        const files = Array.from(e.target.files);
        if (!files.length) return;

        setUploading(true);
        try {
            for (const file of files) {
                const formData = new FormData();
                formData.append('file', file);
                formData.append('description', file.name.split('.')[0]); // Default description from filename

                const response = await api.products.uploadImage(
                    currentProject.id,
                    productId,
                    formData
                );

                if (response.data.success) {
                    // Update local state via callback
                    const newImages = [...images, response.data.image];
                    onImagesChange(newImages);
                }
            }
            toast.success('Images uploaded successfully');
        } catch (error) {
            console.error('Upload failed:', error);
            toast.error('Failed to upload images');
        } finally {
            setUploading(false);
            if (fileInputRef.current) {
                fileInputRef.current.value = '';
            }
        }
    };

    const handleDelete = async (index) => {
        if (!confirm('Are you sure you want to delete this image?')) return;

        try {
            await api.products.deleteImage(currentProject.id, productId, index);

            const newImages = [...images];
            newImages.splice(index, 1);
            // Update order for remaining images
            newImages.forEach((img, idx) => {
                img.order = idx + 1;
            });

            onImagesChange(newImages);
            toast.success('Image deleted');
        } catch (error) {
            console.error('Delete failed:', error);
            toast.error('Failed to delete image');
        }
    };

    const handleUpdateDescription = async (index) => {
        try {
            await api.products.updateImage(currentProject.id, productId, index, {
                description: editDescription
            });

            const newImages = [...images];
            newImages[index].description = editDescription;
            onImagesChange(newImages);

            setEditingIndex(null);
            toast.success('Description updated');
        } catch (error) {
            console.error('Update failed:', error);
            toast.error('Failed to update description');
        }
    };

    const handleMove = async (index, direction) => {
        const newIndex = index + direction;
        if (newIndex < 0 || newIndex >= images.length) return;

        try {
            // Optimistic update
            const newImages = [...images];
            const [movedImage] = newImages.splice(index, 1);
            newImages.splice(newIndex, 0, movedImage);

            // Update order numbers
            newImages.forEach((img, idx) => {
                img.order = idx + 1;
            });

            onImagesChange(newImages);

            // API call
            await api.products.updateImage(currentProject.id, productId, index, {
                order: newIndex + 1 // 1-based index for backend
            });

        } catch (error) {
            console.error('Move failed:', error);
            toast.error('Failed to reorder image');
            // Revert would be complex here, assuming success for now or refresh
        }
    };

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <label className="block text-sm font-medium text-slate-300">Product Images</label>
                <div className="text-xs text-slate-500">{images.length} images</div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                {images.map((image, index) => (
                    <motion.div
                        key={image.filename || index}
                        layout
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="group relative aspect-square rounded-lg overflow-hidden bg-black/20 border border-white/10"
                    >
                        <img
                            src={image.url} // In production, prepend backend URL if relative
                            alt={image.description}
                            className="w-full h-full object-cover"
                        />

                        {/* Overlay */}
                        <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col justify-between p-2">
                            <div className="flex justify-end gap-1">
                                <button
                                    onClick={() => handleDelete(index)}
                                    className="p-1.5 rounded-md bg-red-500/20 text-red-400 hover:bg-red-500/40 transition-colors"
                                    title="Delete"
                                >
                                    <Trash2 className="w-3 h-3" />
                                </button>
                            </div>

                            <div className="space-y-1">
                                {editingIndex === index ? (
                                    <div className="flex gap-1">
                                        <input
                                            type="text"
                                            value={editDescription}
                                            onChange={(e) => setEditDescription(e.target.value)}
                                            className="w-full px-2 py-1 text-xs bg-black/50 border border-white/20 rounded text-white focus:outline-none"
                                            autoFocus
                                            onKeyDown={(e) => {
                                                if (e.key === 'Enter') handleUpdateDescription(index);
                                                if (e.key === 'Escape') setEditingIndex(null);
                                            }}
                                        />
                                        <button
                                            onClick={() => handleUpdateDescription(index)}
                                            className="p-1 rounded bg-green-500/20 text-green-400 hover:bg-green-500/40"
                                        >
                                            <Save className="w-3 h-3" />
                                        </button>
                                    </div>
                                ) : (
                                    <div
                                        className="text-xs text-white truncate cursor-pointer hover:text-sky-300 flex items-center gap-1"
                                        onClick={() => {
                                            setEditingIndex(index);
                                            setEditDescription(image.description || '');
                                        }}
                                    >
                                        <span className="truncate">{image.description || 'No description'}</span>
                                        <Edit2 className="w-2 h-2 opacity-50" />
                                    </div>
                                )}

                                <div className="flex justify-between items-center pt-1 border-t border-white/10">
                                    <div className="flex gap-1">
                                        <button
                                            onClick={() => handleMove(index, -1)}
                                            disabled={index === 0}
                                            className="p-1 rounded hover:bg-white/10 disabled:opacity-30"
                                        >
                                            <MoveUp className="w-3 h-3 text-white" />
                                        </button>
                                        <button
                                            onClick={() => handleMove(index, 1)}
                                            disabled={index === images.length - 1}
                                            className="p-1 rounded hover:bg-white/10 disabled:opacity-30"
                                        >
                                            <MoveDown className="w-3 h-3 text-white" />
                                        </button>
                                    </div>
                                    <span className="text-[10px] text-slate-400">#{index + 1}</span>
                                </div>
                            </div>
                        </div>
                    </motion.div>
                ))}

                {/* Upload Button */}
                <div className="aspect-square rounded-lg border-2 border-dashed border-white/10 hover:border-sky-500/50 hover:bg-sky-500/5 transition-all flex flex-col items-center justify-center cursor-pointer relative">
                    <input
                        ref={fileInputRef}
                        type="file"
                        multiple
                        accept="image/*"
                        onChange={handleFileSelect}
                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                        disabled={!productId || uploading}
                    />
                    {uploading ? (
                        <div className="loading-spinner w-6 h-6 border-2 border-sky-500 border-t-transparent rounded-full animate-spin" />
                    ) : (
                        <>
                            <Upload className="w-6 h-6 text-slate-400 mb-2" />
                            <span className="text-xs text-slate-400 font-medium">Upload Image</span>
                        </>
                    )}
                </div>
            </div>

            {!productId && (
                <p className="text-xs text-cyan-400 flex items-center gap-1">
                    <span className="w-1 h-1 rounded-full bg-cyan-400" />
                    Save product first to upload images
                </p>
            )}
        </div>
    );
}
