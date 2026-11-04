import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/localization/app_localizations.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/websocket/websocket_client.dart';
import '../../inbox/providers/inbox_provider.dart';
import '../../projects/providers/project_provider.dart';

/// Bottom navigation shell hosting primary operational tabs.
class MainShellScreen extends ConsumerStatefulWidget {
  final StatefulNavigationShell navigationShell;

  const MainShellScreen({super.key, required this.navigationShell});

  @override
  ConsumerState<MainShellScreen> createState() => _MainShellScreenState();
}

class _MainShellScreenState extends ConsumerState<MainShellScreen> {
  WebSocketClient? _wsClient;

  @override
  void initState() {
    super.initState();
    _initWebSocket();
  }

  void _initWebSocket() {
    final active = ref.read(activeProjectProvider);
    if (active != null) {
      _wsClient = WebSocketClient(
        onEvent: (event) {
          if (event['type'] == 'new_message') {
            final msg = event['message'];
            if (msg is Map<String, dynamic>) {
              ref.read(inboxProvider.notifier).handleIncomingMessage(msg);
            }
          }
        },
      );
      _wsClient?.connect(active.id);
    }
  }

  @override
  void dispose() {
    _wsClient?.disconnect();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    // Reconnect WS if project changes
    ref.listen(activeProjectProvider, (prev, next) {
      if (next != null && (prev?.id != next.id)) {
        _wsClient?.connect(next.id);
      }
    });

    return Scaffold(
      backgroundColor: AppColors.bgDark,
      body: widget.navigationShell,
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: widget.navigationShell.currentIndex,
        onTap: (index) {
          widget.navigationShell.goBranch(
            index,
            initialLocation: index == widget.navigationShell.currentIndex,
          );
        },
        items: [
          BottomNavigationBarItem(
            icon: const Icon(Icons.dashboard_outlined),
            activeIcon: const Icon(Icons.dashboard_rounded),
            label: context.tr('dashboard'),
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.forum_outlined),
            activeIcon: const Icon(Icons.forum_rounded),
            label: context.tr('inbox'),
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.shopping_bag_outlined),
            activeIcon: const Icon(Icons.shopping_bag_rounded),
            label: context.tr('orders'),
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.psychology_outlined),
            activeIcon: const Icon(Icons.psychology_rounded),
            label: context.tr('agents'),
          ),
          BottomNavigationBarItem(
            icon: const Icon(Icons.grid_view_outlined),
            activeIcon: const Icon(Icons.grid_view_rounded),
            label: context.tr('more'),
          ),
        ],
      ),
    );
  }
}
