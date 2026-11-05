import { MessageSquare, Sparkles, Send, CheckCircle, Clock } from 'lucide-react';
import GlassCard from '@/components/ui/GlassCard';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import { EmptyState } from '@/components/ui/EmptyState';
import SkeletonLoader from '@/components/ui/SkeletonLoader';
import { useTranslation } from '@/lib/translations';

export default function SocialCommentsTab({
  comments,
  isLoading,
  onGenerateResponse,
  onSendResponse,
  generatingFor,
}) {
  const { t } = useTranslation();

  if (isLoading) {
    return (
      <div className="space-y-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <SkeletonLoader key={i} type="card" />
        ))}
      </div>
    );
  }

  if (comments.length === 0) {
    return (
      <EmptyState
        icon={MessageSquare}
        title={t('social.comments.empty_title') || 'No Social Comments'}
        description={t('social.comments.empty_desc') || 'New comments and direct inquiries from Instagram and Facebook will appear here for automated triage.'}
      />
    );
  }

  return (
    <div className="space-y-4">
      {comments.map((comment) => (
        <GlassCard key={comment.id} className="p-5 rounded-2xl border border-border">
          <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3 mb-3">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="font-bold text-text-primary text-sm">{comment.author_name || comment.author_username || 'Customer'}</span>
                <Badge variant="brand" size="sm">{comment.platform}</Badge>
                {comment.responded ? (
                  <Badge variant="success" size="sm">Replied</Badge>
                ) : (
                  <Badge variant="warning" size="sm">Awaiting Reply</Badge>
                )}
              </div>
              <p className="text-xs text-text-muted font-mono">{comment.created_at ? new Date(comment.created_at).toLocaleString() : ''}</p>
            </div>

            <div className="flex items-center gap-2">
              <Button
                onClick={() => onGenerateResponse(comment.id)}
                disabled={generatingFor === comment.id}
                variant="primary"
                size="sm"
                leftIcon={Sparkles}
              >
                {generatingFor === comment.id ? 'Generating...' : 'AI Auto-Draft'}
              </Button>
            </div>
          </div>

          <div className="p-3.5 bg-surface-subtle border border-border rounded-xl text-sm text-text-secondary leading-relaxed">
            "{comment.text || comment.content}"
          </div>

          {(comment.response_text || comment.response_content) && (
            <div className="mt-3 p-3 bg-brand-primary/5 border border-brand-primary/20 rounded-xl text-xs text-brand-primary">
              <span className="font-bold block mb-1">Sent Reply:</span>
              {comment.response_text || comment.response_content}
            </div>
          )}
        </GlassCard>
      ))}
    </div>
  );
}
