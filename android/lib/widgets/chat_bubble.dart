import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:intl/intl.dart';
import 'package:flutter_animate/flutter_animate.dart';

class ChatBubble extends StatelessWidget {
  final String content;
  final bool isUser;
  final DateTime timestamp;
  final bool isLatest;

  const ChatBubble({
    super.key,
    required this.content,
    required this.isUser,
    required this.timestamp,
    this.isLatest = false,
  });

  @override
  Widget build(BuildContext context) {
    final bubbleColor = isUser ? const Color(0xFF6366F1) : const Color(0xFF1E293B);
    final textColor = Colors.white;
    final timeFormat = DateFormat('HH:mm');

    return GestureDetector(
      onLongPress: () async {
        await Clipboard.setData(ClipboardData(text: content));
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Copied to clipboard')),
          );
        }
      },
      child: Align(
        alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
        child: Container(
          margin: const EdgeInsets.symmetric(vertical: 4, horizontal: 16),
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: bubbleColor,
            borderRadius: BorderRadius.only(
              topLeft: const Radius.circular(16),
              topRight: const Radius.circular(16),
              bottomLeft: Radius.circular(isUser ? 16 : 4),
              bottomRight: Radius.circular(isUser ? 4 : 16),
            ),
            border: !isUser
                ? const Border(left: BorderSide(color: Color(0xFF6366F1), width: 2))
                : null,
          ),
          child: Column(
            crossAxisAlignment: isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              if (isUser)
                Text(
                  content,
                  style: TextStyle(color: textColor, fontSize: 16),
                )
              else
                MarkdownBody(
                  data: content,
                  styleSheet: MarkdownStyleSheet(
                    p: TextStyle(color: textColor, fontSize: 16),
                    listBullet: TextStyle(color: textColor),
                    code: TextStyle(
                        color: Colors.white,
                        backgroundColor: Colors.black38,
                        fontFamily: 'monospace'),
                  ),
                ),
              const SizedBox(height: 4),
              Text(
                timeFormat.format(timestamp),
                style: const TextStyle(color: Colors.grey, fontSize: 10),
              ),
            ],
          ),
        ),
      ).animate().fadeIn(duration: 200.ms).slideX(
          begin: isUser ? 0.1 : -0.1,
          end: 0,
        ),
    );
  }
}
