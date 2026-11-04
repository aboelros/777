import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/localization/app_localizations.dart';
import '../../../core/theme/app_colors.dart';
import '../../../shared/utils/validators.dart';
import '../../../shared/widgets/app_button.dart';
import '../../../shared/widgets/app_text_field.dart';
import '../models/product_model.dart';
import '../providers/products_provider.dart';

/// Form screen for adding or updating a catalog product.
class EditProductScreen extends ConsumerStatefulWidget {
  final ProductModel? product;

  const EditProductScreen({super.key, this.product});

  @override
  ConsumerState<EditProductScreen> createState() => _EditProductScreenState();
}

class _EditProductScreenState extends ConsumerState<EditProductScreen> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _nameController;
  late final TextEditingController _priceController;
  late final TextEditingController _stockController;
  late final TextEditingController _skuController;
  late final TextEditingController _descController;
  bool _isSaving = false;

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController(text: widget.product?.name ?? '');
    _priceController = TextEditingController(
      text: widget.product != null ? widget.product!.price.toString() : '',
    );
    _stockController = TextEditingController(
      text: widget.product != null
          ? widget.product!.stockQuantity.toString()
          : '0',
    );
    _skuController = TextEditingController(text: widget.product?.sku ?? '');
    _descController =
        TextEditingController(text: widget.product?.description ?? '');
  }

  @override
  void dispose() {
    _nameController.dispose();
    _priceController.dispose();
    _stockController.dispose();
    _skuController.dispose();
    _descController.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _isSaving = true);

    final price = double.tryParse(_priceController.text.trim()) ?? 0.0;
    final stock = int.tryParse(_stockController.text.trim()) ?? 0;
    final notifier = ref.read(productsProvider.notifier);

    bool success = false;
    if (widget.product == null) {
      success = await notifier.createProduct(
        name: _nameController.text.trim(),
        price: price,
        stockQuantity: stock,
        sku: _skuController.text.trim(),
        description: _descController.text.trim(),
      );
    } else {
      success = await notifier.updateProduct(
        productId: widget.product!.id,
        name: _nameController.text.trim(),
        price: price,
        stockQuantity: stock,
        description: _descController.text.trim(),
      );
    }

    if (success && mounted) {
      Navigator.pop(context);
    } else if (mounted) {
      setState(() => _isSaving = false);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Failed to save product')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final isNew = widget.product == null;

    return Scaffold(
      backgroundColor: AppColors.bgDark,
      appBar: AppBar(
        title: Text(isNew ? context.tr('addProduct') : 'Edit Product'),
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
                  controller: _nameController,
                  label: 'Product Name',
                  hintText: 'e.g. Premium Cotton Shirt',
                  validator: (v) =>
                      AppValidators.requiredField(v, 'Product name'),
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(
                      child: AppTextField(
                        controller: _priceController,
                        label: context.tr('productPrice'),
                        hintText: '99.99',
                        keyboardType: const TextInputType.numberWithOptions(
                            decimal: true),
                        validator: (v) =>
                            AppValidators.requiredField(v, 'Price'),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: AppTextField(
                        controller: _stockController,
                        label: context.tr('productStock'),
                        hintText: '10',
                        keyboardType: TextInputType.number,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                AppTextField(
                  controller: _skuController,
                  label: 'SKU Code',
                  hintText: 'PROD-001',
                ),
                const SizedBox(height: 16),
                AppTextField(
                  controller: _descController,
                  label: 'Description',
                  hintText:
                      'Detailed product information for AI bot to reference...',
                  maxLines: 4,
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
