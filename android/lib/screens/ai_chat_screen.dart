import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../widgets/chat_bubble.dart';
import '../widgets/typing_indicator.dart';
import '../providers/chat_provider.dart';
import '../providers/project_provider.dart';
import '../services/local_storage_service.dart';

class AiChatScreen extends StatefulWidget {
  const AiChatScreen({super.key});

  @override
  State<AiChatScreen> createState() => _AiChatScreenState();
}

class _AiChatScreenState extends State<AiChatScreen> {
  final TextEditingController _textController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  late ChatProvider _chatProvider;
  late ProjectProvider _projectProvider;

  @override
  void initState() {
    super.initState();
    _chatProvider = Provider.of<ChatProvider>(context, listen: false);
    _projectProvider = Provider.of<ProjectProvider>(context, listen: false);
    _loadChatHistory();
  }

  final _storage = LocalStorageService();

  Future<void> _loadChatHistory() async {
    final projectId = _projectProvider.currentProjectId;
    if (projectId != null) {
      final historyJson = await _storage.getChatHistory(projectId);
      if (historyJson != null) {
        try {
          final List<dynamic> decoded = jsonDecode(historyJson);
          final messages = decoded.map((e) => ChatMessage.fromJson(e)).toList();
          _chatProvider.loadMessages(messages);
          _scrollToBottom();
        } catch (e) {
          debugPrint('Error parsing chat history: $e');
        }
      }
    }
  }

  Future<void> _saveChatHistory() async {
    final projectId = _projectProvider.currentProjectId;
    if (projectId != null) {
      final messages = _chatProvider.messages.map((e) => e.toJson()).toList();
      final historyJson = jsonEncode(messages);
      await _storage.saveChatHistory(projectId, historyJson);
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  Future<void> _sendMessage(String text) async {
    final content = text.trim();
    if (content.isEmpty) return;

    _textController.clear();
    final projectId = _projectProvider.currentProjectId ?? '';
    
    await _chatProvider.sendMessage(content, projectId);
    await _saveChatHistory();
    _scrollToBottom();
  }

  void _clearChat() {
    _chatProvider.loadMessages([]);
    _saveChatHistory();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        title: const Text('AI Agent'),
        backgroundColor: const Color(0xFF1E293B),
        actions: [
          IconButton(
            icon: const Icon(Icons.delete_outline),
            onPressed: _clearChat,
          ),
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () {},
          ),
        ],
      ),
      body: Consumer<ChatProvider>(
        builder: (context, chatProvider, child) {
          final messages = chatProvider.messages;

          return Column(
            children: [
              Expanded(
                child: messages.isEmpty
                    ? _buildEmptyState()
                    : ListView.builder(
                        controller: _scrollController,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        itemCount: messages.length + (chatProvider.isLoading ? 1 : 0),
                        itemBuilder: (context, index) {
                          if (index == messages.length) {
                            return const Padding(
                              padding: EdgeInsets.only(left: 16.0, top: 8.0, bottom: 8.0),
                              child: Align(
                                alignment: Alignment.centerLeft,
                                child: TypingIndicator(),
                              ),
                            );
                          }
                          final msg = messages[index];
                          return ChatBubble(
                            content: msg.content,
                            isUser: msg.isUser,
                            timestamp: msg.timestamp,
                            isLatest: index == messages.length - 1,
                          );
                        },
                      ),
              ),
              _buildInputArea(),
            ],
          );
        },
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.smart_toy, size: 64, color: Colors.grey),
          const SizedBox(height: 16),
          const Text(
            'Ask your AI Sales Agent anything',
            style: TextStyle(color: Colors.grey, fontSize: 16),
          ),
          const SizedBox(height: 32),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            alignment: WrapAlignment.center,
            children: [
              _buildSuggestionChip('Today\'s orders'),
              _buildSuggestionChip('Sales summary'),
              _buildSuggestionChip('Top customers'),
              _buildSuggestionChip('Pending orders'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSuggestionChip(String label) {
    return ActionChip(
      label: Text(label, style: const TextStyle(color: Colors.white)),
      backgroundColor: const Color(0xFF1E293B),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
        side: const BorderSide(color: Color(0xFF6366F1)),
      ),
      onPressed: () {
        _textController.text = label;
        _sendMessage(label);
      },
    );
  }

  Widget _buildInputArea() {
    return Container(
      padding: const EdgeInsets.all(16),
      color: const Color(0xFF1E293B),
      child: SafeArea(
        child: Row(
          children: [
            Expanded(
              child: TextField(
                controller: _textController,
                style: const TextStyle(color: Colors.white),
                decoration: InputDecoration(
                  hintText: 'Type a message...',
                  hintStyle: const TextStyle(color: Colors.grey),
                  filled: true,
                  fillColor: const Color(0xFF0F172A),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(24),
                    borderSide: BorderSide.none,
                  ),
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 20,
                    vertical: 12,
                  ),
                ),
                onSubmitted: _sendMessage,
              ),
            ),
            const SizedBox(width: 12),
            Container(
              decoration: const BoxDecoration(
                shape: BoxShape.circle,
                gradient: LinearGradient(
                  colors: [Color(0xFF6366F1), Color(0xFF818CF8)],
                ),
              ),
              child: IconButton(
                icon: const Icon(Icons.send, color: Colors.white),
                onPressed: () => _sendMessage(_textController.text),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
