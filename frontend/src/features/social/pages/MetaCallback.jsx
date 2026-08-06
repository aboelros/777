import { useEffect, useState, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { CheckCircle, AlertCircle, Facebook, Instagram, MessageCircle } from 'lucide-react';
import { toast } from 'sonner';
import api from '../../../services/api';
import { useProjectStore } from '../../../store/projectStore';
import GlassCard from '../../../components/ui/GlassCard';

export default function MetaCallback() {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const { currentProject } = useProjectStore();

    const [status, setStatus] = useState('processing'); // processing, selecting, error, success
    const [accounts, setAccounts] = useState([]);
    const [whatsappAccounts, setWhatsappAccounts] = useState([]);
    const [accessToken, setAccessToken] = useState(null);
    const [selectedAccount, setSelectedAccount] = useState(null);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [activeTab, setActiveTab] = useState('facebook'); // 'facebook', 'instagram', 'whatsapp'

    const exchangeAttempted = useRef(false);

    useEffect(() => {
        const code = searchParams.get('code');
        const error = searchParams.get('error');

        if (error) {
            setStatus('error');
            toast.error('Facebook Login failed');
            return;
        }

        if (code && currentProject && status === 'processing' && !exchangeAttempted.current) {
            exchangeAttempted.current = true;
            handleCodeExchange(code);
        }
    }, [searchParams, currentProject]);

    const handleCodeExchange = async (code) => {
        try {
            const redirectUri = window.location.origin + '/integrations/meta/callback';

            const response = await api.integrations.handleMetaCallback(
                currentProject.id,
                code,
                redirectUri,
                'facebook'
            );

            setAccessToken(response.access_token);
            setAccounts(response.accounts || []);
            setWhatsappAccounts(response.whatsapp_accounts || []);

            if ((response.accounts && response.accounts.length > 0) || (response.whatsapp_accounts && response.whatsapp_accounts.length > 0)) {
                setStatus('selecting');
            } else {
                setStatus('error');
                toast.error('No Pages or WhatsApp accounts found');
            }

        } catch (error) {
            console.error('Meta callback error:', error);
            setStatus('error');
            toast.error(error.message || 'Failed to connect with Meta');
        }
    };

    const handleConnect = async () => {
        if (!selectedAccount || !accessToken) return;

        setIsSubmitting(true);
        try {
            let provider = activeTab;
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
                if (!igAccount) {
                    throw new Error('This Page does not have a linked Instagram Business Account');
                }

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
                    whatsapp_provider: 'business_api'
                };
            }

            await integrations.create(currentProject.id, {
                provider: provider,
                config: config
            });

            let typeName = 'Facebook Page';
            if (activeTab === 'instagram') typeName = 'Instagram Account';
            if (activeTab === 'whatsapp') typeName = 'WhatsApp Number';

            toast.success(`Connected to ${typeName} successfully!`);
            navigate('/integrations');

        } catch (error) {
            console.error('Connection failed:', error);
            toast.error(error.message || 'Failed to save integration');
            setIsSubmitting(false);
        }
    };

    const displayedAccounts = activeTab === 'facebook'
        ? accounts
        : activeTab === 'instagram'
            ? accounts.filter(acc => acc.instagram_business_account)
            : whatsappAccounts;

    if (status === 'processing') {
        return (
            <div className="min-h-screen flex items-center justify-center bg-dark-950">
                <div className="text-center">
                    <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                    <h2 className="text-xl font-semibold text-white">Connecting to Meta...</h2>
                    <p className="text-gray-400">Exchanging tokens and fetching accounts</p>
                </div>
            </div>
        );
    }

    if (status === 'error') {
        return (
            <div className="min-h-screen flex items-center justify-center bg-dark-950">
                <GlassCard className="p-8 max-w-md w-full text-center">
                    <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                        <AlertCircle className="w-8 h-8 text-red-500" />
                    </div>
                    <h2 className="text-xl font-bold text-white mb-2">Connection Failed</h2>
                    <p className="text-gray-400 mb-6">
                        We couldn't connect your Meta account. Please try again.
                    </p>
                    <button
                        onClick={() => navigate('/integrations')}
                        className="px-6 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-white transition-colors"
                    >
                        Return to Integrations
                    </button>
                </GlassCard>
            </div>
        );
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-dark-950 p-4">
            <GlassCard className="max-w-2xl w-full p-8">
                <div className="flex items-center gap-4 mb-6">
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${activeTab === 'facebook' ? 'bg-blue-600' :
                        activeTab === 'instagram' ? 'bg-gradient-to-tr from-yellow-400 via-red-500 to-sky-500' :
                            'bg-green-500'
                        }`}>
                        {activeTab === 'facebook' && <Facebook className="w-6 h-6 text-white" />}
                        {activeTab === 'instagram' && <Instagram className="w-6 h-6 text-white" />}
                        {activeTab === 'whatsapp' && <MessageCircle className="w-6 h-6 text-white" />}
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold text-white">Select Account to Connect</h1>
                        <p className="text-gray-400">
                            Choose the {activeTab === 'facebook' ? 'Facebook Page' : activeTab === 'instagram' ? 'Instagram Account' : 'WhatsApp Number'} you want to integrate
                        </p>
                    </div>
                </div>

                {/* Tabs */}
                <div className="flex gap-2 mb-6 bg-white/5 p-1 rounded-lg overflow-x-auto">
                    <button
                        onClick={() => { setActiveTab('facebook'); setSelectedAccount(null); }}
                        className={`flex-1 flex items-center justify-center gap-2 py-2 px-4 rounded-md transition-all whitespace-nowrap ${activeTab === 'facebook' ? 'bg-blue-600 text-white shadow-lg' : 'text-gray-400 hover:text-white hover:bg-white/5'}`}
                    >
                        <Facebook className="w-4 h-4" />
                        Facebook
                    </button>
                    <button
                        onClick={() => { setActiveTab('instagram'); setSelectedAccount(null); }}
                        className={`flex-1 flex items-center justify-center gap-2 py-2 px-4 rounded-md transition-all whitespace-nowrap ${activeTab === 'instagram' ? 'bg-gradient-to-r from-sky-500 to-sky-500 text-white shadow-lg' : 'text-gray-400 hover:text-white hover:bg-white/5'}`}
                    >
                        <Instagram className="w-4 h-4" />
                        Instagram
                    </button>
                    <button
                        onClick={() => { setActiveTab('whatsapp'); setSelectedAccount(null); }}
                        className={`flex-1 flex items-center justify-center gap-2 py-2 px-4 rounded-md transition-all whitespace-nowrap ${activeTab === 'whatsapp' ? 'bg-green-500 text-white shadow-lg' : 'text-gray-400 hover:text-white hover:bg-white/5'}`}
                    >
                        <MessageCircle className="w-4 h-4" />
                        WhatsApp
                    </button>
                </div>

                <div className="grid grid-cols-1 gap-4 mb-8 max-h-[400px] overflow-y-auto pr-2">
                    {displayedAccounts.length === 0 ? (
                        <div className="text-center py-8 text-gray-500">
                            {activeTab === 'instagram'
                                ? "No Instagram Business accounts found linked to your Facebook Pages."
                                : activeTab === 'whatsapp'
                                    ? "No WhatsApp Business numbers found."
                                    : "No Facebook Pages found."}
                        </div>
                    ) : (
                        displayedAccounts.map((account) => (
                            <motion.div
                                key={account.id}
                                whileHover={{ scale: 1.01 }}
                                whileTap={{ scale: 0.99 }}
                                onClick={() => setSelectedAccount(account)}
                                className={`p-4 rounded-xl border cursor-pointer transition-all ${selectedAccount?.id === account.id
                                    ? 'bg-blue-600/20 border-blue-500'
                                    : 'bg-white/5 border-white/10 hover:bg-white/10'
                                    }`}
                            >
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-3">
                                        <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${activeTab === 'facebook' ? 'bg-blue-500/20 text-blue-400' :
                                            activeTab === 'instagram' ? 'bg-sky-500/20 text-sky-400' :
                                                'bg-green-500/20 text-green-400'
                                            }`}>
                                            {activeTab === 'whatsapp' ? <MessageCircle className="w-5 h-5" /> : account.name.charAt(0)}
                                        </div>
                                        <div>
                                            <h3 className="font-semibold text-white">
                                                {activeTab === 'whatsapp' ? account.display_phone_number : account.name}
                                            </h3>
                                            <p className="text-xs text-gray-400">
                                                {activeTab === 'whatsapp' ? (
                                                    <>
                                                        {account.verified_name} • ID: {account.id}
                                                        <br />
                                                        <span className="opacity-75">WABA: {account.waba_name}</span>
                                                    </>
                                                ) : (
                                                    <>
                                                        Page ID: {account.id}
                                                        {activeTab === 'instagram' && account.instagram_business_account && (
                                                            <span className="ml-2 px-2 py-0.5 bg-sky-500/20 text-sky-400 rounded text-[10px]">
                                                                IG: {account.instagram_business_account.id}
                                                            </span>
                                                        )}
                                                    </>
                                                )}
                                            </p>
                                        </div>
                                    </div>
                                    {selectedAccount?.id === account.id && (
                                        <CheckCircle className="w-6 h-6 text-blue-500" />
                                    )}
                                </div>
                            </motion.div>
                        ))
                    )}
                </div>

                <div className="flex gap-4">
                    <button
                        onClick={() => navigate('/integrations')}
                        className="flex-1 px-6 py-3 bg-white/5 hover:bg-white/10 rounded-xl text-gray-300 transition-colors"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={handleConnect}
                        disabled={!selectedAccount || isSubmitting}
                        className="flex-1 btn-neon disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isSubmitting ? 'Connecting...' : 'Connect Selected'}
                    </button>
                </div>
            </GlassCard>
        </div>
    );
}
