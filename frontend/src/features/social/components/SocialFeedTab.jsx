import { Eye, Heart, MessageCircle, Share2 } from 'lucide-react';
import GlassCard from '@/components/ui/GlassCard';
import Badge from '@/components/ui/Badge';
import { EmptyState } from '@/components/ui/EmptyState';
import SkeletonLoader from '@/components/ui/SkeletonLoader';

export default function SocialFeedTab({ feed, isLoading, onSelectPost }) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {Array.from({ length: 6 }).map((_, i) => (
          <SkeletonLoader key={i} type="card" />
        ))}
      </div>
    );
  }

  if (!feed || feed.length === 0) {
    return (
      <EmptyState
        icon={Eye}
        title="No Feed Items Available"
        description="Connect your Instagram or Facebook business page to stream live posts and track comments."
      />
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {feed.map((post) => (
        <GlassCard
          key={post.id}
          className="rounded-2xl border border-border overflow-hidden flex flex-col justify-between hover:border-brand-primary/30 transition-all cursor-pointer group"
          onClick={() => onSelectPost && onSelectPost(post)}
        >
          {post.media_url && (
            <div className="h-48 w-full overflow-hidden bg-surface-subtle">
              <img
                src={post.media_url}
                alt={post.caption || 'Post media'}
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
              />
            </div>
          )}

          <div className="p-5 flex-1 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-2">
                <Badge variant="brand" size="sm">{post.platform}</Badge>
                <span className="text-xs text-text-muted font-mono">
                  {post.timestamp ? new Date(post.timestamp).toLocaleDateString() : ''}
                </span>
              </div>
              <p className="text-sm text-text-secondary line-clamp-3 mb-4">
                {post.caption || 'No caption'}
              </p>
            </div>

            <div className="flex items-center justify-between pt-3 border-t border-border/50 text-xs text-text-muted">
              <span className="flex items-center gap-1">
                <Heart className="w-3.5 h-3.5 text-rose-400" />
                {post.like_count || 0}
              </span>
              <span className="flex items-center gap-1">
                <MessageCircle className="w-3.5 h-3.5 text-sky-400" />
                {post.comments_count || 0} comments
              </span>
            </div>
          </div>
        </GlassCard>
      ))}
    </div>
  );
}
