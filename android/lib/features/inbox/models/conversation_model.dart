/// Domain model for conversation summaries in the Unified Inbox.
class ConversationModel {
  final String id;
  final String channel;
  final String? customerName;
  final String? customerEmail;
  final String? customerPhone;
  final String? customerAvatar;
  final String? customerId;
  final String? profileId;
  final String? orderId;
  final String? lastMessage;
  final DateTime? lastMessageAt;
  final int unreadCount;
  final int totalMessages;
  final bool aiEnabled;
  final String? overallSentiment;
  final bool isVip;

  const ConversationModel({
    required this.id,
    required this.channel,
    this.customerName,
    this.customerEmail,
    this.customerPhone,
    this.customerAvatar,
    this.customerId,
    this.profileId,
    this.orderId,
    this.lastMessage,
    this.lastMessageAt,
    this.unreadCount = 0,
    this.totalMessages = 0,
    this.aiEnabled = true,
    this.overallSentiment,
    this.isVip = false,
  });

  factory ConversationModel.fromJson(Map<String, dynamic> json) {
    return ConversationModel(
      id: json['id']?.toString() ?? '',
      channel: json['channel']?.toString() ?? 'chat',
      customerName: json['customer_name']?.toString(),
      customerEmail: json['customer_email']?.toString(),
      customerPhone: json['customer_phone']?.toString(),
      customerAvatar: json['customer_avatar']?.toString(),
      customerId: json['customer_id']?.toString(),
      profileId: json['profile_id']?.toString(),
      orderId: json['order_id']?.toString(),
      lastMessage: json['last_message']?.toString(),
      lastMessageAt: json['last_message_at'] != null
          ? DateTime.tryParse(json['last_message_at'].toString())
          : null,
      unreadCount: (json['unread_count'] as num?)?.toInt() ?? 0,
      totalMessages: (json['total_messages'] as num?)?.toInt() ?? 0,
      aiEnabled: json['ai_enabled'] != false,
      overallSentiment: json['overall_sentiment']?.toString(),
      isVip: json['is_vip'] == true,
    );
  }

  ConversationModel copyWith({
    bool? aiEnabled,
    int? unreadCount,
    String? lastMessage,
    DateTime? lastMessageAt,
  }) {
    return ConversationModel(
      id: id,
      channel: channel,
      customerName: customerName,
      customerEmail: customerEmail,
      customerPhone: customerPhone,
      customerAvatar: customerAvatar,
      customerId: customerId,
      profileId: profileId,
      orderId: orderId,
      lastMessage: lastMessage ?? this.lastMessage,
      lastMessageAt: lastMessageAt ?? this.lastMessageAt,
      unreadCount: unreadCount ?? this.unreadCount,
      totalMessages: totalMessages,
      aiEnabled: aiEnabled ?? this.aiEnabled,
      overallSentiment: overallSentiment,
      isVip: isVip,
    );
  }

  String get displayName =>
      (customerName != null && customerName!.trim().isNotEmpty)
          ? customerName!.trim()
          : (customerPhone ?? customerEmail ?? 'Customer');
}
