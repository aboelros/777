import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../config/app_config.dart';

/// Real-time client connecting to Automind's `/ws/{project_id}` WebSocket channel.
class WebSocketClient {
  WebSocketChannel? _channel;
  StreamSubscription? _subscription;
  Timer? _reconnectTimer;
  Timer? _pingTimer;

  String? _currentProjectId;
  bool _isClosedManually = false;
  int _reconnectAttempts = 0;

  final void Function(Map<String, dynamic> event) onEvent;
  final void Function(bool isConnected)? onConnectionChanged;

  WebSocketClient({
    required this.onEvent,
    this.onConnectionChanged,
  });

  void connect(String projectId) {
    if (_currentProjectId == projectId && _channel != null) return;

    disconnect();
    _currentProjectId = projectId;
    _isClosedManually = false;
    _reconnectAttempts = 0;

    _establishConnection();
  }

  void _establishConnection() {
    if (_isClosedManually || _currentProjectId == null) return;

    try {
      final wsUrl = '${AppConfig.webSocketBaseUrl}/ws/$_currentProjectId';
      final uri = Uri.parse(wsUrl);

      _channel = WebSocketChannel.connect(uri);
      onConnectionChanged?.call(true);

      _subscription = _channel?.stream.listen(
        (data) {
          try {
            if (data is String) {
              final json = jsonDecode(data);
              if (json is Map<String, dynamic>) {
                onEvent(json);
              }
            }
          } catch (_) {}
        },
        onError: (_) {
          _handleDisconnect();
        },
        onDone: () {
          _handleDisconnect();
        },
        cancelOnError: true,
      );

      // Start ping heartbeat every 30 seconds
      _pingTimer?.cancel();
      _pingTimer = Timer.periodic(const Duration(seconds: 30), (_) {
        sendPing();
      });
    } catch (_) {
      _handleDisconnect();
    }
  }

  void sendPing() {
    try {
      _channel?.sink.add('ping');
    } catch (_) {}
  }

  void _handleDisconnect() {
    onConnectionChanged?.call(false);
    _cleanupChannel();

    if (!_isClosedManually && _currentProjectId != null) {
      _scheduleReconnect();
    }
  }

  void _scheduleReconnect() {
    _reconnectTimer?.cancel();
    _reconnectAttempts++;
    final delaySeconds = (_reconnectAttempts * 2).clamp(2, 30);

    _reconnectTimer = Timer(Duration(seconds: delaySeconds), () {
      _establishConnection();
    });
  }

  void _cleanupChannel() {
    _pingTimer?.cancel();
    _subscription?.cancel();
    try {
      _channel?.sink.close();
    } catch (_) {}
    _channel = null;
  }

  void disconnect() {
    _isClosedManually = true;
    _currentProjectId = null;
    _reconnectTimer?.cancel();
    _cleanupChannel();
    onConnectionChanged?.call(false);
  }
}
