import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/network/api_endpoints.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_typography.dart';
import '../../../shared/widgets/glass_card.dart';
import '../../../shared/widgets/skeleton_loader.dart';
import '../../../shared/widgets/status_badge.dart';
import '../../auth/providers/auth_provider.dart';
import '../../projects/providers/project_provider.dart';
import '../models/customer_profile_model.dart';

/// Bottom sheet displaying customer details, channel identity, and VIP status.
class CustomerProfileSheet extends ConsumerStatefulWidget {
  final String profileId;

  const CustomerProfileSheet({super.key, required this.profileId});

  static void show(BuildContext context, String profileId) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      isScrollControlled: true,
      builder: (_) => CustomerProfileSheet(profileId: profileId),
    );
  }

  @override
  ConsumerState<CustomerProfileSheet> createState() =>
      _CustomerProfileSheetState();
}

class _CustomerProfileSheetState extends ConsumerState<CustomerProfileSheet> {
  CustomerProfileModel? _profile;
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _fetchProfile();
  }

  Future<void> _fetchProfile() async {
    final activeProject = ref.read(activeProjectProvider);
    if (activeProject == null) return;

    final api = ref.read(apiClientProvider);
    try {
      final endpoint = ApiEndpoints.customerProfile(
        activeProject.id,
        widget.profileId,
      );
      final data = await api.get(endpoint);
      if (data is Map<String, dynamic> && mounted) {
        setState(() {
          _profile = CustomerProfileModel.fromJson(data);
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = 'Failed to load customer profile.';
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(
        color: AppColors.surfaceDark,
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        border: Border(top: BorderSide(color: AppColors.borderStrong)),
      ),
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      child: SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(
              child: Container(
                width: 36,
                height: 4,
                decoration: BoxDecoration(
                  color: AppColors.textDisabled,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            const SizedBox(height: 16),
            Text('Customer Profile', style: AppTypography.sectionTitle),
            const SizedBox(height: 16),
            if (_isLoading)
              const Column(
                children: [
                  SkeletonLoader(width: double.infinity, height: 60),
                  SizedBox(height: 12),
                  SkeletonLoader(width: double.infinity, height: 100),
                ],
              )
            else if (_error != null)
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: Text(_error!,
                    style: const TextStyle(color: AppColors.danger)),
              )
            else if (_profile != null)
              _buildProfileContent(_profile!),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }

  Widget _buildProfileContent(CustomerProfileModel p) {
    return Column(
      children: [
        GlassCard(
          padding: const EdgeInsets.all(14),
          child: Row(
            children: [
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: AppColors.surfaceElevated,
                  shape: BoxShape.circle,
                  border: Border.all(color: AppColors.border),
                ),
                child: Center(
                  child: Text(
                    p.displayName.isNotEmpty
                        ? p.displayName[0].toUpperCase()
                        : '?',
                    style: AppTypography.sectionTitle
                        .copyWith(color: AppColors.brandPrimary),
                  ),
                ),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(p.displayName, style: AppTypography.cardTitle),
                    if (p.phone != null) ...[
                      const SizedBox(height: 2),
                      Text(p.phone!, style: AppTypography.caption),
                    ],
                    if (p.email != null) ...[
                      const SizedBox(height: 2),
                      Text(p.email!, style: AppTypography.caption),
                    ],
                  ],
                ),
              ),
              if (p.isVip)
                const StatusBadge(
                  label: 'VIP',
                  variant: BadgeVariant.warning,
                ),
            ],
          ),
        ),
        const SizedBox(height: 12),
        GlassCard(
          padding: const EdgeInsets.all(14),
          child: Column(
            children: [
              _infoRow(
                  'Channel Platform', p.provider?.toUpperCase() ?? 'DIRECT'),
              const Divider(color: AppColors.border, height: 16),
              _infoRow('AI Automation', p.aiEnabled ? 'Enabled' : 'Paused'),
              if (p.sentiment != null) ...[
                const Divider(color: AppColors.border, height: 16),
                _infoRow('Sentiment', p.sentiment!),
              ],
            ],
          ),
        ),
      ],
    );
  }

  Widget _infoRow(String label, String value) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: AppTypography.bodySecondary),
        Text(value, style: AppTypography.cardTitle),
      ],
    );
  }
}
