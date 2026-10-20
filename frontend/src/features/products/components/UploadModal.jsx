import { useState } from 'react';
import { motion } from 'framer-motion';
import { X, Check, Upload } from 'lucide-react';
import Button from '@/components/ui/Button';

export default function UploadModal({ show, onClose, onUpload }) {
  const [file, setFile] = useState(null);

  const handleUpload = () => {
    if (file) {
      onUpload(file);
      setFile(null);
    }
  };

  if (!show) return null;

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-md flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        className="glass-card p-6 sm:p-8 max-w-lg w-full rounded-2xl border border-border"
      >
        <div className="flex items-center justify-between mb-6 pb-4 border-b border-border">
          <h2 className="text-xl font-bold text-text-primary flex items-center gap-2">
            <Upload className="w-5 h-5 text-brand-primary" />
            Bulk Import Catalog
          </h2>
          <button
            onClick={onClose}
            className="p-2 rounded-xl text-text-muted hover:text-text-primary hover:bg-surface-subtle transition-colors"
            aria-label="Close modal"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="mb-6 space-y-3">
          <p className="text-sm text-text-secondary">
            Upload a CSV formatted file with the following column headers:
          </p>
          <code className="block bg-surface-subtle border border-border p-3 rounded-xl text-xs font-mono text-brand-primary overflow-x-auto">
            name, description, sku, price, currency, stock_quantity, in_stock, category, tags
          </code>
          <a
            href="/sample-products.csv"
            className="text-brand-primary hover:text-brand-primary-hover text-xs font-medium inline-block underline"
          >
            Download sample CSV template
          </a>
        </div>

        <div className="mb-6">
          <input
            type="file"
            accept=".csv"
            onChange={(e) => setFile(e.target.files[0])}
            className="w-full text-sm text-text-secondary file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-brand-primary/10 file:text-brand-primary hover:file:bg-brand-primary/20 file:cursor-pointer"
          />
          {file && (
            <p className="text-xs text-emerald-400 mt-2 flex items-center gap-1">
              <Check className="w-3.5 h-3.5" />
              {file.name} ready for import
            </p>
          )}
        </div>

        <div className="flex gap-3 pt-4 border-t border-border">
          <Button
            type="button"
            onClick={onClose}
            variant="secondary"
            className="flex-1"
          >
            Cancel
          </Button>
          <Button
            type="button"
            onClick={handleUpload}
            disabled={!file}
            variant="primary"
            className="flex-1"
          >
            Import Products
          </Button>
        </div>
      </motion.div>
    </div>
  );
}
