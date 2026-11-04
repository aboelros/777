import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../../shared/widgets/empty_view.dart';
import '../../../shared/widgets/error_view.dart';
import '../../../shared/widgets/skeleton_loader.dart';
import '../../customers/widgets/customer_profile_sheet.dart';
import '../models/conversation_model.dart';
import '../providers/chat_thread_provider.dart';
import '../widgets/chat_bubble.dart';
import '../widgets/message_input_bar.dart';
import '../widgets/takeover_banner.dart';

/// Active conversation thread with Human Takeover controls.
class ChatScreen extends ConsumerWidget {
  final ConversationModel conversation;

  const ChatScreen({super.key, required this.conversation});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final threadState = ref.watch(chatThreadProvider(conversation));
    final threadNotifier = ref.read(chatThreadProvider(conversation).notifier);
    final conv = threadState.conversation;

    return Scaffold(
      backgroundColor: AppColors.bgDark,
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              conv.displayName,
              style: AppTypography.cardTitle,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            Text(
              conv.customerPhone ?? conv.channel.toUpperCase(),
              style: AppTypography.caption,
            ),
          ],
        ),
        actions: [
          if (conv.profileId != null)
            IconButton(
              icon: const Icon(Icons.info_outline_rounded),
              tooltip: 'Customer Profile',
              onPressed: () {
                CustomerProfileSheet.show(context, conv.profileId!);
              },
            ),
        ],
      ),
      body: Column(
        children: [
          TakeoverBanner(
            aiEnabled: conv.aiEnabled,
            onToggle: () => threadNotifier.toggleAiTakeover(!conv.aiEnabled),
          ),
          Expanded(
            child: threadState.isLoading && threadState.messages.isEmpty
                ? _buildLoadingSkeleton()
                : threadState.error != null && threadState.messages.isEmpty
                    ? ErrorView(
                        message: threadState.error,
                        onRetry: () => threadNotifier.loadMessages(),
                      )
                    : threadState.messages.isEmpty
                        ? const EmptyView(
                            title: 'No Messages',
                            subtitle:
                                'Send a message below to start the conversation.',
                            icon: Icons.chat_outlined,
                          )
                        : ListView.builder(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 16, vertical: 12),
                            reverse: false,
                            itemCount: threadState.messages.length,
                            itemBuilder: (context, index) {
                              final msg = threadState.messages[index];
                              return ChatBubble(message: msg);
                            },
                          ),
          ),
          MessageInputBar(
            isSending: threadState.isSending,
            onSend: (text) => threadNotifier.sendMessage(text),
          ),
        ],
      ),
    );
  }

  Widget _buildLoadingSkeleton() {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: 4,
      itemBuilder: (_, index) {
        final isRight = index % 2 == 1;
        return Align(
          alignment: isRight ? Alignment.centerRight : Alignment.centerLeft,
          child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 6),
            child: SkeletonLoader(
              width: 220,
              height: 54,
              borderRadius: 12,
            ),
          ),
        );
      },
    );
  }
}
