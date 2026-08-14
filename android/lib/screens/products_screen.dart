import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:shimmer/shimmer.dart';
import 'package:provider/provider.dart';
import '../providers/project_provider.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';

class ProductModel {
  final String id;
  final String name;
  final String? description;
  final String? sku;
  final double? price;
  final String currency;
  final int? stockQuantity;
  final bool inStock;
  final String? category;
  final List<String> tags;
  final List<String> keywords;
  final List<String> storageLocations;
  final int? reorderPoint;
  final int? safetyStock;
  final String? storageNotes;
  final List<String> storageAttachments;
  
  const ProductModel({
    required this.id,
    required this.name,
    this.description,
    this.sku,
    this.price,
    this.currency = 'USD',
    this.stockQuantity,
    this.inStock = true,
    this.category,
    this.tags = const [],
    this.keywords = const [],
    this.storageLocations = const [],
    this.reorderPoint,
    this.safetyStock,
    this.storageNotes,
    this.storageAttachments = const [],
  });
  
  factory ProductModel.fromJson(Map<String, dynamic> json) => ProductModel(
    id: json['id']?.toString() ?? '',
    name: json['name']?.toString() ?? '',
    description: json['description']?.toString(),
    sku: json['sku']?.toString(),
    price: (json['price'] as num?)?.toDouble(),
    currency: json['currency']?.toString() ?? 'USD',
    stockQuantity: (json['stock_quantity'] as num?)?.toInt(),
    inStock: json['in_stock'] != false,
    category: json['category']?.toString(),
    tags: (json['tags'] as List?)?.map((e) => e.toString()).toList() ?? [],
    keywords: (json['keywords'] as List?)?.map((e) => e.toString()).toList() ?? [],
    storageLocations: json['storage_locations'] is List
        ? (json['storage_locations'] as List).map((e) {
            if (e is String) return e;
            if (e is Map<String, dynamic>) return (e['name'] ?? '').toString();
            return '';
          }).where((e) => e.isNotEmpty).toList()
        : [],
    reorderPoint: (json['reorder_point'] as num?)?.toInt(),
    safetyStock: (json['safety_stock'] as num?)?.toInt(),
    storageNotes: json['storage_notes']?.toString(),
    storageAttachments: (json['storage_attachments'] as List?)?.map((e) => e.toString()).toList() ?? [],
  );
  
  Map<String, dynamic> toJson() => {
    'name': name,
    'description': description,
    'sku': sku,
    'price': price,
    'currency': currency,
    'stock_quantity': stockQuantity,
    'in_stock': inStock,
    'category': category,
    'tags': tags,
    'keywords': keywords,
    'storage_locations': storageLocations,
    'reorder_point': reorderPoint,
    'safety_stock': safetyStock,
    'storage_notes': storageNotes,
    'storage_attachments': storageAttachments,
  };
}

class ProductsScreen extends StatefulWidget {
  const ProductsScreen({super.key});

  @override
  State<ProductsScreen> createState() => _ProductsScreenState();
}

