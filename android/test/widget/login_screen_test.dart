import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:automind/core/localization/app_localizations.dart';
import 'package:automind/core/theme/app_theme.dart';
import 'package:automind/features/auth/screens/login_screen.dart';
import 'package:automind/shared/widgets/app_button.dart';
import 'package:automind/shared/widgets/app_text_field.dart';

void main() {
  testWidgets('LoginScreen renders inputs and validation triggers',
      (tester) async {
    tester.view.physicalSize = const Size(1080, 1920);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(() => tester.view.resetPhysicalSize());

    await tester.pumpWidget(
      ProviderScope(
        child: MaterialApp(
          theme: AppTheme.darkTheme,
          localizationsDelegates: const [
            AppLocalizations.delegate,
            GlobalMaterialLocalizations.delegate,
            GlobalWidgetsLocalizations.delegate,
            GlobalCupertinoLocalizations.delegate,
          ],
          supportedLocales: AppLocalizations.supportedLocales,
          home: const LoginScreen(),
        ),
      ),
    );

    await tester.pump();

    // Verify presence of text fields and sign in button
    expect(find.byType(AppTextField), findsNWidgets(2));
    expect(find.byType(AppButton), findsOneWidget);

    // Ensure button is visible in scroll view and tap
    await tester.ensureVisible(find.byType(ElevatedButton));
    await tester.tap(find.byType(ElevatedButton));
    await tester.pump();

    // Verify validation error appears
    expect(find.text('Email is required'), findsOneWidget);
  });
}
