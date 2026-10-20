import { useState } from 'react';
import { Shield, Copy, Check, Download, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';
import GlassCard from '@/components/ui/GlassCard';
import Button from '@/components/ui/Button';
import { useTranslation } from '@/lib/translations';

export default function TwoFactorBackupCodes({ backupCodes, onComplete }) {
  const [copiedCodes, setCopiedCodes] = useState(false);
  const { t } = useTranslation();

  const copyBackupCodes = () => {
    navigator.clipboard.writeText(backupCodes.join('\n'));
    setCopiedCodes(true);
    toast.success('Backup codes copied');
    setTimeout(() => setCopiedCodes(false), 2000);
  };

  const downloadBackupCodes = () => {
    const blob = new Blob([backupCodes.join('\n')], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'automind-2fa-backup-codes.txt';
    a.click();
    toast.success('Backup codes downloaded');
  };

  return (
    <GlassCard className="p-6 rounded-2xl border border-border">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
          <Check className="w-6 h-6" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-text-primary">Two-Factor Enabled</h2>
          <p className="text-xs text-text-muted">Save these recovery codes in a secure location</p>
        </div>
      </div>

      <div className="space-y-4 mb-6">
        <div className="p-4 bg-amber-500/10 border border-amber-500/20 rounded-xl text-xs text-amber-400 flex gap-2.5">
          <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
          <p>Each code can only be used once. Store them in a secure password manager.</p>
        </div>

        <div className="p-4 bg-surface-subtle border border-border rounded-xl">
          <div className="grid grid-cols-2 gap-2 font-mono text-xs text-text-primary">
            {backupCodes.map((code, index) => (
              <div key={index} className="px-3 py-1.5 bg-surface border border-border rounded-lg text-center">
                {code}
              </div>
            ))}
          </div>
        </div>

        <div className="flex gap-2">
          <Button onClick={copyBackupCodes} variant="secondary" size="sm" className="flex-1" leftIcon={copiedCodes ? Check : Copy}>
            {copiedCodes ? 'Copied' : 'Copy All'}
          </Button>
          <Button onClick={downloadBackupCodes} variant="secondary" size="sm" className="flex-1" leftIcon={Download}>
            Download (.txt)
          </Button>
        </div>
      </div>

      <Button onClick={onComplete} variant="primary" className="w-full">
        Complete Setup
      </Button>
    </GlassCard>
  );
}