class _ProductsScreenState extends State<ProductsScreen> {
  final ApiService _apiService = ApiService();
  List<ProductModel> _products = [];
  bool _isLoading = false;
  String? _error;
  String _searchQuery = '';
  String? _selectedStorageProductId;
  bool _isSearchExpanded = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _fetchProducts();
    });
  }

  Future<void> _fetchProducts() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final projectId = context.read<ProjectProvider>().currentProjectId ?? '';
      if (projectId.isEmpty) {
        throw Exception('No project selected');
      }

      final response = await _apiService.get('/products/$projectId');
      
      List<dynamic> dataList;
      if (response is Map<String, dynamic> && response.containsKey('products')) {
        dataList = response['products'] as List<dynamic>;
      } else if (response is List) {
        dataList = response;
      } else {
        dataList = [];
      }

      setState(() {
        _products = dataList.map((e) => ProductModel.fromJson(e as Map<String, dynamic>)).toList();
        if (_products.isNotEmpty && _selectedStorageProductId == null) {
          _selectedStorageProductId = _products.first.id;
        }
      });
    } catch (e) {
      debugPrint('Error fetching products: $e');
      setState(() => _error = e.toString());
    } finally {
      setState(() => _isLoading = false);
    }
  }

  List<ProductModel> get _filteredProducts {
    if (_searchQuery.isEmpty) return _products;
    return _products.where((p) {
      final query = _searchQuery.toLowerCase();
      return p.name.toLowerCase().contains(query) || 
             (p.sku?.toLowerCase().contains(query) ?? false) ||
             p.tags.any((t) => t.toLowerCase().contains(query));
    }).toList();
  }

  void _showProductForm([ProductModel? product]) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => _ProductFormSheet(
        product: product,
        onSave: (data) async {
          final projectId = context.read<ProjectProvider>().currentProjectId ?? '';
          try {
            if (product == null) {
              await _apiService.post('/products/$projectId', data);
              if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Product added successfully')));
            } else {
              await _apiService.put('/products/$projectId/${product.id}', data);
              if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Product updated successfully')));
            }
            _fetchProducts();
          } catch (e) {
            debugPrint('Error saving product: $e');
            if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e')));
          }
        },
      ),
    );
  }

  Future<void> _deleteProduct(String id) async {
    final projectId = context.read<ProjectProvider>().currentProjectId ?? '';
    try {
      await _apiService.delete('/products/$projectId/$id');
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Product deleted')));
      _fetchProducts();
    } catch (e) {
      debugPrint('Error deleting product: $e');
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error deleting: $e')));
    }
  }

  Widget _buildShimmer() {
    return Shimmer.fromColors(
      baseColor: AppTheme.surfaceDark,
      highlightColor: AppTheme.surfaceDark.withValues(alpha: 0.5),
      child: GridView.builder(
        padding: const EdgeInsets.all(16),
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 2,
          mainAxisSpacing: 16,
          crossAxisSpacing: 16,
          childAspectRatio: 0.75,
        ),
        itemCount: 4,
        itemBuilder: (_, __) => Container(
          decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16)),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final filtered = _filteredProducts;
    final totalProducts = _products.length;
    final inStockProducts = _products.where((p) => p.inStock).length;
    final outOfStockProducts = totalProducts - inStockProducts;

    return Scaffold(
      backgroundColor: AppTheme.backgroundDark,
      appBar: AppBar(
        title: const Text('Products', style: TextStyle(color: Colors.white)),
        flexibleSpace: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [AppTheme.primaryIndigo, Colors.indigo[700]!],
            ),
          ),
        ),
        actions: [
          IconButton(
            icon: Icon(_isSearchExpanded ? Icons.close : Icons.search, color: Colors.white),
            onPressed: () {
              setState(() {
                _isSearchExpanded = !_isSearchExpanded;
                if (!_isSearchExpanded) _searchQuery = '';
              });
            },
          ),
          IconButton(
            icon: const Icon(Icons.add, color: Colors.white),
            onPressed: () => _showProductForm(),
          ),
        ],
      ),
      body: SafeArea(
        child: Column(
          children: [
            if (_isSearchExpanded)
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: TextField(
                  style: const TextStyle(color: Colors.white),
                  decoration: InputDecoration(
                    hintText: 'Search products...',
                    hintStyle: const TextStyle(color: Colors.grey),
                    filled: true,
                    fillColor: AppTheme.surfaceDark,
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide.none,
                    ),
                    prefixIcon: const Icon(Icons.search, color: Colors.grey),
                  ),
                  onChanged: (val) => setState(() => _searchQuery = val),
                ),
              ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
              child: Row(
                children: [
                  _StatChip(label: 'Total: $totalProducts', color: AppTheme.primaryIndigo),
                  const SizedBox(width: 8),
                  _StatChip(label: 'In Stock: $inStockProducts', color: Colors.green),
                  const SizedBox(width: 8),
                  _StatChip(label: 'Out: $outOfStockProducts', color: Colors.red),
                ],
              ),
            ),
            Expanded(
              child: RefreshIndicator(
                onRefresh: _fetchProducts,
                child: _isLoading
                    ? _buildShimmer()
                    : _error != null
                        ? Center(
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Text(_error!, style: const TextStyle(color: Colors.red)),
                                ElevatedButton(onPressed: _fetchProducts, child: const Text('Retry'))
                              ],
                            ),
                          )
                        : filtered.isEmpty
                            ? const Center(child: Text('No products found', style: TextStyle(color: Colors.grey)))
                            : CustomScrollView(
                                slivers: [
                                  SliverPadding(
                                    padding: const EdgeInsets.all(16.0),
                                    sliver: SliverGrid(
                                      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                                        crossAxisCount: 2,
                                        mainAxisSpacing: 16,
                                        crossAxisSpacing: 16,
                                        childAspectRatio: 0.65,
                                      ),
                                      delegate: SliverChildBuilderDelegate(
                                        (context, index) {
                                          final product = filtered[index];
                                          return _ProductCard(
                                            product: product,
                                            onEdit: () => _showProductForm(product),
                                            onDelete: () => _deleteProduct(product.id),
                                          );
                                        },
                                        childCount: filtered.length,
                                      ),
                                    ),
                                  ),
                                  SliverToBoxAdapter(
                                    child: Padding(
                                      padding: const EdgeInsets.only(bottom: 80.0),
                                      child: _StorageSection(
                                        products: _products,
                                        selectedId: _selectedStorageProductId,
                                        onSelect: (id) => setState(() => _selectedStorageProductId = id),
                                      ),
                                    ),
                                  ),
                                ],
                              ),
              ),
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        backgroundColor: AppTheme.primaryIndigo,
        onPressed: () => _showProductForm(),
        child: const Icon(Icons.add, color: Colors.white),
      ),
    );
  }
}

