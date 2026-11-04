import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/network/api_endpoints.dart';
import '../../auth/providers/auth_provider.dart';
import '../../projects/providers/project_provider.dart';
import '../models/order_model.dart';

class OrdersState {
  final List<OrderModel> orders;
  final String statusFilter;
  final bool isLoading;
  final String? error;

  const OrdersState({
    this.orders = const [],
    this.statusFilter = 'all',
    this.isLoading = false,
    this.error,
  });

  OrdersState copyWith({
    List<OrderModel>? orders,
    String? statusFilter,
    bool? isLoading,
    String? error,
  }) {
    return OrdersState(
      orders: orders ?? this.orders,
      statusFilter: statusFilter ?? this.statusFilter,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }

  List<OrderModel> get filteredOrders {
    if (statusFilter == 'all') return orders;
    return orders
        .where((o) => o.status.toLowerCase() == statusFilter.toLowerCase())
        .toList();
  }
}

final ordersProvider =
    StateNotifierProvider<OrdersNotifier, OrdersState>((ref) {
  final api = ref.watch(apiClientProvider);
  final activeProject = ref.watch(activeProjectProvider);
  return OrdersNotifier(api: api, projectId: activeProject?.id);
});

class OrdersNotifier extends StateNotifier<OrdersState> {
  final dynamic _api;
  final String? _projectId;

  OrdersNotifier({required dynamic api, String? projectId})
      : _api = api,
        _projectId = projectId,
        super(const OrdersState()) {
    if (_projectId != null) {
      loadOrders();
    }
  }

  Future<void> loadOrders() async {
    if (_projectId == null) return;
    state = state.copyWith(isLoading: true, error: null);

    try {
      final response = await _api.get(ApiEndpoints.orders(_projectId));
      List<OrderModel> list = [];
      if (response is List) {
        list = response
            .whereType<Map<String, dynamic>>()
            .map((e) => OrderModel.fromJson(e))
            .toList();
      }
      state = state.copyWith(orders: list, isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  void filterByStatus(String status) {
    state = state.copyWith(statusFilter: status);
  }

  Future<bool> updateOrderStatus(String orderId, String newStatus) async {
    if (_projectId == null) return false;

    try {
      final endpoint = ApiEndpoints.order(_projectId, orderId);
      await _api.patch(endpoint, data: {'status': newStatus});

      final updated = state.orders.map((o) {
        if (o.id == orderId) {
          return o.copyWith(status: newStatus);
        }
        return o;
      }).toList();

      state = state.copyWith(orders: updated);
      return true;
    } catch (_) {
      return false;
    }
  }
}
