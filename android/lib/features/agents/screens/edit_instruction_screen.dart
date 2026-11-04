import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/localization/app_localizations.dart';
import '../../../core/theme/app_colors.dart';
import '../../../shared/utils/validators.dart';
import '../../../shared/widgets/app_button.dart';
import '../../../shared/widgets/app_text_field.dart';
import '../models/bot_instruction_model.dart';
import '../providers/agents_provider.dart';

/// Form screen for adding or editing an AI bot prompt instruction.
class EditInstructionScreen extends ConsumerStatefulWidget {
  final BotInstructionModel? instruction;

  const EditInstructionScreen({super.key, this.instruction});

  @override
  ConsumerState<EditInstructionScreen> createState() =>
      _EditInstructionScreenState();
}

class _EditInstructionScreenState extends ConsumerState<EditInstructionScreen> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _titleController;
  late final TextEditingController _bodyController;
  bool _isSaving = false;

  @override
  void initState() {
    super.initState();
    _titleController =
        TextEditingController(text: widget.instruction?.title ?? '');
    _bodyController =
        TextEditingController(text: widget.instruction?.instruction ?? '');
  }

  @override
  void dispose() {
    _titleController.dispose();
    _bodyController.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _isSaving = true);

    bool success = false;
    final notifier = ref.read(agentsProvider.notifier);

    if (widget.instruction == null) {
      success = await notifier.createInstruction(
        title: _titleController.text.trim(),
        instruction: _bodyController.text.trim(),
      );
    } else {
      success = await notifier.updateInstruction(
        instructionId: widget.instruction!.id,
        title: _titleController.text.trim(),
        instruction: _bodyController.text.trim(),
      );
    }

    if (success && mounted) {
      Navigator.pop(context);
    } else if (mounted) {
      setState(() => _isSaving = false);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Failed to save instruction')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final isNew = widget.instruction == null;

    return Scaffold(
      backgroundColor: AppColors.bgDark,
      appBar: AppBar(
        title: Text(
          isNew ? context.tr('addInstruction') : context.tr('editInstruction'),
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                AppTextField(
                  controller: _titleController,
                  label: context.tr('instructionTitle'),
                  hintText: 'e.g. Refund Policy, Greetings, Pricing',
                  validator: (v) =>
                      AppValidators.requiredField(v, 'Instruction title'),
                ),
                const SizedBox(height: 16),
                AppTextField(
                  controller: _bodyController,
                  label: context.tr('instructionBody'),
                  hintText:
                      'Provide strict behavioral guidelines for the AI agent...',
                  maxLines: 8,
                  validator: (v) =>
                      AppValidators.requiredField(v, 'Instruction body'),
                ),
                const SizedBox(height: 24),
                AppButton(
                  text: context.tr('save'),
                  isLoading: _isSaving,
                  icon: Icons.save_rounded,
                  onPressed: _save,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
