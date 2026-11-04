/// Period-scoped metric aggregate from `/api/v1/reports/{project_id}/dashboard-summary`.
class PeriodMetrics {
  final int orders;
  final double revenue;
  final int messages;
  final int escalations;

  const PeriodMetrics({
    this.orders = 0,
    this.revenue = 0.0,
    this.messages = 0,
    this.escalations = 0,
  });

  factory PeriodMetrics.fromJson(Map<String, dynamic>? json) {
    if (json == null) return const PeriodMetrics();
    return PeriodMetrics(
      orders: (json['orders'] as num?)?.toInt() ?? 0,
      revenue: (json['revenue'] as num?)?.toDouble() ?? 0.0,
      messages: (json['messages'] as num?)?.toInt() ?? 0,
      escalations: (json['escalations'] as num?)?.toInt() ?? 0,
    );
  }
}

/// Comprehensive multi-period dashboard metrics model.
class DashboardStatsModel {
  final PeriodMetrics today;
  final PeriodMetrics yesterday;
  final PeriodMetrics thisWeek;
  final PeriodMetrics thisMonth;
  final Map<String, dynamic>? metaStats;

  const DashboardStatsModel({
    required this.today,
    required this.yesterday,
    required this.thisWeek,
    required this.thisMonth,
    this.metaStats,
  });

  factory DashboardStatsModel.fromJson(Map<String, dynamic> json) {
    return DashboardStatsModel(
      today: PeriodMetrics.fromJson(json['today'] as Map<String, dynamic>?),
      yesterday:
          PeriodMetrics.fromJson(json['yesterday'] as Map<String, dynamic>?),
      thisWeek:
          PeriodMetrics.fromJson(json['this_week'] as Map<String, dynamic>?),
      thisMonth:
          PeriodMetrics.fromJson(json['this_month'] as Map<String, dynamic>?),
      metaStats: json['meta_stats'] as Map<String, dynamic>?,
    );
  }

  PeriodMetrics getForPeriod(String periodKey) {
    switch (periodKey) {
      case 'yesterday':
        return yesterday;
      case 'this_week':
        return thisWeek;
      case 'this_month':
        return thisMonth;
      case 'today':
      default:
        return today;
    }
  }
}
