import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:local_auth/local_auth.dart';
import 'package:provider/provider.dart';
import '../providers/theme_provider.dart';
import '../providers/auth_provider.dart';
import '../services/local_storage_service.dart';
import '../theme/app_theme.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({Key? key}) : super(key: key);

  @override
  _SettingsScreenState createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  PackageInfo? _packageInfo;
  bool _biometricEnabled = false;
  bool _biometricAvailable = false;
  final LocalStorageService _storageService = LocalStorageService();
  final LocalAuthentication _auth = LocalAuthentication();

  @override
  void initState() {
    super.initState();
    _initSettings();
  }

  Future<void> _initSettings() async {
    final info = await PackageInfo.fromPlatform();
    final canCheckBiometrics = await _auth.canCheckBiometrics;
    final isDeviceSupported = await _auth.isDeviceSupported();
    
    bool enabled = false;
    try {
      enabled = await _storageService.getBiometricEnabled();
    } catch (e) {
      enabled = false;
    }
    
    setState(() {
      _packageInfo = info;
      _biometricAvailable = canCheckBiometrics || isDeviceSupported;
      _biometricEnabled = enabled;
    });
  }

  void _toggleBiometric(bool value) async {
    setState(() => _biometricEnabled = value);
    try {
      await _storageService.saveBiometricEnabled(value);
    } catch (e) {
      // Ignore exception if it fails to save
    }
  }

  @override
  Widget build(BuildContext context) {
    final themeProvider = Provider.of<ThemeProvider>(context);
    final authProvider = Provider.of<AuthProvider>(context);
    final email = authProvider.user?['email'] as String? ?? 'user@example.com';
    final initial = email.isNotEmpty ? email[0].toUpperCase() : 'U';
    final role = authProvider.user?['role'] as String? ?? 'ADMIN';

    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('Settings'),
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Profile section
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppTheme.surfaceDark,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: Colors.white.withOpacity(0.05)),
            ),
            child: Row(
              children: [
                Container(
                  width: 64,
                  height: 64,
                  decoration: const BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: LinearGradient(
                      colors: [AppTheme.primary, AppTheme.accent],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                  ),
                  child: Center(
                    child: Text(
                      initial,
                      style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Colors.white),
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        email,
                        style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white),
                      ),
                      const SizedBox(height: 8),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                        decoration: BoxDecoration(
                          color: AppTheme.primary.withOpacity(0.2),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Text(
                          role,
                          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: AppTheme.primary),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),
          
          // App Settings section
          const Text('App Settings', style: TextStyle(color: Colors.grey, fontSize: 14, fontWeight: FontWeight.w600)),
          const SizedBox(height: 8),
          Container(
            decoration: BoxDecoration(
              color: AppTheme.surfaceDark,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: Colors.white.withOpacity(0.05)),
            ),
            child: Column(
              children: [
                ListTile(
                  leading: const Icon(Icons.dark_mode, color: Colors.white70),
                  title: const Text('Dark Mode', style: TextStyle(color: Colors.white)),
                  trailing: Switch(
                    value: themeProvider.isDarkMode,
                    onChanged: (val) => themeProvider.toggleTheme(),
                    activeColor: AppTheme.primary,
                  ),
                ),
                if (_biometricAvailable) ...[
                  const Divider(color: Colors.white12, height: 1),
                  ListTile(
                    leading: const Icon(Icons.fingerprint, color: Colors.white70),
                    title: const Text('Biometric Login', style: TextStyle(color: Colors.white)),
                    trailing: Switch(
                      value: _biometricEnabled,
                      onChanged: _toggleBiometric,
                      activeColor: AppTheme.primary,
                    ),
                  ),
                ],
                const Divider(color: Colors.white12, height: 1),
                ListTile(
                  leading: const Icon(Icons.notifications, color: Colors.white70),
                  title: const Text('Notifications', style: TextStyle(color: Colors.white)),
                  trailing: const Icon(Icons.chevron_right, color: Colors.white54),
                  onTap: () {},
                ),
                const Divider(color: Colors.white12, height: 1),
                ListTile(
                  leading: const Icon(Icons.language, color: Colors.white70),
                  title: const Text('Language', style: TextStyle(color: Colors.white)),
                  trailing: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: const [
                      Text('English', style: TextStyle(color: Colors.white54)),
                      SizedBox(width: 8),
                      Icon(Icons.chevron_right, color: Colors.white54),
                    ],
                  ),
                  onTap: () {},
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),

          // Account section
          const Text('Account', style: TextStyle(color: Colors.grey, fontSize: 14, fontWeight: FontWeight.w600)),
          const SizedBox(height: 8),
          Container(
            decoration: BoxDecoration(
              color: AppTheme.surfaceDark,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: Colors.white.withOpacity(0.05)),
            ),
            child: Column(
              children: [
                ListTile(
                  leading: const Icon(Icons.dns, color: Colors.white70),
                  title: const Text('API Server', style: TextStyle(color: Colors.white)),
                  subtitle: const Text('api.onrender.com', style: TextStyle(color: Colors.grey, fontSize: 12)),
                  trailing: IconButton(
                    icon: const Icon(Icons.copy, color: Colors.white54, size: 20),
                    onPressed: () {
                      Clipboard.setData(const ClipboardData(text: 'https://api.onrender.com'));
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('API Server URL copied'), 
                          backgroundColor: AppTheme.surfaceDark
                        ),
                      );
                    },
                  ),
                ),
                const Divider(color: Colors.white12, height: 1),
                ListTile(
                  leading: const Icon(Icons.help_outline, color: Colors.white70),
                  title: const Text('Help & Support', style: TextStyle(color: Colors.white)),
                  onTap: () {},
                ),
                const Divider(color: Colors.white12, height: 1),
                ListTile(
                  leading: const Icon(Icons.logout, color: AppTheme.error),
                  title: const Text('Log Out', style: TextStyle(color: AppTheme.error)),
                  onTap: () async {
                    final confirm = await showDialog<bool>(
                      context: context,
                      builder: (ctx) => AlertDialog(
                        backgroundColor: AppTheme.surfaceDark,
                        title: const Text('Log Out', style: TextStyle(color: Colors.white)),
                        content: const Text('Are you sure you want to log out?', style: TextStyle(color: Colors.white70)),
                        actions: [
                          TextButton(
                            onPressed: () => Navigator.pop(ctx, false),
                            child: const Text('Cancel', style: TextStyle(color: Colors.grey)),
                          ),
                          TextButton(
                            onPressed: () => Navigator.pop(ctx, true),
                            child: const Text('Log Out', style: TextStyle(color: AppTheme.error)),
                          ),
                        ],
                      ),
                    );
                    if (confirm == true) {
                      await authProvider.logout();
                      if (mounted) {
                         Navigator.of(context).pushReplacementNamed('/login');
                      }
                    }
                  },
                ),
              ],
            ),
          ),
          
          const SizedBox(height: 32),
          // Version info
          Center(
            child: Text(
              'Version ${_packageInfo?.version ?? '1.0.0'}',
              style: const TextStyle(color: Colors.grey, fontSize: 12),
            ),
          ),
          const SizedBox(height: 32),
        ],
      ),
    );
  }
}
