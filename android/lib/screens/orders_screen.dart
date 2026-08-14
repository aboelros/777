import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:shimmer/shimmer.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../providers/order_provider.dart';
import '../providers/project_provider.dart';

class OrdersScreen extends StatefulWidget {
  const OrdersScreen({super.key});

  @override
  State<OrdersScreen> createState() => _OrdersScreenState();
}

class _OrdersScreenState extends State<OrdersScreen> {
  String _searchQuery = '';
  String _selectedStatus = 'All';
  bool _isLoadingMore = false;
  final List<String> _statuses = ['All', 'Pending', 'Processing', 'Completed', 'Cancelled'];
  final ScrollController _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _fetchOrders();
    });
  }

  Future<void> _fetchOrders() async {
    final projectId = Provider.of<ProjectProvider>(context, listen: false).currentProjectId;
    if (projectId != null) {
      await Provider.of<OrderProvider>(context, listen: false).fetchOrders(projectId);
    }
  }

  Future<void> _loadMore() async {
    if (_isLoadingMore) return;
    final orderProvider = Provider.of<OrderProvider>(context, listen: false);
    final projectId = Provider.of<ProjectProvider>(context, listen: false).currentProjectId;
    if (projectId != null && orderProvider.hasMore && !orderProvider.isLoading) {
      setState(() => _isLoadingMore = true);
      await orderProvider.fetchMoreOrders(projectId);
      if (mounted) setState(() => _isLoadingMore = false);
    }
  }

  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'completed':
        return Colors.green;
      case 'pending':
        return Colors.orange;
      case 'processing':
        return Colors.blue;
      case 'cancelled':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  void _showOrderDetails(BuildContext context, dynamic order) {
    showModalBottomSheet(
      context: context,
      backgroundColor: const Color(0xFF1E293B),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      isScrollControlled: true,
      builder: (context) {
        return Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: Colors.grey[700],
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              const SizedBox(height: 24),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Order #${order['id']?.toString().substring(0, 8) ?? 'Unknown'}',
                    style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.white),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close, color: Colors.grey),
                    onPressed: () => Navigator.pop(context),
                  )
                ],
              ),
              const SizedBox(height: 16),
              _detailRow('Customer', order['customerName'] ?? 'Unknown'),
              _detailRow('Email', order['customerEmail'] ?? 'N/A'),
              _detailRow('Status', order['status'] ?? 'Unknown', color: _getStatusColor(order['status'] ?? '')),
              _detailRow('Amount', '\$${order['amount']?.toString() ?? '0.00'}'),
              _detailRow('Date', order['createdAt'] != null ? DateTime.parse(order['createdAt']).toString().substring(0, 16) : 'Unknown'),
              const SizedBox(height: 32),
            ],
          ),
        );
      },
    );
  }

  Widget _detailRow(String label, String value, {Color? color}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Colors.grey, fontSize: 16)),
          Text(
            value,
            style: TextStyle(color: color ?? Colors.white, fontSize: 16, fontWeight: FontWeight.w500),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        title: const Text('Orders'),
        backgroundColor: const Color(0xFF1E293B),
      ),
      body: Consumer<OrderProvider>(
        builder: (context, orderProvider, child) {
          List<dynamic> filteredOrders = orderProvider.orders.where((order) {
            final matchesStatus = _selectedStatus == 'All' || order['status']?.toString().toLowerCase() == _selectedStatus.toLowerCase();
            final matchesSearch = _searchQuery.isEmpty || 
                                  (order['customerName']?.toString().toLowerCase().contains(_searchQuery.toLowerCase()) ?? false);
            return matchesStatus && matchesSearch;
          }).toList();

          return Column(
            children: [
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: TextField(
                  style: const TextStyle(color: Colors.white),
                  decoration: InputDecoration(
                    hintText: 'Search by customer name...',
                    hintStyle: const TextStyle(color: Colors.grey),
                    prefixIcon: const Icon(Icons.search, color: Colors.grey),
                    filled: true,
                    fillColor: const Color(0xFF1E293B),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide.none,
                    ),
                  ),
                  onChanged: (value) => setState(() => _searchQuery = value),
                ),
              ),
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                padding: const EdgeInsets.symmetric(horizontal: 16.0),
                child: Row(
                  children: _statuses.map((status) {
                    final isSelected = _selectedStatus == status;
                    return Padding(
                      padding: const EdgeInsets.only(right: 8.0),
                      child: ChoiceChip(
                        label: Text(status),
                        selected: isSelected,
                        onSelected: (selected) {
                          if (selected) setState(() => _selectedStatus = status);
                        },
                        selectedColor: const Color(0xFF6366F1),
                        backgroundColor: const Color(0xFF1E293B),
                        labelStyle: TextStyle(color: isSelected ? Colors.white : Colors.grey),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                      ),
                    );
                  }).toList(),
                ),
              ),
              const SizedBox(height: 8),
              Expanded(
                child: RefreshIndicator(
                  onRefresh: _fetchOrders,
                  color: const Color(0xFF6366F1),
                  child: NotificationListener<ScrollNotification>(
                    onNotification: (ScrollNotification scrollInfo) {
                      if (scrollInfo.metrics.pixels >= scrollInfo.metrics.maxScrollExtent - 100) {
                        _loadMore();
                      }
                      return true;
                    },
                    child: _buildBody(orderProvider, filteredOrders),
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }

  Widget _buildBody(OrderProvider orderProvider, List<dynamic> filteredOrders) {
    if (orderProvider.isLoading && orderProvider.orders.isEmpty) {
      return ListView.builder(
        itemCount: 5,
        padding: const EdgeInsets.all(16),
        itemBuilder: (context, index) {
          return Shimmer.fromColors(
            baseColor: const Color(0xFF1E293B),
            highlightColor: const Color(0xFF334155),
            child: Container(
              margin: const EdgeInsets.only(bottom: 12),
              height: 100,
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
              ),
            ),
          );
        },
      );
    }

    if (orderProvider.error != null && orderProvider.orders.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, color: Colors.red, size: 48),
            const SizedBox(height: 16),
            Text(orderProvider.error!, style: const TextStyle(color: Colors.red)),
            ElevatedButton(
              onPressed: _fetchOrders,
              child: const Text('Retry'),
            ),
          ],
        ),
      );
    }

    if (filteredOrders.isEmpty) {
      return const Center(
        child: Text('No orders found.', style: TextStyle(color: Colors.grey, fontSize: 16)),
      );
    }

    return ListView.builder(
      controller: _scrollController,
      padding: const EdgeInsets.all(16),
      itemCount: filteredOrders.length + (_isLoadingMore ? 1 : 0),
      itemBuilder: (context, index) {
        if (index == filteredOrders.length) {
          return const Center(
            child: Padding(
              padding: EdgeInsets.all(16.0),
              child: CircularProgressIndicator(color: Color(0xFF6366F1)),
            ),
          );
        }

        final order = filteredOrders[index];
        final status = order['status'] ?? 'Unknown';
        
        return InkWell(
          onTap: () => _showOrderDetails(context, order),
          child: Card(
            color: const Color(0xFF1E293B),
            margin: const EdgeInsets.only(bottom: 12),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          order['customerName'] ?? 'Unknown',
                          style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(height: 4),
                        Text(
                          order['createdAt'] != null ? DateTime.parse(order['createdAt']).toString().substring(0, 10) : '',
                          style: const TextStyle(color: Colors.grey, fontSize: 14),
                        ),
                      ],
                    ),
                  ),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Text(
                        '\$${order['amount']?.toString() ?? '0.00'}',
                        style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 8),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: _getStatusColor(status).withOpacity(0.2),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          status,
                          style: TextStyle(color: _getStatusColor(status), fontSize: 12, fontWeight: FontWeight.bold),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ).animate().fadeIn(duration: 200.ms),
        );
      },
    );
  }
}
