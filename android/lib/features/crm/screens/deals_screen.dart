import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../../shared/utils/formatters.dart';
import '../../../shared/widgets/empty_view.dart';
import '../../../shared/widgets/glass_card.dart';
import '../../../shared/widgets/skeleton_loader.dart';
import '../../projects/providers/project_provider.dart';
import '../../projects/widgets/project_selector_sheet.dart';
import '../models/deal_model.dart';
import '../providers/deals_provider.dart';

/// CRM Pipeline and Deals management screen matching web Kanban capabilities.
class DealsScreen extends ConsumerWidget {
  const DealsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final activeProject = ref.watch(activeProjectProvider);
    final dealsState = ref.watch(dealsProvider);

    if (activeProject == null) {
      return Scaffold(
        backgroundColor: AppColors.bgDark,
        appBar: AppBar(title: const Text('Sales Pipeline')),
        body: EmptyView(
          title: 'No workspace selected',
          subtitle: 'Select a workspace to manage CRM deals and leads.',
          actionText: 'Select Workspace',
          onAction: () => ProjectSelectorSheet.show(context),
        ),
      );
    }

    return Scaffold(
      backgroundColor: AppColors.bgDark,
      appBar: AppBar(
        title: const Text('Sales Pipeline'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            onPressed: () => ref.read(dealsProvider.notifier).fetchPipeline(),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () => ref.read(dealsProvider.notifier).fetchPipeline(),
        child: Column(
          children: [
            _buildPipelineSummaryCard(dealsState),
            _buildStageFilters(context, ref, dealsState),
            Expanded(
              child: dealsState.isLoading
                  ? const Padding(
                      padding: EdgeInsets.all(16.0),
                      child: SkeletonLoader(
                        width: double.infinity,
                        height: 120,
                      ),
                    )
                  : dealsState.filteredDeals.isEmpty
                      ? EmptyView(
                          title: 'No deals found',
                          subtitle: 'Create a deal or select another stage.',
                          icon: Icons.view_kanban_outlined,
                        )
                      : ListView.separated(
                          padding: const EdgeInsets.all(16),
                          itemCount: dealsState.filteredDeals.length,
                          separatorBuilder: (_, __) =>
                              const SizedBox(height: 12),
                          itemBuilder: (context, index) {
                            final deal = dealsState.filteredDeals[index];
                            return _buildDealCard(deal);
                          },
                        ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPipelineSummaryCard(DealsState state) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 12),
      child: GlassCard(
        padding: const EdgeInsets.all(16),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'TOTAL PIPELINE VALUE',
                  style: AppTypography.caption.copyWith(
                    fontWeight: FontWeight.w700,
                    letterSpacing: 1.2,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  AppFormatters.currency(state.totalPipelineValue),
                  style: AppTypography.numericLarge,
                ),
              ],
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: AppColors.brandPrimary.withValues(alpha: 0.15),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: AppColors.borderBrand),
              ),
              child: Text(
                '${state.deals.length} Active Deals',
                style: AppTypography.caption.copyWith(
                  color: AppColors.brandPrimary,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStageFilters(
      BuildContext context, WidgetRef ref, DealsState state) {
    return SizedBox(
      height: 38,
      child: ListView(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        children: [
          ChoiceChip(
            label: const Text('All Stages'),
            selected:
                state.selectedStageId == null || state.selectedStageId == 'all',
            onSelected: (_) =>
                ref.read(dealsProvider.notifier).selectStage(null),
          ),
          ...state.stages.map((stage) {
            final isSelected = state.selectedStageId == stage.id;
            return Padding(
              padding: const EdgeInsets.only(left: 8),
              child: ChoiceChip(
                label: Text(stage.name),
                selected: isSelected,
                onSelected: (_) =>
                    ref.read(dealsProvider.notifier).selectStage(stage.id),
              ),
            );
          }),
        ],
      ),
    );
  }

  Widget _buildDealCard(DealModel deal) {
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
                  deal.title,
                  style: AppTypography.cardTitle,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              Text(
                AppFormatters.currency(deal.value),
                style: AppTypography.sectionTitle.copyWith(
                  color: AppColors.success,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: AppColors.surfaceHighlight,
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Text(
                  deal.priority.toUpperCase(),
                  style: AppTypography.caption.copyWith(
                    fontSize: 10,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Text(
                'Win probability: ${(deal.probability * 100).toInt()}%',
                style: AppTypography.caption,
              ),
              const Spacer(),
              Text(
                AppFormatters.date(deal.createdAt),
                style: AppTypography.caption,
              ),
            ],
          ),
        ],
      ),
    );
  }
}
