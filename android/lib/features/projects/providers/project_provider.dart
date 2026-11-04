import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/network/api_endpoints.dart';
import '../../auth/providers/auth_provider.dart';
import '../models/project_model.dart';

class ProjectState {
  final List<ProjectModel> projects;
  final ProjectModel? activeProject;
  final bool isLoading;
  final String? error;

  const ProjectState({
    this.projects = const [],
    this.activeProject,
    this.isLoading = false,
    this.error,
  });

  ProjectState copyWith({
    List<ProjectModel>? projects,
    ProjectModel? activeProject,
    bool? isLoading,
    String? error,
  }) {
    return ProjectState(
      projects: projects ?? this.projects,
      activeProject: activeProject ?? this.activeProject,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

final projectProvider =
    StateNotifierProvider<ProjectNotifier, ProjectState>((ref) {
  final api = ref.watch(apiClientProvider);
  final storage = ref.watch(secureStorageProvider);
  return ProjectNotifier(api: api, storage: storage);
});

final activeProjectProvider = Provider<ProjectModel?>((ref) {
  return ref.watch(projectProvider).activeProject;
});

class ProjectNotifier extends StateNotifier<ProjectState> {
  final dynamic _api;
  final dynamic _storage;

  ProjectNotifier({required dynamic api, required dynamic storage})
      : _api = api,
        _storage = storage,
        super(const ProjectState());

  Future<void> fetchProjects() async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final response = await _api.get(ApiEndpoints.projects);
      List<ProjectModel> list = [];

      if (response is List) {
        list = response
            .whereType<Map<String, dynamic>>()
            .map((e) => ProjectModel.fromJson(e))
            .toList();
      }

      final savedId = await _storage.getActiveProjectId();
      ProjectModel? matched;
      if (savedId != null && list.isNotEmpty) {
        matched = list.firstWhere(
          (p) => p.id == savedId,
          orElse: () => list.first,
        );
      } else if (list.isNotEmpty) {
        matched = list.first;
      }

      if (matched != null) {
        await _storage.saveActiveProjectId(matched.id);
      }

      state = state.copyWith(
        projects: list,
        activeProject: matched,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  Future<void> selectProject(ProjectModel project) async {
    if (state.activeProject?.id == project.id) return;
    await _storage.saveActiveProjectId(project.id);
    state = state.copyWith(activeProject: project);
  }

  void reset() {
    state = const ProjectState();
  }
}
