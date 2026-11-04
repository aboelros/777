import 'package:flutter/material.dart';
import '../../features/auth/models/auth_state.dart';

/// Navigation route guard enforcing authenticated access to protected paths.
class RouteGuards {
  RouteGuards._();

  static String? authRedirect(
      BuildContext context, AuthState authState, String location) {
    final isAuth = authState.isAuthenticated;
    final isCheckingSession = authState.isInitial || authState.isLoading;

    // During boot / session restoration on splash screen
    if (location == '/splash') {
      if (isCheckingSession) return null;
      return isAuth ? '/dashboard' : '/login';
    }

    // Unauthenticated user attempting to access protected area
    if (!isAuth && location != '/login') {
      return '/login';
    }

    // Authenticated user attempting to access login
    if (isAuth && location == '/login') {
      return '/dashboard';
    }

    return null;
  }
}
