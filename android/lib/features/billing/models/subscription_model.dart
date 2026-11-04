/// Subscription and usage domain model.
class SubscriptionModel {
  final String tier;
  final String status;
  final int maxProjects;
  final int maxMessages;
  final int currentMessages;
  final DateTime? currentPeriodEnd;

  const SubscriptionModel({
    required this.tier,
    required this.status,
    this.maxProjects = 1,
    this.maxMessages = 1000,
    this.currentMessages = 0,
    this.currentPeriodEnd,
  });

  factory SubscriptionModel.fromJson(Map<String, dynamic> json) {
    return SubscriptionModel(
      tier: json['tier']?.toString().toUpperCase() ?? 'FREE',
      status: json['status']?.toString().toUpperCase() ?? 'ACTIVE',
      maxProjects: (json['max_projects'] as num?)?.toInt() ?? 1,
      maxMessages: (json['max_messages'] as num?)?.toInt() ?? 1000,
      currentMessages: (json['current_messages'] as num?)?.toInt() ?? 0,
      currentPeriodEnd: json['current_period_end'] != null
          ? DateTime.tryParse(json['current_period_end'].toString())
          : null,
    );
  }

  double get usageRatio =>
      maxMessages > 0 ? (currentMessages / maxMessages).clamp(0.0, 1.0) : 0.0;
}
