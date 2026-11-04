import 'package:flutter/material.dart';
import '../../../core/localization/app_localizations.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';

/// Horizontal segmented period selector for filtering dashboard metrics.
class PeriodSelector extends StatelessWidget {
  final String selectedPeriod;
  final ValueChanged<String> onSelected;

  const PeriodSelector({
    super.key,
    required this.selectedPeriod,
    required this.onSelected,
  });

  @override
  Widget build(BuildContext context) {
    final periods = [
      {'key': 'today', 'label': context.tr('periodToday')},
      {'key': 'yesterday', 'label': context.tr('periodYesterday')},
      {'key': 'this_week', 'label': context.tr('periodWeek')},
      {'key': 'this_month', 'label': context.tr('periodMonth')},
    ];

    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: periods.map((p) {
          final isSelected = p['key'] == selectedPeriod;
          return Padding(
            padding: const EdgeInsets.only(right: 8.0),
            child: ChoiceChip(
              label: Text(
                p['label']!,
                style: AppTypography.caption.copyWith(
                  color: isSelected ? Colors.white : AppColors.textSecondary,
                  fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
                ),
              ),
              selected: isSelected,
              selectedColor: AppColors.brandPrimary,
              backgroundColor: AppColors.surfaceElevated,
              side: BorderSide(
                color: isSelected ? AppColors.brandPrimary : AppColors.border,
              ),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
              showCheckmark: false,
              onSelected: (_) => onSelected(p['key']!),
            ),
          );
        }).toList(),
      ),
    );
  }
}
