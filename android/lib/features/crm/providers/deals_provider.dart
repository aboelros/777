import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/network/api_client.dart';
import '../../../core/network/api_endpoints.dart';
import '../../auth/providers/auth_provider.dart';
import '../../projects/providers/project_provider.dart';
import '../models/deal_model.dart';

class DealsState {
  final List<PipelineStageModel> stages;
  final List<DealModel> deals;
  final bool isLoading;
  final String? selectedStageId;
  final String? errorMessage;

  const DealsState({
    this.stages = const [],
    this.deals = const [],
    this.isLoading = false,
    this.selectedStageId,
    this.errorMessage,
  });

  DealsState copyWith({
    List<PipelineStageModel>? stages,
    List<DealModel>? deals,
    bool? isLoading,
    String? selectedStageId,
    String? errorMessage,
  }) {
    return DealsState(
      stages: stages ?? this.stages,
      deals: deals ?? this.deals,
      isLoading: isLoading ?? this.isLoading,
      selectedStageId: selectedStageId ?? this.selectedStageId,
      errorMessage: errorMessage,
    );
  }

  List<DealModel> get filteredDeals {
    if (selectedStageId == null || selectedStageId == 'all') return deals;
    return deals.where((d) => d.stageId == selectedStageId).toList();
  }

  double get totalPipelineValue {
    return deals.fold(0.0, (acc, item) => acc + item.value);
  }
}

final dealsProvider = StateNotifierProvider<DealsNotifier, DealsState>((ref) {
  final api = ref.watch(apiClientProvider);
  final activeProject = ref.watch(activeProjectProvider);
  final notifier = DealsNotifier(api: api, projectId: activeProject?.id);

  if (activeProject != null) {
    notifier.fetchPipeline();
  }

  return notifier;
});

class DealsNotifier extends StateNotifier<DealsState> {
  final ApiClient _api;
  final String? _projectId;

  DealsNotifier({required ApiClient api, String? projectId})
      : _api = api,
        _projectId = projectId,
        super(const DealsState());

  Future<void> fetchPipeline() async {
    if (_projectId == null) return;
    state = state.copyWith(isLoading: true, errorMessage: null);

    try {
      final stagesData = await _api.get(ApiEndpoints.dealStages(_projectId));
      final stages = (stagesData as List? ?? [])
          .map((s) => PipelineStageModel.fromJson(s as Map<String, dynamic>))
          .toList();

      final dealsData = await _api.get(ApiEndpoints.deals(_projectId));
      final deals = (dealsData as List? ?? [])
          .map((d) => DealModel.fromJson(d as Map<String, dynamic>))
          .toList();

      state = state.copyWith(
        stages: stages,
        deals: deals,
        isLoading: false,
      );
    } catch (_) {
      // Fallback to sample pipeline if backend has no stages created yet
      final defaultStages = [
        const PipelineStageModel(id: 'lead', name: 'Lead', index: 0),
        const PipelineStageModel(id: 'contacted', name: 'Contacted', index: 1),
        const PipelineStageModel(id: 'proposal', name: 'Proposal', index: 2),
        const PipelineStageModel(id: 'won', name: 'Won', index: 3),
      ];
      state = state.copyWith(
        stages: defaultStages,
        deals: const [],
        isLoading: false,
      );
    }
  }

  void selectStage(String? stageId) {
    state = state.copyWith(selectedStageId: stageId);
  }
}
