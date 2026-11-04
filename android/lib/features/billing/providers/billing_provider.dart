import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/network/api_endpoints.dart';
import '../../auth/providers/auth_provider.dart';
import '../models/subscription_model.dart';

class BillingState {
  final SubscriptionModel? subscription;
  final bool isLoading;
  final String? error;

  const BillingState({
    this.subscription,
    this.isLoading = false,
    this.error,
  });

  BillingState copyWith({
    SubscriptionModel? subscription,
    bool? isLoading,
    String? error,
  }) {
    return BillingState(
      subscription: subscription ?? this.subscription,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

final billingProvider =
    StateNotifierProvider<BillingNotifier, BillingState>((ref) {
  final api = ref.watch(apiClientProvider);
  return BillingNotifier(api: api);
});

class BillingNotifier extends StateNotifier<BillingState> {
  final dynamic _api;

  BillingNotifier({required dynamic api})
      : _api = api,
        super(const BillingState()) {
    loadBilling();
  }

  Future<void> loadBilling() async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final response = await _api.get(ApiEndpoints.mySubscription);
      if (response is Map<String, dynamic>) {
        final sub = SubscriptionModel.fromJson(response);
        state = state.copyWith(subscription: sub, isLoading: false);
      } else {
        state = state.copyWith(isLoading: false);
      }
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }
}