class _StatChip extends StatelessWidget {
  final String label;
  final Color color;
  const _StatChip({required this.label, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Text(label, style: TextStyle(color: color, fontSize: 12, fontWeight: FontWeight.bold)),
    );
  }
}

class _ProductCard extends StatelessWidget {
  final ProductModel product;
  final VoidCallback onEdit;
  final VoidCallback onDelete;

  const _ProductCard({required this.product, required this.onEdit, required this.onDelete});

  @override
  Widget build(BuildContext context) {
    return AnimatedContainer(
      duration: const Duration(milliseconds: 300),
      decoration: AppTheme.glassCard,
      child: InkWell(
        onTap: onEdit,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(12.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    child: Text(
                      product.name,
                      style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  Container(
                    width: 10,
                    height: 10,
                    decoration: BoxDecoration(
                      color: product.inStock ? Colors.green : Colors.red,
                      shape: BoxShape.circle,
                    ),
                  )
                ],
              ),
              if (product.sku != null && product.sku!.isNotEmpty) ...[
                const SizedBox(height: 4),
                Text(product.sku!, style: const TextStyle(color: Colors.grey, fontSize: 10)),
              ],
              const SizedBox(height: 8),
              Expanded(
                child: Text(
                  product.description ?? 'No description',
                  style: const TextStyle(color: Colors.grey, fontSize: 11),
                  maxLines: 3,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  const Icon(Icons.attach_money, color: Colors.green, size: 14),
                  Expanded(
                    child: Text(
                      '${product.price?.toStringAsFixed(2) ?? '0.00'} ${product.currency}',
                      style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 4),
              Text(
                product.stockQuantity != null ? 'Qty: ${product.stockQuantity}' : 'Qty: N/A',
                style: const TextStyle(color: Colors.white70, fontSize: 12),
              ),
              const SizedBox(height: 8),
              if (product.tags.isNotEmpty)
                Wrap(
                  spacing: 4,
                  runSpacing: 4,
                  children: product.tags.take(3).map((t) => Container(
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: AppTheme.primaryIndigo.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(t, style: TextStyle(color: AppTheme.primaryIndigo, fontSize: 9)),
                  )).toList(),
                ),
              const Spacer(),
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppTheme.surfaceDark,
                        foregroundColor: Colors.white,
                        padding: EdgeInsets.zero,
                        minimumSize: const Size(0, 32),
                      ),
                      onTap: onEdit,
                      onPressed: onEdit,
                      child: const Text('Edit', style: TextStyle(fontSize: 12)),
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.delete_outline, color: Colors.red, size: 20),
                    onPressed: onDelete,
                    padding: EdgeInsets.zero,
                    constraints: const BoxConstraints(),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    ).animate().fadeIn(duration: 200.ms).slideY(begin: 0.1, end: 0);
  }
}

class _StorageSection extends StatelessWidget {
  final List<ProductModel> products;
  final String? selectedId;
  final Function(String) onSelect;

  const _StorageSection({required this.products, required this.selectedId, required this.onSelect});

  @override
  Widget build(BuildContext context) {
    if (products.isEmpty) {
      return const Padding(
        padding: EdgeInsets.all(16.0),
        child: Text('No products yet', style: TextStyle(color: Colors.grey)),
      );
    }

    final selectedProduct = products.firstWhere((p) => p.id == selectedId, orElse: () => products.first);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Padding(
          padding: EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
          child: Text('📦 Storage Overview', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
        ),
        SizedBox(
          height: 40,
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 16.0),
            itemCount: products.length,
            itemBuilder: (context, index) {
              final product = products[index];
              final isSelected = product.id == selectedProduct.id;
              return Padding(
                padding: const EdgeInsets.only(right: 8.0),
                child: ChoiceChip(
                  label: Text(product.name),
                  selected: isSelected,
                  onSelected: (val) {
                    if (val) onSelect(product.id);
                  },
                  backgroundColor: AppTheme.surfaceDark,
                  selectedColor: AppTheme.primaryIndigo.withValues(alpha: 0.2),
                  labelStyle: TextStyle(color: isSelected ? AppTheme.primaryIndigo : Colors.white),
                  side: BorderSide(color: isSelected ? AppTheme.primaryIndigo : Colors.transparent),
                ),
              );
            },
          ),
        ),
        const SizedBox(height: 16),
        _StorageDetails(product: selectedProduct),
      ],
    );
  }
}

