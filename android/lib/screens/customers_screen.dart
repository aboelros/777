import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../providers/order_provider.dart';
import '../providers/project_provider.dart';
import '../theme/app_theme.dart';
import '../widgets/shimmer_loader.dart';

class CustomerData {
  final String email;
  final String name;
  final int orderCount;
  final double totalSpend;
  final List<dynamic> orders;

  CustomerData({
    required this.email,
    required this.name,
    required this.orderCount,
    required this.totalSpend,
    required this.orders,
  });
}

class CustomersScreen extends StatefulWidget {
  const CustomersScreen({Key? key}) : super(key: key);

  @override
  _CustomersScreenState createState() => _CustomersScreenState();
}

class _CustomersScreenState extends State<CustomersScreen> {
  String _searchQuery = '';

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadOrders();
    });
  }

  Future<void> _loadOrders() async {
    final projectProvider = Provider.of<ProjectProvider>(context, listen: false);
    final projectId = projectProvider.activeProject?.id;
    if (projectId != null) {
      Provider.of<OrderProvider>(context, listen: false).fetchOrders(projectId);
    }
  }

  List<CustomerData> _getCustomers(OrderProvider provider) {
    if (provider.orders.isEmpty) return [];
    
    final Map<String, List<dynamic>> customerOrders = {};
    for (var order in provider.orders) {
      final email = order['customerEmail'] ?? order['customerName'] ?? 'unknown@example.com';
      customerOrders.putIfAbsent(email, () => []).add(order);
    }

    final List<CustomerData> customers = customerOrders.entries.map((e) {
      final email = e.key;
      final orders = e.value;
      final name = orders.first['customerName'] ?? email.split('@').first;
      
      double totalSpend = 0;
      for (var o in orders) {
        totalSpend += (o['totalAmount'] ?? 0).toDouble();
      }
      
      return CustomerData(
        email: email,
        name: name,
        orderCount: orders.length,
        totalSpend: totalSpend,
        orders: orders,
      );
    }).toList();

    customers.sort((a, b) => b.totalSpend.compareTo(a.totalSpend));

    if (_searchQuery.isNotEmpty) {
      final q = _searchQuery.toLowerCase();
      return customers.where((c) => c.name.toLowerCase().contains(q) || c.email.toLowerCase().contains(q)).toList();
    }
    
    return customers;
  }

  void _showCustomerDetails(CustomerData customer) {
    showModalBottomSheet(
      context: context,
      backgroundColor: AppTheme.surfaceDark,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (context) {
        return DraggableScrollableSheet(
          initialChildSize: 0.6,
          minChildSize: 0.4,
          maxChildSize: 0.9,
          expand: false,
          builder: (context, scrollController) {
            return ListView(
              controller: scrollController,
              padding: const EdgeInsets.all(20),
              children: [
                Center(
                  child: Container(width: 40, height: 4, decoration: BoxDecoration(color: Colors.white24, borderRadius: BorderRadius.circular(2))),
                ),
                const SizedBox(height: 20),
                Row(
                  children: [
                    CircleAvatar(
                      radius: 30,
                      backgroundColor: AppTheme.primary.withOpacity(0.2),
                      child: Text(customer.name.isNotEmpty ? customer.name[0].toUpperCase() : '?', style: const TextStyle(color: AppTheme.primary, fontSize: 24, fontWeight: FontWeight.bold)),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(customer.name, style: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold)),
                          Text(customer.email, style: const TextStyle(color: Colors.grey, fontSize: 14)),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 24),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _buildStatBox('Total Orders', '${customer.orderCount}'),
                    _buildStatBox('Total Spend', '\$${customer.totalSpend.toStringAsFixed(2)}'),
                  ],
                ),
                const SizedBox(height: 24),
                const Text('Order History', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
                const SizedBox(height: 12),
                ...customer.orders.map((o) => ListTile(
                  contentPadding: EdgeInsets.zero,
                  leading: const Icon(Icons.receipt, color: Colors.grey),
                  title: Text('Order #${o['id']?.toString().substring(0, 8) ?? 'Unknown'}', style: const TextStyle(color: Colors.white)),
                  subtitle: Text(o['status'] ?? 'Unknown', style: const TextStyle(color: Colors.grey)),
                  trailing: Text('\$${o['totalAmount']}', style: const TextStyle(color: AppTheme.primary, fontWeight: FontWeight.bold)),
                )).toList(),
              ],
            );
          },
        );
      },
    );
  }

  Widget _buildStatBox(String label, String value) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
      decoration: BoxDecoration(color: Colors.white.withOpacity(0.05), borderRadius: BorderRadius.circular(12)),
      child: Column(
        children: [
          Text(value, style: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold)),
          const SizedBox(height: 4),
          Text(label, style: const TextStyle(color: Colors.grey, fontSize: 12)),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final orderProvider = Provider.of<OrderProvider>(context);
    final customers = _getCustomers(orderProvider);

    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('Customers'),
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: TextField(
              style: const TextStyle(color: Colors.white),
              onChanged: (val) => setState(() => _searchQuery = val),
              decoration: InputDecoration(
                hintText: 'Search customers...',
                hintStyle: const TextStyle(color: Colors.grey),
                prefixIcon: const Icon(Icons.search, color: Colors.grey),
                filled: true,
                fillColor: AppTheme.surfaceDark,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide.none,
                ),
              ),
            ),
          ),
          Expanded(
            child: orderProvider.isLoading
                ? ShimmerLoader.list(count: 6)
                : orderProvider.error != null
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Icon(Icons.error_outline, color: AppTheme.error, size: 48),
                            const SizedBox(height: 16),
                            Text(orderProvider.error!, style: const TextStyle(color: Colors.white70)),
                            const SizedBox(height: 16),
                            ElevatedButton(
                              onPressed: _loadOrders,
                              style: ElevatedButton.styleFrom(backgroundColor: AppTheme.primary),
                              child: const Text('Retry'),
                            ),
                          ],
                        ),
                      )
                    : customers.isEmpty
                        ? const Center(
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Icon(Icons.people_outline, color: Colors.grey, size: 64),
                                SizedBox(height: 16),
                                Text('No customers found', style: TextStyle(color: Colors.grey, fontSize: 18)),
                              ],
                            ),
                          )
                        : ListView.builder(
                            itemCount: customers.length,
                            padding: const EdgeInsets.symmetric(horizontal: 16),
                            itemBuilder: (context, index) {
                              final customer = customers[index];
                              return Card(
                                color: AppTheme.surfaceDark,
                                margin: const EdgeInsets.only(bottom: 8),
                                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                                child: ListTile(
                                  onTap: () => _showCustomerDetails(customer),
                                  leading: CircleAvatar(
                                    backgroundColor: AppTheme.primary,
                                    child: Text(
                                      customer.name.isNotEmpty ? customer.name[0].toUpperCase() : '?',
                                      style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                                    ),
                                  ),
                                  title: Text(customer.name, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                                  subtitle: Text(customer.email, style: const TextStyle(color: Colors.grey, fontSize: 12)),
                                  trailing: Column(
                                    mainAxisAlignment: MainAxisAlignment.center,
                                    crossAxisAlignment: CrossAxisAlignment.end,
                                    children: [
                                      Text('\$${customer.totalSpend.toStringAsFixed(2)}', style: const TextStyle(color: AppTheme.primary, fontWeight: FontWeight.bold)),
                                      Text('${customer.orderCount} orders', style: const TextStyle(color: Colors.grey, fontSize: 12)),
                                    ],
                                  ),
                                ),
                              ).animate().fade(delay: (50 * index).ms).slideX(begin: 0.1);
                            },
                          ),
          ),
        ],
      ),
    );
  }
}
