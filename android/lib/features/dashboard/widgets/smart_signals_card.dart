import 'package:flutter/material.dart';
import '../../../core/localization/app_localizations.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../../shared/widgets/glass_card.dart';

/// Real-time AI Predictive Intelligence Feed matching the web Smart Signals component.
class SmartSignalsCard extends StatelessWidget {
  const SmartSignalsCard({super.key});

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(6),
                    decoration: BoxDecoration(
                      color: const Color(0xFF6366F1).withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Icon(
                      Icons.auto_awesome_rounded,
                      color: Color(0xFF818CF8),
                      size: 16,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    context.tr('smartSignals'),
                    style: AppTypography.cardTitle.copyWith(fontSize: 15),
                  ),
                ],
              ),
              Row(
                children: [
                  Container(
                    width: 6,
                    height: 6,
                    decoration: const BoxDecoration(
                      color: Color(0xFF10B981),
                      shape: BoxShape.circle,
                    ),
                  ),
                  const SizedBox(width: 5),
                  Text(
                    'STREAMING',
                    style: TextStyle(
                      color: const Color(0xFF34D399),
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                      letterSpacing: 0.8,
                    ),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 14),
          _buildSignalItem(
            title: context.tr('signalRevVelocity'),
            message: context.tr('signalRevVelocityDesc'),
            time: context.tr('justNow'),
            icon: Icons.trending_up_rounded,
            color: const Color(0xFF10B981),
          ),
          const SizedBox(height: 10),
          _buildSignalItem(
            title: context.tr('signalAnomaly'),
            message: context.tr('signalAnomalyDesc'),
            time: '15m ago',
            icon: Icons.notifications_active_rounded,
            color: const Color(0xFFF59E0B),
          ),
          const SizedBox(height: 10),
          _buildSignalItem(
            title: context.tr('signalConversion'),
            message: context.tr('signalConversionDesc'),
            time: '1h ago',
            icon: Icons.bolt_rounded,
            color: const Color(0xFF38BDF8),
          ),
          const SizedBox(height: 10),
          _buildSignalItem(
            title: context.tr('signalIntegrity'),
            message: context.tr('signalIntegrityDesc'),
            time: '2h ago',
            icon: Icons.shield_rounded,
            color: const Color(0xFF818CF8),
          ),
        ],
      ),
    );
  }

  Widget _buildSignalItem({
    required String title,
    required String message,
    required String time,
    required IconData icon,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: color.withValues(alpha: 0.2)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(6),
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(icon, color: color, size: 16),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      title,
                      style: AppTypography.cardTitle.copyWith(
                        fontSize: 12,
                        color: Colors.white,
                      ),
                    ),
                    Text(
                      time,
                      style: const TextStyle(
                        fontSize: 9,
                        color: AppColors.textMuted,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 2),
                Text(
                  message,
                  style: AppTypography.caption.copyWith(
                    fontSize: 11,
                    color: AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
