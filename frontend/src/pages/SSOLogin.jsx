/**
 * SSO Login Page
 * Provides single sign-on options with Google, Microsoft, and GitHub.
 */
import { motion } from 'framer-motion';
import { Shield, Chrome, Github } from 'lucide-react';
import { toast } from 'sonner';
import GlassCard from '../components/GlassCard';

// Microsoft icon component
const MicrosoftIcon = () => (
    <svg className="w-5 h-5" viewBox="0 0 23 23" fill="currentColor">
        <path d="M0 0h11v11H0z" fill="#f25022" />
        <path d="M12 0h11v11H12z" fill="#00a4ef" />
        <path d="M0 12h11v11H0z" fill="#7fba00" />
        <path d="M12 12h11v11H12z" fill="#ffb900" />
    </svg>
);

export default function SSOLogin({ onSuccess }) {
    const handleSSOLogin = async (provider) => {
        try {
            // Generate state for CSRF protection
            const state = Math.random().toString(36).substring(7);
            sessionStorage.setItem('sso_state', state);

            // Redirect to SSO authorization URL
            const redirectUri = `${window.location.origin}/auth/sso/callback`;
            const response = await fetch(`/api/auth/sso/${provider}/authorize?redirect_uri=${encodeURIComponent(redirectUri)}&state=${state}`);
            const data = await response.json();

            if (data.authorization_url) {
                window.location.href = data.authorization_url;
            } else {
                toast.error('Failed to initiate SSO login');
            }
        } catch (error) {
            toast.error(`Failed to login with ${provider}`);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center p-6">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="w-full max-w-md"
            >
                <GlassCard>
                    <div className="p-8">
                        <div className="flex items-center justify-center mb-8">
                            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-sky-500 to-sky-600 flex items-center justify-center">
                                <Shield className="w-8 h-8 text-white" />
                            </div>
                        </div>

                        <h1 className="text-3xl font-bold text-center mb-2">Welcome Back</h1>
                        <p className="text-gray-400 text-center mb-8">
                            Sign in with your preferred provider
                        </p>

                        <div className="space-y-3">
                            {/* Google SSO */}
                            <button
                                onClick={() => handleSSOLogin('google')}
                                className="w-full flex items-center justify-center gap-3 px-6 py-3 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 transition-all group"
                            >
                                <Chrome className="w-5 h-5 text-gray-400 group-hover:text-white transition-colors" />
                                <span className="font-medium">Continue with Google</span>
                            </button>

                            {/* Microsoft SSO */}
                            <button
                                onClick={() => handleSSOLogin('microsoft')}
                                className="w-full flex items-center justify-center gap-3 px-6 py-3 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 transition-all group"
                            >
                                <MicrosoftIcon />
                                <span className="font-medium">Continue with Microsoft</span>
                            </button>

                            {/* GitHub SSO */}
                            <button
                                onClick={() => handleSSOLogin('github')}
                                className="w-full flex items-center justify-center gap-3 px-6 py-3 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 transition-all group"
                            >
                                <Github className="w-5 h-5 text-gray-400 group-hover:text-white transition-colors" />
                                <span className="font-medium">Continue with GitHub</span>
                            </button>
                        </div>

                        <div className="mt-8 pt-6 border-t border-white/10">
                            <p className="text-sm text-gray-400 text-center">
                                By continuing, you agree to our{' '}
                                <a href="/terms" className="text-sky-400 hover:text-sky-300">
                                    Terms of Service
                                </a>{' '}
                                and{' '}
                                <a href="/privacy" className="text-sky-400 hover:text-sky-300">
                                    Privacy Policy
                                </a>
                            </p>
                        </div>
                    </div>
                </GlassCard>
            </motion.div>
        </div>
    );
}
