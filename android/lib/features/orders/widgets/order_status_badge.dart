import 'package:flutter/material.dart';
import '../../../shared/widgets/status_badge.dart';

/// Semantic status badge specifically configured for Order lifecycle states.
class OrderStatusBadge extends StatelessWidget {
  final String status;

  const OrderStatusBadge({super.key, required this.status});

  @override
  Widget build(BuildContext context) {
    final s = status.toLowerCase();
    BadgeVariant variant = BadgeVariant.neutral;

    switch (s) {
      case 'confirmed':
        variant = BadgeVariant.info;
        break;
      case 'shipped':
        variant = BadgeVariant.warning;
        break;
      case 'delivered':
        variant = BadgeVariant.success;
        break;
      case 'cancelled':
        variant = BadgeVariant.danger;
        break;
      case 'pending':
      default:
        variant = BadgeVariant.neutral;
        break;
    }

    return StatusBadge(
      label: status.toUpperCase(),
      variant: variant,
      showDot: true,
    );
  }
}
