import 'package:flutter/material.dart';
import '../services/api_service.dart';

class OrderProvider extends ChangeNotifier {
  final ApiService _apiService = ApiService();
  List<dynamic> _orders = [];
  bool _isLoading = false;
  String? _error;
  int _currentPage = 1;
  bool _hasMore = true;

  List<dynamic> get orders => _orders;
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get hasMore => _hasMore;

  Future<void> fetchOrders(String projectId) async {
    _isLoading = true;
    _error = null;
    _currentPage = 1;
    _hasMore = true;
    _orders = [];
    notifyListeners();

    try {
      final response = await _apiService.get('/orders/$projectId?page=$_currentPage&limit=20');
      if (response is List) {
        _orders = response;
        if (response.isEmpty || response.length < 20) _hasMore = false;
      } else if (response is Map && response.containsKey('items')) {
        _orders = response['items'] as List;
        if ((response['items'] as List).isEmpty || (response['items'] as List).length < 20) _hasMore = false;
      }
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> fetchMoreOrders(String projectId) async {
    if (!_hasMore || _isLoading) return;

    _currentPage++;
    notifyListeners(); // Optionally notify if you want to show a loading indicator at the bottom

    try {
      final response = await _apiService.get('/orders/$projectId?page=$_currentPage&limit=20');
      List<dynamic> newOrders = [];
      if (response is List) {
        newOrders = response;
      } else if (response is Map && response.containsKey('items')) {
        newOrders = response['items'] as List;
      }

      if (newOrders.isEmpty) {
        _hasMore = false;
      } else {
        _orders.addAll(newOrders);
        if (newOrders.length < 20) _hasMore = false;
      }
    } catch (e) {
      _error = e.toString();
    } finally {
      notifyListeners();
    }
  }
}
