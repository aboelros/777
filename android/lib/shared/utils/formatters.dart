import 'package:intl/intl.dart';

/// Formatting utilities for currency, dates, and numbers.
class AppFormatters {
  AppFormatters._();

  static String currency(num? amount, {String currencySymbol = '\$'}) {
    if (amount == null) return '${currencySymbol}0.00';
    final formatter = NumberFormat.currency(
      symbol: currencySymbol,
      decimalDigits: 2,
    );
    return formatter.format(amount);
  }

  static String compactNumber(num? value) {
    if (value == null) return '0';
    return NumberFormat.compact().format(value);
  }

  static String date(DateTime? dateTime) {
    if (dateTime == null) return '';
    return DateFormat('yyyy-MM-dd').format(dateTime.toLocal());
  }

  static String dateTime(DateTime? dateTime) {
    if (dateTime == null) return '';
    return DateFormat('MMM d, h:mm a').format(dateTime.toLocal());
  }

  static String timeOnly(DateTime? dateTime) {
    if (dateTime == null) return '';
    return DateFormat('h:mm a').format(dateTime.toLocal());
  }
}
