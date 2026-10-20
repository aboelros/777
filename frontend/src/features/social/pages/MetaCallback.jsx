import { useEffect, useState, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Facebook, Instagram, MessageCircle, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';
import api from '@/services/api';
import { useProjectStore } from '@/store/projectStore';
import GlassCard from '@/components/ui/GlassCard';
import Button from '@/components/ui/Button';
import MetaAccountList from '../components/MetaAccountList';

export default function MetaCallback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { currentProject } = useProjectStore();

  const [status, setStatus] = useState('processing');
  const [accounts, setAccounts] = useState([]);
  const [whatsappAccounts, setWhatsappAccounts] = useState([]);
  const [accessToken, setAccessToken] = useState(null);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [activeTab, setActiveTab] = useState('facebook');

  const exchangeAttempted = useRef(false);

  useEffect(() => {
    const code = searchParams.get('code');
    const error = searchParams.get('error');
    const state = searchParams.get('state');

    if (error) {
      setStatus('error');
      toast.error('Meta authorization cancelled');
      return;
    }

    if (code && currentProject && status === 'processing' && !exchangeAttempted.current) {
      exchangeAttempted.current = true;
      handleCodeExchange(code, state);
    }
  }, [searchParams, currentProject]);

  const handleCodeExchange = async (code, state) => {
    try {
      const redirectUri = `${window.location.origin}/integrations/meta/callback`;
      const response = await api.integrations.handleMetaCallback(
        currentProject.id,
        code,
        redirectUri,
        'facebook',
        state
      );

      setAccessToken(response.access_token);
      setAccounts(response.accounts || []);
      setWhatsappAccounts(response.whatsapp_accounts || []);

      if (
        (response.accounts && response.accounts.length > 0) ||
        (response.whatsapp_accounts && response.whatsapp_accounts.length > 0)
      ) {
        setStatus('selecting');
      } else {
        setStatus('error');
        toast.error('No Meta assets found');
      }
    } catch (error) {
      setStatus('error');
      toast.error(error.message || 'Failed to authenticate with Meta');
    }
  };

  const handleConnect = async () => {
    if (!selectedAccount || !accessToken) return;
    setIsSubmitting(true);
    try {
      let config = {};
      if (activeTab === 'facebook') {
        config = {
          page_id: selectedAccount.id,
          page_name: selectedAccount.name,
          access_token: selectedAccount.access_token || accessToken,
          api_key: selectedAccount.access_token || accessToken,
        };
      } else if (activeTab === 'instagram') {
        const igAccount = selectedAccount.instagram_business_account;
        if (!igAccount) throw new Error('Selected page lacks linked Instagram account');
        config = {
          page_id: selectedAccount.id,
          instagram_business_account_id: igAccount.id,
          page_name: selectedAccount.name,
          access_token: selectedAccount.access_token || accessToken,
          api_key: selectedAccount.access_token || accessToken,
        };
      } else if (activeTab === 'whatsapp') {
        config = {
          phone_number: selectedAccount.display_phone_number,
          phone_number_id: selectedAccount.id,
          business_account_id: selectedAccount.waba_id,
          access_token: accessToken,
          api_key: accessToken,
          whatsapp_provider: 'business_api',
        };
      }

      await api.integrations.create(currentProject.id, {
        provider: activeTab,
        config: config,
      });

      toast.success('Channel successfully integrated!');
      navigate('/integrations');
    } catch (error) {
      toast.error(error.message || 'Failed to finalize connection');
      setIsSubmitting(false);
    }
  };

  const displayedAccounts =
    activeTab === 'facebook'
      ? accounts
      : activeTab === 'instagram'
      ? accounts.filter((acc) => acc.instagram_business_account)
      : whatsappAccounts;

  if (status === 'processing') {
    return (
      <div className="min-h-screen flex items-center justify-center p-6">
        <div className="text-center space-y-3">
          <div className="w-12 h-12 border-4 border-brand-primary border-t-transparent rounded-full animate-spin mx-auto" />
          <h2 className="text-xl font-bold text-text-primary">Authenticating with Meta...</h2>
          <p className="text-xs text-text-muted">Fetching associated Facebook pages and WhatsApp channels</p>
        </div>
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div className="min-h-screen flex items-center justify-center p-6">
        <GlassCard className="p-8 max-w-md w-full text-center space-y-4 border border-border">
          <div className="w-14 h-14 bg-red-500/10 border border-red-500/20 text-red-400 rounded-2xl flex items-center justify-center mx-auto">
            <AlertCircle className="w-7 h-7" />
          </div>
          <h2 className="text-xl font-bold text-text-primary">Connection Failed</h2>
          <p className="text-xs text-text-secondary">Could not complete Meta asset authorization.</p>
          <Button onClick={() => navigate('/integrations')} variant="secondary" className="w-full">
            Back to Integrations
          </Button>
        </GlassCard>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <GlassCard className="max-w-xl w-full p-8 rounded-3xl border border-border space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Select Channel to Link</h1>
          <p className="text-xs text-text-muted mt-1">Connect your verified asset to the Automio AI sales router</p>
        </div>

        {/* Channel Selection Tabs */}
        <div className="flex gap-2 p-1 bg-surface-subtle border border-border rounded-xl">
          {[
            { id: 'facebook', label: 'Facebook', icon: Facebook },
            { id: 'instagram', label: 'Instagram', icon: Instagram },
            { id: 'whatsapp', label: 'WhatsApp', icon: MessageCircle },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => { setActiveTab(tab.id); setSelectedAccount(null); }}
              className={`flex-1 py-2 px-3 rounded-lg text-xs font-semibold transition-all flex items-center justify-center gap-2 ${
                activeTab === tab.id ? 'bg-brand-primary text-white shadow-sm' : 'text-text-muted hover:text-text-primary'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>

        <MetaAccountList
          activeTab={activeTab}
          displayedAccounts={displayedAccounts}
          selectedAccount={selectedAccount}
          onSelectAccount={setSelectedAccount}
        />

        <div className="flex gap-3 pt-4 border-t border-border">
          <Button onClick={() => navigate('/integrations')} variant="secondary" className="flex-1">
            Cancel
          </Button>
          <Button
            onClick={handleConnect}
            disabled={!selectedAccount || isSubmitting}
            variant="primary"
            className="flex-1"
            isLoading={isSubmitting}
          >
            Connect Selected Channel
          </Button>
        </div>
      </GlassCard>
    </div>
  );
}
