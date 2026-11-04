import 'dart:async';
import 'package:dio/dio.dart';
import '../config/app_config.dart';
import '../storage/secure_storage_service.dart';
import 'api_endpoints.dart';

/// Interceptor that attaches JWT Bearer tokens and orchestrates atomic token refresh.
class AuthInterceptor extends QueuedInterceptor {
  final SecureStorageService _storage;
  final VoidCallback? _onUnauthorized;
  final Dio _refreshDio;

  AuthInterceptor({
    required SecureStorageService storage,
    VoidCallback? onUnauthorized,
  })  : _storage = storage,
        _onUnauthorized = onUnauthorized,
        _refreshDio = Dio(
          BaseOptions(
            baseUrl: AppConfig.activeBaseUrl,
            connectTimeout: AppConfig.connectTimeout,
            receiveTimeout: AppConfig.receiveTimeout,
            headers: {'Content-Type': 'application/json'},
          ),
        );

  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    // Skip token for unauthenticated endpoints
    if (options.path.contains(ApiEndpoints.login) ||
        options.path.contains(ApiEndpoints.register) ||
        options.path.contains(ApiEndpoints.refresh)) {
      return handler.next(options);
    }

    final token = await _storage.getAccessToken();
    if (token != null && token.isNotEmpty) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    return handler.next(options);
  }

  @override
  Future<void> onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    if (err.response?.statusCode != 401) {
      return handler.next(err);
    }

    // Do not attempt refresh if the failed request was login, register, or refresh itself
    final path = err.requestOptions.path;
    if (path.contains(ApiEndpoints.login) ||
        path.contains(ApiEndpoints.register) ||
        path.contains(ApiEndpoints.refresh)) {
      return handler.next(err);
    }

    final refreshToken = await _storage.getRefreshToken();
    if (refreshToken == null || refreshToken.isEmpty) {
      _onUnauthorized?.call();
      return handler.next(err);
    }

    try {
      final response = await _refreshDio.post(
        ApiEndpoints.refresh,
        data: {'refresh_token': refreshToken},
      );

      final data = response.data;
      if (data is Map<String, dynamic> &&
          data.containsKey('access_token') &&
          data.containsKey('refresh_token')) {
        final newAccess = data['access_token'] as String;
        final newRefresh = data['refresh_token'] as String;

        await _storage.saveTokens(
          accessToken: newAccess,
          refreshToken: newRefresh,
        );

        // Retry the original failed request with the new access token
        final requestOptions = err.requestOptions;
        requestOptions.headers['Authorization'] = 'Bearer $newAccess';

        final retryDio = Dio(
          BaseOptions(
            baseUrl: AppConfig.activeBaseUrl,
            headers: requestOptions.headers,
          ),
        );

        final retryResponse = await retryDio.request(
          requestOptions.path,
          options: Options(
            method: requestOptions.method,
            headers: requestOptions.headers,
            responseType: requestOptions.responseType,
            contentType: requestOptions.contentType,
          ),
          data: requestOptions.data,
          queryParameters: requestOptions.queryParameters,
        );

        return handler.resolve(retryResponse);
      } else {
        _onUnauthorized?.call();
        return handler.next(err);
      }
    } catch (_) {
      // Refresh failed (e.g. revoked or expired refresh token)
      await _storage.clearAll();
      _onUnauthorized?.call();
      return handler.next(err);
    }
  }
}

typedef VoidCallback = void Function();
