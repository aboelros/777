import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:automind/app.dart';

void main() {
  testWidgets('AutomindApp boots and mounts root widget',
      (WidgetTester tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: AutomindApp(),
      ),
    );

    // Initial pump and advance past splash screen timer
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 700));
    await tester.pump();

    expect(find.byType(AutomindApp), findsOneWidget);
  });
}
