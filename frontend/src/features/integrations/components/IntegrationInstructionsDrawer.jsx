import { motion } from 'framer-motion';
import { X, BookOpen } from 'lucide-react';
import Button from '@/components/ui/Button';

export default function IntegrationInstructionsDrawer({ show, integration, onClose }) {
  if (!show || !integration) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex justify-end">
      <motion.div
        initial={{ x: '100%' }}
        animate={{ x: 0 }}
        exit={{ x: '100%' }}
        className="w-full max-w-md h-full bg-surface border-l border-border p-6 flex flex-col justify-between overflow-y-auto"
      >
        <div>
          <div className="flex items-center justify-between pb-4 mb-6 border-b border-border">
            <div className="flex items-center gap-2.5">
              <BookOpen className="w-5 h-5 text-brand-primary" />
              <h2 className="text-lg font-bold text-text-primary">{integration.name} Setup Guide</h2>
            </div>
            <button onClick={onClose} className="p-2 text-text-muted hover:text-text-primary">
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="prose prose-invert prose-sm text-text-secondary leading-relaxed space-y-4">
            <p className="font-medium text-text-primary">{integration.instructions || 'Standard API integration procedure'}</p>
            <div className="p-4 rounded-xl bg-surface-subtle border border-border text-xs space-y-2">
              <p className="font-semibold text-text-primary">Prerequisites:</p>
              <ul className="list-disc pl-4 space-y-1 text-text-muted">
                <li>Active business account on platform</li>
                <li>Admin credentials with read & write webhook scopes</li>
                <li>Webhook endpoint enabled in Automind</li>
              </ul>
            </div>
          </div>
        </div>

        <div className="pt-6 border-t border-border">
          <Button onClick={onClose} variant="secondary" className="w-full">
            Done
          </Button>
        </div>
      </motion.div>
    </div>
  );
}
