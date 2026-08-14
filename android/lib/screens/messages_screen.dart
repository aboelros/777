import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import 'package:shimmer/shimmer.dart';
import '../providers/project_provider.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';

class ConversationModel {
  final String id;
  final String? customerId;
  final String? customerName;
  final String? lastMessage;
  final DateTime? lastMessageAt;
  final int unreadCount;
  final String? channel;
  final bool aiEnabled;
  final bool isVip;
  final String? overallSentiment;
  final String? profileId;
  final String? orderId;
  final Map<String, dynamic>? recipient;

  const ConversationModel({
    required this.id,
    this.customerId,
    this.customerName,
    this.lastMessage,
    this.lastMessageAt,
    this.unreadCount = 0,
    this.channel,
    this.aiEnabled = false,
    this.isVip = false,
    this.overallSentiment,
    this.profileId,
    this.orderId,
    this.recipient,
  });

  factory ConversationModel.fromJson(Map<String, dynamic> json) => ConversationModel(
    id: json['id']?.toString() ?? '',
    customerId: json['customer_id']?.toString(),
    customerName: json['customer_name']?.toString(),
    lastMessage: json['last_message']?.toString(),
    lastMessageAt: json['last_message_at'] != null ? DateTime.tryParse(json['last_message_at'].toString()) : null,
    unreadCount: (json['unread_count'] as num?)?.toInt() ?? 0,
    channel: json['channel']?.toString() ?? json['provider']?.toString(),
    aiEnabled: json['ai_enabled'] == true,
    isVip: json['is_vip'] == true,
    overallSentiment: json['overall_sentiment']?.toString(),
    profileId: json['profile_id']?.toString(),
    orderId: json['order_id']?.toString(),
    recipient: json['recipient'] is Map ? Map<String, dynamic>.from(json['recipient'] as Map) : null,
  );
}

class MessageModel {
  final String id;
  final String content;
  final String direction;
  final bool aiGenerated;
  final String? status;
  final DateTime? createdAt;
  final String? contentType;
  final Map<String, dynamic>? extraData;

  const MessageModel({
    required this.id,
    required this.content,
    this.direction = 'inbound',
    this.aiGenerated = false,
    this.status,
    this.createdAt,
    this.contentType,
    this.extraData,
  });

  factory MessageModel.fromJson(Map<String, dynamic> json) => MessageModel(
    id: json['id']?.toString() ?? '',
    content: json['content']?.toString() ?? '',
    direction: json['direction']?.toString() ?? 'inbound',
    aiGenerated: json['ai_generated'] == true,
    status: json['status']?.toString(),
    createdAt: json['created_at'] != null ? DateTime.tryParse(json['created_at'].toString()) : null,
    contentType: json['content_type']?.toString(),
    extraData: json['extra_data'] is Map ? Map<String, dynamic>.from(json['extra_data'] as Map) : null,
  );
}

class MessagesScreen extends StatefulWidget {
  const MessagesScreen({super.key});

  @override
  State<MessagesScreen> createState() => _MessagesScreenState();
}

class _MessagesScreenState extends State<MessagesScreen> {
  ConversationModel? _selectedConversation;
  String _selectedFilter = 'All';

