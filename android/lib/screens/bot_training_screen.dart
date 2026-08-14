import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:shimmer/shimmer.dart';
import 'package:provider/provider.dart';
import '../providers/project_provider.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';

class InstructionModel {
  final String id;
  final String title;
  final String instruction;
  final String category;
  final int priority;
  final bool isActive;
  
  const InstructionModel({
    required this.id,
    required this.title,
    required this.instruction,
    required this.category,
    required this.priority,
    required this.isActive,
  });
  
  factory InstructionModel.fromJson(Map<String, dynamic> json) => InstructionModel(
    id: json['id']?.toString() ?? '',
    title: json['title']?.toString() ?? '',
    instruction: json['instruction']?.toString() ?? '',
    category: json['category']?.toString() ?? 'tone',
    priority: (json['priority'] as num?)?.toInt() ?? 5,
    isActive: json['is_active'] != false,
  );
  
  Map<String, dynamic> toJson() => {
    'title': title,
    'instruction': instruction,
    'category': category,
    'priority': priority,
    'is_active': isActive,
  };
}

class KnowledgeModel {
  final String id;
  final String title;
  final String content;
  final String sourceType;
  final bool isActive;
  
  const KnowledgeModel({
    required this.id,
    required this.title,
    required this.content,
    required this.sourceType,
    required this.isActive,
  });
  
  factory KnowledgeModel.fromJson(Map<String, dynamic> json) => KnowledgeModel(
    id: json['id']?.toString() ?? '',
    title: json['title']?.toString() ?? '',
    content: json['content']?.toString() ?? '',
    sourceType: json['source_type']?.toString() ?? 'text',
    isActive: json['is_active'] != false,
  );
  
  Map<String, dynamic> toJson() => {
    'title': title,
    'content': content,
    'source_type': sourceType,
    'is_active': isActive,
  };
}

class BotTrainingScreen extends StatefulWidget {
  const BotTrainingScreen({super.key});

  @override
  State<BotTrainingScreen> createState() => _BotTrainingScreenState();
}

