/// Customer profile domain model matching `CustomerProfileResponse`.
class CustomerProfileModel {
  final String id;
  final String? name;
  final String? email;
  final String? phone;
  final String? provider;
  final String? avatarUrl;
  final bool aiEnabled;
  final String? sentiment;
  final bool isVip;
  final Map<String, dynamic>? metadata;

  const CustomerProfileModel({
    required this.id,
    this.name,
    this.email,
    this.phone,
    this.provider,
    this.avatarUrl,
    this.aiEnabled = true,
    this.sentiment,
    this.isVip = false,
    this.metadata,
  });

  factory CustomerProfileModel.fromJson(Map<String, dynamic> json) {
    return CustomerProfileModel(
      id: json['id']?.toString() ?? '',
      name: json['name']?.toString(),
      email: json['email']?.toString(),
      phone: json['phone']?.toString(),
      provider: json['provider']?.toString(),
      avatarUrl: json['avatar_url']?.toString(),
      aiEnabled: json['ai_enabled'] != false,
      sentiment: json['sentiment']?.toString(),
      isVip: json['is_vip'] == true,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  String get displayName => (name != null && name!.trim().isNotEmpty)
      ? name!.trim()
      : (phone ?? email ?? 'Customer');
}