  void _handleConversationSelected(ConversationModel conversation, bool isMobile) {
    setState(() {
      _selectedConversation = conversation;
    });
    if (isMobile) {
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (_) => Scaffold(
            body: _ChatPanel(
              conversation: conversation,
              onClearSelection: () => Navigator.pop(context),
            ),
          ),
        ),
      ).then((_) {
        setState(() {
          _selectedConversation = null;
        });
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.backgroundDark,
      appBar: AppBar(
        title: const Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Messages', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            Text('Omni-channel Inbox', style: TextStyle(fontSize: 12, color: Colors.white70)),
          ],
        ),
        backgroundColor: AppTheme.surfaceDark,
        elevation: 0,
      ),
      body: LayoutBuilder(
        builder: (context, constraints) {
          final isMobile = constraints.maxWidth < 700;
          return Row(
            children: [
              if (!isMobile || _selectedConversation == null)
                SizedBox(
                  width: isMobile ? constraints.maxWidth : 320,
                  child: _ConversationListPanel(
                    selectedFilter: _selectedFilter,
                    onFilterChanged: (val) => setState(() => _selectedFilter = val),
                    selectedConversation: _selectedConversation,
                    onConversationSelected: (conv) => _handleConversationSelected(conv, isMobile),
                  ),
                ),
              if (!isMobile)
                Expanded(
                  child: _selectedConversation == null
                      ? _buildEmptyState()
                      : _ChatPanel(
                          conversation: _selectedConversation!,
                          onClearSelection: () => setState(() => _selectedConversation = null),
                        ),
                ),
            ],
          );
        },
      ),
    );
  }

  Widget _buildEmptyState() {
    return Container(
      color: AppTheme.backgroundDark,
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.message, size: 72, color: Colors.grey.withValues(alpha: 0.5)),
            const SizedBox(height: 16),
            Text(
              'Select a conversation',
              style: TextStyle(color: Colors.grey.withValues(alpha: 0.8), fontSize: 16),
            ),
          ],
        ),
      ),
    );
  }
}

class _ConversationListPanel extends StatefulWidget {
  final String selectedFilter;
  final ValueChanged<String> onFilterChanged;
  final ConversationModel? selectedConversation;
  final ValueChanged<ConversationModel> onConversationSelected;

  const _ConversationListPanel({
    required this.selectedFilter,
    required this.onFilterChanged,
    this.selectedConversation,
    required this.onConversationSelected,
  });

  @override
  State<_ConversationListPanel> createState() => _ConversationListPanelState();
}

class _ConversationListPanelState extends State<_ConversationListPanel> {
  final ApiService _apiService = ApiService();
  final TextEditingController _searchController = TextEditingController();
  List<ConversationModel> _conversations = [];
  bool _isLoading = true;
  Timer? _pollingTimer;

  final Map<String, Color> _filterColors = {
    'All': Colors.grey,
    'WhatsApp': Colors.green,
    'Telegram': Colors.blue,
    'Instagram': Colors.purpleAccent,
    'Facebook': Colors.indigo,
    'SMS': Colors.grey,
  };

  @override
  void initState() {
    super.initState();
    _fetchConversations();
    _startPolling();
  }

  @override
  void dispose() {
    _searchController.dispose();
    _pollingTimer?.cancel();
    super.dispose();
  }

  void _startPolling() {
    _pollingTimer = Timer.periodic(const Duration(seconds: 10), (_) {
      _fetchConversations(silent: true);
    });
  }

  Future<void> _fetchConversations({bool silent = false}) async {
    if (!silent && mounted) setState(() => _isLoading = true);
    final projectId = context.read<ProjectProvider>().currentProjectId;
    if (projectId == null) {
      if (mounted) setState(() => _isLoading = false);
      return;
    }
    try {
      String path = '/conversations/$projectId';
      if (widget.selectedFilter != 'All') {
        path += '?provider=${widget.selectedFilter.toLowerCase()}';
      }
      final response = await _apiService.get(path);
      if (response != null && response is List) {
        final parsed = response.map((e) => ConversationModel.fromJson(e as Map<String, dynamic>)).toList();
        if (mounted) {
          setState(() {
            _conversations = parsed;
            _isLoading = false;
          });
        }
      }
    } catch (e) {
      debugPrint('Error fetching conversations: $e');
      if (mounted) setState(() => _isLoading = false);
    }
  }

