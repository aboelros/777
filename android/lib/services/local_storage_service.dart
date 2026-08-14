import 'package:shared_preferences/shared_preferences.dart';

class LocalStorageService {
  static final LocalStorageService _instance = LocalStorageService._internal();

  factory LocalStorageService() => _instance;

  LocalStorageService._internal();

  static const String _tokenKey = 'auth_token';
  static const String _biometricEnabledKey = 'biometric_enabled';
  static const String _lastProjectIdKey = 'last_project_id';
  static const String _chatHistoryPrefix = 'chat_history_';

  // ── Instance methods ──────────────────────────────────────────────────────

  Future<void> saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, token);
  }

  Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_tokenKey);
  }

  Future<void> clearToken() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
  }

  Future<void> saveBiometricEnabled(bool val) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_biometricEnabledKey, val);
  }

  Future<bool> getBiometricEnabled() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool(_biometricEnabledKey) ?? false;
  }

  Future<void> saveLastProjectId(String id) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_lastProjectIdKey, id);
  }

  Future<String?> getLastProjectId() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_lastProjectIdKey);
  }

  Future<void> saveChatHistory(String projectId, String jsonString) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('$_chatHistoryPrefix$projectId', jsonString);
  }

  Future<String?> getChatHistory(String projectId) async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('$_chatHistoryPrefix$projectId');
  }

  Future<void> clearAll() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
  }

  // ── Static convenience accessors (delegates to singleton instance) ────────

  static Future<void> staticSaveToken(String token) =>
      _instance.saveToken(token);
  static Future<String?> staticGetToken() => _instance.getToken();
  static Future<void> staticClearToken() => _instance.clearToken();
  static Future<void> staticSaveChatHistory(
          String projectId, String jsonString) =>
      _instance.saveChatHistory(projectId, jsonString);
  static Future<String?> staticGetChatHistory(String projectId) =>
      _instance.getChatHistory(projectId);
}
