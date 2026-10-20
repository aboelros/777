import { motion } from 'framer-motion';
import { CheckCircle, MessageCircle } from 'lucide-react';

export default function MetaAccountList({
  activeTab,
  displayedAccounts,
  selectedAccount,
  onSelectAccount,
}) {
  if (displayedAccounts.length === 0) {
    return (
      <div className="text-center py-8 text-text-muted text-sm">
        {activeTab === 'instagram'
          ? 'No Instagram Business accounts found linked to your Facebook Pages.'
          : activeTab === 'whatsapp'
          ? 'No WhatsApp Business numbers found.'
          : 'No Facebook Pages found.'}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-3 max-h-[360px] overflow-y-auto pr-1">
      {displayedAccounts.map((account) => {
        const isSelected = selectedAccount?.id === account.id;
        return (
          <motion.div
            key={account.id}
            whileHover={{ scale: 1.005 }}
            whileTap={{ scale: 0.99 }}
            onClick={() => onSelectAccount(account)}
            className={`p-4 rounded-xl border cursor-pointer transition-all ${
              isSelected
                ? 'bg-brand-primary/15 border-brand-primary text-text-primary'
                : 'bg-surface-subtle border-border hover:bg-surface-hover text-text-secondary'
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-brand-primary/10 border border-brand-primary/20 flex items-center justify-center font-bold text-brand-primary">
                  {activeTab === 'whatsapp' ? (
                    <MessageCircle className="w-5 h-5" />
                  ) : activeTab === 'instagram' && account.instagram_business_account?.username ? (
                    account.instagram_business_account.username.charAt(0).toUpperCase()
                  ) : (
                    account.name?.charAt(0) || 'M'
                  )}
                </div>
                <div>
                  <h4 className="font-semibold text-text-primary text-sm">
                    {activeTab === 'whatsapp'
                      ? account.display_phone_number
                      : activeTab === 'instagram' && account.instagram_business_account?.username
                      ? `@${account.instagram_business_account.username}`
                      : account.name}
                  </h4>
                  <p className="text-xs text-text-muted">
                    {activeTab === 'whatsapp'
                      ? `${account.verified_name || ''} • ID: ${account.id}`
                      : `Page ID: ${account.id}`}
                  </p>
                </div>
              </div>
              {isSelected && <CheckCircle className="w-5 h-5 text-brand-primary" />}
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}
