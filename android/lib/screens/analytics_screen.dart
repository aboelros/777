import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:provider/provider.dart';
import '../providers/analytics_provider.dart';
import '../providers/project_provider.dart';
import '../theme/app_theme.dart';
import '../widgets/shimmer_loader.dart';

class AnalyticsScreen extends StatefulWidget {
  const AnalyticsScreen({Key? key}) : super(key: key);

  @override
  _AnalyticsScreenState createState() => _AnalyticsScreenState();
}

class _AnalyticsScreenState extends State<AnalyticsScreen> {
  String _selectedPeriod = '7d';

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadData();
    });
  }

  Future<void> _loadData() async {
    final projectProvider = Provider.of<ProjectProvider>(context, listen: false);
    final projectId = projectProvider.activeProject?.id;
    if (projectId != null) {
      Provider.of<AnalyticsProvider>(context, listen: false).fetchAnalytics(projectId);
    }
  }

  @override
  Widget build(BuildContext context) {
    final provider = Provider.of<AnalyticsProvider>(context);
    final isLoading = provider.isLoading;
    final error = provider.error;
    final data = provider.data;

    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('Analytics'),
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),
      body: error != null
          ? Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.error_outline, color: AppTheme.error, size: 48),
                  const SizedBox(height: 16),
                  Text(error, style: const TextStyle(color: Colors.white70)),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: _loadData,
                    style: ElevatedButton.styleFrom(backgroundColor: AppTheme.primary),
                    child: const Text('Retry'),
                  ),
                ],
              ),
            )
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                // Period Toggle
                Container(
                  decoration: BoxDecoration(
                    color: AppTheme.surfaceDark,
                    borderRadius: BorderRadius.circular(24),
                  ),
                  child: Row(
                    children: [
                      _buildPeriodBtn('7 Days', '7d'),
                      _buildPeriodBtn('30 Days', '30d'),
                    ],
                  ),
                ).animate().fade().slideY(begin: -0.1),
                const SizedBox(height: 24),

                // Stats Row
                if (isLoading)
                  Row(
                    children: List.generate(
                      3,
                      (index) => Expanded(
                        child: Padding(
                          padding: EdgeInsets.only(left: index == 0 ? 0 : 8, right: index == 2 ? 0 : 8),
                          child: ShimmerLoader.card(height: 80),
                        ),
                      ),
                    ),
                  )
                else
                  Row(
                    children: [
                      Expanded(child: _buildStatCard('Total Revenue', data?['totalRevenue']?.toString() ?? '--', Icons.attach_money)),
                      const SizedBox(width: 8),
                      Expanded(child: _buildStatCard('Orders', data?['totalOrders']?.toString() ?? '--', Icons.shopping_bag)),
                      const SizedBox(width: 8),
                      Expanded(child: _buildStatCard('Avg Order Value', data?['avgOrderValue']?.toString() ?? '--', Icons.analytics)),
                    ],
                  ).animate().fade().slideY(begin: 0.1),
                const SizedBox(height: 24),

                // Revenue Chart
                if (isLoading)
                  ShimmerLoader.card(height: 220)
                else
                  Container(
                    height: 220,
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: AppTheme.surfaceDark,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: Colors.white.withOpacity(0.05)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('Revenue Overview', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                        const SizedBox(height: 16),
                        Expanded(child: _buildLineChart()),
                      ],
                    ),
                  ).animate().fade(delay: 100.ms).slideY(begin: 0.1),
                const SizedBox(height: 24),

                // Orders by Status
                if (isLoading)
                  ShimmerLoader.card(height: 220)
                else
                  Container(
                    height: 220,
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: AppTheme.surfaceDark,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: Colors.white.withOpacity(0.05)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('Orders by Status', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                        const SizedBox(height: 16),
                        Expanded(
                          child: Row(
                            children: [
                              Expanded(child: _buildPieChart()),
                              const SizedBox(width: 16),
                              Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  _buildLegend('Completed', Colors.green),
                                  _buildLegend('Pending', Colors.orange),
                                  _buildLegend('Cancelled', Colors.red),
                                  _buildLegend('Other', Colors.blue),
                                ],
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ).animate().fade(delay: 200.ms).slideY(begin: 0.1),
                const SizedBox(height: 24),

                // Top Customers
                const Text('Top Customers', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
                const SizedBox(height: 12),
                if (isLoading)
                  ShimmerLoader.list(count: 3)
                else
                  ...List.generate(3, (index) {
                    final isFirst = index == 0;
                    return Container(
                      margin: const EdgeInsets.only(bottom: 8),
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: AppTheme.surfaceDark,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: isFirst ? AppTheme.primary.withOpacity(0.3) : Colors.transparent),
                      ),
                      child: Row(
                        children: [
                          CircleAvatar(
                            backgroundColor: isFirst ? AppTheme.primary : Colors.white12,
                            radius: 16,
                            child: Text('${index + 1}', style: TextStyle(color: isFirst ? Colors.white : Colors.white70, fontSize: 12, fontWeight: FontWeight.bold)),
                          ),
                          const SizedBox(width: 12),
                          const Expanded(
                            child: Text('Customer Placeholder', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w500)),
                          ),
                          const Text('--', style: TextStyle(color: AppTheme.primary, fontWeight: FontWeight.bold)),
                        ],
                      ),
                    );
                  }).animate().fade(delay: 300.ms),
              ],
            ),
    );
  }

  Widget _buildPeriodBtn(String title, String value) {
    final isSelected = _selectedPeriod == value;
    return Expanded(
      child: GestureDetector(
        onTap: () {
          setState(() => _selectedPeriod = value);
          _loadData();
        },
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 12),
          decoration: BoxDecoration(
            color: isSelected ? AppTheme.primary : Colors.transparent,
            borderRadius: BorderRadius.circular(24),
          ),
          alignment: Alignment.center,
          child: Text(
            title,
            style: TextStyle(
              color: isSelected ? Colors.white : Colors.grey,
              fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppTheme.surfaceDark,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white.withOpacity(0.05)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: AppTheme.primary, size: 20),
          const SizedBox(height: 8),
          Text(value, style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold), overflow: TextOverflow.ellipsis),
          const SizedBox(height: 4),
          Text(title, style: const TextStyle(color: Colors.grey, fontSize: 10), overflow: TextOverflow.ellipsis),
        ],
      ),
    );
  }

  Widget _buildLineChart() {
    return LineChart(
      LineChartData(
        gridData: const FlGridData(show: false),
        titlesData: const FlTitlesData(show: false),
        borderData: FlBorderData(show: false),
        lineBarsData: [
          LineChartBarData(
            spots: const [
              FlSpot(0, 1),
              FlSpot(1, 1.5),
              FlSpot(2, 1.4),
              FlSpot(3, 3.4),
              FlSpot(4, 2),
              FlSpot(5, 2.2),
              FlSpot(6, 1.8),
            ],
            isCurved: true,
            color: AppTheme.primary,
            barWidth: 3,
            isStrokeCapRound: true,
            dotData: const FlDotData(show: false),
            belowBarData: BarAreaData(
              show: true,
              gradient: LinearGradient(
                colors: [AppTheme.primary.withOpacity(0.3), Colors.transparent],
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPieChart() {
    return PieChart(
      PieChartData(
        sectionsSpace: 2,
        centerSpaceRadius: 30,
        sections: [
          PieChartSectionData(value: 40, color: Colors.green, showTitle: false, radius: 15),
          PieChartSectionData(value: 30, color: Colors.orange, showTitle: false, radius: 15),
          PieChartSectionData(value: 15, color: Colors.red, showTitle: false, radius: 15),
          PieChartSectionData(value: 15, color: Colors.blue, showTitle: false, radius: 15),
        ],
      ),
    );
  }

  Widget _buildLegend(String label, Color color) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Row(
        children: [
          Container(width: 10, height: 10, decoration: BoxDecoration(color: color, shape: BoxShape.circle)),
          const SizedBox(width: 8),
          Text(label, style: const TextStyle(color: Colors.white70, fontSize: 12)),
        ],
      ),
    );
  }
}