  void _onFilterTap(String filter) {
    widget.onFilterChanged(filter);
    _fetchConversations();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      color: AppTheme.surfaceDark,
      child: Column(
        children: [
          _buildSearchAndFilters(),
          Expanded(
            child: _isLoading && _conversations.isEmpty
                ? _buildShimmer()
                : RefreshIndicator(
                    onRefresh: () => _fetchConversations(),
                    child: ListView.builder(
                      itemCount: _conversations.length,
                      itemBuilder: (context, index) {
                        final conv = _conversations[index];
                        if (_searchController.text.isNotEmpty) {
                          if (!(conv.customerName ?? '').toLowerCase().contains(_searchController.text.toLowerCase())) {
                            return const SizedBox.shrink();
                          }
                        }
                        return _ConversationTile(
                          conversation: conv,
                          isSelected: widget.selectedConversation?.id == conv.id,
                          onTap: () => widget.onConversationSelected(conv),
                        );
                      },
                    ),
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildSearchAndFilters() {
    return Padding(
      padding: const EdgeInsets.all(12.0),
      child: Column(
        children: [
          TextField(
            controller: _searchController,
            style: const TextStyle(color: Colors.white),
            decoration: InputDecoration(
              hintText: 'Search conversations...',
              hintStyle: TextStyle(color: Colors.white.withValues(alpha: 0.5)),
              prefixIcon: const Icon(Icons.search, color: Colors.grey),
              filled: true,
              fillColor: AppTheme.backgroundDark,
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide.none,
              ),
              contentPadding: const EdgeInsets.symmetric(vertical: 0),
            ),
            onChanged: (_) => setState(() {}),
          ),
          const SizedBox(height: 12),
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: _filterColors.entries.map((e) {
                final isSelected = widget.selectedFilter == e.key;
                return Padding(
                  padding: const EdgeInsets.only(right: 8.0),
                  child: FilterChip(
                    label: Text(e.key),
                    selected: isSelected,
                    onSelected: (_) => _onFilterTap(e.key),
                    backgroundColor: AppTheme.backgroundDark,
                    selectedColor: e.value.withValues(alpha: 0.2),
                    checkmarkColor: e.value,
                    labelStyle: TextStyle(
                      color: isSelected ? e.value : Colors.white70,
                      fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                    ),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                      side: BorderSide(
                        color: isSelected ? e.value : Colors.grey.withValues(alpha: 0.2),
                      ),
                    ),
                  ),
                );
              }).toList(),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildShimmer() {
    return ListView.builder(
      itemCount: 4,
      itemBuilder: (_, __) => Shimmer.fromColors(
        baseColor: Colors.grey[850]!,
        highlightColor: Colors.grey[700]!,
        child: ListTile(
          leading: const CircleAvatar(radius: 22),
          title: Container(height: 12, width: 100, color: Colors.white),
          subtitle: Container(height: 10, width: double.infinity, color: Colors.white, margin: const EdgeInsets.only(top: 8)),
        ),
      ),
    );
  }
}

class _ConversationTile extends StatelessWidget {
  final ConversationModel conversation;
  final bool isSelected;
  final VoidCallback onTap;

  const _ConversationTile({
    required this.conversation,
    required this.isSelected,
    required this.onTap,
  });

  String _getInitials(String? name) {
    if (name == null || name.isEmpty) return '?';
    final parts = name.split(' ').where((e) => e.isNotEmpty).toList();
    if (parts.length > 1) return '${parts[0][0]}${parts[1][0]}'.toUpperCase();
    return parts[0].substring(0, parts[0].length > 1 ? 2 : 1).toUpperCase();
  }

  IconData _getChannelIcon() {
    final ch = conversation.channel?.toLowerCase() ?? '';
    if (ch.contains('whatsapp')) return Icons.wechat;
    if (ch.contains('telegram')) return Icons.telegram;
    if (ch.contains('instagram')) return Icons.camera_alt;
    if (ch.contains('facebook')) return Icons.facebook;
    if (ch.contains('sms')) return Icons.sms;
    return Icons.message;
  }

  Color _getChannelColor() {
    final ch = conversation.channel?.toLowerCase() ?? '';
    if (ch.contains('whatsapp')) return Colors.green;
    if (ch.contains('telegram')) return Colors.blue;
    if (ch.contains('instagram')) return Colors.purpleAccent;
    if (ch.contains('facebook')) return Colors.indigo;
    return Colors.grey;
  }

  String _formatTime(DateTime? time) {
    if (time == null) return '';
    final now = DateTime.now();
    final diff = now.difference(time);
    if (diff.inDays > 0) return '${diff.inDays}d';
    if (diff.inHours > 0) return '${diff.inHours}h';
    if (diff.inMinutes > 0) return '${diff.inMinutes}m';
    return 'now';
  }

  @override
  Widget build(BuildContext context) {
    final bool hasUnread = conversation.unreadCount > 0;
    return InkWell(
      onTap: onTap,
      child: Container(
        decoration: BoxDecoration(
          color: isSelected ? AppTheme.primaryIndigo.withValues(alpha: 0.08) : Colors.transparent,
          border: Border(
            left: BorderSide(
              color: isSelected ? AppTheme.primaryIndigo : Colors.transparent,
              width: 3,
            ),
          ),
        ),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Stack(
              children: [
                CircleAvatar(
                  radius: 22,
                  backgroundColor: AppTheme.backgroundDark,
                  child: Text(_getInitials(conversation.customerName), style: const TextStyle(color: Colors.white, fontSize: 16)),
                ),
                Positioned(
                  bottom: 0,
                  right: 0,
                  child: Container(
                    padding: const EdgeInsets.all(2),
                    decoration: BoxDecoration(
                      color: _getChannelColor(),
                      shape: BoxShape.circle,
                      border: Border.all(color: AppTheme.surfaceDark, width: 2),
                    ),
                    child: Icon(_getChannelIcon(), size: 10, color: Colors.white),
                  ),
                ),
              ],
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Text(
                          conversation.customerName ?? 'Unknown',
                          style: TextStyle(
                            color: Colors.white,
                            fontWeight: hasUnread ? FontWeight.bold : FontWeight.normal,
                            fontSize: 15,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      Text(
                        _formatTime(conversation.lastMessageAt),
                        style: TextStyle(color: hasUnread ? AppTheme.primaryIndigo : Colors.grey, fontSize: 12),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    conversation.lastMessage ?? 'No messages yet',
                    style: TextStyle(
                      color: hasUnread ? Colors.white : Colors.grey,
                      fontSize: 13,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      if (hasUnread)
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(color: AppTheme.primaryIndigo, borderRadius: BorderRadius.circular(10)),
                          child: Text('${conversation.unreadCount}', style: const TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold)),
                        ),
                      if (hasUnread) const SizedBox(width: 8),
                      if (conversation.aiEnabled)
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: Colors.amber.withValues(alpha: 0.2),
                            borderRadius: BorderRadius.circular(4),
                            border: Border.all(color: Colors.amber.withValues(alpha: 0.5)),
                          ),
                          child: const Text('AUTO', style: TextStyle(color: Colors.amber, fontSize: 10, fontWeight: FontWeight.bold)),
                        ),
                      if (conversation.overallSentiment != null) ...[
                        const Spacer(),
                        Icon(
                          conversation.overallSentiment == 'positive'
                              ? Icons.sentiment_satisfied_alt
                              : conversation.overallSentiment == 'negative'
                                  ? Icons.sentiment_very_dissatisfied
                                  : Icons.sentiment_neutral,
                          size: 14,
                          color: conversation.overallSentiment == 'positive'
                              ? Colors.green
                              : conversation.overallSentiment == 'negative'
                                  ? Colors.red
                                  : Colors.grey,
                        ),
                      ]
                    ],
                  )
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ChatPanel extends StatefulWidget {
  final ConversationModel conversation;
  final VoidCallback onClearSelection;

  const _ChatPanel({required this.conversation, required this.onClearSelection});

  @override
  State<_ChatPanel> createState() => _ChatPanelState();
}

class _ChatPanelState extends State<_ChatPanel> {
  final ApiService _apiService = ApiService();
  final ScrollController _scrollController = ScrollController();
  List<MessageModel> _messages = [];
  bool _isLoading = true;
  bool _isLoadingAI = false;
  Timer? _pollingTimer;

  @override
  void initState() {
    super.initState();
    _fetchMessages();
    _markAsRead();
    _startPolling();
  }

  @override
  void didUpdateWidget(covariant _ChatPanel oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.conversation.id != widget.conversation.id) {
      _messages.clear();
      _isLoading = true;
      _fetchMessages();
      _markAsRead();
    }
  }

  @override
  void dispose() {
    _scrollController.dispose();
    _pollingTimer?.cancel();
    super.dispose();
  }

  void _startPolling() {
    _pollingTimer = Timer.periodic(const Duration(seconds: 5), (_) {
      _fetchMessages(silent: true);
    });
  }

  Future<void> _fetchMessages({bool silent = false}) async {
    final projectId = context.read<ProjectProvider>().currentProjectId;
    if (projectId == null) return;
    try {
      final response = await _apiService.get('/conversations/$projectId/${widget.conversation.id}/messages');
      if (response != null && response is List) {
        final parsed = response.map((e) => MessageModel.fromJson(e as Map<String, dynamic>)).toList();
        parsed.sort((a, b) => (a.createdAt ?? DateTime.now()).compareTo(b.createdAt ?? DateTime.now()));
        
        bool isAtBottom = true;
        if (_scrollController.hasClients) {
           isAtBottom = _scrollController.position.pixels >= _scrollController.position.maxScrollExtent - 50;
        }

        if (mounted) {
          setState(() {
            _messages = parsed;
            _isLoading = false;
          });
          if (isAtBottom && !silent) {
            _scrollToBottom();
          }
        }
      }
    } catch (e) {
      debugPrint('Error fetching messages: $e');
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _markAsRead() async {
    final projectId = context.read<ProjectProvider>().currentProjectId;
    if (projectId == null || widget.conversation.unreadCount == 0) return;
    try {
      await _apiService.put('/conversations/$projectId/${widget.conversation.id}/read', {});
    } catch (e) {
      debugPrint('Error marking as read: $e');
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
    final projectId = context.read<ProjectProvider>().currentProjectId;
    if (projectId == null || text.trim().isEmpty) return;

    final tempMsg = MessageModel(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      content: text,
      direction: 'outbound',
      createdAt: DateTime.now(),
      status: 'sending',
    );
    setState(() => _messages.add(tempMsg));
    _scrollToBottom();

    try {
      await _apiService.post('/messages/$projectId/send', {
        'content': text,
        'provider': widget.conversation.channel,
        'recipient': {'customer_id': widget.conversation.customerId},
        'order_id': widget.conversation.orderId,
      });
      _fetchMessages(silent: true);
    } catch (e) {
      debugPrint('Error sending message: $e');
      setState(() {
        _messages.removeLast();
      });
    }
  }

  Future<void> _requestAIReply() async {
    final projectId = context.read<ProjectProvider>().currentProjectId;
    if (projectId == null) return;
    
    final lastInbound = _messages.reversed.firstWhere(
      (m) => m.direction == 'inbound',
      orElse: () => const MessageModel(id: '', content: ''),
    );
    if (lastInbound.id.isEmpty) return;

    setState(() => _isLoadingAI = true);
    _scrollToBottom();
    try {
      await _apiService.post('/messages/$projectId/ai-reply', {
        'order_id': widget.conversation.orderId,
        'customer_message': lastInbound.content,
      });
      _fetchMessages();
    } catch (e) {
      debugPrint('Error requesting AI reply: $e');
    } finally {
      if (mounted) setState(() => _isLoadingAI = false);
    }
  }

  Future<void> _clearChat() async {
    final projectId = context.read<ProjectProvider>().currentProjectId;
    if (projectId == null) return;
    try {
      await _apiService.delete('/conversations/$projectId/${widget.conversation.id}');
      widget.onClearSelection();
    } catch (e) {
      debugPrint('Error clearing chat: $e');
    }
  }

  Future<void> _toggleAI() async {
    final projectId = context.read<ProjectProvider>().currentProjectId;
    if (projectId == null || widget.conversation.profileId == null) return;
    try {
      await _apiService.post('/customers/$projectId/${widget.conversation.profileId}/toggle-ai', {});
      widget.onClearSelection(); 
    } catch (e) {
      debugPrint('Error toggling AI: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      color: AppTheme.backgroundDark,
      child: Column(
        children: [
          _buildChatAppBar(),
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : ListView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
                    itemCount: _messages.length + (_isLoadingAI ? 1 : 0),
                    itemBuilder: (context, index) {
                      if (index == _messages.length && _isLoadingAI) {
                        return _buildTypingIndicator();
                      }
                      return _MessageBubble(message: _messages[index]);
                    },
                  ),
          ),
          _ChatInputBar(onSend: _sendMessage),
        ],
      ),
    );
  }

  Widget _buildChatAppBar() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      color: AppTheme.surfaceDark,
      child: Row(
        children: [
          IconButton(
            icon: const Icon(Icons.arrow_back, color: Colors.white),
            onPressed: widget.onClearSelection,
            constraints: const BoxConstraints(),
            padding: const EdgeInsets.only(right: 16),
          ),
          CircleAvatar(
            radius: 20,
            backgroundColor: AppTheme.backgroundDark,
            child: Text(
              widget.conversation.customerName != null && widget.conversation.customerName!.isNotEmpty 
                ? widget.conversation.customerName![0].toUpperCase() 
                : '?',
              style: const TextStyle(color: Colors.white),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  widget.conversation.customerName ?? 'Unknown',
                  style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
                ),
                Text(
                  widget.conversation.channel?.toUpperCase() ?? 'UNKNOWN CHANNEL',
                  style: const TextStyle(color: Colors.grey, fontSize: 12),
                ),
              ],
            ),
          ),
          IconButton(
            tooltip: 'Toggle AI Auto-Reply',
            icon: Icon(Icons.smart_toy, color: widget.conversation.aiEnabled ? Colors.amber : Colors.grey),
            onPressed: _toggleAI,
          ),
          IconButton(
            tooltip: 'Generate AI Reply',
            icon: const Icon(Icons.auto_awesome, color: AppTheme.primaryIndigo),
            onPressed: _requestAIReply,
          ),
          IconButton(
            tooltip: 'Clear Chat',
            icon: const Icon(Icons.delete_outline, color: Colors.redAccent),
            onPressed: _clearChat,
          ),
        ],
      ),
    );
  }

  Widget _buildTypingIndicator() {
    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 16, top: 8),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: const Color(0xFF2A2D35),
          borderRadius: BorderRadius.circular(16),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.auto_awesome, size: 14, color: AppTheme.primaryIndigo),
            const SizedBox(width: 8),
            Text('AI is typing...', style: TextStyle(color: Colors.grey[400], fontStyle: FontStyle.italic)),
          ],
        ),
      ).animate().fade().slideY(begin: 0.2, end: 0),
    );
  }
}

class _MessageBubble extends StatelessWidget {
  final MessageModel message;

