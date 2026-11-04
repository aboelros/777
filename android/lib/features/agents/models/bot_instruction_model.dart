/// AI Bot Instruction domain model matching backend `BotInstruction`.
class BotInstructionModel {
  final String id;
  final String title;
  final String instruction;
  final String? category;
  final int priority;
  final bool isActive;
  final List<String> activeForPlatforms;

  const BotInstructionModel({
    required this.id,
    required this.title,
    required this.instruction,
    this.category,
    this.priority = 0,
    this.isActive = true,
    this.activeForPlatforms = const [],
  });

  factory BotInstructionModel.fromJson(Map<String, dynamic> json) {
    return BotInstructionModel(
      id: json['id']?.toString() ?? '',
      title: json['title']?.toString() ?? 'Instruction',
      instruction: json['instruction']?.toString() ?? '',
      category: json['category']?.toString(),
      priority: (json['priority'] as num?)?.toInt() ?? 0,
      isActive: json['is_active'] != false,
      activeForPlatforms: (json['active_for_platforms'] as List?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'title': title,
      'instruction': instruction,
      'category': category,
      'priority': priority,
      'is_active': isActive,
      'active_for_platforms': activeForPlatforms,
    };
  }
}