class _BotTrainingScreenState extends State<BotTrainingScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  
  bool _isLoading = true;
  List<InstructionModel> _instructions = [];
  List<KnowledgeModel> _knowledgeList = [];
  String _searchQuery = '';
  
  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _tabController.addListener(() {
      setState(() {});
    });
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadData();
    });
  }
  
  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    try {
      final projectId = context.read<ProjectProvider>().currentProject?.id;
      if (projectId == null) throw Exception('No active project');
      
      final instRes = await ApiService.get('/bot-training/$projectId/instructions');
      final knowRes = await ApiService.get('/knowledge/$projectId');
      
      if (mounted) {
        setState(() {
          _instructions = (instRes['instructions'] as List?)
              ?.map((e) => InstructionModel.fromJson(e))
              .toList() ?? [];
          _knowledgeList = (knowRes['data'] as List?)
              ?.map((e) => KnowledgeModel.fromJson(e))
              .toList() ?? [];
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to load training data: $e'), backgroundColor: Colors.red),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _seedInstructions() async {
    setState(() => _isLoading = true);
    try {
      final projectId = context.read<ProjectProvider>().currentProject?.id;
      if (projectId != null) {
        await ApiService.post('/bot-training/$projectId/instructions/seed', {});
        await _loadData();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to seed instructions: $e'), backgroundColor: Colors.red),
        );
      }
      setState(() => _isLoading = false);
    }
  }

  void _showInstructionForm([InstructionModel? instruction]) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => _InstructionFormSheet(
        instruction: instruction,
        onSaved: _loadData,
      ),
    );
  }

  void _showKnowledgeForm([KnowledgeModel? knowledge]) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => _KnowledgeFormSheet(
        knowledge: knowledge,
        onSaved: _loadData,
      ),
    );
  }

  void _showScrapeDialog() {
    showDialog(
      context: context,
      builder: (ctx) => _ScrapeUrlDialog(onScraped: _loadData),
    );
  }

  Future<void> _deleteInstruction(String id) async {
    try {
      final projectId = context.read<ProjectProvider>().currentProject?.id;
      if (projectId != null) {
        await ApiService.delete('/bot-training/$projectId/instructions/$id');
        await _loadData();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to delete instruction: $e'), backgroundColor: Colors.red),
        );
      }
    }
  }

  Future<void> _deleteKnowledge(String id) async {
    try {
      final projectId = context.read<ProjectProvider>().currentProject?.id;
      if (projectId != null) {
        await ApiService.delete('/knowledge/$projectId/$id');
        await _loadData();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to delete knowledge: $e'), backgroundColor: Colors.red),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final isInstructionsTab = _tabController.index == 0;
    
    final filteredInstructions = _instructions.where((i) => 
      i.title.toLowerCase().contains(_searchQuery.toLowerCase()) ||
      i.instruction.toLowerCase().contains(_searchQuery.toLowerCase())
    ).toList();
    
    final filteredKnowledge = _knowledgeList.where((k) => 
      k.title.toLowerCase().contains(_searchQuery.toLowerCase()) ||
      k.content.toLowerCase().contains(_searchQuery.toLowerCase())
    ).toList();

    return Scaffold(
      backgroundColor: AppTheme.backgroundDark,
      appBar: AppBar(
        backgroundColor: AppTheme.backgroundDark,
        elevation: 0,
        title: Row(
          children: const [
            Icon(Icons.school, color: AppTheme.primaryIndigo),
            SizedBox(width: 8),
            Text('Bot Training', style: TextStyle(color: Colors.white)),
          ],
        ),
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: AppTheme.primaryIndigo,
          labelColor: AppTheme.primaryIndigo,
          unselectedLabelColor: Colors.grey,
          tabs: const [
            Tab(text: 'Instructions'),
            Tab(text: 'Knowledge Base'),
          ],
        ),
        actions: isInstructionsTab 
            ? [
                if (_instructions.isEmpty && !_isLoading)
                  IconButton(
                    icon: const Icon(Icons.bolt, color: Colors.amber),
                    tooltip: 'Seed',
                    onPressed: _seedInstructions,
                  ),
                IconButton(
                  icon: const Icon(Icons.add, color: Colors.white),
                  tooltip: 'Add',
                  onPressed: () => _showInstructionForm(),
                ),
              ]
            : [
                IconButton(
                  icon: const Icon(Icons.link, color: Colors.greenAccent),
                  tooltip: 'Scrape URL',
                  onPressed: _showScrapeDialog,
                ),
                IconButton(
                  icon: const Icon(Icons.add, color: Colors.white),
                  tooltip: 'Add',
                  onPressed: () => _showKnowledgeForm(),
                ),
              ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: Colors.green.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Container(
                        width: 8,
                        height: 8,
                        decoration: const BoxDecoration(
                          color: Colors.green,
                          shape: BoxShape.circle,
                        ),
                      ),
                      const SizedBox(width: 6),
                      Text(
                        'LIVE',
                        style: const TextStyle(
                          color: Colors.green,
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 12),
                Text(
                  isInstructionsTab ? '${_instructions.length} Rules' : '${_knowledgeList.length} Items',
                  style: const TextStyle(color: Colors.grey),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: TextField(
                    style: const TextStyle(color: Colors.white),
                    decoration: InputDecoration(
                      hintText: 'Search...',
                      hintStyle: const TextStyle(color: Colors.grey),
                      prefixIcon: const Icon(Icons.search, color: Colors.grey),
                      filled: true,
                      fillColor: AppTheme.surfaceDark,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide.none,
                      ),
                      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                    ),
                    onChanged: (val) => setState(() => _searchQuery = val),
                  ),
                ),
              ],
            ),
          ),
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: [
                _buildInstructionsTab(filteredInstructions),
                _buildKnowledgeTab(filteredKnowledge),
              ],
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        backgroundColor: AppTheme.primaryIndigo,
        child: const Icon(Icons.add, color: Colors.white),
        onPressed: () {
          if (isInstructionsTab) {
            _showInstructionForm();
          } else {
            _showKnowledgeForm();
          }
        },
      ),
    );
  }

  Widget _buildInstructionsTab(List<InstructionModel> items) {
    if (_isLoading) {
      return _buildShimmerGrid();
    }
    
    if (_instructions.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.school, size: 72, color: Colors.grey),
            const SizedBox(height: 16),
            const Text('No instructions yet', style: TextStyle(color: Colors.grey, fontSize: 18)),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              icon: const Icon(Icons.bolt, color: Colors.amber),
              label: const Text('Seed Default Instructions'),
              style: ElevatedButton.styleFrom(
                backgroundColor: AppTheme.surfaceDark,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
              ),
              onPressed: _seedInstructions,
            ),
          ],
        ),
      );
    }
    
    final width = MediaQuery.of(context).size.width;
    final crossAxisCount = (width ~/ 300).clamp(1, 4);

    return GridView.builder(
      padding: const EdgeInsets.all(16),
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: crossAxisCount,
        childAspectRatio: 0.9,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
      ),
      itemCount: items.length,
      itemBuilder: (context, index) {
        return _InstructionCard(
          item: items[index],
          onEdit: () => _showInstructionForm(items[index]),
          onDelete: () => _deleteInstruction(items[index].id),
        );
      },
    );
  }

  Widget _buildKnowledgeTab(List<KnowledgeModel> items) {
    if (_isLoading) {
      return _buildShimmerList();
    }
    
    if (_knowledgeList.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.menu_book, size: 72, color: Colors.grey),
            const SizedBox(height: 16),
            const Text('No knowledge items yet', style: TextStyle(color: Colors.grey, fontSize: 18)),
            const SizedBox(height: 24),
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: AppTheme.primaryIndigo,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
              ),
              onPressed: () => _showKnowledgeForm(),
              child: const Text('Add Knowledge'),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: items.length,
      itemBuilder: (context, index) {
        return _KnowledgeCard(
          item: items[index],
          onEdit: () => _showKnowledgeForm(items[index]),
          onDelete: () => _deleteKnowledge(items[index].id),
        );
      },
    );
  }

  Widget _buildShimmerGrid() {
    final width = MediaQuery.of(context).size.width;
    final crossAxisCount = (width ~/ 300).clamp(1, 4);
    return GridView.builder(
      padding: const EdgeInsets.all(16),
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: crossAxisCount,
        childAspectRatio: 0.9,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
      ),
      itemCount: 4,
      itemBuilder: (context, index) {
        return Shimmer.fromColors(
          baseColor: AppTheme.surfaceDark,
          highlightColor: Colors.grey[800]!,
          child: Container(
            decoration: BoxDecoration(
              color: AppTheme.surfaceDark,
              borderRadius: BorderRadius.circular(16),
            ),
          ),
        );
      },
    );
  }

  Widget _buildShimmerList() {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: 4,
      itemBuilder: (context, index) {
        return Shimmer.fromColors(
          baseColor: AppTheme.surfaceDark,
          highlightColor: Colors.grey[800]!,
          child: Container(
            height: 120,
            margin: const EdgeInsets.only(bottom: 12),
            decoration: BoxDecoration(
              color: AppTheme.surfaceDark,
              borderRadius: BorderRadius.circular(16),
            ),
          ),
        );
      },
    );
  }
}

