import 'package:flutter_test/flutter_test.dart';
import 'package:automind/features/inbox/models/conversation_model.dart';
import 'package:automind/features/inbox/models/message_model.dart';

void main() {
  group('Inbox & Message Models', () {
    test('ConversationModel fromJson maps fields and takeover flag', () {
      final json = {
        'id': 'conv-101',
        'channel': 'whatsapp',
        'customer_name': 'Omar Sharif',
        'customer_phone': '+201012345678',
        'last_message': 'Order confirmed',
        'unread_count': 3,
        'ai_enabled': false,
        'is_vip': true,
      };

      final conv = ConversationModel.fromJson(json);
      expect(conv.id, 'conv-101');
      expect(conv.channel, 'whatsapp');
      expect(conv.displayName, 'Omar Sharif');
      expect(conv.unreadCount, 3);
      expect(conv.aiEnabled, false); // Human Takeover active
      expect(conv.isVip, true);
    });

    test('MessageModel calculates direction properly', () {
      final inbound = MessageModel(
        id: 'm-1',
        direction: 'inbound',
        provider: 'meta',
        content: 'Hi',
        createdAt: DateTime.now(),
      );
      expect(inbound.isInbound, true);
      expect(inbound.isOutbound, false);

      final outbound = MessageModel(
        id: 'm-2',
        direction: 'outbound',
        provider: 'meta',
        content: 'Hello, how can I help?',
        createdAt: DateTime.now(),
        aiGenerated: true,
      );
      expect(outbound.isInbound, false);
      expect(outbound.isOutbound, true);
      expect(outbound.aiGenerated, true);
    });
  });
}
