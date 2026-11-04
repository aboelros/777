/// Application environment and network configuration constants.
class AppConfig {
  AppConfig._();

  /// Default production API base URL.
  static const String prodApiBaseUrl =
      'https://ai-sales-bot-api-vdr6.onrender.com';

  /// Android emulator loopback host for local development.
  static const String emulatorApiBaseUrl = 'http://10.0.2.2:8000';

  /// Physical device localhost (when using adb reverse).
  static const String localDeviceApiBaseUrl = 'http://localhost:8000';

  /// Current active base URL.
  static String activeBaseUrl = prodApiBaseUrl;

  /// Default connect and receive timeouts for Dio.
  static const Duration connectTimeout = Duration(seconds: 15);
  static const Duration receiveTimeout = Duration(seconds: 15);
  static const Duration sendTimeout = Duration(seconds: 15);

  /// WebSocket base URL derivation.
  static String get webSocketBaseUrl {
    final base = activeBaseUrl.replaceFirst(RegExp(r'^http'), 'ws');
    return base;
  }
}
