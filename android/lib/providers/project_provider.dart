import 'package:flutter/material.dart';
import '../models/project_model.dart';
import '../services/api_service.dart';

class ProjectProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  
  List<Project> _projects = [];
  Project? _selectedProject;
  bool _isLoading = false;
  String? _errorMessage;

  List<Project> get projects => _projects;
  Project? get selectedProject => _selectedProject;
  // Aliases used by screens
  Project? get activeProject => _selectedProject;
  String? get currentProjectId => _selectedProject?.id;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  Future<void> fetchProjects() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final response = await _apiService.get('/projects');
      if (response != null && response is List) {
        _projects = response.map((data) => Project.fromJson(data)).toList();
        
        // Auto-select first project if none selected
        if (_projects.isNotEmpty && _selectedProject == null) {
          _selectedProject = _projects.first;
        }
      }
    } catch (e) {
      _errorMessage = 'Failed to load projects: $e';
    }

    _isLoading = false;
    notifyListeners();
  }

  void selectProject(Project project) {
    _selectedProject = project;
    notifyListeners();
  }
}
