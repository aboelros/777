/// Domain model for chat messages inside a conversation thread.
class MessageModel {
  final String id;
  final String direction; // 'inbound' or 'outbound'
  final String provider; // 'whatsapp', 'meta', 'telegram'
  final String content;
  final DateTime createdAt;
  final bool aiGenerated;
  final bool isRead;
  final String? status;
  final Map<String, dynamic>? metadata;

  const MessageModel({
    required this.id,
    required this.direction,
    required this.provider,
    required this.content,
    required this.createdAt,
    this.aiGenerated = false,
    this.isRead = false,
    this.status,
    this.metadata,
  });

  factory MessageModel.fromJson(Map<String, dynamic> json) {
    return MessageModel(
      id: json['id']?.toString() ?? '',
      direction: json['direction']?.toString() ?? 'inbound',
      provider: json['provider']?.toString() ?? 'chat',
      content: json['content']?.toString() ?? '',
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at'].toString()) ?? DateTime.now()
          : DateTime.now(),
      aiGenerated: json['ai_generated'] == true,
      isRead: json['is_read'] == true,
      status: json['status']?.toString(),
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  bool get isInbound => direction.toLowerCase() == 'inbound';
  bool get isOutbound => !isInbound;
}
