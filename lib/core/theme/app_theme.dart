// lib/core/theme/app_theme.dart
import 'package:flutter/material.dart';

class AppTheme {
  static const Color _green      = Color(0xFF1D9E75);
  static const Color _greenLight = Color(0xFFE1F5EE);
  static const Color _greenDark  = Color(0xFF085041);
  static const Color _amber      = Color(0xFFBA7517);
  static const Color _red        = Color(0xFFE24B4A);
  static const Color _blue       = Color(0xFF378ADD);

  // ── THÈME CLAIR ──────────────────────────────────────────

  static ThemeData get light => ThemeData(
    useMaterial3:   true,
    brightness:     Brightness.light,
    colorScheme:    ColorScheme.fromSeed(
      seedColor:  _green,
      brightness: Brightness.light,
      primary:    _green,
      secondary:  _amber,
      error:      _red,
    ),
    fontFamily: 'Cairo',

    // AppBar
    appBarTheme: const AppBarTheme(
      backgroundColor: _green,
      foregroundColor: Colors.white,
      elevation:       0,
      centerTitle:     true,
      titleTextStyle:  TextStyle(
        fontFamily: 'Cairo',
        fontSize:   18,
        fontWeight: FontWeight.w600,
        color:      Colors.white,
      ),
    ),

    // Cards
    // cardTheme: CardTheme(
    //   elevation:    0,
    //   color:        Colors.white,
    //   shape: RoundedRectangleBorder(
    //     borderRadius: BorderRadius.circular(14),
    //     side: BorderSide(color: Colors.black.withOpacity(0.07)),
    //   ),
    // ),

    // Inputs
    inputDecorationTheme: InputDecorationTheme(
      filled:          true,
      fillColor:       const Color(0xFFF5F5F5),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide:   BorderSide.none,
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide:   BorderSide(color: Colors.black.withOpacity(0.1)),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide:   const BorderSide(color: _green, width: 1.5),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide:   const BorderSide(color: _red, width: 1.2),
      ),
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      labelStyle: TextStyle(color: Colors.black.withOpacity(0.5)),
    ),

    // Boutons
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: _green,
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        textStyle: const TextStyle(
          fontFamily: 'Cairo',
          fontSize: 15,
          fontWeight: FontWeight.w600,
        ),
        elevation: 0,
      ),
    ),

    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: _green,
        side:            const BorderSide(color: _green),
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        textStyle: const TextStyle(
          fontFamily: 'Cairo',
          fontSize:   14,
          fontWeight: FontWeight.w500,
        ),
      ),
    ),

    // BottomNav
    bottomNavigationBarTheme: const BottomNavigationBarThemeData(
      type:              BottomNavigationBarType.fixed,
      selectedItemColor: _green,
      unselectedItemColor: Colors.grey,
      backgroundColor:   Colors.white,
      elevation:         8,
    ),

    // Chips
    chipTheme: ChipThemeData(
      backgroundColor:   _greenLight,
      labelStyle: const TextStyle(
        fontFamily: 'Cairo',
        color:      _greenDark,
        fontSize:   12,
      ),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
    ),

    scaffoldBackgroundColor: const Color(0xFFF8F8F6),

    extensions: const [CreditStockColors.light],
  );

  // ── THÈME SOMBRE ─────────────────────────────────────────

  static ThemeData get dark => ThemeData(
    useMaterial3:   true,
    brightness:     Brightness.dark,
    colorScheme:    ColorScheme.fromSeed(
      seedColor:  _green,
      brightness: Brightness.dark,
      primary:    _green,
      secondary:  _amber,
      error:      _red,
      surface:    const Color(0xFF1E2130),
    ),
    fontFamily: 'Cairo',

    appBarTheme: const AppBarTheme(
      backgroundColor: Color(0xFF161925),
      foregroundColor: Colors.white,
      elevation:       0,
      centerTitle:     true,
      titleTextStyle:  TextStyle(
        fontFamily: 'Cairo',
        fontSize:   18,
        fontWeight: FontWeight.w600,
        color:      Colors.white,
      ),
    ),

    // cardTheme: CardTheme(
    //   elevation: 0,
    //   color:     const Color(0xFF252A3D),
    //   shape: RoundedRectangleBorder(
    //     borderRadius: BorderRadius.circular(14),
    //     side: BorderSide(color: Colors.white.withOpacity(0.07)),
    //   ),
    // ),

    inputDecorationTheme: InputDecorationTheme(
      filled:    true,
      fillColor: const Color(0xFF1E2130),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide:   BorderSide.none,
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide:   BorderSide(color: Colors.white.withOpacity(0.12)),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide:   const BorderSide(color: _green, width: 1.5),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide:   const BorderSide(color: _red, width: 1.2),
      ),
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      labelStyle: TextStyle(color: Colors.white.withOpacity(0.5)),
    ),

    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: _green,
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        textStyle: const TextStyle(
          fontFamily: 'Cairo',
          fontSize:   15,
          fontWeight: FontWeight.w600,
        ),
        elevation: 0,
      ),
    ),

    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: _green,
        side:            const BorderSide(color: _green),
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    ),

    bottomNavigationBarTheme: const BottomNavigationBarThemeData(
      type:                BottomNavigationBarType.fixed,
      selectedItemColor:   _green,
      unselectedItemColor: Colors.grey,
      backgroundColor:     Color(0xFF161925),
      elevation:           8,
    ),

    scaffoldBackgroundColor: const Color(0xFF12151F),

    extensions: const [CreditStockColors.dark],
  );
}

