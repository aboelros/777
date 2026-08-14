class Order {
  final String id;
  final String customerName;
  final String? customerEmail;
  final String status;
  final double totalAmount;
  final String? currency;
  final String? paymentStatus;
  final DateTime createdAt;

  Order({
    required this.id,
    required this.customerName,
    this.customerEmail,
    required this.status,
    required this.totalAmount,
    this.currency,
    this.paymentStatus,
    required this.createdAt,
  });

  factory Order.fromJson(Map<String, dynamic> json) {
    return Order(
      id: json['id'],
      customerName: json['customer_name'] ?? 'Unknown Customer',
      customerEmail: json['customer_email'],
      status: json['status'] ?? 'pending',
      totalAmount: json['total_amount'] != null ? (json['total_amount'] as num).toDouble() : 0.0,
      currency: json['currency'] ?? 'USD',
      paymentStatus: json['payment_status'] ?? 'pending',
      createdAt: json['created_at'] != null ? DateTime.parse(json['created_at']) : DateTime.now(),
    );
  }
}
