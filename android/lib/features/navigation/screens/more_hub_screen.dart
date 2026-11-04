import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/localization/app_localizations.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../../shared/widgets/glass_card.dart';
import '../../auth/providers/auth_provider.dart';
import '../../projects/providers/project_provider.dart';
import '../../projects/widgets/project_selector_sheet.dart';
import '../widgets/hub_tile.dart';

/// Central Operations Hub providing unified mobile access to all Automind modules.
class MoreHubScreen extends ConsumerWidget {
  const MoreHubScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authNotifierProvider);
    final activeProject = ref.watch(activeProjectProvider);
    final user = authState.user;

    return Scaffold(
      backgroundColor: AppColors.bgDark,
      appBar: AppBar(
        title: Text(context.tr('operationsHub')),
        actions: [
          IconButton(
            icon: const Icon(Icons.swap_horiz_rounded),
            tooltip: context.tr('switchWorkspace'),
            onPressed: () => ProjectSelectorSheet.show(context),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        children: [
          _buildUserProfileHeader(context, user?.email ?? 'Operator',
              activeProject?.name ?? context.tr('noProject')),
          const SizedBox(height: 20),
          _buildSectionHeader(context.tr('salesCommerce')),
          HubTile(
            title: context.tr('crmDealsTitle'),
            subtitle: context.tr('crmDealsSubtitle'),
            icon: Icons.view_kanban_rounded,
            color: const Color(0xFF38BDF8),
            onTap: () => context.push('/deals'),
          ),
          HubTile(
            title: context.tr('productsTitle'),
            subtitle: context.tr('productsSubtitle'),
            icon: Icons.inventory_2_rounded,
            color: const Color(0xFF818CF8),
            onTap: () => context.push('/products'),
          ),
          HubTile(
            title: context.tr('dripTitle'),
            subtitle: context.tr('dripSubtitle'),
            icon: Icons.alt_route_rounded,
            color: const Color(0xFFF472B6),
            onTap: () => context.push('/campaigns'),
          ),
          const SizedBox(height: 16),
          _buildSectionHeader(context.tr('channelsSocial')),
          HubTile(
            title: context.tr('integrationsTitle'),
            subtitle: context.tr('integrationsSubtitle'),
            icon: Icons.extension_rounded,
            color: const Color(0xFF34D399),
            onTap: () => context.push('/integrations'),
          ),
          HubTile(
            title: context.tr('socialTitle'),
            subtitle: context.tr('socialSubtitle'),
            icon: Icons.tag_rounded,
            color: const Color(0xFFFBBF24),
            onTap: () => context.push('/social-media'),
          ),
          const SizedBox(height: 16),
          _buildSectionHeader(context.tr('telemetryAnalytics')),
          HubTile(
            title: context.tr('reportsTitle'),
            subtitle: context.tr('reportsSubtitle'),
            icon: Icons.insights_rounded,
            color: const Color(0xFF60A5FA),
            onTap: () => context.push('/analytics'),
          ),
          HubTile(
            title: context.tr('usageTitle'),
            subtitle: context.tr('usageSubtitle'),
            icon: Icons.pie_chart_rounded,
            color: const Color(0xFFA78BFA),
            onTap: () => context.push('/usage'),
          ),
          const SizedBox(height: 16),
          _buildSectionHeader(context.tr('orgConfig')),
          HubTile(
            title: context.tr('workspacesTitle'),
            subtitle: context.tr('workspacesSubtitle'),
            icon: Icons.domain_rounded,
            color: const Color(0xFF38BDF8),
            onTap: () => context.push('/projects'),
          ),
          HubTile(
            title: context.tr('billingTitle'),
            subtitle: context.tr('billingSubtitle'),
            icon: Icons.credit_card_rounded,
            color: const Color(0xFF10B981),
            onTap: () => context.push('/billing'),
          ),
          HubTile(
            title: context.tr('settingsTitle'),
            subtitle: context.tr('settingsSubtitle'),
            icon: Icons.settings_rounded,
            color: const Color(0xFF94A3B8),
            onTap: () => context.push('/settings'),
          ),
          const SizedBox(height: 24),
          _buildSignOutTile(context, ref),
          const SizedBox(height: 32),
        ],
      ),
    );
  }

  Widget _buildUserProfileHeader(
      BuildContext context, String email, String workspace) {
    return GlassCard(
      padding: const EdgeInsets.all(16),
      borderColor: AppColors.borderStrong,
      child: Row(
        children: [
          Container(
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF38BDF8), Color(0xFF2563EB)],
              ),
              borderRadius: BorderRadius.circular(12),
            ),
            alignment: Alignment.center,
            child: Text(
              email.isNotEmpty ? email[0].toUpperCase() : 'A',
              style: AppTypography.cardTitle.copyWith(color: Colors.white),
            ),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(email,
                    style: AppTypography.cardTitle,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis),
                const SizedBox(height: 2),
                Text('Workspace: $workspace',
                    style: AppTypography.caption
                        .copyWith(color: AppColors.brandPrimary)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.only(left: 4, bottom: 8),
      child: Text(
        title,
        style: AppTypography.caption.copyWith(
          letterSpacing: 1.4,
          fontWeight: FontWeight.w700,
          color: AppColors.textMuted,
        ),
      ),
    );
  }

  Widget _buildSignOutTile(BuildContext context, WidgetRef ref) {
    return GlassCard(
      onTap: () {
        ref.read(authNotifierProvider.notifier).logout();
        context.go('/login');
      },
      borderColor: AppColors.danger.withValues(alpha: 0.3),
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.logout_rounded, color: AppColors.danger, size: 20),
          const SizedBox(width: 8),
          Text(
            context.tr('signOutAutomind'),
            style: const TextStyle(
              color: AppColors.danger,
              fontWeight: FontWeight.w600,
              fontSize: 14,
            ),
          ),
        ],
      ),
    );
  }
}