class _StorageDetails extends StatelessWidget {
  final ProductModel product;
  const _StorageDetails({required this.product});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16.0),
      padding: const EdgeInsets.all(16.0),
      decoration: BoxDecoration(
        color: AppTheme.surfaceDark,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _StatBox(label: 'Current Stock', value: product.stockQuantity?.toString() ?? 'N/A', icon: Icons.inventory),
              _StatBox(label: 'Reorder Pt', value: product.reorderPoint?.toString() ?? '-', icon: Icons.warning_amber),
              _StatBox(label: 'Safety Stock', value: product.safetyStock?.toString() ?? '-', icon: Icons.security),
            ],
          ),
          const SizedBox(height: 16),
          const Text('Storage Locations:', style: TextStyle(color: Colors.white70, fontSize: 12)),
          const SizedBox(height: 8),
          if (product.storageLocations.isEmpty)
            const Text('No locations defined', style: TextStyle(color: Colors.grey, fontSize: 12))
          else
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: product.storageLocations.map((loc) => Chip(
                label: Text(loc, style: const TextStyle(color: Colors.white, fontSize: 12)),
                backgroundColor: AppTheme.backgroundDark,
                side: BorderSide.none,
              )).toList(),
            ),
          if (product.storageNotes != null && product.storageNotes!.isNotEmpty) ...[
            const SizedBox(height: 16),
            const Text('Notes:', style: TextStyle(color: Colors.white70, fontSize: 12)),
            const SizedBox(height: 4),
            Text(product.storageNotes!, style: const TextStyle(color: Colors.white, fontSize: 13)),
          ],
        ],
      ),
    );
  }
}

class _StatBox extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;

  const _StatBox({required this.label, required this.value, required this.icon});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Icon(icon, color: AppTheme.primaryIndigo, size: 24),
        const SizedBox(height: 8),
        Text(value, style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
        const SizedBox(height: 4),
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 10)),
      ],
    );
  }
}

