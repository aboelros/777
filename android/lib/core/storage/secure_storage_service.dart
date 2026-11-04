import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Hardware-backed secure storage for sensitive credentials and session data.
class SecureStorageService {
  final FlutterSecureStorage _storage;

  SecureStorageService([FlutterSecureStorage? storage])
      : _storage = storage ??
            const FlutterSecureStorage(
              aOptions: AndroidOptions(
                encryptedSharedPreferences: true,
              ),
            );

  static const String _keyAccessToken = 'automind_access_token';
  static const String _keyRefreshToken = 'automind_refresh_token';
  static const String _keyUserId = 'automind_user_id';
  static const String _keyUserEmail = 'automind_user_email';
  static const String _keyActiveProjectId = 'automind_active_project_id';

  Future<void> saveTokens({
    required String accessToken,
    required String refreshToken,
  }) async {
    await _storage.write(key: _keyAccessToken, value: accessToken);
    await _storage.write(key: _keyRefreshToken, value: refreshToken);
  }

  Future<String?> getAccessToken() async {
    return await _storage.read(key: _keyAccessToken);
  }

  Future<String?> getRefreshToken() async {
    return await _storage.read(key: _keyRefreshToken);
  }

  Future<void> saveActiveProjectId(String projectId) async {
    await _storage.write(key: _keyActiveProjectId, value: projectId);
  }

  Future<String?> getActiveProjectId() async {
    return await _storage.read(key: _keyActiveProjectId);
  }

  Future<void> saveUserMetadata({
    required String id,
    required String email,
  }) async {
    await _storage.write(key: _keyUserId, value: id);
    await _storage.write(key: _keyUserEmail, value: email);
  }

  Future<void> clearAll() async {
    await _storage.deleteAll();
  }
}
