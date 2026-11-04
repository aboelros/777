import 'package:flutter/material.dart';
import '../../../core/localization/app_localizations.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../../shared/widgets/status_badge.dart';

/// Banner at the top of chat thread providing Human Takeover controls.
class TakeoverBanner extends StatelessWidget {
  final bool aiEnabled;
  final VoidCallback onToggle;

  const TakeoverBanner({
    super.key,
    required this.aiEnabled,
    required this.onToggle,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      decoration: BoxDecoration(
        color: aiEnabled ? AppColors.surfaceElevated : AppColors.warningSurface,
        border: Border(
          bottom: BorderSide(
            color: aiEnabled
                ? AppColors.border
                : AppColors.warning.withValues(alpha: 0.3),
          ),
        ),
      ),
      child: Row(
        children: [
          Icon(
            aiEnabled ? Icons.smart_toy_outlined : Icons.person_rounded,
            size: 20,
            color: aiEnabled ? AppColors.brandPrimary : AppColors.warning,
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Row(
                  children: [
                    Text(
                      aiEnabled
                          ? context.tr('aiHandling')
                          : context.tr('humanControl'),
                      style: AppTypography.cardTitle.copyWith(
                        color: aiEnabled
                            ? AppColors.textPrimary
                            : AppColors.warning,
                        fontSize: 13,
                      ),
                    ),
                    const SizedBox(width: 6),
                    StatusBadge(
                      label: aiEnabled ? 'Autonomous' : 'Manual',
                      variant:
                          aiEnabled ? BadgeVariant.info : BadgeVariant.warning,
                      showDot: true,
                    ),
                  ],
                ),
                Text(
                  aiEnabled
                      ? 'AI bot responds automatically'
                      : 'AI replies are paused for this customer',
                  style: AppTypography.caption,
                ),
              ],
            ),
          ),
          const SizedBox(width: 8),
          TextButton(
            onPressed: onToggle,
            style: TextButton.styleFrom(
              backgroundColor: aiEnabled
                  ? AppColors.warning.withValues(alpha: 0.2)
                  : AppColors.brandPrimary.withValues(alpha: 0.2),
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
            ),
            child: Text(
              aiEnabled
                  ? context.tr('takeOverControl')
                  : context.tr('restoreAi'),
              style: TextStyle(
                color: aiEnabled ? AppColors.warning : AppColors.brandLight,
                fontWeight: FontWeight.w600,
                fontSize: 12,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
