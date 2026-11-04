import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/localization/app_localizations.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../../shared/widgets/empty_view.dart';
import '../../../shared/widgets/error_view.dart';
import '../../../shared/widgets/skeleton_loader.dart';
import '../../projects/providers/project_provider.dart';
import '../models/conversation_model.dart';
import '../providers/inbox_provider.dart';
import '../widgets/conversation_tile.dart';

/// Unified Inbox screen displaying multi-channel conversations.
class InboxScreen extends ConsumerWidget {
  const InboxScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final activeProject = ref.watch(activeProjectProvider);
    final inboxState = ref.watch(inboxProvider);
    final conversations = inboxState.filteredConversations;

    return Scaffold(
      backgroundColor: AppColors.bgDark,
      appBar: AppBar(
        title: Text(context.tr('inbox'), style: AppTypography.pageTitle),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(96),
          child: Column(
            children: [
              _buildSearchBar(context, ref),
              _buildChannelFilterBar(context, ref, inboxState.selectedChannel),
            ],
          ),
        ),
      ),
      body: activeProject == null
          ? EmptyView(
              title: context.tr('noProject'),
              subtitle: 'Select a workspace to view customer conversations.',
            )
          : inboxState.isLoading && inboxState.conversations.isEmpty
              ? _buildSkeletonList()
              : inboxState.error != null && inboxState.conversations.isEmpty
                  ? ErrorView(
                      message: inboxState.error,
                      onRetry: () =>
                          ref.read(inboxProvider.notifier).loadConversations(),
                    )
                  : conversations.isEmpty
                      ? EmptyView(
                          title: 'No Conversations',
                          subtitle: inboxState.searchQuery.isNotEmpty
                              ? 'No results matching "${inboxState.searchQuery}"'
                              : 'Incoming customer chats will appear here.',
                          icon: Icons.chat_bubble_outline_rounded,
                        )
                      : RefreshIndicator(
                          color: AppColors.brandPrimary,
                          backgroundColor: AppColors.surfaceElevated,
                          onRefresh: () => ref
                              .read(inboxProvider.notifier)
                              .loadConversations(),
                          child: ListView.separated(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 16, vertical: 12),
                            itemCount: conversations.length,
                            separatorBuilder: (_, __) =>
                                const SizedBox(height: 8),
                            itemBuilder: (context, index) {
                              final conv = conversations[index];
                              return ConversationTile(
                                conversation: conv,
                                onTap: () => _openChat(context, conv),
                              );
                            },
                          ),
                        ),
    );
  }

  void _openChat(BuildContext context, ConversationModel conversation) {
    context.push('/inbox/chat', extra: conversation);
  }

  Widget _buildSearchBar(BuildContext context, WidgetRef ref) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: Container(
        height: 38,
        decoration: BoxDecoration(
          color: AppColors.surfaceElevated,
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: AppColors.border),
        ),
        child: TextField(
          style: AppTypography.bodySecondary,
          decoration: InputDecoration(
            hintText: context.tr('search'),
            hintStyle:
                AppTypography.caption.copyWith(color: AppColors.textMuted),
            prefixIcon: const Icon(Icons.search_rounded,
                size: 18, color: AppColors.textSecondary),
            border: InputBorder.none,
            contentPadding: const EdgeInsets.symmetric(vertical: 8),
          ),
          onChanged: (q) => ref.read(inboxProvider.notifier).search(q),
        ),
      ),
    );
  }

  Widget _buildChannelFilterBar(
      BuildContext context, WidgetRef ref, String selected) {
    final channels = [
      {'key': 'all', 'label': 'All'},
      {'key': 'whatsapp', 'label': 'WhatsApp'},
      {'key': 'meta', 'label': 'Meta'},
      {'key': 'telegram', 'label': 'Telegram'},
    ];

    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      child: Row(
        children: channels.map((c) {
          final isSelected = c['key'] == selected;
          return Padding(
            padding: const EdgeInsets.only(right: 8),
            child: ChoiceChip(
              label: Text(
                c['label']!,
                style: AppTypography.caption.copyWith(
                  color: isSelected ? Colors.white : AppColors.textSecondary,
                  fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
                ),
              ),
              selected: isSelected,
              selectedColor: AppColors.brandPrimary,
              backgroundColor: AppColors.surfaceElevated,
              side: BorderSide(
                color: isSelected ? AppColors.brandPrimary : AppColors.border,
              ),
              showCheckmark: false,
              onSelected: (_) =>
                  ref.read(inboxProvider.notifier).filterByChannel(c['key']!),
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildSkeletonList() {
    return ListView.separated(
      padding: const EdgeInsets.all(16),
      itemCount: 6,
      separatorBuilder: (_, __) => const SizedBox(height: 8),
      itemBuilder: (_, __) =>
          const SkeletonLoader(width: double.infinity, height: 78),
    );
  }
}
