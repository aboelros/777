import 'package:dio/dio.dart';
import '../config/app_config.dart';
import '../storage/secure_storage_service.dart';
import 'auth_interceptor.dart';
import 'exceptions.dart';

/// Central HTTP Client for Automind API communicating via Dio.
class ApiClient {
  late final Dio dio;
  final SecureStorageService storage;
  void Function()? onUnauthorized;

  ApiClient({
    required this.storage,
    this.onUnauthorized,
    String? baseUrl,
  }) {
    dio = Dio(
      BaseOptions(
        baseUrl: baseUrl ?? AppConfig.activeBaseUrl,
        connectTimeout: AppConfig.connectTimeout,
        receiveTimeout: AppConfig.receiveTimeout,
        sendTimeout: AppConfig.sendTimeout,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );

    dio.interceptors.add(
      AuthInterceptor(
        storage: storage,
        onUnauthorized: () => onUnauthorized?.call(),
      ),
    );
  }

  Future<dynamic> get(
    String path, {
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      final response = await dio.get(
        path,
        queryParameters: queryParameters,
        options: options,
      );
      return response.data;
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  Future<dynamic> post(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      final response = await dio.post(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
      );
      return response.data;
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  Future<dynamic> patch(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      final response = await dio.patch(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
      );
      return response.data;
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  Future<dynamic> put(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      final response = await dio.put(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
      );
      return response.data;
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  Future<dynamic> delete(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    try {
      final response = await dio.delete(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
      );
      return response.data;
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  ApiException _handleDioError(DioException e) {
    if (e.type == DioExceptionType.connectionTimeout ||
        e.type == DioExceptionType.receiveTimeout ||
        e.type == DioExceptionType.sendTimeout ||
        e.type == DioExceptionType.connectionError) {
      return const NetworkException();
    }

    final statusCode = e.response?.statusCode;
    final data = e.response?.data;
    String detail = 'Unexpected error occurred.';

    if (data is Map<String, dynamic>) {
      if (data['detail'] is String) {
        detail = data['detail'];
      } else if (data['detail'] is List) {
        detail = (data['detail'] as List)
            .map((x) => x['msg'] ?? x.toString())
            .join(', ');
      } else if (data['message'] is String) {
        detail = data['message'];
      }
    }

    switch (statusCode) {
      case 401:
        return AuthException(message: detail);
      case 403:
        return PermissionException(message: detail);
      case 404:
        return NotFoundException(message: detail);
      case 422:
        return ValidationException(
          message: detail,
          validationErrors: data is Map<String, dynamic> ? data : null,
        );
      case 429:
        return RateLimitException(message: detail);
      default:
        if (statusCode != null && statusCode >= 500) {
          return ServerException(message: detail);
        }
        return ApiException(
            message: detail, statusCode: statusCode, details: data);
    }
  }
}
