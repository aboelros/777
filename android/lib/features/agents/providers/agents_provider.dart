import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/network/api_endpoints.dart';
import '../../auth/providers/auth_provider.dart';
import '../../projects/providers/project_provider.dart';
import '../models/bot_instruction_model.dart';

class AgentsState {
  final List<BotInstructionModel> instructions;
  final bool isLoading;
  final String? error;

  const AgentsState({
    this.instructions = const [],
    this.isLoading = false,
    this.error,
  });

  AgentsState copyWith({
    List<BotInstructionModel>? instructions,
    bool? isLoading,
    String? error,
  }) {
    return AgentsState(
      instructions: instructions ?? this.instructions,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

final agentsProvider =
    StateNotifierProvider<AgentsNotifier, AgentsState>((ref) {
  final api = ref.watch(apiClientProvider);
  final activeProject = ref.watch(activeProjectProvider);
  return AgentsNotifier(api: api, projectId: activeProject?.id);
});

class AgentsNotifier extends StateNotifier<AgentsState> {
  final dynamic _api;
  final String? _projectId;

  AgentsNotifier({required dynamic api, String? projectId})
      : _api = api,
        _projectId = projectId,
        super(const AgentsState()) {
    if (_projectId != null) {
      loadInstructions();
    }
  }

  Future<void> loadInstructions() async {
    if (_projectId == null) return;
    state = state.copyWith(isLoading: true, error: null);

    try {
      final response = await _api.get(ApiEndpoints.botInstructions(_projectId));
      List<BotInstructionModel> list = [];
      if (response is List) {
        list = response
            .whereType<Map<String, dynamic>>()
            .map((e) => BotInstructionModel.fromJson(e))
            .toList();
      }
      state = state.copyWith(instructions: list, isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<bool> createInstruction({
    required String title,
    required String instruction,
    String? category,
  }) async {
    if (_projectId == null) return false;
    try {
      final payload = {
        'title': title,
        'instruction': instruction,
        'category': category ?? 'general',
        'priority': 0,
        'active_for_platforms': ['whatsapp', 'meta'],
      };
      await _api.post(ApiEndpoints.botInstructions(_projectId), data: payload);
      await loadInstructions();
      return true;
    } catch (_) {
      return false;
    }
  }

  Future<bool> updateInstruction({
    required String instructionId,
    required String title,
    required String instruction,
  }) async {
    if (_projectId == null) return false;
    try {
      final payload = {
        'title': title,
        'instruction': instruction,
      };
      await _api.put(
        ApiEndpoints.botInstruction(_projectId, instructionId),
        data: payload,
      );
      await loadInstructions();
      return true;
    } catch (_) {
      return false;
    }
  }

  Future<bool> deleteInstruction(String instructionId) async {
    if (_projectId == null) return false;
    try {
      await _api.delete(ApiEndpoints.botInstruction(_projectId, instructionId));
      state = state.copyWith(
        instructions:
            state.instructions.where((i) => i.id != instructionId).toList(),
      );
      return true;
    } catch (_) {
      return false;
    }
  }
}
