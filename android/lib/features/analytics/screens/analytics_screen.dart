import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../../shared/utils/formatters.dart';
import '../../../shared/widgets/glass_card.dart';
import '../../dashboard/providers/dashboard_provider.dart';

/// Detailed analytics screen featuring period comparison and visual metrics.
class AnalyticsScreen extends ConsumerWidget {
  const AnalyticsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final dashboardState = ref.watch(dashboardProvider);
    final stats = dashboardState.stats;

    return Scaffold(
      backgroundColor: AppColors.bgDark,
      appBar: AppBar(
        title: Text('Analytics & Trends', style: AppTypography.pageTitle),
      ),
      body: stats == null
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                _buildRevenueCard(stats.today.revenue, stats.yesterday.revenue),
                const SizedBox(height: 16),
                _buildConversationVolumeCard(
                  stats.today.messages,
                  stats.yesterday.messages,
                ),
                const SizedBox(height: 16),
                _buildBarChartCard(stats),
              ],
            ),
    );
  }

  Widget _buildRevenueCard(double today, double yesterday) {
    return GlassCard(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Revenue Comparison', style: AppTypography.cardTitle),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _metricColumn(
                  'Today', AppFormatters.currency(today), AppColors.success),
              _metricColumn('Yesterday', AppFormatters.currency(yesterday),
                  AppColors.textSecondary),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildConversationVolumeCard(int today, int yesterday) {
    return GlassCard(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Customer Message Activity', style: AppTypography.cardTitle),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _metricColumn('Today', '$today messages', AppColors.brandPrimary),
              _metricColumn(
                  'Yesterday', '$yesterday messages', AppColors.textSecondary),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildBarChartCard(dynamic stats) {
    return GlassCard(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Activity Breakdown', style: AppTypography.cardTitle),
          const SizedBox(height: 24),
          SizedBox(
            height: 180,
            child: BarChart(
              BarChartData(
                alignment: BarChartAlignment.spaceAround,
                maxY: 100,
                barTouchData: BarTouchData(enabled: false),
                titlesData: FlTitlesData(
                  show: true,
                  bottomTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      getTitlesWidget: (val, _) {
                        switch (val.toInt()) {
                          case 0:
                            return const Text('Orders',
                                style: AppTypography.caption);
                          case 1:
                            return const Text('Chats',
                                style: AppTypography.caption);
                          case 2:
                            return const Text('Alerts',
                                style: AppTypography.caption);
                          default:
                            return const Text('');
                        }
                      },
                    ),
                  ),
                  leftTitles: const AxisTitles(
                      sideTitles: SideTitles(showTitles: false)),
                  topTitles: const AxisTitles(
                      sideTitles: SideTitles(showTitles: false)),
                  rightTitles: const AxisTitles(
                      sideTitles: SideTitles(showTitles: false)),
                ),
                borderData: FlBorderData(show: false),
                gridData: const FlGridData(show: false),
                barGroups: [
                  BarChartGroupData(
                    x: 0,
                    barRods: [
                      BarChartRodData(
                        toY: ((stats.today.orders as int) * 5.0)
                            .clamp(10.0, 90.0),
                        color: AppColors.success,
                        width: 18,
                        borderRadius: BorderRadius.circular(4),
                      ),
                    ],
                  ),
                  BarChartGroupData(
                    x: 1,
                    barRods: [
                      BarChartRodData(
                        toY: ((stats.today.messages as int) * 2.0)
                            .clamp(15.0, 95.0),
                        color: AppColors.brandPrimary,
                        width: 18,
                        borderRadius: BorderRadius.circular(4),
                      ),
                    ],
                  ),
                  BarChartGroupData(
                    x: 2,
                    barRods: [
                      BarChartRodData(
                        toY: ((stats.today.escalations as int) * 10.0)
                            .clamp(5.0, 80.0),
                        color: AppColors.warning,
                        width: 18,
                        borderRadius: BorderRadius.circular(4),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _metricColumn(String label, String value, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: AppTypography.caption),
        const SizedBox(height: 4),
        Text(value, style: AppTypography.sectionTitle.copyWith(color: color)),
      ],
    );
  }
}
