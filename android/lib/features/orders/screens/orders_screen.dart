import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/localization/app_localizations.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../../shared/widgets/empty_view.dart';
import '../../../shared/widgets/error_view.dart';
import '../../../shared/widgets/skeleton_loader.dart';
import '../../projects/providers/project_provider.dart';
import '../models/order_model.dart';
import '../providers/orders_provider.dart';
import '../widgets/order_card.dart';

/// Screen listing customer orders with status filters.
class OrdersScreen extends ConsumerWidget {
  const OrdersScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final activeProject = ref.watch(activeProjectProvider);
    final ordersState = ref.watch(ordersProvider);
    final orders = ordersState.filteredOrders;

    return Scaffold(
      backgroundColor: AppColors.bgDark,
      appBar: AppBar(
        title: Text(context.tr('orders'), style: AppTypography.pageTitle),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(48),
          child: _buildStatusFilterBar(context, ref, ordersState.statusFilter),
        ),
      ),
      body: activeProject == null
          ? EmptyView(
              title: context.tr('noProject'),
              subtitle: 'Select a workspace to view customer orders.',
            )
          : ordersState.isLoading && ordersState.orders.isEmpty
              ? _buildSkeletonList()
              : ordersState.error != null && ordersState.orders.isEmpty
                  ? ErrorView(
                      message: ordersState.error,
                      onRetry: () =>
                          ref.read(ordersProvider.notifier).loadOrders(),
                    )
                  : orders.isEmpty
                      ? const EmptyView(
                          title: 'No Orders Found',
                          subtitle:
                              'Orders synced from channels will appear here.',
                          icon: Icons.shopping_bag_outlined,
                        )
                      : RefreshIndicator(
                          color: AppColors.brandPrimary,
                          backgroundColor: AppColors.surfaceElevated,
                          onRefresh: () =>
                              ref.read(ordersProvider.notifier).loadOrders(),
                          child: ListView.separated(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 16, vertical: 12),
                            itemCount: orders.length,
                            separatorBuilder: (_, __) =>
                                const SizedBox(height: 10),
                            itemBuilder: (context, index) {
                              final order = orders[index];
                              return OrderCard(
                                order: order,
                                onTap: () => _openOrderDetail(context, order),
                              );
                            },
                          ),
                        ),
    );
  }

  void _openOrderDetail(BuildContext context, OrderModel order) {
    context.push('/orders/detail', extra: order);
  }

  Widget _buildStatusFilterBar(
      BuildContext context, WidgetRef ref, String selected) {
    final statuses = [
      {'key': 'all', 'label': 'All'},
      {'key': 'pending', 'label': context.tr('statusPending')},
      {'key': 'confirmed', 'label': context.tr('statusConfirmed')},
      {'key': 'shipped', 'label': context.tr('statusShipped')},
      {'key': 'delivered', 'label': context.tr('statusDelivered')},
      {'key': 'cancelled', 'label': context.tr('statusCancelled')},
    ];

    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Row(
        children: statuses.map((s) {
          final isSelected = s['key'] == selected;
          return Padding(
            padding: const EdgeInsets.only(right: 8),
            child: ChoiceChip(
              label: Text(
                s['label']!,
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
              showCheckmark: false,
              onSelected: (_) =>
                  ref.read(ordersProvider.notifier).filterByStatus(s['key']!),
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildSkeletonList() {
    return ListView.separated(
      padding: const EdgeInsets.all(16),
      itemCount: 5,
      separatorBuilder: (_, __) => const SizedBox(height: 10),
      itemBuilder: (_, __) =>
          const SkeletonLoader(width: double.infinity, height: 110),
    );
  }
}
