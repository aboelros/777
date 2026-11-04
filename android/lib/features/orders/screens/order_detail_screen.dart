import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/localization/app_localizations.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../../shared/utils/formatters.dart';
import '../../../shared/widgets/app_button.dart';
import '../../../shared/widgets/glass_card.dart';
import '../models/order_model.dart';
import '../providers/orders_provider.dart';
import '../widgets/order_status_badge.dart';

/// Detailed view of a customer order with status update controls.
class OrderDetailScreen extends ConsumerStatefulWidget {
  final OrderModel order;

  const OrderDetailScreen({super.key, required this.order});

  @override
  ConsumerState<OrderDetailScreen> createState() => _OrderDetailScreenState();
}

class _OrderDetailScreenState extends ConsumerState<OrderDetailScreen> {
  late OrderModel _currentOrder;
  bool _isUpdating = false;

  @override
  void initState() {
    super.initState();
    _currentOrder = widget.order;
  }

  Future<void> _changeStatus(String newStatus) async {
    setState(() => _isUpdating = true);
    final success = await ref
        .read(ordersProvider.notifier)
        .updateOrderStatus(_currentOrder.id, newStatus);

    if (success && mounted) {
      setState(() {
        _currentOrder = _currentOrder.copyWith(status: newStatus);
        _isUpdating = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Order status updated successfully')),
      );
    } else if (mounted) {
      setState(() => _isUpdating = false);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Failed to update order status')),
      );
    }
  }

  void _showStatusDialog() {
    showModalBottomSheet(
      context: context,
      backgroundColor: AppColors.surfaceDark,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) {
        final options = [
          'pending',
          'confirmed',
          'shipped',
          'delivered',
          'cancelled'
        ];
        return SafeArea(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const SizedBox(height: 16),
              Text(context.tr('updateStatus'),
                  style: AppTypography.sectionTitle),
              const SizedBox(height: 12),
              ...options.map((s) => ListTile(
                    title:
                        Text(s.toUpperCase(), style: AppTypography.cardTitle),
                    trailing: _currentOrder.status == s
                        ? const Icon(Icons.check, color: AppColors.brandPrimary)
                        : null,
                    onTap: () {
                      Navigator.pop(ctx);
                      _changeStatus(s);
                    },
                  )),
              const SizedBox(height: 16),
            ],
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bgDark,
      appBar: AppBar(
        title: Text(context.tr('orderDetails')),
        actions: [
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Center(
              child: OrderStatusBadge(status: _currentOrder.status),
            ),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _buildCustomerCard(),
          const SizedBox(height: 16),
          _buildItemsCard(),
          const SizedBox(height: 24),
          AppButton(
            text: context.tr('updateStatus'),
            isLoading: _isUpdating,
            icon: Icons.edit_note_rounded,
            onPressed: _showStatusDialog,
          ),
        ],
      ),
    );
  }

  Widget _buildCustomerCard() {
    return GlassCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Customer Information', style: AppTypography.cardTitle),
          const Divider(color: AppColors.border, height: 20),
          _row('Name', _currentOrder.customerName),
          if (_currentOrder.customer['phone'] != null) ...[
            const SizedBox(height: 8),
            _row('Phone', _currentOrder.customer['phone'].toString()),
          ],
          if (_currentOrder.customer['address'] != null) ...[
            const SizedBox(height: 8),
            _row('Address', _currentOrder.customer['address'].toString()),
          ],
          const SizedBox(height: 8),
          _row('External ID', '#${_currentOrder.externalId}'),
          const SizedBox(height: 8),
          _row('Order Date', AppFormatters.dateTime(_currentOrder.orderDate)),
        ],
      ),
    );
  }

  Widget _buildItemsCard() {
    return GlassCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(context.tr('orderItems'), style: AppTypography.cardTitle),
          const Divider(color: AppColors.border, height: 20),
          if (_currentOrder.items.isEmpty)
            Text('No item details recorded', style: AppTypography.caption)
          else
            ..._currentOrder.items.map((item) {
              final name = item['name']?.toString() ?? 'Item';
              final qty = item['quantity']?.toString() ?? '1';
              final price = (item['price'] as num?)?.toDouble() ?? 0.0;
              return Padding(
                padding: const EdgeInsets.symmetric(vertical: 4),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('$qty x $name', style: AppTypography.body),
                    Text(AppFormatters.currency(price),
                        style: AppTypography.numericMedium),
                  ],
                ),
              );
            }),
          const Divider(color: AppColors.border, height: 20),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(context.tr('total'), style: AppTypography.sectionTitle),
              Text(
                AppFormatters.currency(_currentOrder.total,
                    currencySymbol:
                        _currentOrder.currency == 'EGP' ? 'EGP ' : '\$'),
                style: AppTypography.numericLarge
                    .copyWith(color: AppColors.brandPrimary),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _row(String label, String value) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: AppTypography.bodySecondary),
        Text(value, style: AppTypography.cardTitle),
      ],
    );
  }
}
