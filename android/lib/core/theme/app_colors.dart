import 'package:flutter/material.dart';

/// Automind Design System Color Palette based on official visual identity.
class AppColors {
  AppColors._();

  // Brand Primaries (Sky Palette)
  static const Color brandPrimary = Color(0xFF0EA5E9); // Sky 500
  static const Color brandHover = Color(0xFF0284C7); // Sky 600
  static const Color brandLight = Color(0xFF38BDF8); // Sky 400
  static const Color brandGlow = Color(0x400EA5E9);

  // Backgrounds & Surfaces (Slate Palette)
  static const Color bgDark = Color(0xFF020617); // Slate 950
  static const Color surfaceDark = Color(0xFF0F172A); // Slate 900
  static const Color surfaceElevated = Color(0xFF1E293B); // Slate 800
  static const Color surfaceHighlight = Color(0xFF334155); // Slate 700

  // Glass Surfaces
  static const Color glassSurface = Color(0xBF0F172A); // 75% opacity
  static const Color glassSurfaceHover = Color(0xCC1E293B); // 80% opacity

  // Text Colors
  static const Color textPrimary = Color(0xFFF8FAFC); // Slate 50
  static const Color textSecondary = Color(0xFF94A3B8); // Slate 400
  static const Color textMuted = Color(0xFF64748B); // Slate 500
  static const Color textDisabled = Color(0xFF475569); // Slate 600

  // Semantic Status Colors
  static const Color success = Color(0xFF10B981); // Emerald 500
  static const Color successSurface = Color(0x2010B981);
  static const Color warning = Color(0xFFF59E0B); // Amber 500
  static const Color warningSurface = Color(0x20F59E0B);
  static const Color danger = Color(0xFFF43F5E); // Rose 500
  static const Color dangerSurface = Color(0x20F43F5E);
  static const Color info = Color(0xFF38BDF8); // Sky 400
  static const Color infoSurface = Color(0x2038BDF8);

  // Borders & Dividers
  static const Color border = Color(0x14FFFFFF); // 8% white
  static const Color borderStrong = Color(0x29FFFFFF); // 16% white
  static const Color borderBrand = Color(0x4D0EA5E9); // 30% brand

  // Gradients
  static const LinearGradient brandGradient = LinearGradient(
    colors: [Color(0xFF0EA5E9), Color(0xFF0284C7)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient cardGradient = LinearGradient(
    colors: [Color(0xBF0F172A), Color(0xBF020617)],
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
  );
}
