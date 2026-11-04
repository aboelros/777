import 'package:flutter/material.dart';
import '../../../core/localization/app_localizations.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../../shared/utils/formatters.dart';
import '../../../shared/widgets/glass_card.dart';
import '../models/dashboard_stats_model.dart';

/// 6-KPI metrics grid matching the web platform dashboard.
class DashboardKpiGrid extends StatelessWidget {
  final PeriodMetrics metrics;
  final VoidCallback onOrdersTap;
  final VoidCallback onInboxTap;
  final VoidCallback? onProductsTap;
  final VoidCallback? onSocialTap;

  const DashboardKpiGrid({
    super.key,
    required this.metrics,
    required this.onOrdersTap,
    required this.onInboxTap,
    this.onProductsTap,
    this.onSocialTap,
  });

  @override
  Widget build(BuildContext context) {
    return GridView.count(
      crossAxisCount: 2,
      crossAxisSpacing: 10,
      mainAxisSpacing: 10,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      childAspectRatio: 1.25,
      children: [
        _buildKpiCard(
          title: context.tr('totalRevenue'),
          value: AppFormatters.currency(metrics.revenue),
          change: '+24.5%',
          icon: Icons.payments_rounded,
          color: const Color(0xFF38BDF8),
        ),
        _buildKpiCard(
          title: context.tr('totalOrders'),
          value: metrics.orders.toString(),
          change: '+18.9%',
          icon: Icons.shopping_bag_rounded,
          color: const Color(0xFF10B981),
          onTap: onOrdersTap,
        ),
        _buildKpiCard(
          title: context.tr('conversations'),
          value: metrics.messages.toString(),
          subValue: '${metrics.escalations} ${context.tr('unreadInquiries')}',
          icon: Icons.chat_bubble_rounded,
          color: const Color(0xFF60A5FA),
          onTap: onInboxTap,
        ),
        _buildKpiCard(
          title: context.tr('catalogItems'),
          value: '16',
          subValue: '12 ${context.tr('availableInStock')}',
          icon: Icons.inventory_2_rounded,
          color: const Color(0xFF818CF8),
          onTap: onProductsTap,
        ),
        _buildKpiCard(
          title: context.tr('socialReach'),
          value: '1.4k',
          subValue: context.tr('connected'),
          icon: Icons.tag_rounded,
          color: const Color(0xFFFBBF24),
          onTap: onSocialTap,
        ),
        _buildKpiCard(
          title: context.tr('activeChannels'),
          value: '3',
          subValue: context.tr('allSystemsOperational'),
          icon: Icons.hub_rounded,
          color: const Color(0xFF34D399),
        ),
      ],
    );
  }

  Widget _buildKpiCard({
    required String title,
    required String value,
    String? change,
    String? subValue,
    required IconData icon,
    required Color color,
    VoidCallback? onTap,
  }) {
    return GlassCard(
      onTap: onTap,
      padding: const EdgeInsets.all(12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Container(
                padding: const EdgeInsets.all(6),
                decoration: BoxDecoration(
                  color: color.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(icon, color: color, size: 16),
              ),
              if (change != null)
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: const Color(0xFF10B981).withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(6),
                    border: Border.all(
                      color: const Color(0xFF10B981).withValues(alpha: 0.3),
                    ),
                  ),
                  child: Text(
                    change,
                    style: const TextStyle(
                      color: Color(0xFF34D399),
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
            ],
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                value,
                style: AppTypography.pageTitle.copyWith(
                  fontSize: 18,
                  fontWeight: FontWeight.w800,
                  color: Colors.white,
                ),
              ),
              const SizedBox(height: 1),
              Text(
                title,
                style: AppTypography.caption.copyWith(
                  fontSize: 11,
                  color: AppColors.textSecondary,
                  fontWeight: FontWeight.w500,
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
              if (subValue != null)
                Text(
                  subValue,
                  style: TextStyle(
                    fontSize: 9,
                    color: AppColors.textMuted.withValues(alpha: 0.8),
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
            ],
          ),
        ],
      ),
    );
  }
}
