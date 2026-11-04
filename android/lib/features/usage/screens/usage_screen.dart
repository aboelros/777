import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../../shared/widgets/empty_view.dart';
import '../../../shared/widgets/glass_card.dart';
import '../../projects/providers/project_provider.dart';
import '../../projects/widgets/project_selector_sheet.dart';

/// Resource consumption and AI usage quota telemetry dashboard.
class UsageScreen extends ConsumerWidget {
  const UsageScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final activeProject = ref.watch(activeProjectProvider);

    if (activeProject == null) {
      return Scaffold(
        backgroundColor: AppColors.bgDark,
        appBar: AppBar(title: const Text('Resource & Quota Usage')),
        body: EmptyView(
          title: 'No workspace selected',
          subtitle: 'Select a workspace to view current resource metrics.',
          actionText: 'Select Workspace',
          onAction: () => ProjectSelectorSheet.show(context),
        ),
      );
    }

    return Scaffold(
      backgroundColor: AppColors.bgDark,
      appBar: AppBar(
        title: const Text('Resource & Quotas'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _buildPlanTierCard(),
          const SizedBox(height: 20),
          Text(
            'USAGE METERS',
            style: AppTypography.caption.copyWith(
              fontWeight: FontWeight.w700,
              letterSpacing: 1.2,
            ),
          ),
          const SizedBox(height: 12),
          _buildQuotaMeter(
            title: 'AI Messages Limit',
            used: 1420,
            total: 5000,
            unit: 'messages',
            color: AppColors.brandPrimary,
          ),
          const SizedBox(height: 14),
          _buildQuotaMeter(
            title: 'Cognitive Token Consumption',
            used: 320000,
            total: 1000000,
            unit: 'tokens',
            color: const Color(0xFF8B5CF6),
          ),
          const SizedBox(height: 14),
          _buildQuotaMeter(
            title: 'Media & Product Storage',
            used: 2.1,
            total: 10.0,
            unit: 'GB',
            color: const Color(0xFF10B981),
          ),
          const SizedBox(height: 24),
          _buildHealthStatusCard(),
        ],
      ),
    );
  }

  Widget _buildPlanTierCard() {
    return GlassCard(
      padding: const EdgeInsets.all(16),
      borderColor: AppColors.borderBrand,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('CURRENT TIER', style: AppTypography.caption),
              const SizedBox(height: 4),
              Text('PRO ACCELERATOR',
                  style: AppTypography.cardTitle
                      .copyWith(color: AppColors.brandPrimary)),
              const SizedBox(height: 4),
              Text('Cycle resets on 1st of month',
                  style: AppTypography.caption),
            ],
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
            decoration: BoxDecoration(
              color: AppColors.surfaceHighlight,
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Text('Active',
                style: TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 12)),
          ),
        ],
      ),
    );
  }

  Widget _buildQuotaMeter({
    required String title,
    required num used,
    required num total,
    required String unit,
    required Color color,
  }) {
    final percent = (used / total).clamp(0.0, 1.0);

    return GlassCard(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(title,
                  style: AppTypography.cardTitle.copyWith(fontSize: 14)),
              Text(
                '${(percent * 100).toInt()}%',
                style: AppTypography.cardTitle
                    .copyWith(color: color, fontSize: 14),
              ),
            ],
          ),
          const SizedBox(height: 8),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: percent,
              backgroundColor: AppColors.surfaceElevated,
              valueColor: AlwaysStoppedAnimation<Color>(color),
              minHeight: 6,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '$used / $total $unit utilized',
            style: AppTypography.caption,
          ),
        ],
      ),
    );
  }

  Widget _buildHealthStatusCard() {
    return GlassCard(
      padding: const EdgeInsets.all(14),
      child: Row(
        children: [
          const Icon(Icons.check_circle_rounded,
              color: AppColors.success, size: 20),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              'All AI engines & rate limiters operating nominally.',
              style: AppTypography.bodySecondary
                  .copyWith(color: AppColors.textPrimary),
            ),
          ),
        ],
      ),
    );
  }
}
