import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/network/api_endpoints.dart';
import '../../auth/providers/auth_provider.dart';
import '../../projects/providers/project_provider.dart';
import '../models/product_model.dart';

class ProductsState {
  final List<ProductModel> products;
  final bool isLoading;
  final String? error;

  const ProductsState({
    this.products = const [],
    this.isLoading = false,
    this.error,
  });

  ProductsState copyWith({
    List<ProductModel>? products,
    bool? isLoading,
    String? error,
  }) {
    return ProductsState(
      products: products ?? this.products,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

final productsProvider =
    StateNotifierProvider<ProductsNotifier, ProductsState>((ref) {
  final api = ref.watch(apiClientProvider);
  final activeProject = ref.watch(activeProjectProvider);
  return ProductsNotifier(api: api, projectId: activeProject?.id);
});

class ProductsNotifier extends StateNotifier<ProductsState> {
  final dynamic _api;
  final String? _projectId;

  ProductsNotifier({required dynamic api, String? projectId})
      : _api = api,
        _projectId = projectId,
        super(const ProductsState()) {
    if (_projectId != null) {
      loadProducts();
    }
  }

  Future<void> loadProducts() async {
    if (_projectId == null) return;
    state = state.copyWith(isLoading: true, error: null);

    try {
      final response = await _api.get(ApiEndpoints.products(_projectId));
      List<ProductModel> list = [];
      if (response is List) {
        list = response
            .whereType<Map<String, dynamic>>()
            .map((e) => ProductModel.fromJson(e))
            .toList();
      }
      state = state.copyWith(products: list, isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<bool> createProduct({
    required String name,
    required double price,
    int stockQuantity = 0,
    String? description,
    String? sku,
  }) async {
    if (_projectId == null) return false;
    try {
      final payload = {
        'name': name,
        'price': price,
        'stock_quantity': stockQuantity,
        'description': description,
        'sku': sku,
        'in_stock': stockQuantity > 0,
      };
      await _api.post(ApiEndpoints.products(_projectId), data: payload);
      await loadProducts();
      return true;
    } catch (_) {
      return false;
    }
  }

  Future<bool> updateProduct({
    required String productId,
    required String name,
    required double price,
    int stockQuantity = 0,
    String? description,
  }) async {
    if (_projectId == null) return false;
    try {
      final payload = {
        'name': name,
        'price': price,
        'stock_quantity': stockQuantity,
        'description': description,
        'in_stock': stockQuantity > 0,
      };
      await _api.put(
        ApiEndpoints.product(_projectId, productId),
        data: payload,
      );
      await loadProducts();
      return true;
    } catch (_) {
      return false;
    }
  }

  Future<bool> deleteProduct(String productId) async {
    if (_projectId == null) return false;
    try {
      await _api.delete(ApiEndpoints.product(_projectId, productId));
      state = state.copyWith(
        products: state.products.where((p) => p.id != productId).toList(),
      );
      return true;
    } catch (_) {
      return false;
    }
  }
}
