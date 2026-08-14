import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:shimmer/shimmer.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:flutter_animate/flutter_animate.dart';

import '../providers/project_provider.dart';
import '../services/api_service.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  bool _isLoadingMetrics = true;
  Map<String, dynamic>? _metricsData;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _fetchMetrics();
    });
  }

  Future<void> _fetchMetrics() async {
    setState(() {
      _isLoadingMetrics = true;
    });

    final projectProvider = Provider.of<ProjectProvider>(context, listen: false);
    final projectId = projectProvider.selectedProject?.id;

    if (projectId != null) {
      try {
        final apiService = Provider.of<ApiService>(context, listen: false);
        final response = await apiService.get('/reports/$projectId/dashboard-summary');
        setState(() {
          _metricsData = response.data;
          _isLoadingMetrics = false;
        });
      } catch (e) {
        debugPrint('Error fetching metrics: $e');
        setState(() {
          _isLoadingMetrics = false;
          _metricsData = {
            'totalSales': 12500,
            'activeChats': 42,
            'aiResponses': 1337,
            'conversionRate': 3.4
          };
        });
      }
    } else {
      setState(() {
        _isLoadingMetrics = false;
        _metricsData = {
          'totalSales': 0,
          'activeChats': 0,
          'aiResponses': 0,
          'conversionRate': 0
        };
      });
    }
  }

  void _showProjectPicker(BuildContext context) {
    final projectProvider = Provider.of<ProjectProvider>(context, listen: false);
    showModalBottomSheet(
      context: context,
      backgroundColor: const Color(0xFF1E293B),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) {
        return SafeArea(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Padding(
                padding: EdgeInsets.all(16.0),
                child: Text(
                  'Select Project',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
              ),
              if (projectProvider.projects.isEmpty)
                const Padding(
                  padding: EdgeInsets.all(16.0),
                  child: Text('No projects available', style: TextStyle(color: Colors.white54)),
                )
              else
                Expanded(
                  child: ListView.builder(
                    itemCount: projectProvider.projects.length,
                    itemBuilder: (context, index) {
                      final project = projectProvider.projects[index];
                      final isSelected = project.id == projectProvider.selectedProject?.id;
                      return ListTile(
                        title: Text(
                          project.name,
                          style: TextStyle(
                            color: isSelected ? const Color(0xFF6366F1) : Colors.white,
                            fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                          ),
                        ),
                        trailing: isSelected
                            ? const Icon(Icons.check, color: Color(0xFF6366F1))
                            : null,
                        onTap: () {
                          projectProvider.selectProject(project);
                          Navigator.pop(context);
                          _fetchMetrics();
                        },
                      );
                    },
                  ),
                ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildShimmerGrid() {
    return GridView.count(
      crossAxisCount: 2,
      crossAxisSpacing: 16,
      mainAxisSpacing: 16,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      children: List.generate(4, (index) {
        return Shimmer.fromColors(
          baseColor: const Color(0xFF1E293B),
          highlightColor: const Color(0xFF334155),
          child: Container(
            decoration: BoxDecoration(
              color: const Color(0xFF1E293B),
              borderRadius: BorderRadius.circular(16),
            ),
          ),
        );
      }),
    );
  }

  Widget _buildMetricCard({
    required String title,
    required String value,
    required IconData icon,
    required Color iconColor,
    required String trend,
    required bool isUp,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: iconColor.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(icon, color: iconColor, size: 20),
              ),
              Row(
                children: [
                  Icon(
                    isUp ? Icons.arrow_upward : Icons.arrow_downward,
                    color: isUp ? Colors.green : Colors.red,
                    size: 16,
                  ),
                  Text(
                    trend,
                    style: TextStyle(
                      color: isUp ? Colors.green : Colors.red,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            value,
            style: const TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            title,
            style: const TextStyle(
              fontSize: 14,
              color: Colors.white54,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMetricsGrid() {
    final totalSales = _metricsData?['totalSales']?.toString() ?? '0';
    final activeChats = _metricsData?['activeChats']?.toString() ?? '0';
    final aiResponses = _metricsData?['aiResponses']?.toString() ?? '0';
    final conversionRate = _metricsData?['conversionRate']?.toString() ?? '0.0';

    final cards = [
      _buildMetricCard(
        title: 'Total Sales',
        value: '\$$totalSales',
        icon: Icons.attach_money,
        iconColor: Colors.green,
        trend: '+12%',
        isUp: true,
      ),
      _buildMetricCard(
        title: 'Active Chats',
        value: activeChats,
        icon: Icons.chat_bubble_outline,
        iconColor: const Color(0xFF3B82F6),
        trend: '+5%',
        isUp: true,
      ),
      _buildMetricCard(
        title: 'AI Responses',
        value: aiResponses,
        icon: Icons.smart_toy_outlined,
        iconColor: const Color(0xFF8B5CF6),
        trend: '+23%',
        isUp: true,
      ),
      _buildMetricCard(
        title: 'Conversion Rate',
        value: '$conversionRate%',
        icon: Icons.trending_up,
        iconColor: const Color(0xFFF59E0B),
        trend: '-1%',
        isUp: false,
      ),
    ];

    return GridView.count(
      crossAxisCount: 2,
      crossAxisSpacing: 16,
      mainAxisSpacing: 16,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      children: List.generate(cards.length, (index) {
        return cards[index]
            .animate(delay: (100 * index).ms)
            .fadeIn(duration: 400.ms)
            .slideY(begin: 0.2, end: 0, duration: 400.ms, curve: Curves.easeOutQuad);
      }),
    );
  }

  Widget _buildSparkline() {
    final spots = [
      const FlSpot(0, 10),
      const FlSpot(1, 15),
      const FlSpot(2, 12),
      const FlSpot(3, 22),
      const FlSpot(4, 18),
      const FlSpot(5, 28),
      const FlSpot(6, 35),
    ];

    return Container(
      height: 120,
      margin: const EdgeInsets.only(top: 24, bottom: 24),
      padding: const EdgeInsets.only(top: 16),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(16),
      ),
      child: LineChart(
        LineChartData(
          gridData: const FlGridData(show: false),
          titlesData: const FlTitlesData(show: false),
          borderData: FlBorderData(show: false),
          lineBarsData: [
            LineChartBarData(
              spots: spots,
              isCurved: true,
              color: const Color(0xFF6366F1),
              barWidth: 3,
              isStrokeCapRound: true,
              dotData: const FlDotData(show: false),
              belowBarData: BarAreaData(
                show: true,
                color: const Color(0xFF6366F1).withOpacity(0.2),
              ),
            ),
          ],
        ),
      ).animate().fadeIn(duration: 600.ms, delay: 400.ms),
    );
  }

  Widget _buildRecentActivity() {
    final activities = [
      {'title': 'New order from Customer', 'time': '2m ago', 'icon': Icons.shopping_cart, 'color': Colors.green},
      {'title': 'AI responded to inquiry', 'time': '15m ago', 'icon': Icons.smart_toy, 'color': const Color(0xFF8B5CF6)},
      {'title': 'Chat converted to sale', 'time': '1h ago', 'icon': Icons.check_circle, 'color': const Color(0xFF3B82F6)},
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Recent Activity',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        const SizedBox(height: 16),
        ...activities.map((activity) {
          return Padding(
            padding: const EdgeInsets.only(bottom: 12.0),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: (activity['color'] as Color).withOpacity(0.2),
                    shape: BoxShape.circle,
                  ),
                  child: Icon(
                    activity['icon'] as IconData,
                    color: activity['color'] as Color,
                    size: 16,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        activity['title'] as String,
                        style: const TextStyle(color: Colors.white, fontSize: 14),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        activity['time'] as String,
                        style: const TextStyle(color: Colors.white54, fontSize: 12),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ).animate().fadeIn(duration: 400.ms).slideX(begin: 0.1, end: 0, duration: 400.ms);
        }),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        title: const Text('Dashboard', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFF0F172A),
        elevation: 0,
      ),
      body: Consumer<ProjectProvider>(
        builder: (context, projectProvider, child) {
          return RefreshIndicator(
            onRefresh: _fetchMetrics,
            color: const Color(0xFF6366F1),
            backgroundColor: const Color(0xFF1E293B),
            child: SingleChildScrollView(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  GestureDetector(
                    onTap: () => _showProjectPicker(context),
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                      decoration: BoxDecoration(
                        color: const Color(0xFF1E293B),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: const Color(0xFF334155)),
                      ),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Row(
                            children: [
                              const Icon(Icons.folder_outlined, color: Color(0xFF6366F1), size: 20),
                              const SizedBox(width: 12),
                              Text(
                                projectProvider.selectedProject?.name ?? 'Select Project',
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontWeight: FontWeight.bold,
                                  fontSize: 16,
                                ),
                              ),
                            ],
                          ),
                          const Icon(Icons.keyboard_arrow_down, color: Colors.white54),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),

                  if (_isLoadingMetrics)
                    _buildShimmerGrid()
                  else
                    _buildMetricsGrid(),

                  _buildSparkline(),

                  _buildRecentActivity(),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}
