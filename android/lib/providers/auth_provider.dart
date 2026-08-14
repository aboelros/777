import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../services/local_storage_service.dart';

class AuthProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();
  final LocalStorageService _storage = LocalStorageService();
  bool _isAuthenticated = false;
  bool _isLoading = true;
  Map<String, dynamic>? _user;

  bool get isAuthenticated => _isAuthenticated;
  bool get isLoading => _isLoading;
  Map<String, dynamic>? get user => _user;

  AuthProvider() {
    _checkAuthStatus();
  }

  Future<void> _checkAuthStatus() async {
    _isLoading = true;
    notifyListeners();

    final token = await _storage.getToken();
    if (token != null) {
      try {
        final response = await _apiService.get('/auth/me');
        _user = response;
        _isAuthenticated = true;
      } catch (e) {
        await _storage.clearToken();
        _isAuthenticated = false;
      }
    } else {
      _isAuthenticated = false;
    }

    _isLoading = false;
    notifyListeners();
  }

  Future<bool> login(String email, String password) async {
    _isLoading = true;
    notifyListeners();

    try {
      final response = await _apiService.postForm('/auth/login', {
        'username': email,
        'password': password,
      });

      final token = response['access_token'];
      if (token != null) {
        await _storage.saveToken(token);
        _isAuthenticated = true;
        _user = await _apiService.get('/auth/me');
        _isLoading = false;
        notifyListeners();
        return true;
      }
    } catch (e) {
      debugPrint('Login error: $e');
    }

    _isLoading = false;
    notifyListeners();
    return false;
  }

  Future<void> logout() async {
    await _storage.clearToken();
    _isAuthenticated = false;
    _user = null;
    notifyListeners();
  }
}
