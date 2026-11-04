import 'package:flutter_test/flutter_test.dart';
import 'package:automind/core/routing/route_guards.dart';
import 'package:automind/features/auth/models/auth_state.dart';
import 'package:automind/features/auth/models/user_model.dart';
import 'package:flutter/material.dart';

void main() {
  group('RouteGuards', () {
    testWidgets(
        'unauthenticated user redirected to /login when visiting /dashboard',
        (tester) async {
      await tester.pumpWidget(MaterialApp(
        home: Builder(
          builder: (context) {
            final redirect = RouteGuards.authRedirect(
              context,
              AuthState.unauthenticated(),
              '/dashboard',
            );
            expect(redirect, '/login');
            return const Placeholder();
          },
        ),
      ));
    });

    testWidgets('authenticated user redirected from /login to /dashboard',
        (tester) async {
      const user = UserModel(
        id: 'u-1',
        email: 'test@automio.online',
        role: 'ADMIN',
      );

      await tester.pumpWidget(MaterialApp(
        home: Builder(
          builder: (context) {
            final redirect = RouteGuards.authRedirect(
              context,
              AuthState.authenticated(user),
              '/login',
            );
            expect(redirect, '/dashboard');
            return const Placeholder();
          },
        ),
      ));
    });
  });
}
