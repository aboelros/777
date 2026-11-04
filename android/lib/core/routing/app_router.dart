import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../features/agents/models/bot_instruction_model.dart';
import '../../features/agents/screens/agents_screen.dart';
import '../../features/agents/screens/edit_instruction_screen.dart';
import '../../features/analytics/screens/analytics_screen.dart';
import '../../features/auth/models/auth_state.dart';
import '../../features/auth/providers/auth_provider.dart';
import '../../features/auth/screens/login_screen.dart';
import '../../features/auth/screens/splash_screen.dart';
import '../../features/billing/screens/billing_screen.dart';
import '../../features/campaigns/screens/campaigns_screen.dart';
import '../../features/crm/screens/deals_screen.dart';
import '../../features/dashboard/screens/dashboard_screen.dart';
import '../../features/inbox/models/conversation_model.dart';
import '../../features/inbox/screens/chat_screen.dart';
import '../../features/inbox/screens/inbox_screen.dart';
import '../../features/integrations/screens/integrations_screen.dart';
import '../../features/navigation/screens/main_shell_screen.dart';
import '../../features/navigation/screens/more_hub_screen.dart';
import '../../features/orders/models/order_model.dart';
import '../../features/orders/screens/order_detail_screen.dart';
import '../../features/orders/screens/orders_screen.dart';
import '../../features/products/models/product_model.dart';
import '../../features/products/screens/edit_product_screen.dart';
import '../../features/products/screens/products_screen.dart';
import '../../features/projects/screens/projects_screen.dart';
import '../../features/settings/screens/settings_screen.dart';
import '../../features/social/screens/social_media_screen.dart';
import '../../features/usage/screens/usage_screen.dart';
import 'route_guards.dart';

final _rootNavigatorKey = GlobalKey<NavigatorState>();

/// Listenable adapter linking Riverpod auth state changes to GoRouter refreshes.
class RouterNotifier extends ChangeNotifier {
  final Ref _ref;

  RouterNotifier(this._ref) {
    _ref.listen<AuthState>(
      authNotifierProvider,
      (_, __) => notifyListeners(),
    );
  }
}

final routerNotifierProvider = Provider<RouterNotifier>((ref) {
  return RouterNotifier(ref);
});

final routerProvider = Provider<GoRouter>((ref) {
  final notifier = ref.watch(routerNotifierProvider);

  return GoRouter(
    navigatorKey: _rootNavigatorKey,
    initialLocation: '/splash',
    refreshListenable: notifier,
    redirect: (context, state) {
      final authState = ref.read(authNotifierProvider);
      return RouteGuards.authRedirect(
          context, authState, state.matchedLocation);
    },
    routes: [
      GoRoute(
        path: '/splash',
        builder: (_, __) => const SplashScreen(),
      ),
      GoRoute(
        path: '/login',
        builder: (_, __) => const LoginScreen(),
      ),
      StatefulShellRoute.indexedStack(
        builder: (context, state, navigationShell) {
          return MainShellScreen(navigationShell: navigationShell);
        },
        branches: [
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/dashboard',
                builder: (_, __) => const DashboardScreen(),
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/inbox',
                builder: (_, __) => const InboxScreen(),
                routes: [
                  GoRoute(
                    path: 'chat',
                    parentNavigatorKey: _rootNavigatorKey,
                    builder: (_, state) => ChatScreen(
                      conversation: state.extra as ConversationModel,
                    ),
                  ),
                ],
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/orders',
                builder: (_, __) => const OrdersScreen(),
                routes: [
                  GoRoute(
                    path: 'detail',
                    parentNavigatorKey: _rootNavigatorKey,
                    builder: (_, state) => OrderDetailScreen(
                      order: state.extra as OrderModel,
                    ),
                  ),
                ],
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/agents',
                builder: (_, __) => const AgentsScreen(),
                routes: [
                  GoRoute(
                    path: 'edit',
                    parentNavigatorKey: _rootNavigatorKey,
                    builder: (_, state) => EditInstructionScreen(
                      instruction: state.extra as BotInstructionModel?,
                    ),
                  ),
                ],
              ),
            ],
          ),
          StatefulShellBranch(
            routes: [
              GoRoute(
                path: '/more',
                builder: (_, __) => const MoreHubScreen(),
              ),
            ],
          ),
        ],
      ),
      GoRoute(
        path: '/deals',
        parentNavigatorKey: _rootNavigatorKey,
        builder: (_, __) => const DealsScreen(),
      ),
      GoRoute(
        path: '/products',
        parentNavigatorKey: _rootNavigatorKey,
        builder: (_, __) => const ProductsScreen(),
        routes: [
          GoRoute(
            path: 'edit',
            parentNavigatorKey: _rootNavigatorKey,
            builder: (_, state) => EditProductScreen(
              product: state.extra as ProductModel?,
            ),
          ),
        ],
      ),
      GoRoute(
        path: '/integrations',
        parentNavigatorKey: _rootNavigatorKey,
        builder: (_, __) => const IntegrationsScreen(),
      ),
      GoRoute(
        path: '/social-media',
        parentNavigatorKey: _rootNavigatorKey,
        builder: (_, __) => const SocialMediaScreen(),
      ),
      GoRoute(
        path: '/campaigns',
        parentNavigatorKey: _rootNavigatorKey,
        builder: (_, __) => const CampaignsScreen(),
      ),
      GoRoute(
        path: '/billing',
        parentNavigatorKey: _rootNavigatorKey,
        builder: (_, __) => const BillingScreen(),
      ),
      GoRoute(
        path: '/analytics',
        parentNavigatorKey: _rootNavigatorKey,
        builder: (_, __) => const AnalyticsScreen(),
      ),
      GoRoute(
        path: '/usage',
        parentNavigatorKey: _rootNavigatorKey,
        builder: (_, __) => const UsageScreen(),
      ),
      GoRoute(
        path: '/projects',
        parentNavigatorKey: _rootNavigatorKey,
        builder: (_, __) => const ProjectsScreen(),
      ),
      GoRoute(
        path: '/settings',
        parentNavigatorKey: _rootNavigatorKey,
        builder: (_, __) => const SettingsScreen(),
      ),
    ],
  );
});
