import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../../shared/widgets/empty_view.dart';
import '../../../shared/widgets/glass_card.dart';
import '../../../shared/widgets/status_badge.dart';
import '../../projects/providers/project_provider.dart';
import '../../projects/widgets/project_selector_sheet.dart';

/// Automated Drip Campaigns and re-engagement sequence manager.
class CampaignsScreen extends ConsumerWidget {
  const CampaignsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final activeProject = ref.watch(activeProjectProvider);

    if (activeProject == null) {
      return Scaffold(
        backgroundColor: AppColors.bgDark,
        appBar: AppBar(title: const Text('Drip Campaigns')),
        body: EmptyView(
          title: 'No workspace selected',
          subtitle: 'Select a workspace to configure automated campaigns.',
          actionText: 'Select Workspace',
          onAction: () => ProjectSelectorSheet.show(context),
        ),
      );
    }

    return Scaffold(
      backgroundColor: AppColors.bgDark,
      appBar: AppBar(
        title: const Text('Drip Campaigns'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _buildMetricsOverview(),
          const SizedBox(height: 20),
          Text(
            'ACTIVE SEQUENCES',
            style: AppTypography.caption.copyWith(
              fontWeight: FontWeight.w700,
              letterSpacing: 1.2,
            ),
          ),
          const SizedBox(height: 12),
          _buildCampaignCard(
            name: 'Abandoned Cart Recovery',
            trigger: 'Customer leaves checkout',
            stepsCount: 3,
            isActive: true,
            conversionRate: '18.4%',
          ),
          const SizedBox(height: 12),
          _buildCampaignCard(
            name: 'Post-Purchase Satisfaction',
            trigger: 'Order status changed to Delivered',
            stepsCount: 2,
            isActive: true,
            conversionRate: '42.1%',
          ),
          const SizedBox(height: 12),
          _buildCampaignCard(
            name: 'VIP Re-engagement Offer',
            trigger: 'No orders within 30 days',
            stepsCount: 2,
            isActive: false,
            conversionRate: '8.7%',
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
                Text('TOTAL DISPATCHED', style: AppTypography.caption),
                const SizedBox(height: 4),
                Text('3,812', style: AppTypography.numericLarge),
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
                Text('AVG CONVERSION', style: AppTypography.caption),
                const SizedBox(height: 4),
                Text('23.6%',
                    style: AppTypography.numericLarge
                        .copyWith(color: AppColors.success)),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildCampaignCard({
    required String name,
    required String trigger,
    required int stepsCount,
    required bool isActive,
    required String conversionRate,
  }) {
    return GlassCard(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Text(
                  name,
                  style: AppTypography.cardTitle,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              StatusBadge(
                label: isActive ? 'RUNNING' : 'PAUSED',
                variant: isActive ? BadgeVariant.success : BadgeVariant.neutral,
              ),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            'Trigger: $trigger',
            style:
                AppTypography.caption.copyWith(color: AppColors.textSecondary),
          ),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  const Icon(Icons.linear_scale_rounded,
                      size: 16, color: AppColors.brandPrimary),
                  const SizedBox(width: 6),
                  Text('$stepsCount Sequence Steps',
                      style: AppTypography.caption),
                ],
              ),
              Text(
                'Conv: $conversionRate',
                style: AppTypography.caption.copyWith(
                  fontWeight: FontWeight.w700,
                  color: AppColors.success,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