class _InstructionCard extends StatelessWidget {
  final InstructionModel item;
  final VoidCallback onEdit;
  final VoidCallback onDelete;

  const _InstructionCard({
    required this.item,
    required this.onEdit,
    required this.onDelete,
  });

  Color _getCategoryColor(String cat) {
    switch (cat.toLowerCase()) {
      case 'tone': return AppTheme.primaryIndigo;
      case 'product_knowledge': return Colors.green[600] ?? Colors.green;
      case 'response_style': return Colors.blue[600] ?? Colors.blue;
      case 'promotions': return Colors.amber[600] ?? Colors.amber;
      case 'service': return Colors.red[600] ?? Colors.red;
      default: return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    final catColor = _getCategoryColor(item.category);
    
    return Container(
      decoration: AppTheme.glassCard(),
      child: Stack(
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: catColor.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: catColor.withValues(alpha: 0.5)),
                  ),
                  child: Text(
                    item.category.toUpperCase(),
                    style: TextStyle(color: catColor, fontSize: 10, fontWeight: FontWeight.bold),
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  item.title,
                  style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: AppTheme.primaryIndigo.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    'P:${item.priority}',
                    style: const TextStyle(color: AppTheme.primaryIndigo, fontSize: 10),
                  ),
                ),
                const SizedBox(height: 12),
                Expanded(
                  child: Text(
                    item.instruction,
                    style: const TextStyle(color: Colors.grey, fontSize: 13),
                    maxLines: 3,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    TextButton.icon(
                      onPressed: onEdit,
                      icon: const Icon(Icons.edit, size: 16, color: Colors.white),
                      label: const Text('Edit', style: TextStyle(color: Colors.white)),
                    ),
                    IconButton(
                      icon: const Icon(Icons.delete, color: Colors.red, size: 20),
                      onPressed: onDelete,
                    ),
                  ],
                ),
              ],
            ),
          ),
          Positioned(
            top: 12,
            right: 12,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
              decoration: BoxDecoration(
                color: item.isActive ? Colors.green.withValues(alpha: 0.2) : Colors.grey.withValues(alpha: 0.2),
                borderRadius: BorderRadius.circular(4),
                border: Border.all(color: item.isActive ? Colors.green : Colors.grey),
              ),
              child: Text(
                item.isActive ? 'ON' : 'OFF',
                style: TextStyle(
                  color: item.isActive ? Colors.green : Colors.grey,
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
        ],
      ),
    ).animate().fadeIn(duration: 200.ms).slideY(begin: 0.1);
  }
}

