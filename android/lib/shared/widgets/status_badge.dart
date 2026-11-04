import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';

enum BadgeVariant { success, warning, danger, info, neutral }

/// Status badge indicator with optional pulsing dot.
class StatusBadge extends StatelessWidget {
  final String label;
  final BadgeVariant variant;
  final bool showDot;

  const StatusBadge({
    super.key,
    required this.label,
    this.variant = BadgeVariant.neutral,
    this.showDot = false,
  });

  @override
  Widget build(BuildContext context) {
    final colors = _resolveColors();

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: colors.surface,
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: colors.border, width: 1),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (showDot) ...[
            Container(
              width: 6,
              height: 6,
              decoration: BoxDecoration(
                color: colors.foreground,
                shape: BoxShape.circle,
              ),
            ),
            const SizedBox(width: 6),
          ],
          Text(
            label,
            style: AppTypography.caption.copyWith(
              color: colors.foreground,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  ({Color surface, Color foreground, Color border}) _resolveColors() {
    switch (variant) {
      case BadgeVariant.success:
        return (
          surface: AppColors.successSurface,
          foreground: AppColors.success,
          border: AppColors.success.withValues(alpha: 0.3),
        );
      case BadgeVariant.warning:
        return (
          surface: AppColors.warningSurface,
          foreground: AppColors.warning,
          border: AppColors.warning.withValues(alpha: 0.3),
        );
      case BadgeVariant.danger:
        return (
          surface: AppColors.dangerSurface,
          foreground: AppColors.danger,
          border: AppColors.danger.withValues(alpha: 0.3),
        );
      case BadgeVariant.info:
        return (
          surface: AppColors.infoSurface,
          foreground: AppColors.info,
          border: AppColors.info.withValues(alpha: 0.3),
        );
      case BadgeVariant.neutral:
        return (
          surface: AppColors.surfaceElevated,
          foreground: AppColors.textSecondary,
          border: AppColors.border,
        );
    }
  }
}
