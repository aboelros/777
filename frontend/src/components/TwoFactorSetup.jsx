/**
 * 2FA Setup Component
 * Allows users to enable two-factor authentication with QR code scanning.
 */
import { useState } from 'react';
import { motion } from 'framer-motion';
import { Shield, Copy, Check, Download, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';
import GlassCard from './GlassCard';
import { useTranslation } from '../lib/translations';

export default function TwoFactorSetup({ onComplete, onCancel }) {
    const [step, setStep] = useState(1); // 1: QR Code, 2: Verify, 3: Backup Codes
    const [qrCode, setQrCode] = useState(null);
    const [secret, setSecret] = useState('');
    const [backupCodes, setBackupCodes] = useState([]);
    const [verificationCode, setVerificationCode] = useState('');
    const [loading, setLoading] = useState(false);
    const [copiedCodes, setCopiedCodes] = useState(false);
    const { t } = useTranslation();

    const handleSetup2FA = async () => {
        setLoading(true);
        try {
            // TODO: API call to setup 2FA
            const response = await fetch('/api/auth/2fa/setup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await response.json();

            setQrCode(data.qr_code);
            setSecret(data.secret);
            setBackupCodes(data.backup_codes);
            setStep(2);
        } catch (error) {
            toast.error(t('common.error'));
        } finally {
            setLoading(false);
        }
    };

    const handleVerify = async () => {
        if (verificationCode.length !== 6) {
            toast.error(t('common.error'));
            return;
        }

        setLoading(true);
        try {
            // TODO: API call to verify 2FA
            const response = await fetch('/api/auth/2fa/verify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token: verificationCode })
            });

            if (response.ok) {
                setStep(3);
                toast.success(t('integrations.connect_success'));
            } else {
                toast.error(t('common.error'));
            }
        } catch (error) {
            toast.error(t('common.error'));
        } finally {
            setLoading(false);
        }
    };

    const copyBackupCodes = () => {
        const codesText = backupCodes.join('\n');
        navigator.clipboard.writeText(codesText);
        setCopiedCodes(true);
        toast.success(t('common.save'));
        setTimeout(() => setCopiedCodes(false), 2000);
    };

    const downloadBackupCodes = () => {
        const codesText = backupCodes.join('\n');
        const blob = new Blob([codesText], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = '2fa-backup-codes.txt';
        a.click();
        toast.success(t('common.save'));
    };

    if (step === 1) {
        return (
            <GlassCard>
                <div className="p-6">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center">
                            <Shield className="w-6 h-6 text-white" />
                        </div>
                        <div>
                            <h2 className="text-2xl font-bold">{t('settings.account')}</h2>
                            <p className="text-sm text-gray-400">{t('settings.subtitle')}</p>
                        </div>
                    </div>

                    <div className="space-y-4 mb-6">
                        <div className="flex items-start gap-3 p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                            <AlertCircle className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
                            <div className="text-sm text-gray-300">
                                <p className="font-medium text-blue-400 mb-1">What you'll need:</p>
                                <ul className="list-disc list-inside space-y-1 text-gray-400">
                                    <li>An authenticator app (Google Authenticator, Authy, etc.)</li>
                                    <li>Your smartphone or tablet</li>
                                    <li>A few minutes to complete setup</li>
                                </ul>
                            </div>
                        </div>
                    </div>

                    <div className="flex gap-3">
                        <button
                            onClick={handleSetup2FA}
                            disabled={loading}
                            className="btn-neon flex-1"
                        >
                            {loading ? t('reports.controls.generating') : t('common.active')}
                        </button>
                        <button
                            onClick={onCancel}
                            className="px-6 py-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
                        >
                            {t('common.cancel')}
                        </button>
                    </div>
                </div>
            </GlassCard>
        );
    }

    if (step === 2) {
        return (
            <GlassCard>
                <div className="p-6">
                    <h2 className="text-2xl font-bold mb-6">{t('integrations.connect_with_meta').replace('Meta', '2FA')}</h2>

                    <div className="space-y-6">
                        <div className="flex flex-col items-center">
                            {qrCode && (
                                <img
                                    src={qrCode}
                                    alt="2FA QR Code"
                                    className="w-64 h-64 rounded-lg bg-white p-4"
                                />
                            )}
                            <p className="text-sm text-gray-400 mt-4 text-center">
                                {t('settings.subtitle')}
                            </p>
                        </div>

                        <div className="p-4 bg-dark-800/50 rounded-lg">
                            <p className="text-xs text-gray-400 mb-2">Or enter this code manually:</p>
                            <div className="flex items-center gap-2">
                                <code className="flex-1 px-3 py-2 bg-dark-900 rounded font-mono text-sm">
                                    {secret}
                                </code>
                                <button
                                    onClick={() => {
                                        navigator.clipboard.writeText(secret);
                                        toast.success(t('common.save'));
                                    }}
                                    className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
                                >
                                    <Copy className="w-4 h-4" />
                                </button>
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-2">
                                {t('auth.roles.admin')}
                            </label>
                            <input
                                type="text"
                                maxLength={6}
                                value={verificationCode}
                                onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, ''))}
                                placeholder="000000"
                                className="w-full px-4 py-3 bg-dark-800 rounded-lg text-center text-2xl tracking-widest font-mono focus:outline-none focus:ring-2 focus:ring-purple-500"
                            />
                        </div>

                        <div className="flex gap-3">
                            <button
                                onClick={handleVerify}
                                disabled={loading || verificationCode.length !== 6}
                                className="btn-neon flex-1"
                            >
                                {loading ? t('reports.controls.generating') : t('common.active')}
                            </button>
                            <button
                                onClick={() => setStep(1)}
                                className="px-6 py-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
                            >
                                {t('common.cancel')}
                            </button>
                        </div>
                    </div>
                </div>
            </GlassCard>
        );
    }

    if (step === 3) {
        return (
            <GlassCard>
                <div className="p-6">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center">
                            <Check className="w-6 h-6 text-white" />
                        </div>
                        <div>
                            <h2 className="text-2xl font-bold">{t('common.save')}</h2>
                            <p className="text-sm text-gray-400">{t('settings.subtitle')}</p>
                        </div>
                    </div>

                    <div className="space-y-4 mb-6">
                        <div className="p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                            <div className="flex items-start gap-3">
                                <AlertCircle className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
                                <div className="text-sm">
                                    <p className="font-medium text-yellow-400 mb-1">Important!</p>
                                    <p className="text-gray-300">
                                        Each backup code can only be used once. Save them securely - you'll need them if you lose access to your authenticator app.
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div className="p-4 bg-dark-800/50 rounded-lg">
                            <div className="grid grid-cols-2 gap-2 font-mono text-sm">
                                {backupCodes.map((code, index) => (
                                    <div key={index} className="px-3 py-2 bg-dark-900 rounded text-center">
                                        {code}
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="flex gap-3">
                            <button
                                onClick={copyBackupCodes}
                                className="flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
                            >
                                {copiedCodes ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                                {copiedCodes ? t('common.save') : t('common.save')}
                            </button>
                            <button
                                onClick={downloadBackupCodes}
                                className="flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
                            >
                                <Download className="w-4 h-4" />
                                Download
                            </button>
                        </div>
                    </div>

                    <button
                        onClick={onComplete}
                        className="btn-neon w-full"
                    >
                        {t('common.save')}
                    </button>
                </div>
            </GlassCard>
        );
    }

    return null;
}
