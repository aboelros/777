import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_colors.dart';
import '../../../shared/widgets/brand_logo.dart';
import '../../projects/providers/project_provider.dart';
import '../providers/auth_provider.dart';

/// Initial splash and boot screen restoring hardware-backed sessions.
class SplashScreen extends ConsumerStatefulWidget {
  const SplashScreen({super.key});

  @override
  ConsumerState<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends ConsumerState<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _initialize();
  }

  Future<void> _initialize() async {
    try {
      await Future.delayed(const Duration(milliseconds: 600));

      final authNotifier = ref.read(authNotifierProvider.notifier);
      await authNotifier.restoreSession();

      if (!mounted) return;

      final authState = ref.read(authNotifierProvider);
      if (authState.isAuthenticated) {
        await ref.read(projectProvider.notifier).fetchProjects();
        if (!mounted) return;
        context.go('/dashboard');
      } else {
        context.go('/login');
      }
    } catch (_) {
      if (mounted) {
        context.go('/login');
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bgDark,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const BrandLogo(
              size: 56,
              variant: BrandLogoVariant.full,
              subtitle: 'AI SALES OPERATING SYSTEM',
            ),
            const SizedBox(height: 48),
            const SizedBox(
              width: 24,
              height: 24,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                valueColor:
                    AlwaysStoppedAnimation<Color>(AppColors.brandPrimary),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
