import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/localization/app_localizations.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../../shared/widgets/app_button.dart';
import '../../../shared/widgets/glass_card.dart';
import '../../../shared/widgets/status_badge.dart';
import '../../auth/providers/auth_provider.dart';
import '../providers/settings_provider.dart';

/// Application settings, profile overview, and language preferences.
class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authNotifierProvider);
    final user = authState.user;
    final settings = ref.watch(settingsProvider);
    final isArabic = settings.locale.languageCode == 'ar';

    return Scaffold(
      backgroundColor: AppColors.bgDark,
      appBar: AppBar(
        title: Text(context.tr('settings'), style: AppTypography.pageTitle),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          if (user != null) ...[
            GlassCard(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  Container(
                    width: 52,
                    height: 52,
                    decoration: BoxDecoration(
                      color: AppColors.surfaceElevated,
                      shape: BoxShape.circle,
                      border: Border.all(color: AppColors.border),
                    ),
                    child: Center(
                      child: Text(
                        user.displayName[0].toUpperCase(),
                        style: AppTypography.sectionTitle
                            .copyWith(color: AppColors.brandPrimary),
                      ),
                    ),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(user.displayName, style: AppTypography.cardTitle),
                        const SizedBox(height: 2),
                        Text(user.email, style: AppTypography.caption),
                      ],
                    ),
                  ),
                  StatusBadge(
                    label: user.role,
                    variant: user.role == 'ADMIN'
                        ? BadgeVariant.info
                        : BadgeVariant.neutral,
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),
          ],
          Text(context.tr('preferences'), style: AppTypography.sectionTitle),
          const SizedBox(height: 12),
          GlassCard(
            padding: const EdgeInsets.all(14),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    const Icon(Icons.language_rounded,
                        color: AppColors.brandPrimary, size: 22),
                    const SizedBox(width: 12),
                    Text(context.tr('language'),
                        style: AppTypography.cardTitle),
                  ],
                ),
                SegmentedButton<String>(
                  segments: const [
                    ButtonSegment(value: 'en', label: Text('EN')),
                    ButtonSegment(value: 'ar', label: Text('عربي')),
                  ],
                  selected: {isArabic ? 'ar' : 'en'},
                  onSelectionChanged: (val) {
                    ref.read(settingsProvider.notifier).setLocale(val.first);
                  },
                  style: ButtonStyle(
                    backgroundColor: WidgetStateProperty.resolveWith(
                      (states) => states.contains(WidgetState.selected)
                          ? AppColors.brandPrimary
                          : AppColors.surfaceElevated,
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),
          Text(context.tr('orgConfig'), style: AppTypography.sectionTitle),
          const SizedBox(height: 12),
          GlassCard(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
            child: Column(
              children: [
                _navTile(
                  icon: Icons.integration_instructions_outlined,
                  title: context.tr('integrations'),
                  onTap: () => context.push('/integrations'),
                ),
                const Divider(color: AppColors.border, height: 1),
                _navTile(
                  icon: Icons.credit_card_rounded,
                  title: context.tr('billing'),
                  onTap: () => context.push('/billing'),
                ),
                const Divider(color: AppColors.border, height: 1),
                _navTile(
                  icon: Icons.inventory_2_outlined,
                  title: context.tr('products'),
                  onTap: () => context.push('/products'),
                ),
                const Divider(color: AppColors.border, height: 1),
                _navTile(
                  icon: Icons.insights_rounded,
                  title: 'Analytics Trends',
                  onTap: () => context.push('/analytics'),
                ),
              ],
            ),
          ),
          const SizedBox(height: 28),
          AppButton(
            text: context.tr('signOut'),
            variant: AppButtonVariant.danger,
            icon: Icons.logout_rounded,
            onPressed: () => _confirmSignOut(context, ref),
          ),
          const SizedBox(height: 20),
          Center(
            child: Text(
              '${context.tr('appName')} Mobile v1.0.0 (Production Engine)',
              style: AppTypography.caption,
            ),
          ),
        ],
      ),
    );
  }

  Widget _navTile({
    required IconData icon,
    required String title,
    required VoidCallback onTap,
  }) {
    return ListTile(
      leading: Icon(icon, color: AppColors.textSecondary, size: 20),
      title: Text(title, style: AppTypography.body),
      trailing: const Icon(Icons.arrow_forward_ios_rounded,
          color: AppColors.textMuted, size: 14),
      onTap: onTap,
      contentPadding: EdgeInsets.zero,
    );
  }

  void _confirmSignOut(BuildContext context, WidgetRef ref) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppColors.surfaceElevated,
        title: Text(context.tr('signOut'), style: AppTypography.cardTitle),
        content: Text(context.tr('signOutConfirm'),
            style: AppTypography.bodySecondary),
        actions: [
          TextButton(
            child: Text(context.tr('cancel'),
                style: const TextStyle(color: AppColors.textSecondary)),
            onPressed: () => Navigator.pop(ctx),
          ),
          TextButton(
            child: Text(context.tr('signOut'),
                style: const TextStyle(color: AppColors.danger)),
            onPressed: () async {
              Navigator.pop(ctx);
              await ref.read(authNotifierProvider.notifier).logout();
              if (context.mounted) {
                context.go('/login');
              }
            },
          ),
        ],
      ),
    );
  }
}
