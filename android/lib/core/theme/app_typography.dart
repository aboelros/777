import 'package:flutter/material.dart';
import 'app_colors.dart';

/// Automind standard typography scale supporting Latin and Arabic scripts.
class AppTypography {
  AppTypography._();

  static const List<String> fontFamilyFallback = [
    'Inter',
    'Noto Sans Arabic',
    'Roboto',
    'sans-serif',
  ];

  static const TextStyle pageTitle = TextStyle(
    fontSize: 24,
    fontWeight: FontWeight.w700,
    color: AppColors.textPrimary,
    letterSpacing: -0.5,
    fontFamilyFallback: fontFamilyFallback,
  );

  static const TextStyle sectionTitle = TextStyle(
    fontSize: 18,
    fontWeight: FontWeight.w600,
    color: AppColors.textPrimary,
    letterSpacing: -0.2,
    fontFamilyFallback: fontFamilyFallback,
  );

  static const TextStyle cardTitle = TextStyle(
    fontSize: 15,
    fontWeight: FontWeight.w600,
    color: AppColors.textPrimary,
    fontFamilyFallback: fontFamilyFallback,
  );

  static const TextStyle body = TextStyle(
    fontSize: 14,
    fontWeight: FontWeight.w400,
    color: AppColors.textPrimary,
    height: 1.45,
    fontFamilyFallback: fontFamilyFallback,
  );

  static const TextStyle bodySecondary = TextStyle(
    fontSize: 13,
    fontWeight: FontWeight.w400,
    color: AppColors.textSecondary,
    height: 1.4,
    fontFamilyFallback: fontFamilyFallback,
  );

  static const TextStyle caption = TextStyle(
    fontSize: 11,
    fontWeight: FontWeight.w500,
    color: AppColors.textMuted,
    letterSpacing: 0.2,
    fontFamilyFallback: fontFamilyFallback,
  );

  static const TextStyle button = TextStyle(
    fontSize: 14,
    fontWeight: FontWeight.w600,
    color: Colors.white,
    letterSpacing: 0.1,
    fontFamilyFallback: fontFamilyFallback,
  );

  static const TextStyle numericLarge = TextStyle(
    fontSize: 24,
    fontWeight: FontWeight.w700,
    color: AppColors.textPrimary,
    fontFeatures: [FontFeature.tabularFigures()],
    fontFamilyFallback: fontFamilyFallback,
  );

  static const TextStyle numericMedium = TextStyle(
    fontSize: 16,
    fontWeight: FontWeight.w600,
    color: AppColors.textPrimary,
    fontFeatures: [FontFeature.tabularFigures()],
    fontFamilyFallback: fontFamilyFallback,
  );
}
