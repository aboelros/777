import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/network/api_client.dart';
import '../../../core/network/api_endpoints.dart';
import '../../../core/network/exceptions.dart';
import '../../../core/storage/secure_storage_service.dart';
import '../models/auth_state.dart';
import '../models/user_model.dart';

final secureStorageProvider = Provider<SecureStorageService>((ref) {
  return SecureStorageService();
});

final apiClientProvider = Provider<ApiClient>((ref) {
  final storage = ref.watch(secureStorageProvider);
  return ApiClient(storage: storage);
});

final authNotifierProvider =
    StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  final storage = ref.watch(secureStorageProvider);
  final api = ref.watch(apiClientProvider);
  final notifier = AuthNotifier(storage: storage, api: api);
  api.onUnauthorized = notifier.handleSessionExpired;
  return notifier;
});

class AuthNotifier extends StateNotifier<AuthState> {
  final SecureStorageService _storage;
  final ApiClient _api;

  AuthNotifier({
    required SecureStorageService storage,
    required ApiClient api,
  })  : _storage = storage,
        _api = api,
        super(AuthState.initial());

  Future<void> restoreSession() async {
    state = AuthState.authenticating();
    try {
      final token = await _storage.getAccessToken();
      if (token == null || token.isEmpty) {
        state = AuthState.unauthenticated();
        return;
      }

      final data = await _api.get(ApiEndpoints.me);
      if (data is Map<String, dynamic>) {
        final user = UserModel.fromJson(data);
        await _storage.saveUserMetadata(id: user.id, email: user.email);
        state = AuthState.authenticated(user);
      } else {
        await _storage.clearAll();
        state = AuthState.unauthenticated();
      }
    } catch (_) {
      await _storage.clearAll();
      state = AuthState.unauthenticated();
    }
  }

  Future<bool> login(String email, String password) async {
    state = AuthState.authenticating();
    try {
      final response = await _api.post(
        ApiEndpoints.login,
        data: {
          'email': email.trim().toLowerCase(),
          'password': password.trim(),
        },
      );

      if (response is Map<String, dynamic> &&
          response.containsKey('access_token')) {
        final accessToken = response['access_token'] as String;
        final refreshToken = response['refresh_token'] as String? ?? '';

        await _storage.saveTokens(
          accessToken: accessToken,
          refreshToken: refreshToken,
        );

        // Fetch current user details
        final meData = await _api.get(ApiEndpoints.me);
        final user = UserModel.fromJson(meData as Map<String, dynamic>);
        await _storage.saveUserMetadata(id: user.id, email: user.email);

        state = AuthState.authenticated(user);
        return true;
      } else {
        state = AuthState.error('Invalid server response format.');
        return false;
      }
    } on ApiException catch (e) {
      state = AuthState.error(e.message);
      return false;
    } catch (e) {
      state = AuthState.error('Login failed: ${e.toString()}');
      return false;
    }
  }

  Future<bool> register(String email, String password, String name) async {
    state = AuthState.authenticating();
    try {
      await _api.post(
        ApiEndpoints.register,
        data: {
          'email': email.trim().toLowerCase(),
          'password': password.trim(),
          'name': name.trim(),
        },
      );

      // Auto-login after successful registration
      return await login(email, password);
    } on ApiException catch (e) {
      state = AuthState.error(e.message);
      return false;
    } catch (e) {
      state = AuthState.error('Registration failed: ${e.toString()}');
      return false;
    }
  }

  Future<void> logout() async {
    try {
      final refreshToken = await _storage.getRefreshToken();
      await _api.post(
        ApiEndpoints.logout,
        data: refreshToken != null ? {'refresh_token': refreshToken} : null,
      );
    } catch (_) {}
    await _storage.clearAll();
    state = AuthState.unauthenticated();
  }

  void handleSessionExpired() {
    state = AuthState.unauthenticated();
  }
}
