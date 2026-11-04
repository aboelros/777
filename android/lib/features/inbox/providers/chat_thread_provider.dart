import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/network/api_endpoints.dart';
import '../../auth/providers/auth_provider.dart';
import '../../projects/providers/project_provider.dart';
import '../models/conversation_model.dart';
import '../models/message_model.dart';
import 'inbox_provider.dart';

class ChatThreadState {
  final ConversationModel conversation;
  final List<MessageModel> messages;
  final bool isLoading;
  final bool isSending;
  final String? error;

  const ChatThreadState({
    required this.conversation,
    this.messages = const [],
    this.isLoading = false,
    this.isSending = false,
    this.error,
  });

  ChatThreadState copyWith({
    ConversationModel? conversation,
    List<MessageModel>? messages,
    bool? isLoading,
    bool? isSending,
    String? error,
  }) {
    return ChatThreadState(
      conversation: conversation ?? this.conversation,
      messages: messages ?? this.messages,
      isLoading: isLoading ?? this.isLoading,
      isSending: isSending ?? this.isSending,
      error: error,
    );
  }
}

final chatThreadProvider = StateNotifierProvider.autoDispose
    .family<ChatThreadNotifier, ChatThreadState, ConversationModel>(
        (ref, conv) {
  final api = ref.watch(apiClientProvider);
  final activeProject = ref.watch(activeProjectProvider);
  return ChatThreadNotifier(
    api: api,
    projectId: activeProject?.id,
    conversation: conv,
    onTakeoverChanged: (enable) {
      if (conv.profileId != null) {
        ref
            .read(inboxProvider.notifier)
            .toggleCustomerAi(conv.profileId!, enable);
      }
    },
  );
});

class ChatThreadNotifier extends StateNotifier<ChatThreadState> {
  final dynamic _api;
  final String? _projectId;
  final void Function(bool enable)? _onTakeoverChanged;

  ChatThreadNotifier({
    required dynamic api,
    String? projectId,
    required ConversationModel conversation,
    void Function(bool enable)? onTakeoverChanged,
  })  : _api = api,
        _projectId = projectId,
        _onTakeoverChanged = onTakeoverChanged,
        super(ChatThreadState(conversation: conversation)) {
    loadMessages();
    markRead();
  }

  Future<void> loadMessages() async {
    if (_projectId == null) return;
    state = state.copyWith(isLoading: true, error: null);

    try {
      final endpoint = ApiEndpoints.conversationMessages(
        _projectId,
        state.conversation.id,
      );
      final response = await _api.get(endpoint);
      List<MessageModel> list = [];
      if (response is List) {
        list = response
            .whereType<Map<String, dynamic>>()
            .map((e) => MessageModel.fromJson(e))
            .toList();
      }
      state = state.copyWith(messages: list, isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<bool> sendMessage(String text) async {
    if (_projectId == null || text.trim().isEmpty) return false;
    state = state.copyWith(isSending: true);

    try {
      final endpoint = ApiEndpoints.sendMessage(_projectId);
      final payload = {
        'content': text.trim(),
        'channel': state.conversation.channel,
        'customer_id': state.conversation.customerId,
        'conversation_id': state.conversation.id,
        'recipient': {
          'id': state.conversation.customerId ?? state.conversation.id,
          'phone': state.conversation.customerPhone,
        },
      };

      final response = await _api.post(endpoint, data: payload);
      if (response is Map<String, dynamic>) {
        final newMsg = MessageModel.fromJson(response);
        state = state.copyWith(
          messages: [...state.messages, newMsg],
          isSending: false,
        );
      } else {
        await loadMessages();
        state = state.copyWith(isSending: false);
      }
      return true;
    } catch (e) {
      state =
          state.copyWith(isSending: false, error: 'Failed to send message.');
      return false;
    }
  }

  Future<void> toggleAiTakeover(bool enable) async {
    final profileId = state.conversation.profileId;
    if (_projectId == null || profileId == null) return;

    try {
      await _api.patch(
        '${ApiEndpoints.toggleCustomerAi(_projectId, profileId)}?enabled=$enable',
      );
      state = state.copyWith(
        conversation: state.conversation.copyWith(aiEnabled: enable),
      );
      _onTakeoverChanged?.call(enable);
    } catch (_) {}
  }

  Future<void> markRead() async {
    if (_projectId == null) return;
    try {
      await _api.patch(
        ApiEndpoints.markConversationRead(_projectId, state.conversation.id),
      );
    } catch (_) {}
  }
}
