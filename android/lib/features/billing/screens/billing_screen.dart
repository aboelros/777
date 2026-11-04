import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/localization/app_localizations.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../../shared/utils/formatters.dart';
import '../../../shared/widgets/glass_card.dart';
import '../../../shared/widgets/status_badge.dart';
import '../providers/billing_provider.dart';

/// Screen displaying active subscription plan, limits, and usage progress.
class BillingScreen extends ConsumerWidget {
  const BillingScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(billingProvider);
    final sub = state.subscription;

    return Scaffold(
      backgroundColor: AppColors.bgDark,
      appBar: AppBar(
        title: Text(context.tr('billing'), style: AppTypography.pageTitle),
      ),
      body: RefreshIndicator(
        color: AppColors.brandPrimary,
        backgroundColor: AppColors.surfaceElevated,
        onRefresh: () => ref.read(billingProvider.notifier).loadBilling(),
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            GlassCard(
              padding: const EdgeInsets.all(18),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('Current Plan', style: AppTypography.caption),
                      StatusBadge(
                        label: sub?.status ?? 'ACTIVE',
                        variant: BadgeVariant.success,
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    sub?.tier ?? 'PRO TIER',
                    style: AppTypography.pageTitle
                        .copyWith(color: AppColors.brandPrimary),
                  ),
                  if (sub?.currentPeriodEnd != null) ...[
                    const SizedBox(height: 4),
                    Text(
                      'Renews on ${AppFormatters.date(sub!.currentPeriodEnd)}',
                      style: AppTypography.caption,
                    ),
                  ],
                ],
              ),
            ),
            const SizedBox(height: 16),
            Text(context.tr('usage'), style: AppTypography.sectionTitle),
            const SizedBox(height: 12),
            GlassCard(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('AI Messages Quota', style: AppTypography.cardTitle),
                      Text(
                        '${sub?.currentMessages ?? 0} / ${sub?.maxMessages ?? 1000}',
                        style: AppTypography.caption,
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(4),
                    child: LinearProgressIndicator(
                      value: sub?.usageRatio ?? 0.25,
                      minHeight: 8,
                      backgroundColor: AppColors.surfaceElevated,
                      valueColor: const AlwaysStoppedAnimation<Color>(
                        AppColors.brandPrimary,
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  const Divider(color: AppColors.border, height: 16),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('Workspaces Allowed',
                          style: AppTypography.bodySecondary),
                      Text(
                        '${sub?.maxProjects ?? 3} Workspaces',
                        style: AppTypography.cardTitle,
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
