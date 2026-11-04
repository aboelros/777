import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../../shared/utils/formatters.dart';
import '../models/message_model.dart';

/// Message bubble distinguishing inbound customer, outbound agent, and AI bot messages.
class ChatBubble extends StatelessWidget {
  final MessageModel message;

  const ChatBubble({super.key, required this.message});

  @override
  Widget build(BuildContext context) {
    final isOutbound = message.isOutbound;

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment:
            isOutbound ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          if (!isOutbound) const SizedBox(width: 8),
          Flexible(
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
              decoration: BoxDecoration(
                color: isOutbound
                    ? (message.aiGenerated
                        ? AppColors.surfaceElevated
                        : AppColors.brandPrimary)
                    : AppColors.surfaceDark,
                borderRadius: BorderRadius.only(
                  topLeft: const Radius.circular(14),
                  topRight: const Radius.circular(14),
                  bottomLeft: Radius.circular(isOutbound ? 14 : 2),
                  bottomRight: Radius.circular(isOutbound ? 2 : 14),
                ),
                border: Border.all(
                  color: isOutbound && !message.aiGenerated
                      ? Colors.transparent
                      : AppColors.border,
                ),
              ),
              child: Column(
                crossAxisAlignment: isOutbound
                    ? CrossAxisAlignment.end
                    : CrossAxisAlignment.start,
                children: [
                  if (message.aiGenerated) ...[
                    Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(Icons.auto_awesome_rounded,
                            size: 12, color: AppColors.brandLight),
                        const SizedBox(width: 4),
                        Text(
                          'AI Assistant',
                          style: AppTypography.caption.copyWith(
                            color: AppColors.brandLight,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                  ],
                  Text(
                    message.content,
                    style: AppTypography.body.copyWith(
                      color: isOutbound && !message.aiGenerated
                          ? Colors.white
                          : AppColors.textPrimary,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    AppFormatters.timeOnly(message.createdAt),
                    style: AppTypography.caption.copyWith(
                      color: isOutbound && !message.aiGenerated
                          ? Colors.white.withValues(alpha: 0.7)
                          : AppColors.textMuted,
                      fontSize: 10,
                    ),
                  ),
                ],
              ),
            ),
          ),
          if (isOutbound) const SizedBox(width: 8),
        ],
      ),
    );
  }
}
