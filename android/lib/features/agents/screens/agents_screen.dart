import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/localization/app_localizations.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../../shared/widgets/empty_view.dart';
import '../../../shared/widgets/error_view.dart';
import '../../../shared/widgets/skeleton_loader.dart';
import '../../projects/providers/project_provider.dart';
import '../models/bot_instruction_model.dart';
import '../providers/agents_provider.dart';
import '../widgets/instruction_card.dart';

/// Screen managing AI sales agent rules, prompt instructions, and behaviors.
class AgentsScreen extends ConsumerWidget {
  const AgentsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final activeProject = ref.watch(activeProjectProvider);
    final agentsState = ref.watch(agentsProvider);
    final instructions = agentsState.instructions;

    return Scaffold(
      backgroundColor: AppColors.bgDark,
      appBar: AppBar(
        title: Text(context.tr('agents'), style: AppTypography.pageTitle),
      ),
      floatingActionButton: activeProject != null
          ? FloatingActionButton(
              backgroundColor: AppColors.brandPrimary,
              child: const Icon(Icons.add, color: Colors.white),
              onPressed: () => context.push('/agents/edit'),
            )
          : null,
      body: activeProject == null
          ? EmptyView(
              title: context.tr('noProject'),
              subtitle: 'Select a workspace to configure AI agents.',
            )
          : agentsState.isLoading && instructions.isEmpty
              ? _buildSkeletonList()
              : agentsState.error != null && instructions.isEmpty
                  ? ErrorView(
                      message: agentsState.error,
                      onRetry: () =>
                          ref.read(agentsProvider.notifier).loadInstructions(),
                    )
                  : instructions.isEmpty
                      ? EmptyView(
                          title: 'No AI Instructions',
                          subtitle:
                              'Add instructions to train your AI sales bot.',
                          icon: Icons.psychology_outlined,
                          actionText: context.tr('addInstruction'),
                          onAction: () => context.push('/agents/edit'),
                        )
                      : RefreshIndicator(
                          color: AppColors.brandPrimary,
                          backgroundColor: AppColors.surfaceElevated,
                          onRefresh: () => ref
                              .read(agentsProvider.notifier)
                              .loadInstructions(),
                          child: ListView.separated(
                            padding: const EdgeInsets.all(16),
                            itemCount: instructions.length,
                            separatorBuilder: (_, __) =>
                                const SizedBox(height: 10),
                            itemBuilder: (context, index) {
                              final inst = instructions[index];
                              return InstructionCard(
                                instruction: inst,
                                onTap: () => _editInstruction(context, inst),
                                onDelete: () => _confirmDelete(
                                    context, ref, inst.id, inst.title),
                              );
                            },
                          ),
                        ),
    );
  }

  void _editInstruction(BuildContext context, BotInstructionModel inst) {
    context.push('/agents/edit', extra: inst);
  }

  void _confirmDelete(
      BuildContext context, WidgetRef ref, String id, String title) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppColors.surfaceElevated,
        title: Text('Delete Instruction', style: AppTypography.cardTitle),
        content: Text('Are you sure you want to delete "$title"?',
            style: AppTypography.bodySecondary),
        actions: [
          TextButton(
            child: Text(context.tr('cancel'),
                style: const TextStyle(color: AppColors.textSecondary)),
            onPressed: () => Navigator.pop(ctx),
          ),
          TextButton(
            child: Text(context.tr('delete'),
                style: const TextStyle(color: AppColors.danger)),
            onPressed: () {
              Navigator.pop(ctx);
              ref.read(agentsProvider.notifier).deleteInstruction(id);
            },
          ),
        ],
      ),
    );
  }

  Widget _buildSkeletonList() {
    return ListView.separated(
      padding: const EdgeInsets.all(16),
      itemCount: 4,
      separatorBuilder: (_, __) => const SizedBox(height: 10),
      itemBuilder: (_, __) =>
          const SkeletonLoader(width: double.infinity, height: 95),
    );
  }
}
