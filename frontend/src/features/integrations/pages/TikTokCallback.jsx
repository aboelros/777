import { useEffect, useState, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { CheckCircle, AlertCircle, ShoppingBag } from 'lucide-react';
import { toast } from 'sonner';
import { integrations } from '../../../services/api/integrations';
import { useProjectStore } from '../../../store/projectStore';
import GlassCard from '../../../components/ui/GlassCard';

export default function TikTokCallback() {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const { currentProject } = useProjectStore();

    const [status, setStatus] = useState('processing'); // processing, selecting, error
    const [shops, setShops] = useState([]);
    const [accessToken, setAccessToken] = useState(null);
    const [selectedShop, setSelectedShop] = useState(null);
    const [isSubmitting, setIsSubmitting] = useState(false);

    const exchangeAttempted = useRef(false);

    useEffect(() => {
        const code = searchParams.get('code');
        const error = searchParams.get('error');

        if (error) {
            setStatus('error');
            toast.error('TikTok Login failed');
            return;
        }

        if (code && currentProject && status === 'processing' && !exchangeAttempted.current) {
            exchangeAttempted.current = true;
            handleCodeExchange(code);
        }
    }, [searchParams, currentProject]);

    const handleCodeExchange = async (code) => {
        try {
            const redirectUri = window.location.origin + '/integrations/tiktok/callback';

            const response = await integrations.handleTikTokCallback(
                currentProject.id,
                code,
                redirectUri
            );

            setAccessToken(response.access_token);
            
            // Format returned shops if any
            const shopList = response.shops || [];
            setShops(shopList);

            if (shopList.length > 0) {
                setStatus('selecting');
                if (shopList.length === 1) {
                    setSelectedShop(shopList[0]);
                }
            } else {
                setStatus('error');
                toast.error('No TikTok Shops found for this account.');
            }

        } catch (error) {
            console.error('TikTok callback error:', error);
            setStatus('error');
            toast.error(error.message || 'Failed to connect with TikTok');
        }
    };

    const handleConnect = async () => {
        if (!selectedShop || !accessToken) return;

        setIsSubmitting(true);
        try {
            const config = {
                shop_id: selectedShop.shop_cipher || selectedShop.shop_id, // TikTok uses cipher
                shop_name: selectedShop.shop_name,
                access_token: accessToken,
                api_key: accessToken,
                setup_method: 'oauth'
            };

            await integrations.create(currentProject.id, {
                provider: 'tiktok',
                config: config
            });

            toast.success(`Connected to TikTok Shop successfully!`);
            navigate('/integrations');

        } catch (error) {
            console.error('Connection failed:', error);
            toast.error(error.message || 'Failed to save integration');
            setIsSubmitting(false);
        }
    };

    if (status === 'processing') {
        return (
            <div className="min-h-screen flex items-center justify-center bg-dark-950">
                <div className="text-center">
                    <div className="w-16 h-16 border-4 border-pink-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                    <h2 className="text-xl font-semibold text-white">Connecting to TikTok Shop...</h2>
                    <p className="text-gray-400">Exchanging tokens and fetching shops</p>
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
                        We couldn't connect your TikTok account. Please try again.
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
                    <div className="w-12 h-12 rounded-xl flex items-center justify-center bg-gradient-to-br from-pink-500 to-cyan-500">
                        <ShoppingBag className="w-6 h-6 text-white" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold text-white">Select Shop to Connect</h1>
                        <p className="text-gray-400">
                            Choose the TikTok Shop you want to integrate
                        </p>
                    </div>
                </div>

                <div className="grid grid-cols-1 gap-4 mb-8 max-h-[400px] overflow-y-auto pr-2">
                    {shops.map((shop) => (
                        <motion.div
                            key={shop.shop_id || shop.shop_cipher}
                            whileHover={{ scale: 1.01 }}
                            whileTap={{ scale: 0.99 }}
                            onClick={() => setSelectedShop(shop)}
                            className={`p-4 rounded-xl border cursor-pointer transition-all ${selectedShop?.shop_id === shop.shop_id
                                ? 'bg-pink-600/20 border-pink-500'
                                : 'bg-white/5 border-white/10 hover:bg-white/10'
                                }`}
                        >
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 rounded-full flex items-center justify-center font-bold bg-pink-500/20 text-pink-400">
                                        <ShoppingBag className="w-5 h-5" />
                                    </div>
                                    <div>
                                        <h3 className="font-semibold text-white">
                                            {shop.shop_name}
                                        </h3>
                                        <p className="text-xs text-gray-400">
                                            Shop ID: {shop.shop_cipher || shop.shop_id}
                                        </p>
                                    </div>
                                </div>
                                {selectedShop?.shop_id === shop.shop_id && (
                                    <CheckCircle className="w-6 h-6 text-pink-500" />
                                )}
                            </div>
                        </motion.div>
                    ))}
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
                        disabled={!selectedShop || isSubmitting}
                        className="flex-1 px-6 py-3 rounded-xl font-medium transition-all duration-300 shadow-neon disabled:opacity-50 disabled:cursor-not-allowed bg-accent-500 hover:bg-accent-600 text-white"
                    >
                        {isSubmitting ? 'Connecting...' : 'Connect Selected Shop'}
                    </button>
                </div>
            </GlassCard>
        </div>
    );
}
