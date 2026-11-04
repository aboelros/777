import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../../shared/utils/formatters.dart';
import '../../../shared/widgets/glass_card.dart';
import '../../../shared/widgets/status_badge.dart';
import '../models/conversation_model.dart';

/// List tile representing a conversation thread in the inbox.
class ConversationTile extends StatelessWidget {
  final ConversationModel conversation;
  final VoidCallback onTap;

  const ConversationTile({
    super.key,
    required this.conversation,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      onTap: onTap,
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildAvatar(),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Text(
                        conversation.displayName,
                        style: AppTypography.cardTitle,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    Text(
                      AppFormatters.timeOnly(conversation.lastMessageAt),
                      style: AppTypography.caption,
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  conversation.lastMessage ?? 'No messages yet',
                  style: AppTypography.bodySecondary.copyWith(
                    color: conversation.unreadCount > 0
                        ? AppColors.textPrimary
                        : AppColors.textSecondary,
                    fontWeight: conversation.unreadCount > 0
                        ? FontWeight.w500
                        : FontWeight.w400,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    _buildChannelBadge(conversation.channel),
                    const SizedBox(width: 8),
                    StatusBadge(
                      label: conversation.aiEnabled
                          ? 'AI Active'
                          : 'Human Takeover',
                      variant: conversation.aiEnabled
                          ? BadgeVariant.info
                          : BadgeVariant.warning,
                      showDot: true,
                    ),
                    const Spacer(),
                    if (conversation.unreadCount > 0)
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: AppColors.brandPrimary,
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: Text(
                          conversation.unreadCount.toString(),
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 11,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAvatar() {
    return Container(
      width: 44,
      height: 44,
      decoration: BoxDecoration(
        color: AppColors.surfaceElevated,
        shape: BoxShape.circle,
        border: Border.all(color: AppColors.border),
      ),
      child: Center(
        child: Text(
          conversation.displayName.isNotEmpty
              ? conversation.displayName[0].toUpperCase()
              : '?',
          style:
              AppTypography.cardTitle.copyWith(color: AppColors.brandPrimary),
        ),
      ),
    );
  }

  Widget _buildChannelBadge(String channel) {
    Color color = AppColors.textSecondary;
    IconData icon = Icons.chat_rounded;

    if (channel.toLowerCase().contains('whatsapp')) {
      color = const Color(0xFF25D366);
      icon = Icons.message_rounded;
    } else if (channel.toLowerCase().contains('meta') ||
        channel.toLowerCase().contains('facebook') ||
        channel.toLowerCase().contains('instagram')) {
      color = const Color(0xFF1877F2);
      icon = Icons.share_rounded;
    } else if (channel.toLowerCase().contains('telegram')) {
      color = const Color(0xFF0088CC);
      icon = Icons.send_rounded;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 12, color: color),
          const SizedBox(width: 4),
          Text(
            channel.toUpperCase(),
            style: TextStyle(
              color: color,
              fontSize: 10,
              fontWeight: FontWeight.w700,
            ),
          ),
        ],
      ),
    );
  }
}
