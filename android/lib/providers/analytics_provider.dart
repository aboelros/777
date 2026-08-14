import 'package:flutter/material.dart';
import '../services/api_service.dart';

class AnalyticsProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  Map<String, dynamic>? _data;
  bool _isLoading = false;
  String? _error;
  DateTime? _lastFetched;

  Map<String, dynamic>? get data => _data;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> fetchAnalytics(String projectId) async {
    // Cache: don't refetch if fetched within 5 minutes
    if (_lastFetched != null && DateTime.now().difference(_lastFetched!).inMinutes < 5) return;
    
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _apiService.get('/reports/$projectId/dashboard-summary');
      _data = response as Map<String, dynamic>?;
      _lastFetched = DateTime.now();
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  void invalidate() {
    _lastFetched = null;
  }
}
