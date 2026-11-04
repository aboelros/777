import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/localization/app_localizations.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../../shared/widgets/empty_view.dart';
import '../../../shared/widgets/error_view.dart';
import '../../../shared/widgets/glass_card.dart';
import '../../../shared/widgets/skeleton_loader.dart';
import '../../../shared/widgets/status_badge.dart';
import '../../projects/providers/project_provider.dart';
import '../models/integration_model.dart';
import '../providers/integrations_provider.dart';

/// Screen displaying status of connected messaging channels and platforms.
class IntegrationsScreen extends ConsumerWidget {
  const IntegrationsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final activeProject = ref.watch(activeProjectProvider);
    final state = ref.watch(integrationsProvider);

    return Scaffold(
      backgroundColor: AppColors.bgDark,
      appBar: AppBar(
        title: Text(context.tr('integrations'), style: AppTypography.pageTitle),
      ),
      body: activeProject == null
          ? EmptyView(
              title: context.tr('noProject'),
              subtitle: 'Select a workspace to view connected channels.',
            )
          : state.isLoading && state.integrations.isEmpty
              ? _buildSkeletonList()
              : state.error != null && state.integrations.isEmpty
                  ? ErrorView(
                      message: state.error,
                      onRetry: () => ref
                          .read(integrationsProvider.notifier)
                          .loadIntegrations(),
                    )
                  : RefreshIndicator(
                      color: AppColors.brandPrimary,
                      backgroundColor: AppColors.surfaceElevated,
                      onRefresh: () => ref
                          .read(integrationsProvider.notifier)
                          .loadIntegrations(),
                      child: ListView(
                        padding: const EdgeInsets.all(16),
                        children: [
                          _buildIntegrationTile(
                            name: 'WhatsApp Business Gateway',
                            description:
                                'Direct multi-session WhatsApp automation',
                            icon: Icons.message_rounded,
                            iconColor: const Color(0xFF25D366),
                            integration: _find(state.integrations, 'whatsapp'),
                          ),
                          const SizedBox(height: 12),
                          _buildIntegrationTile(
                            name: 'Meta (Instagram & Facebook)',
                            description:
                                'Direct messages and comments auto-reply',
                            icon: Icons.share_rounded,
                            iconColor: const Color(0xFF1877F2),
                            integration: _find(state.integrations, 'meta'),
                          ),
                          const SizedBox(height: 12),
                          _buildIntegrationTile(
                            name: 'Telegram Bot',
                            description: 'Automated 24/7 customer service chat',
                            icon: Icons.send_rounded,
                            iconColor: const Color(0xFF0088CC),
                            integration: _find(state.integrations, 'telegram'),
                          ),
                          const SizedBox(height: 12),
                          _buildIntegrationTile(
                            name: 'Shopify Store',
                            description:
                                'Product catalog and order synchronization',
                            icon: Icons.shopping_cart_outlined,
                            iconColor: const Color(0xFF96BF48),
                            integration: _find(state.integrations, 'shopify'),
                          ),
                        ],
                      ),
                    ),
    );
  }

  IntegrationModel? _find(List<IntegrationModel> list, String provider) {
    try {
      return list.firstWhere(
        (i) => i.provider.toLowerCase().contains(provider.toLowerCase()),
      );
    } catch (_) {
      return null;
    }
  }

  Widget _buildIntegrationTile({
    required String name,
    required String description,
    required IconData icon,
    required Color iconColor,
    required IntegrationModel? integration,
  }) {
    final isConnected = integration?.isConnected ?? false;

    return GlassCard(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: iconColor.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, color: iconColor, size: 24),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(name, style: AppTypography.cardTitle),
                const SizedBox(height: 2),
                Text(description, style: AppTypography.caption),
              ],
            ),
          ),
          const SizedBox(width: 8),
          StatusBadge(
            label: isConnected ? 'Connected' : 'Disconnected',
            variant: isConnected ? BadgeVariant.success : BadgeVariant.neutral,
            showDot: true,
          ),
        ],
      ),
    );
  }

  Widget _buildSkeletonList() {
    return ListView.separated(
      padding: const EdgeInsets.all(16),
      itemCount: 4,
      separatorBuilder: (_, __) => const SizedBox(height: 12),
      itemBuilder: (_, __) =>
          const SkeletonLoader(width: double.infinity, height: 75),
    );
  }
}
