import { useEffect, useState, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { CheckCircle, AlertCircle, ShoppingBag } from 'lucide-react';
import { toast } from 'sonner';
import { integrations } from '../../../services/api/integrations';
import { useProjectStore } from '../../../store/projectStore';
import GlassCard from '../../../components/ui/GlassCard';

export default function ShopifyCallback() {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const { currentProject } = useProjectStore();

    const [status, setStatus] = useState('processing'); // processing, error, success

    const exchangeAttempted = useRef(false);

    useEffect(() => {
        const code = searchParams.get('code');
        const shop = searchParams.get('shop');
        const hmac = searchParams.get('hmac');
        const state = searchParams.get('state');
        const host = searchParams.get('host');

        if (!code || !shop || !hmac) {
            setStatus('error');
            toast.error('Invalid callback parameters from Shopify');
            return;
        }

        if (currentProject && status === 'processing' && !exchangeAttempted.current) {
            exchangeAttempted.current = true;
            handleCodeExchange(code, shop, hmac, state, host);
        }
    }, [searchParams, currentProject]);

    const handleCodeExchange = async (code, shop, hmac, state, host) => {
        try {
            const response = await integrations.handleShopifyCallback(
                currentProject.id,
                code,
                shop,
                hmac,
                state,
                host
            );

            // Once the token is exchanged and returned, we save it in the backend
            // In a fully integrated system, `handleShopifyCallback` backend endpoint 
            // should also save the integration record. If it doesn't, we create it here.
            
            const config = {
                shop_domain: response.shop_domain || shop,
                api_secret: response.access_token,
                setup_method: 'oauth'
            };

            await integrations.create(currentProject.id, {
                provider: 'shopify',
                config: config
            });

            setStatus('success');
            toast.success(`Connected to Shopify successfully!`);
            
            // Redirect after a short delay
            setTimeout(() => {
                navigate('/integrations');
            }, 2000);

        } catch (error) {
            console.error('Shopify callback error:', error);
            setStatus('error');
            toast.error(error.message || 'Failed to connect with Shopify');
        }
    };

    if (status === 'processing') {
        return (
            <div className="min-h-screen flex items-center justify-center bg-dark-950">
                <div className="text-center">
                    <div className="w-16 h-16 border-4 border-green-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                    <h2 className="text-xl font-semibold text-white">Connecting to Shopify...</h2>
                    <p className="text-gray-400">Verifying authentication and securing tokens</p>
                </div>
            </div>
        );
    }

    if (status === 'success') {
        return (
            <div className="min-h-screen flex items-center justify-center bg-dark-950">
                <GlassCard className="p-8 max-w-md w-full text-center">
                    <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                        <CheckCircle className="w-8 h-8 text-green-500" />
                    </div>
                    <h2 className="text-xl font-bold text-white mb-2">Successfully Connected!</h2>
                    <p className="text-gray-400 mb-6">
                        Your Shopify store has been integrated. Redirecting you back to the dashboard...
                    </p>
                </GlassCard>
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
                        We couldn't connect your Shopify account. Please try again.
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

    return null;
}
