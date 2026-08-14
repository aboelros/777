import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'local_storage_service.dart';

class ApiException implements Exception {
  final int statusCode;
  final String message;

  ApiException(this.statusCode, this.message);

  @override
  String toString() => 'ApiException: $statusCode - $message';
}

class ApiService {
  static const String baseUrl = 'https://ai-sales-bot-api-vdr6.onrender.com/api/v1';
  static const Duration _timeout = Duration(seconds: 30);
  final LocalStorageService _localStorage = LocalStorageService();
  VoidCallback? onUnauthorized;

  Future<Map<String, String>> _getHeaders() async {
    final token = await _localStorage.getToken();
    return {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  Future<dynamic> _handleResponse(http.Response response) async {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      if (response.body.isEmpty) return null;
      try {
        return jsonDecode(response.body);
      } catch (e) {
        return response.body;
      }
    } else if (response.statusCode == 401) {
      onUnauthorized?.call();
      throw ApiException(response.statusCode, 'Unauthorized');
    } else {
      String errorMessage = 'Unknown error';
      try {
        final body = jsonDecode(response.body);
        if (body is Map && body.containsKey('detail')) {
          errorMessage = body['detail'].toString();
        } else {
          errorMessage = response.body;
        }
      } catch (e) {
        errorMessage = response.body;
      }
      throw ApiException(response.statusCode, errorMessage);
    }
  }

  Future<dynamic> _executeWithRetry(Future<http.Response> Function() request) async {
    try {
      final response = await request().timeout(_timeout);
      return await _handleResponse(response);
    } on TimeoutException catch (_) {
      debugPrint('Request timed out, retrying once...');
    } on SocketException catch (_) {
      debugPrint('Network error, retrying once...');
    }
    
    await Future.delayed(const Duration(milliseconds: 500));
    try {
      final response = await request().timeout(_timeout);
      return await _handleResponse(response);
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException(500, 'Network request failed: $e');
    }
  }

  Future<dynamic> get(String endpoint) async {
    final headers = await _getHeaders();
    return _executeWithRetry(() => http.get(Uri.parse('$baseUrl$endpoint'), headers: headers));
  }

  Future<dynamic> post(String endpoint, Map<String, dynamic> body) async {
    final headers = await _getHeaders();
    return _executeWithRetry(() => http.post(
      Uri.parse('$baseUrl$endpoint'),
      headers: headers,
      body: jsonEncode(body),
    ));
  }

  Future<dynamic> postForm(String endpoint, Map<String, String> fields) async {
    final token = await _localStorage.getToken();
    final request = http.MultipartRequest('POST', Uri.parse('$baseUrl$endpoint'));
    if (token != null) {
      request.headers['Authorization'] = 'Bearer $token';
    }
    request.fields.addAll(fields);
    
    try {
      final streamedResponse = await request.send().timeout(_timeout);
      final response = await http.Response.fromStream(streamedResponse);
      return await _handleResponse(response);
    } catch (e) {
      throw ApiException(500, 'Form submission failed: $e');
    }
  }

  Future<dynamic> put(String endpoint, Map<String, dynamic> body) async {
    final headers = await _getHeaders();
    return _executeWithRetry(() => http.put(
      Uri.parse('$baseUrl$endpoint'),
      headers: headers,
      body: jsonEncode(body),
    ));
  }

  Future<dynamic> delete(String endpoint) async {
    final headers = await _getHeaders();
    return _executeWithRetry(() => http.delete(Uri.parse('$baseUrl$endpoint'), headers: headers));
  }
}
