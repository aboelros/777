/// Order domain model matching `OrderResponse`.
class OrderModel {
  final String id;
  final String projectId;
  final String externalId;
  final String provider;
  final String status;
  final Map<String, dynamic> customer;
  final List<Map<String, dynamic>> items;
  final double total;
  final String currency;
  final DateTime? orderDate;
  final DateTime? fulfilledDate;

  const OrderModel({
    required this.id,
    required this.projectId,
    required this.externalId,
    required this.provider,
    required this.status,
    this.customer = const {},
    this.items = const [],
    this.total = 0.0,
    this.currency = 'USD',
    this.orderDate,
    this.fulfilledDate,
  });

  factory OrderModel.fromJson(Map<String, dynamic> json) {
    return OrderModel(
      id: json['id']?.toString() ?? '',
      projectId: json['project_id']?.toString() ?? '',
      externalId: json['external_id']?.toString() ?? '',
      provider: json['provider']?.toString() ?? 'direct',
      status: json['status']?.toString().toLowerCase() ?? 'pending',
      customer: (json['customer'] as Map<String, dynamic>?) ?? {},
      items: (json['items'] as List?)
              ?.whereType<Map<String, dynamic>>()
              .toList() ??
          [],
      total: (json['total'] as num?)?.toDouble() ?? 0.0,
      currency: json['currency']?.toString() ?? 'USD',
      orderDate: json['order_date'] != null
          ? DateTime.tryParse(json['order_date'].toString())
          : null,
      fulfilledDate: json['fulfilled_date'] != null
          ? DateTime.tryParse(json['fulfilled_date'].toString())
          : null,
    );
  }

  OrderModel copyWith({String? status}) {
    return OrderModel(
      id: id,
      projectId: projectId,
      externalId: externalId,
      provider: provider,
      status: status ?? this.status,
      customer: customer,
      items: items,
      total: total,
      currency: currency,
      orderDate: orderDate,
      fulfilledDate: fulfilledDate,
    );
  }

  String get customerName {
    final name = customer['name']?.toString();
    if (name != null && name.trim().isNotEmpty) return name.trim();
    return customer['phone']?.toString() ??
        customer['email']?.toString() ??
        'Customer';
  }
}
