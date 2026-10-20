import { useState } from 'react';
import { Shield, Copy, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';
import GlassCard from '@/components/ui/GlassCard';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import { useTranslation } from '@/lib/translations';
import TwoFactorBackupCodes from './twofactor/TwoFactorBackupCodes';

export default function TwoFactorSetup({ onComplete, onCancel }) {
  const [step, setStep] = useState(1);
  const [qrCode, setQrCode] = useState(null);
  const [secret, setSecret] = useState('');
  const [backupCodes, setBackupCodes] = useState([]);
  const [verificationCode, setVerificationCode] = useState('');
  const [loading, setLoading] = useState(false);
  const { t } = useTranslation();

  const handleSetup2FA = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/auth/2fa/setup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      const data = await response.json();
      setQrCode(data.qr_code);
      setSecret(data.secret);
      setBackupCodes(data.backup_codes || []);
      setStep(2);
    } catch {
      toast.error('Failed to initiate 2FA setup');
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async () => {
    if (verificationCode.length !== 6) {
      toast.error('Please enter a valid 6-digit code');
      return;
    }
    setLoading(true);
    try {
      const response = await fetch('/api/auth/2fa/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: verificationCode }),
      });
      if (response.ok) {
        setStep(3);
        toast.success('Two-factor authentication verified');
      } else {
        toast.error('Invalid verification code');
      }
    } catch {
      toast.error('Failed to verify token');
    } finally {
      setLoading(false);
    }
  };

  if (step === 1) {
    return (
      <GlassCard className="p-6 rounded-2xl border border-border max-w-md mx-auto">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-12 h-12 rounded-xl bg-brand-primary/10 border border-brand-primary/20 text-brand-primary flex items-center justify-center">
            <Shield className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-text-primary">Two-Factor Security</h2>
            <p className="text-xs text-text-muted">Protect your Automio account with TOTP</p>
          </div>
        </div>

        <div className="p-4 bg-surface-subtle border border-border rounded-xl text-xs text-text-secondary space-y-2 mb-6">
          <p className="font-semibold text-text-primary">Prerequisites:</p>
          <ul className="list-disc pl-4 space-y-1 text-text-muted">
            <li>Authenticator app (Google Authenticator, 1Password, Authy)</li>
            <li>Mobile device ready to scan QR code</li>
          </ul>
        </div>

        <div className="flex gap-2">
          <Button onClick={handleSetup2FA} disabled={loading} variant="primary" className="flex-1" isLoading={loading}>
            Begin 2FA Setup
          </Button>
          <Button onClick={onCancel} variant="secondary">
            Cancel
          </Button>
        </div>
      </GlassCard>
    );
  }

  if (step === 2) {
    return (
      <GlassCard className="p-6 rounded-2xl border border-border max-w-md mx-auto space-y-5">
        <h2 className="text-xl font-bold text-text-primary">Scan QR Code</h2>
        <div className="flex flex-col items-center">
          {qrCode && (
            <img src={qrCode} alt="2FA QR Code" className="w-56 h-56 rounded-xl bg-white p-3 border border-border" />
          )}
          <p className="text-xs text-text-muted mt-3 text-center">
            Scan this barcode using your mobile authenticator application.
          </p>
        </div>

        {secret && (
          <div className="p-3 bg-surface-subtle border border-border rounded-xl flex items-center justify-between">
            <code className="text-xs font-mono text-text-primary truncate">{secret}</code>
            <Button
              onClick={() => { navigator.clipboard.writeText(secret); toast.success('Key copied'); }}
              variant="ghost"
              size="sm"
            >
              <Copy className="w-3.5 h-3.5" />
            </Button>
          </div>
        )}

        <div>
          <Input
            label="6-Digit Verification Code"
            type="text"
            maxLength={6}
            value={verificationCode}
            onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, ''))}
            placeholder="000000"
            className="text-center font-mono tracking-widest text-lg"
          />
        </div>

        <div className="flex gap-2 pt-2 border-t border-border">
          <Button onClick={handleVerify} disabled={loading || verificationCode.length !== 6} variant="primary" className="flex-1" isLoading={loading}>
            Verify & Activate
          </Button>
          <Button onClick={() => setStep(1)} variant="secondary">
            Back
          </Button>
        </div>
      </GlassCard>
    );
  }

  if (step === 3) {
    return <TwoFactorBackupCodes backupCodes={backupCodes} onComplete={onComplete} />;
  }

  return null;
}