  const _MessageBubble({required this.message});

  void _copyToClipboard(BuildContext context) {
    Clipboard.setData(ClipboardData(text: message.content));
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Copied'), duration: Duration(seconds: 1)),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (message.contentType != null && message.contentType!.contains('event') || 
        message.content.startsWith('System Event:')) {
      return Container(
        margin: const EdgeInsets.symmetric(vertical: 16),
        child: Center(
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            decoration: BoxDecoration(
              color: AppTheme.surfaceDark,
              borderRadius: BorderRadius.circular(16),
            ),
            child: Text(
              message.content,
              style: TextStyle(color: Colors.grey.withValues(alpha: 0.8), fontSize: 12),
              textAlign: TextAlign.center,
            ),
          ),
        ),
      );
    }

    final isOutbound = message.direction == 'outbound';

    return GestureDetector(
      onLongPress: () => _copyToClipboard(context),
      child: Padding(
        padding: const EdgeInsets.only(bottom: 16),
        child: Column(
          crossAxisAlignment: isOutbound ? CrossAxisAlignment.end : CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: isOutbound ? MainAxisAlignment.end : MainAxisAlignment.start,
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                if (isOutbound && message.aiGenerated)
                  const Padding(
                    padding: EdgeInsets.only(right: 8.0, bottom: 4.0),
                    child: Icon(Icons.auto_awesome, size: 14, color: AppTheme.primaryIndigo),
                  ),
                Flexible(
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                    decoration: BoxDecoration(
                      color: isOutbound ? AppTheme.surfaceDark : const Color(0xFF2A2D35),
                      borderRadius: BorderRadius.only(
                        topLeft: Radius.circular(isOutbound ? 16 : 4),
                        topRight: Radius.circular(isOutbound ? 4 : 16),
                        bottomLeft: const Radius.circular(16),
                        bottomRight: const Radius.circular(16),
                      ),
                      border: isOutbound && message.aiGenerated
                          ? const Border(left: BorderSide(color: AppTheme.primaryIndigo, width: 2))
                          : null,
                    ),
                    child: Text(
                      message.content,
                      style: const TextStyle(color: Colors.white, fontSize: 15, height: 1.3),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 4),
            Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  message.createdAt != null ? DateFormat('HH:mm').format(message.createdAt!) : '',
                  style: const TextStyle(color: Colors.grey, fontSize: 11),
                ),
                if (message.extraData?['sentiment'] != null) ...[
                  const SizedBox(width: 4),
                  Text(
                    message.extraData!['sentiment'] == 'positive' ? '😊' :
                    message.extraData!['sentiment'] == 'negative' ? '😠' : '😐',
                    style: const TextStyle(fontSize: 11),
                  ),
                ],
                if (isOutbound) ...[
                  const SizedBox(width: 4),
                  Icon(
                    message.status == 'sending' ? Icons.access_time : Icons.done_all,
                    size: 12,
                    color: message.status == 'sending' ? Colors.grey : Colors.blue,
                  ),
                ],
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _ChatInputBar extends StatefulWidget {
  final ValueChanged<String> onSend;

  const _ChatInputBar({required this.onSend});

  @override
  State<_ChatInputBar> createState() => _ChatInputBarState();
}

class _ChatInputBarState extends State<_ChatInputBar> {
  final TextEditingController _controller = TextEditingController();

  void _handleSend() {
    if (_controller.text.trim().isEmpty) return;
    widget.onSend(_controller.text);
    _controller.clear();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.surfaceDark,
        border: Border(top: BorderSide(color: Colors.grey.withValues(alpha: 0.1))),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          Expanded(
            child: Container(
              decoration: BoxDecoration(
                color: AppTheme.backgroundDark,
                borderRadius: BorderRadius.circular(20),
              ),
              child: CallbackShortcuts(
                bindings: {
                  const SingleActivator(LogicalKeyboardKey.enter, shift: false): _handleSend,
                },
                child: TextField(
                  controller: _controller,
                  maxLines: 4,
                  minLines: 1,
                  textInputAction: TextInputAction.send,
                  onSubmitted: (_) => _handleSend(),
                  style: const TextStyle(color: Colors.white),
                  decoration: InputDecoration(
                    hintText: 'Type a message...',
                    hintStyle: TextStyle(color: Colors.grey.withValues(alpha: 0.7)),
                    border: InputBorder.none,
                    contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                  ),
                ),
              ),
            ),
          ),
          const SizedBox(width: 12),
          GestureDetector(
            onTap: _handleSend,
            child: Container(
              height: 48,
              width: 48,
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [AppTheme.primaryIndigo, Colors.indigo[400]!],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.send, color: Colors.white, size: 20),
            ),
          ),
        ],
      ),
    );
  }
}
