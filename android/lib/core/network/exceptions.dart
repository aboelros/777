/// Typed domain exceptions representing mapped HTTP and network errors.
class ApiException implements Exception {
  final String message;
  final int? statusCode;
  final dynamic details;

  const ApiException({
    required this.message,
    this.statusCode,
    this.details,
  });

  @override
  String toString() => 'ApiException($statusCode): $message';
}

/// Authentication failure (HTTP 401).
class AuthException extends ApiException {
  const AuthException(
      {super.message = 'Authentication required or session expired.'})
      : super(statusCode: 401);
}

/// Permission denied (HTTP 403).
class PermissionException extends ApiException {
  const PermissionException(
      {super.message = 'Access denied. Insufficient permissions.'})
      : super(statusCode: 403);
}

/// Resource or tenant not found (HTTP 404).
class NotFoundException extends ApiException {
  const NotFoundException({super.message = 'Requested resource not found.'})
      : super(statusCode: 404);
}

/// Unprocessable entity or validation error (HTTP 422).
class ValidationException extends ApiException {
  final Map<String, dynamic>? validationErrors;

  const ValidationException({
    super.message = 'Invalid request parameters.',
    this.validationErrors,
  }) : super(statusCode: 422, details: validationErrors);
}

/// Rate limit exceeded (HTTP 429).
class RateLimitException extends ApiException {
  const RateLimitException(
      {super.message = 'Rate limit exceeded. Please wait.'})
      : super(statusCode: 429);
}

/// Internal server error (HTTP 500+).
class ServerException extends ApiException {
  const ServerException(
      {super.message = 'Server encountered an unexpected error.'})
      : super(statusCode: 500);
}

/// Network timeout or connectivity loss.
class NetworkException extends ApiException {
  const NetworkException(
      {super.message = 'Network connection failed or timed out.'})
      : super(statusCode: null);
}
