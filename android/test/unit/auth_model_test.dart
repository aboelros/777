import 'package:flutter_test/flutter_test.dart';
import 'package:automind/features/auth/models/user_model.dart';
import 'package:automind/features/projects/models/project_model.dart';

void main() {
  group('Domain Models Serialization', () {
    test('UserModel.fromJson parses valid payload', () {
      final json = {
        'id': '123e4567-e89b-12d3-a456-426614174000',
        'email': 'ceo@automio.online',
        'name': 'Founder',
        'role': 'admin',
        'is_active': true,
        'created_at': '2026-01-01T12:00:00Z',
      };

      final user = UserModel.fromJson(json);
      expect(user.id, '123e4567-e89b-12d3-a456-426614174000');
      expect(user.email, 'ceo@automio.online');
      expect(user.role, 'ADMIN');
      expect(user.displayName, 'Founder');
    });

    test('ProjectModel.fromJson parses project payload', () {
      final json = {
        'id': 'proj-1',
        'name': 'Electronics Store',
        'description': 'Main retail channel',
        'role': 'OWNER',
      };

      final project = ProjectModel.fromJson(json);
      expect(project.id, 'proj-1');
      expect(project.name, 'Electronics Store');
      expect(project.isOwner, true);
    });
  });
}
