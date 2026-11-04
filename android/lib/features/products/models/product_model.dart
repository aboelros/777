/// Product domain model matching backend `ProductResponse`.
class ProductModel {
  final String id;
  final String name;
  final String? description;
  final String? sku;
  final double price;
  final String currency;
  final int stockQuantity;
  final bool inStock;
  final List<Map<String, dynamic>> images;
  final String? category;
  final bool isActive;

  const ProductModel({
    required this.id,
    required this.name,
    this.description,
    this.sku,
    this.price = 0.0,
    this.currency = 'USD',
    this.stockQuantity = 0,
    this.inStock = true,
    this.images = const [],
    this.category,
    this.isActive = true,
  });

  factory ProductModel.fromJson(Map<String, dynamic> json) {
    return ProductModel(
      id: json['id']?.toString() ?? '',
      name: json['name']?.toString() ?? 'Product',
      description: json['description']?.toString(),
      sku: json['sku']?.toString(),
      price: (json['price'] as num?)?.toDouble() ?? 0.0,
      currency: json['currency']?.toString() ?? 'USD',
      stockQuantity: (json['stock_quantity'] as num?)?.toInt() ?? 0,
      inStock: json['in_stock'] != false,
      images: (json['images'] as List?)
              ?.whereType<Map<String, dynamic>>()
              .toList() ??
          [],
      category: json['category']?.toString(),
      isActive: json['is_active'] != false,
    );
  }

  String? get primaryImageUrl {
    if (images.isEmpty) return null;
    return images.first['url']?.toString() ?? images.first['src']?.toString();
  }
}
