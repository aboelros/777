import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';

import 'package:ai_sales_commander/main.dart';
import 'package:ai_sales_commander/providers/auth_provider.dart';
import 'package:ai_sales_commander/providers/project_provider.dart';
import 'package:ai_sales_commander/providers/chat_provider.dart';
import 'package:ai_sales_commander/providers/order_provider.dart';
import 'package:ai_sales_commander/providers/theme_provider.dart';
import 'package:ai_sales_commander/providers/analytics_provider.dart';

void main() {
  testWidgets('App renders without crashing', (WidgetTester tester) async {
    await tester.pumpWidget(
      MultiProvider(
        providers: [
          ChangeNotifierProvider(create: (_) => ThemeProvider()),
          ChangeNotifierProvider(create: (_) => AuthProvider()),
          ChangeNotifierProvider(create: (_) => ProjectProvider()),
          ChangeNotifierProvider(create: (_) => ChatProvider()),
          ChangeNotifierProvider(create: (_) => OrderProvider()),
          ChangeNotifierProvider(create: (_) => AnalyticsProvider()),
        ],
        child: const AISalesCommanderApp(),
      ),
    );
    expect(find.byType(MaterialApp), findsOneWidget);
  });
}
