import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/network/api_endpoints.dart';
import '../../auth/providers/auth_provider.dart';
import '../../projects/providers/project_provider.dart';
import '../models/conversation_model.dart';

class InboxState {
  final List<ConversationModel> conversations;
  final String selectedChannel;
  final String searchQuery;
  final bool isLoading;
  final String? error;

  const InboxState({
    this.conversations = const [],
    this.selectedChannel = 'all',
    this.searchQuery = '',
    this.isLoading = false,
    this.error,
  });

  InboxState copyWith({
    List<ConversationModel>? conversations,
    String? selectedChannel,
    String? searchQuery,
    bool? isLoading,
    String? error,
  }) {
    return InboxState(
      conversations: conversations ?? this.conversations,
      selectedChannel: selectedChannel ?? this.selectedChannel,
      searchQuery: searchQuery ?? this.searchQuery,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }

  List<ConversationModel> get filteredConversations {
    return conversations.where((c) {
      if (selectedChannel != 'all' &&
          c.channel.toLowerCase() != selectedChannel.toLowerCase()) {
        return false;
      }
      if (searchQuery.isNotEmpty) {
        final q = searchQuery.toLowerCase();
        final nameMatch = c.displayName.toLowerCase().contains(q);
        final msgMatch = c.lastMessage?.toLowerCase().contains(q) ?? false;
        return nameMatch || msgMatch;
      }
      return true;
    }).toList();
  }
}

final inboxProvider = StateNotifierProvider<InboxNotifier, InboxState>((ref) {
  final api = ref.watch(apiClientProvider);
  final activeProject = ref.watch(activeProjectProvider);
  return InboxNotifier(api: api, projectId: activeProject?.id);
});

class InboxNotifier extends StateNotifier<InboxState> {
  final dynamic _api;
  final String? _projectId;

  InboxNotifier({required dynamic api, String? projectId})
      : _api = api,
        _projectId = projectId,
        super(const InboxState()) {
    if (_projectId != null) {
      loadConversations();
    }
  }

  Future<void> loadConversations() async {
    if (_projectId == null) return;
    state = state.copyWith(isLoading: true, error: null);

    try {
      final response = await _api.get(ApiEndpoints.conversations(_projectId));
      List<ConversationModel> list = [];
      if (response is List) {
        list = response
            .whereType<Map<String, dynamic>>()
            .map((e) => ConversationModel.fromJson(e))
            .toList();
      }
      state = state.copyWith(conversations: list, isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  void filterByChannel(String channel) {
    state = state.copyWith(selectedChannel: channel);
  }

  void search(String query) {
    state = state.copyWith(searchQuery: query.trim());
  }

  Future<bool> toggleCustomerAi(String profileId, bool enable) async {
    if (_projectId == null) return false;
    try {
      await _api.patch(
        '${ApiEndpoints.toggleCustomerAi(_projectId, profileId)}?enabled=$enable',
      );

      // Update local state immediately
      final updated = state.conversations.map((c) {
        if (c.profileId == profileId) {
          return c.copyWith(aiEnabled: enable);
        }
        return c;
      }).toList();

      state = state.copyWith(conversations: updated);
      return true;
    } catch (_) {
      return false;
    }
  }

  void handleIncomingMessage(Map<String, dynamic> msgData) {
    // Re-fetch conversations to keep ordering and unread counts accurate
    loadConversations();
  }
}
