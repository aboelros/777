import { motion } from 'framer-motion';
import { X, Facebook, AlertTriangle } from 'lucide-react';
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
  const isWhatsApp = selectedProvider.id === 'whatsapp';
  const whatsappMode = credentials.whatsapp_provider || 'baileys';

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
            ) : isWhatsApp ? (
              <div className="space-y-4">
                <div className="space-y-1.5">
                  <label className="block text-xs font-semibold uppercase tracking-wider text-text-secondary">
                    WhatsApp Provider *
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      type="button"
                      onClick={() => setCredentials({ ...credentials, whatsapp_provider: 'baileys' })}
                      className={`p-3 rounded-xl border text-left transition-all ${
                        whatsappMode === 'baileys'
                          ? 'border-amber-500 bg-amber-500/10 text-text-primary'
                          : 'border-border bg-bg-surface/50 text-text-muted hover:border-border-hover'
                      }`}
                    >
                      <div className="font-semibold text-xs flex items-center justify-between text-amber-400">
                        Baileys Gateway
                      </div>
                      <p className="text-[11px] text-text-secondary mt-1">Unofficial / Self-hosted</p>
                    </button>
                    <button
                      type="button"
                      onClick={() => setCredentials({ ...credentials, whatsapp_provider: 'business_api' })}
                      className={`p-3 rounded-xl border text-left transition-all ${
                        whatsappMode === 'business_api'
                          ? 'border-emerald-500 bg-emerald-500/10 text-text-primary'
                          : 'border-border bg-bg-surface/50 text-text-muted hover:border-border-hover'
                      }`}
                    >
                      <div className="font-semibold text-xs flex items-center justify-between">
                        Official Cloud API
                      </div>
                      <p className="text-[11px] text-text-secondary mt-1">Meta Business API</p>
                    </button>
                  </div>
                </div>

                {whatsappMode === 'business_api' ? (
                  <>
                    <Input
                      label="WhatsApp Phone Number *"
                      placeholder="+1234567890"
                      value={credentials.whatsappPhoneNumber || ''}
                      onChange={(e) => setCredentials({ ...credentials, whatsappPhoneNumber: e.target.value })}
                      required
                    />
                    <Input
                      label="Business Account ID (Optional)"
                      placeholder="e.g. 1092837465"
                      value={credentials.whatsappBusinessAccountId || ''}
                      onChange={(e) => setCredentials({ ...credentials, whatsappBusinessAccountId: e.target.value })}
                    />
                  </>
                ) : (
                  <div className="space-y-3">
                    <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-xl text-amber-300 text-xs space-y-1">
                      <div className="font-semibold flex items-center gap-1.5 text-amber-400">
                        <AlertTriangle className="w-4 h-4 shrink-0" />
                        Unofficial Gateway Notice
                      </div>
                      <p className="text-[11px] text-amber-300/80 leading-relaxed">
                        Baileys is an unofficial self-hosted WhatsApp gateway. Pair via QR code to automate chats directly with customers.
                      </p>
                    </div>
                    <Input
                      label="WhatsApp Phone Number (Optional)"
                      placeholder="+1234567890"
                      value={credentials.whatsappPhoneNumber || ''}
                      onChange={(e) => setCredentials({ ...credentials, whatsappPhoneNumber: e.target.value, whatsapp_provider: 'baileys' })}
                    />
                    <Input
                      label="Gateway Service URL (Optional)"
                      placeholder="https://ai-sales-bot-whatsapp-vdr6.onrender.com"
                      value={credentials.base_url || ''}
                      onChange={(e) => setCredentials({ ...credentials, base_url: e.target.value, whatsapp_provider: 'baileys' })}
                    />
                  </div>
                )}
              </div>
            ) : (
              <Input
                label={`${selectedProvider.name} Token / API Key *`}
                placeholder="Enter access token..."
                value={credentials.apiKey || ''}
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
