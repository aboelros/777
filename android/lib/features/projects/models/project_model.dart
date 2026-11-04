/// Multi-tenant Project / Workspace domain model.
class ProjectModel {
  final String id;
  final String name;
  final String? description;
  final String? ownerId;
  final String? role;
  final DateTime? createdAt;

  const ProjectModel({
    required this.id,
    required this.name,
    this.description,
    this.ownerId,
    this.role,
    this.createdAt,
  });

  factory ProjectModel.fromJson(Map<String, dynamic> json) {
    return ProjectModel(
      id: json['id']?.toString() ?? '',
      name: json['name']?.toString() ?? 'Workspace',
      description: json['description']?.toString(),
      ownerId: json['owner_id']?.toString(),
      role: json['role']?.toString().toUpperCase() ?? 'MEMBER',
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at'].toString())
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'owner_id': ownerId,
      'role': role,
      'created_at': createdAt?.toIso8601String(),
    };
  }

  bool get isOwner => role == 'OWNER' || role == 'ADMIN';
}
