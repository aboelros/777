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
import '../models/product_model.dart';
import '../providers/products_provider.dart';
import '../widgets/product_card.dart';

/// Screen managing product catalog, inventory stock, and pricing.
class ProductsScreen extends ConsumerWidget {
  const ProductsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final activeProject = ref.watch(activeProjectProvider);
    final productsState = ref.watch(productsProvider);
    final products = productsState.products;

    return Scaffold(
      backgroundColor: AppColors.bgDark,
      appBar: AppBar(
        title: Text(context.tr('products'), style: AppTypography.pageTitle),
      ),
      floatingActionButton: activeProject != null
          ? FloatingActionButton(
              backgroundColor: AppColors.brandPrimary,
              child: const Icon(Icons.add, color: Colors.white),
              onPressed: () => context.push('/products/edit'),
            )
          : null,
      body: activeProject == null
          ? EmptyView(
              title: context.tr('noProject'),
              subtitle: 'Select a workspace to manage catalog products.',
            )
          : productsState.isLoading && products.isEmpty
              ? _buildSkeletonList()
              : productsState.error != null && products.isEmpty
                  ? ErrorView(
                      message: productsState.error,
                      onRetry: () =>
                          ref.read(productsProvider.notifier).loadProducts(),
                    )
                  : products.isEmpty
                      ? EmptyView(
                          title: 'No Products in Catalog',
                          subtitle: 'Add products for your AI agents to sell.',
                          icon: Icons.inventory_2_outlined,
                          actionText: context.tr('addProduct'),
                          onAction: () => context.push('/products/edit'),
                        )
                      : RefreshIndicator(
                          color: AppColors.brandPrimary,
                          backgroundColor: AppColors.surfaceElevated,
                          onRefresh: () => ref
                              .read(productsProvider.notifier)
                              .loadProducts(),
                          child: ListView.separated(
                            padding: const EdgeInsets.all(16),
                            itemCount: products.length,
                            separatorBuilder: (_, __) =>
                                const SizedBox(height: 10),
                            itemBuilder: (context, index) {
                              final p = products[index];
                              return ProductCard(
                                product: p,
                                onTap: () => _editProduct(context, p),
                                onDelete: () =>
                                    _confirmDelete(context, ref, p.id, p.name),
                              );
                            },
                          ),
                        ),
    );
  }

  void _editProduct(BuildContext context, ProductModel product) {
    context.push('/products/edit', extra: product);
  }

  void _confirmDelete(
      BuildContext context, WidgetRef ref, String id, String name) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppColors.surfaceElevated,
        title: Text('Delete Product', style: AppTypography.cardTitle),
        content: Text('Are you sure you want to delete "$name"?',
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
              ref.read(productsProvider.notifier).deleteProduct(id);
            },
          ),
        ],
      ),
    );
  }

  Widget _buildSkeletonList() {
    return ListView.separated(
      padding: const EdgeInsets.all(16),
      itemCount: 5,
      separatorBuilder: (_, __) => const SizedBox(height: 10),
      itemBuilder: (_, __) =>
          const SkeletonLoader(width: double.infinity, height: 80),
    );
  }
}
