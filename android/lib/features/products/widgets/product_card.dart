import 'package:flutter/material.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../../shared/utils/formatters.dart';
import '../../../shared/widgets/glass_card.dart';
import '../../../shared/widgets/status_badge.dart';
import '../models/product_model.dart';

/// Card widget displaying catalog product item.
class ProductCard extends StatelessWidget {
  final ProductModel product;
  final VoidCallback onTap;
  final VoidCallback onDelete;

  const ProductCard({
    super.key,
    required this.product,
    required this.onTap,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      onTap: onTap,
      padding: const EdgeInsets.all(14),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 50,
            height: 50,
            decoration: BoxDecoration(
              color: AppColors.surfaceElevated,
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: AppColors.border),
            ),
            child: const Icon(
              Icons.inventory_2_outlined,
              color: AppColors.brandPrimary,
              size: 24,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Text(
                        product.name,
                        style: AppTypography.cardTitle,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.delete_outline_rounded,
                          size: 18, color: AppColors.textMuted),
                      onPressed: onDelete,
                      padding: EdgeInsets.zero,
                      constraints: const BoxConstraints(),
                    ),
                  ],
                ),
                if (product.sku != null && product.sku!.isNotEmpty)
                  Text('SKU: ${product.sku}', style: AppTypography.caption),
                const SizedBox(height: 6),
                Row(
                  children: [
                    Text(
                      AppFormatters.currency(product.price,
                          currencySymbol:
                              product.currency == 'EGP' ? 'EGP ' : '\$'),
                      style: AppTypography.numericMedium
                          .copyWith(color: AppColors.brandLight),
                    ),
                    const SizedBox(width: 12),
                    StatusBadge(
                      label: product.stockQuantity > 0
                          ? '${product.stockQuantity} in stock'
                          : 'Out of stock',
                      variant: product.stockQuantity > 0
                          ? BadgeVariant.success
                          : BadgeVariant.danger,
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
