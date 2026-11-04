import 'package:flutter_test/flutter_test.dart';
import 'package:automind/core/network/api_endpoints.dart';

void main() {
  group('ApiEndpoints', () {
    test('resolves auth endpoints properly', () {
      expect(ApiEndpoints.login, '/api/v1/auth/login');
      expect(ApiEndpoints.register, '/api/v1/auth/register');
      expect(ApiEndpoints.refresh, '/api/v1/auth/refresh');
      expect(ApiEndpoints.me, '/api/v1/auth/me');
    });

    test('resolves tenant scoped endpoints', () {
      const pId = 'project-xyz';
      expect(ApiEndpoints.conversations(pId),
          '/api/v1/messages/project-xyz/conversations');
      expect(ApiEndpoints.orders(pId), '/api/v1/orders/project-xyz');
      expect(ApiEndpoints.dashboardSummary(pId),
          '/api/v1/reports/project-xyz/dashboard-summary');
      expect(ApiEndpoints.toggleCustomerAi(pId, 'cust-1'),
          '/api/v1/messages/project-xyz/customers/cust-1/toggle-ai');
    });
  });
}
