import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../../shared/widgets/empty_view.dart';
import '../../../shared/widgets/glass_card.dart';
import '../../../shared/widgets/status_badge.dart';
import '../../projects/providers/project_provider.dart';
import '../../projects/widgets/project_selector_sheet.dart';

/// Social Media management and auto-reply monitoring screen.
class SocialMediaScreen extends ConsumerWidget {
  const SocialMediaScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final activeProject = ref.watch(activeProjectProvider);

    if (activeProject == null) {
      return Scaffold(
        backgroundColor: AppColors.bgDark,
        appBar: AppBar(title: const Text('Social Media & Auto-Reply')),
        body: EmptyView(
          title: 'No workspace selected',
          subtitle: 'Select a workspace to manage connected social channels.',
          actionText: 'Select Workspace',
          onAction: () => ProjectSelectorSheet.show(context),
        ),
      );
    }

    return Scaffold(
      backgroundColor: AppColors.bgDark,
      appBar: AppBar(
        title: const Text('Social Media & Auto-Reply'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _buildMetricsOverview(),
          const SizedBox(height: 20),
          Text(
            'CONNECTED ACCOUNTS',
            style: AppTypography.caption.copyWith(
              fontWeight: FontWeight.w700,
              letterSpacing: 1.2,
            ),
          ),
          const SizedBox(height: 12),
          _buildAccountCard(
            name: 'Meta Business Page',
            channel: 'Facebook & Instagram',
            icon: Icons.facebook_rounded,
            color: const Color(0xFF1877F2),
            isConnected: true,
            autoReplyEnabled: true,
          ),
          const SizedBox(height: 12),
          _buildAccountCard(
            name: 'TikTok Commercial Profile',
            channel: 'TikTok Video Comments',
            icon: Icons.music_note_rounded,
            color: const Color(0xFF00F2FE),
            isConnected: false,
            autoReplyEnabled: false,
          ),
          const SizedBox(height: 24),
          Text(
            'RECENT AUTO-RESPONSES',
            style: AppTypography.caption.copyWith(
              fontWeight: FontWeight.w700,
              letterSpacing: 1.2,
            ),
          ),
          const SizedBox(height: 12),
          _buildRecentCommentCard(
            author: 'Amr Hassan',
            post: 'Automind Enterprise Announcement',
            comment: 'How much is the annual subscription?',
            aiReply:
                'Hello Amr! Our Pro plan is \$49/mo, or \$39/mo billed annually. Check automio.online/pricing!',
            timeAgo: '12m ago',
          ),
        ],
      ),
    );
  }

  Widget _buildMetricsOverview() {
    return Row(
      children: [
        Expanded(
          child: GlassCard(
            padding: const EdgeInsets.all(14),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('TOTAL COMMENTS', style: AppTypography.caption),
                const SizedBox(height: 4),
                Text('1,248', style: AppTypography.numericLarge),
              ],
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: GlassCard(
            padding: const EdgeInsets.all(14),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('AUTO-REPLIED', style: AppTypography.caption),
                const SizedBox(height: 4),
                Text('94.2%',
                    style: AppTypography.numericLarge
                        .copyWith(color: AppColors.success)),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildAccountCard({
    required String name,
    required String channel,
    required IconData icon,
    required Color color,
    required bool isConnected,
    required bool autoReplyEnabled,
  }) {
    return GlassCard(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(icon, color: color, size: 24),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(name, style: AppTypography.cardTitle),
                const SizedBox(height: 2),
                Text(channel, style: AppTypography.caption),
              ],
            ),
          ),
          StatusBadge(
            label: isConnected ? 'CONNECTED' : 'DISCONNECTED',
            variant: isConnected ? BadgeVariant.success : BadgeVariant.neutral,
          ),
        ],
      ),
    );
  }

  Widget _buildRecentCommentCard({
    required String author,
    required String post,
    required String comment,
    required String aiReply,
    required String timeAgo,
  }) {
    return GlassCard(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(author,
                  style: AppTypography.sectionTitle.copyWith(fontSize: 14)),
              Text(timeAgo, style: AppTypography.caption),
            ],
          ),
          const SizedBox(height: 4),
          Text('Post: $post',
              style: AppTypography.caption
                  .copyWith(color: AppColors.brandPrimary)),
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: AppColors.surfaceElevated,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Customer: "$comment"',
                    style: AppTypography.bodySecondary),
                const SizedBox(height: 6),
                Text('🤖 AI Reply: "$aiReply"',
                    style: AppTypography.bodySecondary
                        .copyWith(color: AppColors.textPrimary)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
