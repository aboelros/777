/// Integration channel status model.
class IntegrationModel {
  final String id;
  final String provider;
  final String status;
  final DateTime? createdAt;
  final Map<String, dynamic>? metadata;

  const IntegrationModel({
    required this.id,
    required this.provider,
    required this.status,
    this.createdAt,
    this.metadata,
  });

  factory IntegrationModel.fromJson(Map<String, dynamic> json) {
    return IntegrationModel(
      id: json['id']?.toString() ?? '',
      provider: json['provider']?.toString() ?? 'generic',
      status: json['status']?.toString().toLowerCase() ?? 'disconnected',
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at'].toString())
          : null,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  bool get isConnected =>
      status == 'connected' || status == 'active' || status == 'authenticated';
}
