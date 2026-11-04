import 'package:flutter_test/flutter_test.dart';
import 'package:automind/features/orders/models/order_model.dart';

void main() {
  group('OrderModel', () {
    test('fromJson parses order properties properly', () {
      final json = {
        'id': 'ord-123',
        'project_id': 'proj-abc',
        'external_id': 'EXT-998',
        'provider': 'whatsapp',
        'status': 'confirmed',
        'customer': {
          'name': 'Sarah Connor',
          'phone': '+1234567890',
        },
        'items': [
          {'name': 'Widget A', 'quantity': 2, 'price': 50.0},
        ],
        'total': 100.0,
        'currency': 'USD',
      };

      final order = OrderModel.fromJson(json);
      expect(order.id, 'ord-123');
      expect(order.externalId, 'EXT-998');
      expect(order.status, 'confirmed');
      expect(order.customerName, 'Sarah Connor');
      expect(order.total, 100.0);
      expect(order.items.length, 1);
    });

    test('copyWith updates status accurately', () {
      const order = OrderModel(
        id: 'ord-1',
        projectId: 'p-1',
        externalId: 'E-1',
        provider: 'direct',
        status: 'pending',
      );

      final updated = order.copyWith(status: 'shipped');
      expect(updated.status, 'shipped');
      expect(updated.id, 'ord-1');
    });
  });
}