// ── Extension couleurs métier ─────────────────────────────

class CreditStockColors extends ThemeExtension<CreditStockColors> {
  final Color green;
  final Color greenLight;
  final Color greenDark;
  final Color amber;
  final Color amberLight;
  final Color red;
  final Color redLight;
  final Color blue;
  final Color blueLight;
  final Color cardBg;
  final Color textSecondary;

  const CreditStockColors({
    required this.green,
    required this.greenLight,
    required this.greenDark,
    required this.amber,
    required this.amberLight,
    required this.red,
    required this.redLight,
    required this.blue,
    required this.blueLight,
    required this.cardBg,
    required this.textSecondary,
  });

  static const light = CreditStockColors(
    green:         Color(0xFF1D9E75),
    greenLight:    Color(0xFFE1F5EE),
    greenDark:     Color(0xFF085041),
    amber:         Color(0xFFBA7517),
    amberLight:    Color(0xFFFAEEDA),
    red:           Color(0xFFE24B4A),
    redLight:      Color(0xFFFCEBEB),
    blue:          Color(0xFF378ADD),
    blueLight:     Color(0xFFE6F1FB),
    cardBg:        Colors.white,
    textSecondary: Color(0xFF888780),
  );

  static const dark = CreditStockColors(
    green:         Color(0xFF27C98F),
    greenLight:    Color(0xFF1A3D30),
    greenDark:     Color(0xFF7FFFD4),
    amber:         Color(0xFFE8A83A),
    amberLight:    Color(0xFF3D2E10),
    red:           Color(0xFFFF6B6B),
    redLight:      Color(0xFF3D1515),
    blue:          Color(0xFF5BA8F5),
    blueLight:     Color(0xFF1A2C40),
    cardBg:        Color(0xFF252A3D),
    textSecondary: Color(0xFFAAAAAA),
  );

  @override
  CreditStockColors copyWith({
    Color? green, Color? greenLight, Color? greenDark,
    Color? amber, Color? amberLight,
    Color? red,   Color? redLight,
    Color? blue,  Color? blueLight,
    Color? cardBg, Color? textSecondary,
  }) => CreditStockColors(
    green:         green         ?? this.green,
    greenLight:    greenLight    ?? this.greenLight,
    greenDark:     greenDark     ?? this.greenDark,
    amber:         amber         ?? this.amber,
    amberLight:    amberLight    ?? this.amberLight,
    red:           red           ?? this.red,
    redLight:      redLight      ?? this.redLight,
    blue:          blue          ?? this.blue,
    blueLight:     blueLight     ?? this.blueLight,
    cardBg:        cardBg        ?? this.cardBg,
    textSecondary: textSecondary ?? this.textSecondary,
  );

  @override
  CreditStockColors lerp(CreditStockColors? other, double t) {
    if (other == null) return this;
    return CreditStockColors(
      green:         Color.lerp(green,         other.green,         t)!,
      greenLight:    Color.lerp(greenLight,    other.greenLight,    t)!,
      greenDark:     Color.lerp(greenDark,     other.greenDark,     t)!,
      amber:         Color.lerp(amber,         other.amber,         t)!,
      amberLight:    Color.lerp(amberLight,    other.amberLight,    t)!,
      red:           Color.lerp(red,           other.red,           t)!,
      redLight:      Color.lerp(redLight,      other.redLight,      t)!,
      blue:          Color.lerp(blue,          other.blue,          t)!,
      blueLight:     Color.lerp(blueLight,     other.blueLight,     t)!,
      cardBg:        Color.lerp(cardBg,        other.cardBg,        t)!,
      textSecondary: Color.lerp(textSecondary, other.textSecondary, t)!,
    );
  }
}
