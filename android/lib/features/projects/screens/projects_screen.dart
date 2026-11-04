import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../../shared/utils/formatters.dart';
import '../../../shared/widgets/empty_view.dart';
import '../../../shared/widgets/glass_card.dart';
import '../../../shared/widgets/status_badge.dart';
import '../models/project_model.dart';
import '../providers/project_provider.dart';
import '../widgets/project_selector_sheet.dart';

/// Workspace and tenant project management screen.
class ProjectsScreen extends ConsumerWidget {
  const ProjectsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final projectState = ref.watch(projectProvider);
    final activeProject = ref.watch(activeProjectProvider);

    return Scaffold(
      backgroundColor: AppColors.bgDark,
      appBar: AppBar(
        title: const Text('Workspaces & Projects'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add_rounded),
            tooltip: 'Switch Workspace',
            onPressed: () => ProjectSelectorSheet.show(context),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () => ref.read(projectProvider.notifier).fetchProjects(),
        child: projectState.projects.isEmpty
            ? EmptyView(
                title: 'No workspaces found',
                subtitle: 'Select or create your first workspace to begin.',
                actionText: 'Open Workspace Selector',
                onAction: () => ProjectSelectorSheet.show(context),
              )
            : ListView.separated(
                padding: const EdgeInsets.all(16),
                itemCount: projectState.projects.length,
                separatorBuilder: (_, __) => const SizedBox(height: 12),
                itemBuilder: (context, index) {
                  final project = projectState.projects[index];
                  final isActive = project.id == activeProject?.id;
                  return _buildProjectCard(context, ref, project, isActive);
                },
              ),
      ),
    );
  }

  Widget _buildProjectCard(
    BuildContext context,
    WidgetRef ref,
    ProjectModel project,
    bool isActive,
  ) {
    return GlassCard(
      padding: const EdgeInsets.all(16),
      borderColor: isActive ? AppColors.brandPrimary : AppColors.border,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Text(
                  project.name,
                  style: AppTypography.cardTitle,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              if (isActive)
                const StatusBadge(
                  label: 'ACTIVE',
                  variant: BadgeVariant.success,
                )
              else
                TextButton(
                  onPressed: () {
                    ref.read(projectProvider.notifier).selectProject(project);
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('Switched to ${project.name}')),
                    );
                  },
                  child: const Text('Select'),
                ),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              const Icon(Icons.shield_outlined,
                  size: 16, color: AppColors.textMuted),
              const SizedBox(width: 4),
              Text(project.role ?? 'MEMBER', style: AppTypography.caption),
              const SizedBox(width: 16),
              const Icon(Icons.calendar_today_outlined,
                  size: 16, color: AppColors.textMuted),
              const SizedBox(width: 4),
              Text(
                project.createdAt != null
                    ? 'Created: ${AppFormatters.date(project.createdAt!)}'
                    : 'Created: Recently',
                style: AppTypography.caption,
              ),
            ],
          ),
        ],
      ),
    );
  }
}
