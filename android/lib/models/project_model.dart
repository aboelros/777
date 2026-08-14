class Project {
  final String id;
  final String name;
  final String? description;
  final String? status;
  final DateTime createdAt;

  Project({
    required this.id,
    required this.name,
    this.description,
    this.status,
    required this.createdAt,
  });

  factory Project.fromJson(Map<String, dynamic> json) {
    return Project(
      id: json['id'],
      name: json['name'],
      description: json['description'],
      status: json['status'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}