class _ProductFormSheet extends StatefulWidget {
  final ProductModel? product;
  final Function(Map<String, dynamic>) onSave;

  const _ProductFormSheet({this.product, required this.onSave});

  @override
  State<_ProductFormSheet> createState() => _ProductFormSheetState();
}

class _ProductFormSheetState extends State<_ProductFormSheet> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _nameController;
  late TextEditingController _descController;
  late TextEditingController _skuController;
  late TextEditingController _categoryController;
  late TextEditingController _priceController;
  late TextEditingController _stockController;
  late TextEditingController _tagsController;
  late TextEditingController _keywordsController;
  late TextEditingController _locationsController;
  late TextEditingController _reorderController;
  late TextEditingController _safetyController;
  late TextEditingController _notesController;
  
  bool _inStock = true;
  String _currency = 'USD';
  final List<String> _currencies = ['USD', 'EUR', 'GBP', 'EGP'];

  @override
  void initState() {
    super.initState();
    final p = widget.product;
    _nameController = TextEditingController(text: p?.name ?? '');
    _descController = TextEditingController(text: p?.description ?? '');
    _skuController = TextEditingController(text: p?.sku ?? '');
    _categoryController = TextEditingController(text: p?.category ?? '');
    _priceController = TextEditingController(text: p?.price?.toString() ?? '');
    _stockController = TextEditingController(text: p?.stockQuantity?.toString() ?? '');
    _tagsController = TextEditingController(text: p?.tags.join(', ') ?? '');
    _keywordsController = TextEditingController(text: p?.keywords.join(', ') ?? '');
    _locationsController = TextEditingController(text: p?.storageLocations.join(' | ') ?? '');
    _reorderController = TextEditingController(text: p?.reorderPoint?.toString() ?? '');
    _safetyController = TextEditingController(text: p?.safetyStock?.toString() ?? '');
    _notesController = TextEditingController(text: p?.storageNotes ?? '');
    
    _inStock = p?.inStock ?? true;
    if (p != null && _currencies.contains(p.currency)) {
      _currency = p.currency;
    }
  }

  @override
  void dispose() {
    _nameController.dispose();
    _descController.dispose();
    _skuController.dispose();
    _categoryController.dispose();
    _priceController.dispose();
    _stockController.dispose();
    _tagsController.dispose();
    _keywordsController.dispose();
    _locationsController.dispose();
    _reorderController.dispose();
    _safetyController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  void _submit() {
    if (_formKey.currentState!.validate()) {
      final data = {
        'name': _nameController.text.trim(),
        'description': _descController.text.trim(),
        'sku': _skuController.text.trim(),
        'category': _categoryController.text.trim(),
        'price': double.tryParse(_priceController.text),
        'currency': _currency,
        'stock_quantity': int.tryParse(_stockController.text),
        'in_stock': _inStock,
        'tags': _tagsController.text.split(',').map((e) => e.trim()).where((e) => e.isNotEmpty).toList(),
        'keywords': _keywordsController.text.split(',').map((e) => e.trim()).where((e) => e.isNotEmpty).toList(),
        'storage_locations': _locationsController.text.split('|').map((e) => e.trim()).where((e) => e.isNotEmpty).toList(),
        'reorder_point': int.tryParse(_reorderController.text),
        'safety_stock': int.tryParse(_safetyController.text),
        'storage_notes': _notesController.text.trim(),
      };
      widget.onSave(data);
      Navigator.pop(context);
    }
  }

  Widget _buildTextField(TextEditingController controller, String label, {int maxLines = 1, TextInputType? keyboardType, String? hintText}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16.0),
      child: TextFormField(
        controller: controller,
        maxLines: maxLines,
        keyboardType: keyboardType,
        style: const TextStyle(color: Colors.white),
        decoration: InputDecoration(
          labelText: label,
          labelStyle: const TextStyle(color: Colors.grey),
          hintText: hintText,
          hintStyle: const TextStyle(color: Colors.white30),
          filled: true,
          fillColor: AppTheme.surfaceDark,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: BorderSide.none,
          ),
        ),
        validator: label == 'Name' ? (v) => v!.isEmpty ? 'Required' : null : null,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return DraggableScrollableSheet(
      initialChildSize: 0.9,
      maxChildSize: 0.9,
      minChildSize: 0.5,
      builder: (_, scrollController) => Container(
        decoration: const BoxDecoration(
          color: AppTheme.backgroundDark,
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        ),
        child: Column(
          children: [
            Center(
              child: Container(
                margin: const EdgeInsets.only(top: 12, bottom: 16),
                width: 40,
                height: 4,
                decoration: BoxDecoration(color: Colors.grey[700], borderRadius: BorderRadius.circular(2)),
              ),
            ),
            Text(widget.product == null ? 'Add Product' : 'Edit Product', style: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 16),
            Expanded(
              child: ListView(
                controller: scrollController,
                padding: const EdgeInsets.symmetric(horizontal: 20),
                children: [
                  Form(
                    key: _formKey,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        _buildTextField(_nameController, 'Name'),
                        _buildTextField(_descController, 'Description', maxLines: 3),
                        _buildTextField(_skuController, 'SKU'),
                        _buildTextField(_categoryController, 'Category'),
                        Row(
                          children: [
                            Expanded(child: _buildTextField(_priceController, 'Price', keyboardType: TextInputType.number)),
                            const SizedBox(width: 16),
                            Container(
                              margin: const EdgeInsets.only(bottom: 16.0),
                              padding: const EdgeInsets.symmetric(horizontal: 12),
                              decoration: BoxDecoration(color: AppTheme.surfaceDark, borderRadius: BorderRadius.circular(12)),
                              child: DropdownButtonHideUnderline(
                                child: DropdownButton<String>(
                                  value: _currency,
                                  dropdownColor: AppTheme.surfaceDark,
                                  style: const TextStyle(color: Colors.white),
                                  onChanged: (v) => setState(() => _currency = v!),
                                  items: _currencies.map((c) => DropdownMenuItem(value: c, child: Text(c))).toList(),
                                ),
                              ),
                            ),
                          ],
                        ),
                        _buildTextField(_stockController, 'Stock Quantity', keyboardType: TextInputType.number),
                        SwitchListTile(
                          title: const Text('In Stock', style: TextStyle(color: Colors.white)),
                          value: _inStock,
                          activeColor: AppTheme.primaryIndigo,
                          contentPadding: EdgeInsets.zero,
                          onChanged: (v) => setState(() => _inStock = v),
                        ),
                        _buildTextField(_tagsController, 'Tags', hintText: 'tag1, tag2'),
                        _buildTextField(_keywordsController, 'Keywords', hintText: 'keyword1, keyword2'),
                        _buildTextField(_locationsController, 'Storage Locations', hintText: 'Main Warehouse | Shelf B3'),
                        Row(
                          children: [
                            Expanded(child: _buildTextField(_reorderController, 'Reorder Point', keyboardType: TextInputType.number)),
                            const SizedBox(width: 16),
                            Expanded(child: _buildTextField(_safetyController, 'Safety Stock', keyboardType: TextInputType.number)),
                          ],
                        ),
                        _buildTextField(_notesController, 'Storage Notes', maxLines: 3),
                        const SizedBox(height: 24),
                        Row(
                          children: [
                            Expanded(
                              child: TextButton(
                                onPressed: () => Navigator.pop(context),
                                child: const Text('Cancel', style: TextStyle(color: Colors.grey)),
                              ),
                            ),
                            const SizedBox(width: 16),
                            Expanded(
                              child: Container(
                                decoration: BoxDecoration(
                                  gradient: LinearGradient(colors: [AppTheme.primaryIndigo, Colors.indigo[700]!]),
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: ElevatedButton(
                                  style: ElevatedButton.styleFrom(backgroundColor: Colors.transparent, shadowColor: Colors.transparent),
                                  onPressed: _submit,
                                  child: const Text('Save', style: TextStyle(color: Colors.white)),
                                ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 40),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
