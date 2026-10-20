import { motion } from 'framer-motion';
import { X, Facebook } from 'lucide-react';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';

export default function IntegrationConnectModal({
  show,
  selectedProvider,
  credentials,
  setCredentials,
  onClose,
  onSubmit,
  onMetaConnect,
  isConnecting,
}) {
  if (!show || !selectedProvider) return null;

  const isMeta = selectedProvider.id === 'facebook' || selectedProvider.id === 'instagram';

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-md flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.96 }}
        animate={{ opacity: 1, scale: 1 }}
        className="glass-card p-6 sm:p-8 max-w-md w-full rounded-2xl border border-border"
      >
        <div className="flex items-center justify-between mb-6 pb-4 border-b border-border">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${selectedProvider.color} flex items-center justify-center text-white`}>
              <selectedProvider.icon className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-text-primary">Connect {selectedProvider.name}</h2>
              <p className="text-xs text-text-muted">{selectedProvider.description}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 text-text-muted hover:text-text-primary">
            <X className="w-5 h-5" />
          </button>
        </div>

        {isMeta ? (
          <div className="text-center py-6 space-y-4">
            <p className="text-sm text-text-secondary">
              Connect your Meta business account to automatically route customer comments and messages.
            </p>
            <Button
              onClick={onMetaConnect}
              variant="primary"
              className="w-full bg-[#1877F2] hover:bg-[#0C63D4] text-white"
              leftIcon={Facebook}
            >
              Continue with Meta Business
            </Button>
          </div>
        ) : (
          <form
            onSubmit={(e) => {
              e.preventDefault();
              onSubmit();
            }}
            className="space-y-4"
          >
            {selectedProvider.id === 'shopify' ? (
              <Input
                label="Shopify Domain *"
                placeholder="mystore.myshopify.com"
                value={credentials.shopDomain}
                onChange={(e) => setCredentials({ ...credentials, shopDomain: e.target.value })}
                required
              />
            ) : selectedProvider.id === 'whatsapp' ? (
              <>
                <Input
                  label="WhatsApp Phone Number *"
                  placeholder="+1234567890"
                  value={credentials.whatsappPhoneNumber}
                  onChange={(e) => setCredentials({ ...credentials, whatsappPhoneNumber: e.target.value })}
                  required
                />
                <Input
                  label="Business Account ID (Optional)"
                  placeholder="e.g. 1092837465"
                  value={credentials.whatsappBusinessAccountId}
                  onChange={(e) => setCredentials({ ...credentials, whatsappBusinessAccountId: e.target.value })}
                />
              </>
            ) : (
              <Input
                label={`${selectedProvider.name} Token / API Key *`}
                placeholder="Enter access token..."
                value={credentials.apiKey}
                onChange={(e) => setCredentials({ ...credentials, apiKey: e.target.value })}
                required
              />
            )}

            <div className="flex gap-3 pt-4 border-t border-border">
              <Button type="button" onClick={onClose} variant="secondary" className="flex-1">
                Cancel
              </Button>
              <Button type="submit" variant="primary" className="flex-1" isLoading={isConnecting}>
                Save Connection
              </Button>
            </div>
          </form>
        )}
      </motion.div>
    </div>
  );
}
