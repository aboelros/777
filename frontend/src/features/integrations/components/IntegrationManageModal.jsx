import { motion } from 'framer-motion';
import { X } from 'lucide-react';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';

export default function IntegrationManageModal({
  show,
  isEditing,
  formData,
  setFormData,
  onClose,
  onSubmit,
}) {
  if (!show) return null;

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-md flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        className="glass-card p-6 sm:p-8 max-w-xl w-full rounded-2xl max-h-[90vh] overflow-y-auto border border-border"
      >
        <div className="flex items-center justify-between mb-6 pb-4 border-b border-border">
          <h2 className="text-xl font-bold text-text-primary">
            {isEditing ? 'Edit Integration Settings' : 'Add New Custom Integration'}
          </h2>
          <button onClick={onClose} className="p-2 text-text-muted hover:text-text-primary">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={onSubmit} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-text-secondary mb-1.5">
                Provider *
              </label>
              <select
                value={formData.provider}
                onChange={(e) => setFormData({ ...formData, provider: e.target.value })}
                className="input-fluid w-full text-sm"
                required
              >
                <option value="">Select provider</option>
                <option value="shopify">Shopify</option>
                <option value="whatsapp">WhatsApp</option>
                <option value="telegram">Telegram</option>
                <option value="facebook">Facebook</option>
                <option value="instagram">Instagram</option>
                <option value="discord">Discord</option>
                <option value="tiktok">TikTok</option>
                <option value="custom">Custom Webhook</option>
              </select>
            </div>

            <Input
              label="Display Name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="e.g. US Store VIP"
            />
          </div>

          <Input
            label="API Key / Token *"
            value={formData.apiKey}
            onChange={(e) => setFormData({ ...formData, apiKey: e.target.value })}
            placeholder="Enter API token..."
            required
          />

          <Input
            label="API Secret (Optional)"
            type="password"
            value={formData.apiSecret}
            onChange={(e) => setFormData({ ...formData, apiSecret: e.target.value })}
            placeholder="Secret key..."
          />

          <Input
            label="Webhook Destination URL"
            type="url"
            value={formData.webhookUrl}
            onChange={(e) => setFormData({ ...formData, webhookUrl: e.target.value })}
            placeholder="https://api.example.com/webhook"
          />

          <div className="flex gap-3 pt-4 border-t border-border">
            <Button type="button" onClick={onClose} variant="secondary" className="flex-1">
              Cancel
            </Button>
            <Button type="submit" variant="primary" className="flex-1">
              {isEditing ? 'Save Changes' : 'Create Integration'}
            </Button>
          </div>
        </form>
      </motion.div>
    </div>
  );
}