class _KnowledgeCard extends StatelessWidget {
  final KnowledgeModel item;
  final VoidCallback onEdit;
  final VoidCallback onDelete;

  const _KnowledgeCard({
    required this.item,
    required this.onEdit,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: AppTheme.glassCard(),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.menu_book, color: Colors.green, size: 18),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    item.title,
                    style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16),
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: item.isActive ? Colors.green.withValues(alpha: 0.2) : Colors.grey.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(4),
                    border: Border.all(color: item.isActive ? Colors.green : Colors.grey),
                  ),
                  child: Text(
                    item.isActive ? 'ON' : 'OFF',
                    style: TextStyle(
                      color: item.isActive ? Colors.green : Colors.grey,
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFF1E1E2A), // surfaceDark2 fallback
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                item.content,
                style: const TextStyle(color: Colors.grey, fontSize: 14),
                maxLines: 4,
                overflow: TextOverflow.ellipsis,
              ),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: AppTheme.primaryIndigo.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    item.sourceType.toUpperCase(),
                    style: const TextStyle(color: AppTheme.primaryIndigo, fontSize: 10, fontWeight: FontWeight.bold),
                  ),
                ),
                const Spacer(),
                IconButton(
                  icon: const Icon(Icons.edit, color: Colors.white, size: 20),
                  onPressed: onEdit,
                ),
                IconButton(
                  icon: const Icon(Icons.delete, color: Colors.red, size: 20),
                  onPressed: onDelete,
                ),
              ],
            ),
          ],
        ),
      ),
    ).animate().fadeIn(duration: 200.ms);
  }
}

class _InstructionFormSheet extends StatefulWidget {
  final InstructionModel? instruction;
  final VoidCallback onSaved;

  const _InstructionFormSheet({this.instruction, required this.onSaved});

  @override
  State<_InstructionFormSheet> createState() => _InstructionFormSheetState();
}

