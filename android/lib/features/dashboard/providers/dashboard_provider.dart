import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/network/api_endpoints.dart';
import '../../auth/providers/auth_provider.dart';
import '../../projects/providers/project_provider.dart';
import '../models/dashboard_stats_model.dart';

class DashboardState {
  final DashboardStatsModel? stats;
  final String selectedPeriod;
  final bool isLoading;
  final String? error;

  const DashboardState({
    this.stats,
    this.selectedPeriod = 'today',
    this.isLoading = false,
    this.error,
  });

  DashboardState copyWith({
    DashboardStatsModel? stats,
    String? selectedPeriod,
    bool? isLoading,
    String? error,
  }) {
    return DashboardState(
      stats: stats ?? this.stats,
      selectedPeriod: selectedPeriod ?? this.selectedPeriod,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }

  PeriodMetrics get currentMetrics =>
      stats?.getForPeriod(selectedPeriod) ?? const PeriodMetrics();
}

final dashboardProvider =
    StateNotifierProvider<DashboardNotifier, DashboardState>((ref) {
  final api = ref.watch(apiClientProvider);
  final activeProject = ref.watch(activeProjectProvider);
  return DashboardNotifier(api: api, projectId: activeProject?.id);
});

class DashboardNotifier extends StateNotifier<DashboardState> {
  final dynamic _api;
  final String? _projectId;

  DashboardNotifier({required dynamic api, String? projectId})
      : _api = api,
        _projectId = projectId,
        super(const DashboardState()) {
    if (_projectId != null) {
      loadStats();
    }
  }

  Future<void> loadStats() async {
    if (_projectId == null) return;
    state = state.copyWith(isLoading: true, error: null);

    try {
      final response =
          await _api.get(ApiEndpoints.dashboardSummary(_projectId));
      if (response is Map<String, dynamic>) {
        final stats = DashboardStatsModel.fromJson(response);
        state = state.copyWith(stats: stats, isLoading: false);
      } else {
        state = state.copyWith(
          isLoading: false,
          error: 'Unexpected dashboard data format.',
        );
      }
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  void selectPeriod(String period) {
    if (state.selectedPeriod != period) {
      state = state.copyWith(selectedPeriod: period);
    }
  }
}
