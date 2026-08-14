import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

class TypingIndicator extends StatelessWidget {
  const TypingIndicator({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B), // surfaceDark
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          _buildDot(0.ms),
          const SizedBox(width: 4),
          _buildDot(200.ms),
          const SizedBox(width: 4),
          _buildDot(400.ms),
        ],
      ),
    );
  }

  Widget _buildDot(Duration delay) {
    return Container(
      width: 8,
      height: 8,
      decoration: BoxDecoration(
        color: Colors.grey[500],
        shape: BoxShape.circle,
      ),
    )
        .animate(
          onPlay: (c) => c.repeat(),
          delay: delay,
        )
        .moveY(begin: 0, end: -6, duration: 300.ms, curve: Curves.easeInOut)
        .then()
        .moveY(begin: -6, end: 0, duration: 300.ms, curve: Curves.easeInOut);
  }
}
