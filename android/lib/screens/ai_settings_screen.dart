import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/project_provider.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';

class AISettingsScreen extends StatefulWidget {
  const AISettingsScreen({Key? key}) : super(key: key);

  @override
  _AISettingsScreenState createState() => _AISettingsScreenState();
}

class _AISettingsScreenState extends State<AISettingsScreen> {
  final _promptController = TextEditingController();
  final ApiService _apiService = ApiService();
  bool _isLoading = false;
  String? _instructionId;
  bool _isActive = true;

  @override
  void initState() {
    super.initState();
    _promptController.addListener(() {
      setState(() {});
    });
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadInstructions();
    });
  }

  @override
  void dispose() {
    _promptController.dispose();
    super.dispose();
  }

  Future<void> _loadInstructions() async {
    final projectProvider = Provider.of<ProjectProvider>(context, listen: false);
    final projectId = projectProvider.activeProject?.id;
    if (projectId == null) return;

    setState(() => _isLoading = true);
    try {
      final res = await _apiService.get('/bot-training/$projectId/instructions');
      if (res is List && res.isNotEmpty) {
        final instruction = res.first;
        setState(() {
          _instructionId = instruction['id'];
          _promptController.text = instruction['content'] ?? '';
          _isActive = instruction['is_active'] ?? true;
        });
      }
    } catch (e) {
      debugPrint('Error loading instructions: $e');
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _saveInstructions() async {
    final projectProvider = Provider.of<ProjectProvider>(context, listen: false);
    final projectId = projectProvider.activeProject?.id;
    if (projectId == null) return;

    setState(() => _isLoading = true);
    try {
      if (_instructionId != null) {
        await _apiService.put(
          '/bot-training/$projectId/instructions/$_instructionId',
          {'content': _promptController.text, 'is_active': _isActive},
        );
      } else {
        await _apiService.post(
          '/bot-training/$projectId/instructions',
          {'content': _promptController.text, 'is_active': _isActive},
        );
      }
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Saved successfully'), backgroundColor: AppTheme.success),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error saving: $e'), backgroundColor: AppTheme.error),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _toggleActive(bool value) async {
    final projectProvider = Provider.of<ProjectProvider>(context, listen: false);
    final projectId = projectProvider.activeProject?.id;
    if (projectId == null || _instructionId == null) return;

    setState(() {
      _isActive = value;
      _isLoading = true;
    });

    try {
      await _apiService.put(
        '/bot-training/$projectId/instructions/$_instructionId/toggle',
        {'is_active': value},
      );
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error toggling state: $e'), backgroundColor: AppTheme.error),
        );
      }
      setState(() => _isActive = !value); // revert
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('AI Configuration'),
        backgroundColor: Colors.transparent,
        elevation: 0,
        actions: [
          TextButton(
            onPressed: _isLoading ? null : _saveInstructions,
            child: const Text('Save', style: TextStyle(color: AppTheme.primary, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
      body: _isLoading && _promptController.text.isEmpty
          ? const Center(child: CircularProgressIndicator(color: AppTheme.primary))
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: AppTheme.surfaceDark,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: Colors.white.withOpacity(0.05)),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('AI Assistant Status', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
                          SizedBox(height: 4),
                          Text('Enable or disable the AI responding', style: TextStyle(color: Colors.grey, fontSize: 12)),
                        ],
                      ),
                      Switch(
                        value: _isActive,
                        onChanged: _instructionId == null ? null : _toggleActive,
                        activeColor: AppTheme.primary,
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
                
                // Instructions section
                const Text('Instructions', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
                const SizedBox(height: 4),
                const Text('Each instruction shapes how your AI responds to customers.', style: TextStyle(color: Colors.grey, fontSize: 14)),
                const SizedBox(height: 16),
                Container(
                  decoration: BoxDecoration(
                    color: AppTheme.surfaceDark,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: Colors.white.withOpacity(0.05)),
                  ),
                  child: TextField(
                    controller: _promptController,
                    maxLines: 15,
                    maxLength: 4000,
                    style: const TextStyle(color: Colors.white),
                    decoration: const InputDecoration(
                      hintText: 'Enter system prompt here...',
                      hintStyle: TextStyle(color: Colors.grey),
                      border: InputBorder.none,
                      contentPadding: EdgeInsets.all(16),
                      counterText: '', // Hide default counter
                    ),
                  ),
                ),
                const SizedBox(height: 8),
                Align(
                  alignment: Alignment.centerRight,
                  child: Text(
                    '${_promptController.text.length} / 4000 characters',
                    style: const TextStyle(color: Colors.grey, fontSize: 12),
                  ),
                ),
              ],
            ),
    );
  }
}
