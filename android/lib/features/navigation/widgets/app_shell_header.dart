import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/localization/app_localizations.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../../shared/widgets/brand_logo.dart';
import '../../auth/providers/auth_provider.dart';
import '../../projects/providers/project_provider.dart';
import '../../projects/widgets/project_selector_sheet.dart';
import '../../settings/providers/settings_provider.dart';

/// Master Application Shell Header with Official Brand Logo,
/// Workspace Selector, Notification status, and User Profile telemetry.
class AppShellHeader extends ConsumerWidget implements PreferredSizeWidget {
  const AppShellHeader({super.key});

  @override
  Size get preferredSize => const Size.fromHeight(58);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final activeProject = ref.watch(activeProjectProvider);
    final authState = ref.watch(authNotifierProvider);
    final settings = ref.watch(settingsProvider);
    final isArabic = settings.locale.languageCode == 'ar';
    final user = authState.user;

    final initial = (user?.name?.isNotEmpty == true)
        ? user!.name![0].toUpperCase()
        : (user?.email.isNotEmpty == true)
            ? user!.email[0].toUpperCase()
            : 'A';

    return AppBar(
      backgroundColor: AppColors.bgDark.withValues(alpha: 0.95),
      elevation: 0,
      scrolledUnderElevation: 0,
      titleSpacing: 16,
      centerTitle: false,
      title: const BrandLogo(
        size: 26,
        variant: BrandLogoVariant.compact,
      ),
      actions: [
        // Workspace Selector Pill
        GestureDetector(
          onTap: () => ProjectSelectorSheet.show(context),
          child: Container(
            margin: const EdgeInsets.symmetric(vertical: 12),
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: AppColors.surfaceElevated,
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: AppColors.borderStrong),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 6,
                  height: 6,
                  decoration: const BoxDecoration(
                    color: AppColors.brandPrimary,
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 6),
                ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 110),
                  child: Text(
                    activeProject?.name ?? context.tr('noProject'),
                    style: AppTypography.caption.copyWith(
                      color: AppColors.textPrimary,
                      fontWeight: FontWeight.w600,
                    ),
                    overflow: TextOverflow.ellipsis,
                    maxLines: 1,
                  ),
                ),
                const SizedBox(width: 4),
                const Icon(
                  Icons.keyboard_arrow_down_rounded,
                  color: AppColors.textSecondary,
                  size: 16,
                ),
              ],
            ),
          ),
        ),
        const SizedBox(width: 8),

        // Instant Language Toggle Chip
        GestureDetector(
          onTap: () {
            final nextLang = isArabic ? 'en' : 'ar';
            ref.read(settingsProvider.notifier).setLocale(nextLang);
          },
          child: Container(
            margin: const EdgeInsets.symmetric(vertical: 12),
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: AppColors.surfaceElevated,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: AppColors.borderStrong),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(
                  Icons.language_rounded,
                  size: 14,
                  color: AppColors.brandPrimary,
                ),
                const SizedBox(width: 4),
                Text(
                  isArabic ? 'EN' : 'عربي',
                  style: AppTypography.caption.copyWith(
                    fontWeight: FontWeight.bold,
                    color: AppColors.textPrimary,
                  ),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(width: 4),

        // Notifications
        IconButton(
          icon: const Icon(Icons.notifications_outlined, size: 20),
          color: AppColors.textSecondary,
          tooltip: 'Notifications',
          onPressed: () {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('No unread system alerts.'),
                duration: Duration(seconds: 2),
              ),
            );
          },
        ),

        // User Avatar Chip
        GestureDetector(
          onTap: () => context.push('/settings'),
          child: Container(
            margin: const EdgeInsets.only(right: 16, left: 4),
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF38BDF8), Color(0xFF2563EB)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(10),
            ),
            padding: const EdgeInsets.all(1.5),
            child: Container(
              decoration: BoxDecoration(
                color: AppColors.surfaceDark,
                borderRadius: BorderRadius.circular(9),
              ),
              alignment: Alignment.center,
              child: Text(
                initial,
                style: AppTypography.caption.copyWith(
                  fontWeight: FontWeight.w800,
                  color: AppColors.brandPrimary,
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}
