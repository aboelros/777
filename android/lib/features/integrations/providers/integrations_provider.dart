import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/network/api_endpoints.dart';
import '../../auth/providers/auth_provider.dart';
import '../../projects/providers/project_provider.dart';
import '../models/integration_model.dart';

class IntegrationsState {
  final List<IntegrationModel> integrations;
  final bool isLoading;
  final String? error;

  const IntegrationsState({
    this.integrations = const [],
    this.isLoading = false,
    this.error,
  });

  IntegrationsState copyWith({
    List<IntegrationModel>? integrations,
    bool? isLoading,
    String? error,
  }) {
    return IntegrationsState(
      integrations: integrations ?? this.integrations,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

final integrationsProvider =
    StateNotifierProvider<IntegrationsNotifier, IntegrationsState>((ref) {
  final api = ref.watch(apiClientProvider);
  final activeProject = ref.watch(activeProjectProvider);
  return IntegrationsNotifier(api: api, projectId: activeProject?.id);
});

class IntegrationsNotifier extends StateNotifier<IntegrationsState> {
  final dynamic _api;
  final String? _projectId;

  IntegrationsNotifier({required dynamic api, String? projectId})
      : _api = api,
        _projectId = projectId,
        super(const IntegrationsState()) {
    if (_projectId != null) {
      loadIntegrations();
    }
  }

  Future<void> loadIntegrations() async {
    if (_projectId == null) return;
    state = state.copyWith(isLoading: true, error: null);

    try {
      final response = await _api.get(ApiEndpoints.integrations(_projectId));
      List<IntegrationModel> list = [];
      if (response is List) {
        list = response
            .whereType<Map<String, dynamic>>()
            .map((e) => IntegrationModel.fromJson(e))
            .toList();
      }
      state = state.copyWith(integrations: list, isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }
}
