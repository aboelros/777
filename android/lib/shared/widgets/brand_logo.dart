import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import '../../core/theme/app_colors.dart';
import '../../core/theme/app_typography.dart';

enum BrandLogoVariant { full, compact, symbol }

/// Official Automind Master Brand Logo with Typographic Gradient Lockup
/// and live status telemetry indicator.
class BrandLogo extends StatelessWidget {
  final BrandLogoVariant variant;
  final double size;
  final String? subtitle;
  final bool showStatusDot;

  const BrandLogo({
    super.key,
    this.variant = BrandLogoVariant.full,
    this.size = 36,
    this.subtitle,
    this.showStatusDot = true,
  });

  @override
  Widget build(BuildContext context) {
    if (variant == BrandLogoVariant.symbol) {
      return _buildSymbol();
    }

    return Directionality(
      textDirection: TextDirection.ltr,
      child: Row(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          _buildSymbol(),
          const SizedBox(width: 12),
          Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildWordmark(),
              if (variant == BrandLogoVariant.full) ...[
                const SizedBox(height: 3),
                _buildSubtitleRow(),
              ],
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSymbol() {
    return Container(
      width: size,
      height: size,
      padding: EdgeInsets.all(size * 0.16),
      decoration: BoxDecoration(
        color: AppColors.surfaceElevated,
        borderRadius: BorderRadius.circular(size * 0.3),
        border: Border.all(color: AppColors.borderStrong),
        boxShadow: const [
          BoxShadow(
            color: AppColors.brandGlow,
            blurRadius: 16,
            offset: Offset(0, 4),
          ),
        ],
      ),
      child: SvgPicture.asset(
        'assets/icons/automind-symbol.svg',
        placeholderBuilder: (_) => Icon(
          Icons.auto_awesome_rounded,
          color: AppColors.brandPrimary,
          size: size * 0.6,
        ),
      ),
    );
  }

  Widget _buildWordmark() {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          'AUTO',
          style: AppTypography.cardTitle.copyWith(
            letterSpacing: 1.2,
            fontWeight: FontWeight.w800,
            fontSize: size * 0.52,
            color: Colors.white,
          ),
        ),
        ShaderMask(
          shaderCallback: (bounds) => const LinearGradient(
            colors: [Color(0xFF38BDF8), Color(0xFF60A5FA)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ).createShader(bounds),
          child: Text(
            'MIND',
            style: AppTypography.cardTitle.copyWith(
              letterSpacing: 1.2,
              fontWeight: FontWeight.w800,
              fontSize: size * 0.52,
              color: Colors.white,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildSubtitleRow() {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          (subtitle ?? 'AI SALES PLATFORM').toUpperCase(),
          style: AppTypography.caption.copyWith(
            fontSize: 9,
            fontWeight: FontWeight.w700,
            letterSpacing: 1.6,
            color: AppColors.textMuted,
          ),
        ),
        if (showStatusDot) ...[
          const SizedBox(width: 6),
          Container(
            width: 6,
            height: 6,
            decoration: const BoxDecoration(
              color: AppColors.success,
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(
                  color: AppColors.success,
                  blurRadius: 6,
                  spreadRadius: 1,
                ),
              ],
            ),
          ),
        ],
      ],
    );
  }
}
