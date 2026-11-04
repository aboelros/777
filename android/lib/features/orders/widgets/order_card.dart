import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../../shared/utils/formatters.dart';
import '../../../shared/widgets/glass_card.dart';
import '../models/order_model.dart';
import 'order_status_badge.dart';

/// Card widget summarizing an order in the orders list.
class OrderCard extends StatelessWidget {
  final OrderModel order;
  final VoidCallback onTap;

  const OrderCard({super.key, required this.order, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      onTap: onTap,
      padding: const EdgeInsets.all(14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: AppColors.surfaceElevated,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Icon(Icons.shopping_bag_outlined,
                        size: 18, color: AppColors.brandPrimary),
                  ),
                  const SizedBox(width: 10),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '#${order.externalId}',
                        style: AppTypography.cardTitle,
                      ),
                      Text(
                        AppFormatters.date(order.orderDate),
                        style: AppTypography.caption,
                      ),
                    ],
                  ),
                ],
              ),
              OrderStatusBadge(status: order.status),
            ],
          ),
          const Divider(color: AppColors.border, height: 20),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Customer', style: AppTypography.caption),
                    Text(
                      order.customerName,
                      style: AppTypography.bodySecondary
                          .copyWith(color: AppColors.textPrimary),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text('Total', style: AppTypography.caption),
                  Text(
                    AppFormatters.currency(order.total,
                        currencySymbol:
                            order.currency == 'EGP' ? 'EGP ' : '\$'),
                    style: AppTypography.numericMedium,
                  ),
                ],
              ),
            ],
          ),
        ],
      ),
    );
  }
}