class _InstructionFormSheetState extends State<_InstructionFormSheet> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _titleCtrl;
  late TextEditingController _textCtrl;
  late TextEditingController _priorityCtrl;
  String _category = 'tone';
  bool _isActive = true;
  bool _isSaving = false;

  final _categories = ['tone', 'product_knowledge', 'response_style', 'promotions', 'service'];

  @override
  void initState() {
    super.initState();
    _titleCtrl = TextEditingController(text: widget.instruction?.title ?? '');
    _textCtrl = TextEditingController(text: widget.instruction?.instruction ?? '');
    _priorityCtrl = TextEditingController(text: widget.instruction?.priority.toString() ?? '5');
    _category = widget.instruction?.category ?? 'tone';
    if (!_categories.contains(_category)) _category = 'tone';
    _isActive = widget.instruction?.isActive ?? true;
  }

  @override
  void dispose() {
    _titleCtrl.dispose();
    _textCtrl.dispose();
    _priorityCtrl.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    
    setState(() => _isSaving = true);
    
    try {
      final projectId = context.read<ProjectProvider>().currentProject?.id;
      if (projectId == null) throw Exception('No active project');
      
      final payload = {
        'title': _titleCtrl.text,
        'instruction': _textCtrl.text,
        'category': _category,
        'priority': int.tryParse(_priorityCtrl.text) ?? 5,
        'is_active': _isActive,
      };

      if (widget.instruction == null) {
        await ApiService.post('/bot-training/$projectId/instructions', payload);
      } else {
        await ApiService.put('/bot-training/$projectId/instructions/${widget.instruction!.id}', payload);
      }
      
      if (mounted) {
        widget.onSaved();
        Navigator.of(context).pop();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to save: $e'), backgroundColor: Colors.red),
        );
      }
    } finally {
      if (mounted) setState(() => _isSaving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(
        bottom: MediaQuery.of(context).viewInsets.bottom,
      ),
      child: Container(
        padding: const EdgeInsets.all(24),
        decoration: const BoxDecoration(
          color: AppTheme.backgroundDark,
          borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
        ),
        child: Form(
          key: _formKey,
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Center(
                  child: Container(
                    width: 40,
                    height: 4,
                    decoration: BoxDecoration(
                      color: Colors.grey[700],
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                Text(
                  widget.instruction == null ? 'Add Instruction' : 'Edit Instruction',
                  style: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 24),
                TextFormField(
                  controller: _titleCtrl,
                  style: const TextStyle(color: Colors.white),
                  decoration: InputDecoration(
                    labelText: 'Title',
                    labelStyle: const TextStyle(color: Colors.grey),
                    filled: true,
                    fillColor: AppTheme.surfaceDark,
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
                  ),
                  validator: (val) => val == null || val.isEmpty ? 'Required' : null,
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _textCtrl,
                  style: const TextStyle(color: Colors.white),
                  maxLines: 6,
                  decoration: InputDecoration(
                    labelText: 'Instruction Text',
                    labelStyle: const TextStyle(color: Colors.grey),
                    filled: true,
                    fillColor: AppTheme.surfaceDark,
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
                  ),
                  validator: (val) => val == null || val.isEmpty ? 'Required' : null,
                ),
                const SizedBox(height: 16),
                DropdownButtonFormField<String>(
                  value: _category,
                  dropdownColor: AppTheme.surfaceDark,
                  style: const TextStyle(color: Colors.white),
                  decoration: InputDecoration(
                    labelText: 'Category',
                    labelStyle: const TextStyle(color: Colors.grey),
                    filled: true,
                    fillColor: AppTheme.surfaceDark,
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
                  ),
                  items: _categories.map((c) => DropdownMenuItem(value: c, child: Text(c.toUpperCase()))).toList(),
                  onChanged: (val) {
                    if (val != null) setState(() => _category = val);
                  },
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(
                      child: TextFormField(
                        controller: _priorityCtrl,
                        style: const TextStyle(color: Colors.white),
                        keyboardType: TextInputType.number,
                        decoration: InputDecoration(
                          labelText: 'Priority (1-10)',
                          labelStyle: const TextStyle(color: Colors.grey),
                          filled: true,
                          fillColor: AppTheme.surfaceDark,
                          border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
                        ),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: SwitchListTile(
                        title: const Text('Is Active', style: TextStyle(color: Colors.white)),
                        value: _isActive,
                        activeColor: AppTheme.primaryIndigo,
                        onChanged: (val) => setState(() => _isActive = val),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),
                Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    TextButton(
                      onPressed: () => Navigator.of(context).pop(),
                      child: const Text('Cancel', style: TextStyle(color: Colors.grey)),
                    ),
                    const SizedBox(width: 16),
                    Container(
                      decoration: BoxDecoration(
                        gradient: AppTheme.primaryGradient,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: ElevatedButton(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.transparent,
                          shadowColor: Colors.transparent,
                          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                        ),
                        onPressed: _isSaving ? null : _save,
                        child: _isSaving
                            ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                            : const Text('Save', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _KnowledgeFormSheet extends StatefulWidget {
  final KnowledgeModel? knowledge;
  final VoidCallback onSaved;

  const _KnowledgeFormSheet({this.knowledge, required this.onSaved});

  @override
  State<_KnowledgeFormSheet> createState() => _KnowledgeFormSheetState();
}

class _KnowledgeFormSheetState extends State<_KnowledgeFormSheet> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _titleCtrl;
  late TextEditingController _contentCtrl;
  String _sourceType = 'text';
  bool _isActive = true;
  bool _isSaving = false;

  final _sourceTypes = ['text', 'faq', 'policy', 'document'];

  @override
  void initState() {
    super.initState();
    _titleCtrl = TextEditingController(text: widget.knowledge?.title ?? '');
    _contentCtrl = TextEditingController(text: widget.knowledge?.content ?? '');
    _sourceType = widget.knowledge?.sourceType ?? 'text';
    if (!_sourceTypes.contains(_sourceType)) _sourceType = 'text';
    _isActive = widget.knowledge?.isActive ?? true;
  }

  @override
  void dispose() {
    _titleCtrl.dispose();
    _contentCtrl.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    
    setState(() => _isSaving = true);
    
    try {
      final projectId = context.read<ProjectProvider>().currentProject?.id;
      if (projectId == null) throw Exception('No active project');
      
      final payload = {
        'title': _titleCtrl.text,
        'content': _contentCtrl.text,
        'source_type': _sourceType,
        'is_active': _isActive,
      };

      if (widget.knowledge == null) {
        await ApiService.post('/knowledge/$projectId', payload);
      } else {
        await ApiService.put('/knowledge/$projectId/${widget.knowledge!.id}', payload);
      }
      
      if (mounted) {
        widget.onSaved();
        Navigator.of(context).pop();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to save: $e'), backgroundColor: Colors.red),
        );
      }
    } finally {
      if (mounted) setState(() => _isSaving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(
        bottom: MediaQuery.of(context).viewInsets.bottom,
      ),
      child: Container(
        padding: const EdgeInsets.all(24),
        decoration: const BoxDecoration(
          color: AppTheme.backgroundDark,
          borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
        ),
        child: Form(
          key: _formKey,
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Center(
                  child: Container(
                    width: 40,
                    height: 4,
                    decoration: BoxDecoration(
                      color: Colors.grey[700],
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                Text(
                  widget.knowledge == null ? 'Add Knowledge' : 'Edit Knowledge',
                  style: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 24),
                TextFormField(
                  controller: _titleCtrl,
                  style: const TextStyle(color: Colors.white),
                  decoration: InputDecoration(
                    labelText: 'Title',
                    labelStyle: const TextStyle(color: Colors.grey),
                    filled: true,
                    fillColor: AppTheme.surfaceDark,
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
                  ),
                  validator: (val) => val == null || val.isEmpty ? 'Required' : null,
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _contentCtrl,
                  style: const TextStyle(color: Colors.white),
                  maxLines: 8,
                  decoration: InputDecoration(
                    labelText: 'Content',
                    labelStyle: const TextStyle(color: Colors.grey),
                    filled: true,
                    fillColor: AppTheme.surfaceDark,
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
                  ),
                  validator: (val) => val == null || val.isEmpty ? 'Required' : null,
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(
                      flex: 2,
                      child: DropdownButtonFormField<String>(
                        value: _sourceType,
                        dropdownColor: AppTheme.surfaceDark,
                        style: const TextStyle(color: Colors.white),
                        decoration: InputDecoration(
                          labelText: 'Source Type',
                          labelStyle: const TextStyle(color: Colors.grey),
                          filled: true,
                          fillColor: AppTheme.surfaceDark,
                          border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
                        ),
                        items: _sourceTypes.map((c) => DropdownMenuItem(value: c, child: Text(c.toUpperCase()))).toList(),
                        onChanged: (val) {
                          if (val != null) setState(() => _sourceType = val);
                        },
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      flex: 1,
                      child: SwitchListTile(
                        contentPadding: EdgeInsets.zero,
                        title: const Text('Active', style: TextStyle(color: Colors.white, fontSize: 12)),
                        value: _isActive,
                        activeColor: AppTheme.primaryIndigo,
                        onChanged: (val) => setState(() => _isActive = val),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),
                Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    TextButton(
                      onPressed: () => Navigator.of(context).pop(),
                      child: const Text('Cancel', style: TextStyle(color: Colors.grey)),
                    ),
                    const SizedBox(width: 16),
                    Container(
                      decoration: BoxDecoration(
                        gradient: AppTheme.primaryGradient,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: ElevatedButton(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.transparent,
                          shadowColor: Colors.transparent,
                          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                        ),
                        onPressed: _isSaving ? null : _save,
                        child: _isSaving
                            ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                            : const Text('Save', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _ScrapeUrlDialog extends StatefulWidget {
  final VoidCallback onScraped;

  const _ScrapeUrlDialog({required this.onScraped});

  @override
  State<_ScrapeUrlDialog> createState() => _ScrapeUrlDialogState();
}

class _ScrapeUrlDialogState extends State<_ScrapeUrlDialog> {
  final _urlCtrl = TextEditingController();
  bool _isScraping = false;

  @override
  void dispose() {
    _urlCtrl.dispose();
    super.dispose();
  }

  Future<void> _scrape() async {
    final url = _urlCtrl.text.trim();
    if (url.isEmpty) return;
    
    setState(() => _isScraping = true);
    
    try {
      final projectId = context.read<ProjectProvider>().currentProject?.id;
      if (projectId == null) throw Exception('No active project');
      
      await ApiService.post('/knowledge/$projectId/scrape', {'url': url});
      
      if (mounted) {
        widget.onScraped();
        Navigator.of(context).pop();
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Successfully scraped URL'), backgroundColor: Colors.green),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to scrape URL: $e'), backgroundColor: Colors.red),
        );
      }
    } finally {
      if (mounted) setState(() => _isScraping = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      backgroundColor: AppTheme.backgroundDark,
      title: const Text('Scrape URL for Knowledge', style: TextStyle(color: Colors.white)),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Enter a webpage URL to extract and add to the knowledge base',
            style: TextStyle(color: Colors.grey, fontSize: 14),
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _urlCtrl,
            style: const TextStyle(color: Colors.white),
            decoration: InputDecoration(
              labelText: 'URL',
              labelStyle: const TextStyle(color: Colors.grey),
              filled: true,
              fillColor: AppTheme.surfaceDark,
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
            ),
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: _isScraping ? null : () => Navigator.of(context).pop(),
          child: const Text('Cancel', style: TextStyle(color: Colors.grey)),
        ),
        ElevatedButton(
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.green, // emerald/green
            foregroundColor: Colors.white,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          ),
          onPressed: _isScraping ? null : _scrape,
          child: _isScraping
              ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
              : const Text('Scrape', style: TextStyle(fontWeight: FontWeight.bold)),
        ),
      ],
    );
  }
}
