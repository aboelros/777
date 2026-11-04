import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/localization/app_localizations.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../../shared/widgets/empty_view.dart';
import '../../../shared/widgets/error_view.dart';
import '../../../shared/widgets/skeleton_loader.dart';
import '../../navigation/widgets/app_shell_header.dart';
import '../../projects/providers/project_provider.dart';
import '../../projects/widgets/project_selector_sheet.dart';
import '../providers/dashboard_provider.dart';
import '../widgets/dashboard_kpi_grid.dart';
import '../widgets/inventory_health_card.dart';
import '../widgets/period_selector.dart';
import '../widgets/revenue_chart_card.dart';
import '../widgets/smart_signals_card.dart';

/// Master operational dashboard screen achieving full parity with the web platform.
class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final activeProject = ref.watch(activeProjectProvider);
    final dashboardState = ref.watch(dashboardProvider);

    return Scaffold(
      backgroundColor: AppColors.bgDark,
      appBar: const AppShellHeader(),
      body: activeProject == null
          ? EmptyView(
              title: context.tr('noProject'),
              subtitle: 'Select or create a workspace to view live analytics.',
              actionText: context.tr('selectProject'),
              onAction: () => ProjectSelectorSheet.show(context),
            )
          : dashboardState.isLoading && dashboardState.stats == null
              ? _buildLoadingSkeleton()
              : dashboardState.error != null && dashboardState.stats == null
                  ? ErrorView(
                      message: dashboardState.error,
                      onRetry: () =>
                          ref.read(dashboardProvider.notifier).loadStats(),
                    )
                  : RefreshIndicator(
                      color: AppColors.brandPrimary,
                      backgroundColor: AppColors.surfaceElevated,
                      onRefresh: () =>
                          ref.read(dashboardProvider.notifier).loadStats(),
                      child: ListView(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 16, vertical: 12),
                        children: [
                          _buildWebHeader(context),
                          const SizedBox(height: 14),
                          PeriodSelector(
                            selectedPeriod: dashboardState.selectedPeriod,
                            onSelected: (p) => ref
                                .read(dashboardProvider.notifier)
                                .selectPeriod(p),
                          ),
                          const SizedBox(height: 16),
                          DashboardKpiGrid(
                            metrics: dashboardState.currentMetrics,
                            onOrdersTap: () => context.go('/orders'),
                            onInboxTap: () => context.go('/inbox'),
                            onProductsTap: () => context.push('/products'),
                            onSocialTap: () => context.push('/social-media'),
                          ),
                          const SizedBox(height: 16),
                          const RevenueChartCard(),
                          const SizedBox(height: 16),
                          const SmartSignalsCard(),
                          const SizedBox(height: 16),
                          const InventoryHealthCard(),
                          const SizedBox(height: 28),
                        ],
                      ),
                    ),
    );
  }

  Widget _buildWebHeader(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                context.tr('commandDashboard'),
                style: AppTypography.pageTitle.copyWith(fontSize: 18),
              ),
              const SizedBox(height: 2),
              Text(
                context.tr('welcomeSubtitle'),
                style: AppTypography.caption.copyWith(
                  color: AppColors.textMuted,
                  fontSize: 11,
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
        const SizedBox(width: 8),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: AppColors.brandPrimary.withValues(alpha: 0.12),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: AppColors.brandPrimary.withValues(alpha: 0.25),
            ),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 6,
                height: 6,
                decoration: const BoxDecoration(
                  color: AppColors.brandPrimary,
                  shape: BoxShape.circle,
                ),
              ),
              const SizedBox(width: 5),
              Text(
                context.tr('systemLive'),
                style: const TextStyle(
                  color: AppColors.brandPrimary,
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 0.6,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildLoadingSkeleton() {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          const SkeletonLoader(width: double.infinity, height: 40),
          const SizedBox(height: 16),
          GridView.count(
            crossAxisCount: 2,
            crossAxisSpacing: 10,
            mainAxisSpacing: 10,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            childAspectRatio: 1.25,
            children: List.generate(
              6,
              (_) => const SkeletonLoader(width: double.infinity, height: 90),
            ),
          ),
          const SizedBox(height: 16),
          const SkeletonLoader(width: double.infinity, height: 160),
        ],
      ),
    );
  }
}
