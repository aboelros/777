/// Immutable domain model representing a CRM pipeline deal.
class DealModel {
  final String id;
  final String stageId;
  final String projectId;
  final String title;
  final double value;
  final String currency;
  final double probability;
  final String priority;
  final String status;
  final String? notes;
  final DateTime createdAt;

  const DealModel({
    required this.id,
    required this.stageId,
    required this.projectId,
    required this.title,
    required this.value,
    this.currency = 'USD',
    this.probability = 0.5,
    this.priority = 'medium',
    this.status = 'open',
    this.notes,
    required this.createdAt,
  });

  factory DealModel.fromJson(Map<String, dynamic> json) {
    return DealModel(
      id: json['id']?.toString() ?? '',
      stageId: json['stage_id']?.toString() ?? '',
      projectId: json['project_id']?.toString() ?? '',
      title: json['title'] as String? ?? 'Untitled Deal',
      value: (json['value'] as num?)?.toDouble() ?? 0.0,
      currency: json['currency'] as String? ?? 'USD',
      probability: (json['probability'] as num?)?.toDouble() ?? 0.5,
      priority: json['priority'] as String? ?? 'medium',
      status: json['status'] as String? ?? 'open',
      notes: json['notes'] as String?,
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at'].toString()) ?? DateTime.now()
          : DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'stage_id': stageId,
        'project_id': projectId,
        'title': title,
        'value': value,
        'currency': currency,
        'probability': probability,
        'priority': priority,
        'status': status,
        if (notes != null) 'notes': notes,
      };
}

/// Stage definition in CRM sales pipeline.
class PipelineStageModel {
  final String id;
  final String name;
  final int index;
  final String color;

  const PipelineStageModel({
    required this.id,
    required this.name,
    this.index = 0,
    this.color = '#0EA5E9',
  });

  factory PipelineStageModel.fromJson(Map<String, dynamic> json) {
    return PipelineStageModel(
      id: json['id']?.toString() ?? '',
      name: json['name'] as String? ?? 'Stage',
      index: json['index'] as int? ?? 0,
      color: json['color'] as String? ?? '#0EA5E9',
    );
  }
}
