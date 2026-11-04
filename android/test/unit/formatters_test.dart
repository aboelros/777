import 'package:flutter_test/flutter_test.dart';
import 'package:automind/shared/utils/formatters.dart';

void main() {
  group('AppFormatters', () {
    test('currency formats properly with default dollar symbol', () {
      expect(AppFormatters.currency(1450.5), '\$1,450.50');
      expect(AppFormatters.currency(0), '\$0.00');
      expect(AppFormatters.currency(null), '\$0.00');
    });

    test('currency formats with custom currency symbol', () {
      expect(AppFormatters.currency(500, currencySymbol: 'EGP '), 'EGP 500.00');
    });

    test('compactNumber formats large numbers', () {
      expect(AppFormatters.compactNumber(1500), '1.5K');
      expect(AppFormatters.compactNumber(0), '0');
      expect(AppFormatters.compactNumber(null), '0');
    });

    test('date formats DateTime correctly', () {
      final dt = DateTime(2026, 10, 22);
      expect(AppFormatters.date(dt), '2026-10-22');
      expect(AppFormatters.date(null), '');
    });
  });
}
