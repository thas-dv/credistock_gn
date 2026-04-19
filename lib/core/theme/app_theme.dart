import 'package:flutter/material.dart';

abstract class AppColors {
  // Brand
  static const green = Color(0xFF1D9E75);
  static const greenLight = Color(0xFFE1F5EE);
  static const greenDark = Color(0xFF085041);

  // Sémantique
  static const amber = Color(0xFFBA7517);
  static const amberLight = Color(0xFFFAEEDA);
  static const red = Color(0xFFE24B4A);
  static const redLight = Color(0xFFFCEBEB);
  static const blue = Color(0xFF378ADD);
  static const blueLight = Color(0xFFE6F1FB);

  // Neutres
  static const gray50 = Color(0xFFF1EFE8);
  static const gray200 = Color(0xFFB4B2A9);
  static const gray400 = Color(0xFF888780);
  static const gray600 = Color(0xFF5F5E5A);
  static const gray800 = Color(0xFF444441);
  static const gray900 = Color(0xFF2C2C2A);
}

abstract class AppTheme {
  static ThemeData get light => ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: AppColors.green,
          primary: AppColors.green,
          secondary: AppColors.amber,
          error: AppColors.red,
          surface: Colors.white,
          background: AppColors.gray50,
        ),
        fontFamily: 'Inter',
        scaffoldBackgroundColor: AppColors.gray50,
        appBarTheme: const AppBarTheme(
          backgroundColor: Colors.white,
          foregroundColor: AppColors.gray900,
          elevation: 0,
          centerTitle: false,
          titleTextStyle: TextStyle(
            fontFamily: 'Inter',
            fontSize: 17,
            fontWeight: FontWeight.w500,
            color: AppColors.gray900,
          ),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: AppColors.green,
            foregroundColor: Colors.white,
            elevation: 0,
            minimumSize: const Size(double.infinity, 50),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            textStyle: const TextStyle(
              fontFamily: 'Inter',
              fontSize: 15,
              fontWeight: FontWeight.w500,
            ),
          ),
        ),
        outlinedButtonTheme: OutlinedButtonThemeData(
          style: OutlinedButton.styleFrom(
            foregroundColor: AppColors.gray900,
            side: BorderSide(color: Colors.black.withOpacity(0.15), width: 0.5),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(10),
            ),
          ),
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: AppColors.gray50,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(10),
            borderSide:
                BorderSide(color: Colors.black.withOpacity(0.1), width: 0.5),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(10),
            borderSide:
                BorderSide(color: Colors.black.withOpacity(0.1), width: 0.5),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(10),
            borderSide: const BorderSide(color: AppColors.green, width: 1.5),
          ),
          contentPadding:
              const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
          hintStyle: const TextStyle(color: AppColors.gray400, fontSize: 13),
        ),
        chipTheme: ChipThemeData(
          backgroundColor: AppColors.gray50,
          selectedColor: AppColors.greenLight,
          side: BorderSide(color: Colors.black.withOpacity(0.1), width: 0.5),
          labelStyle: const TextStyle(fontSize: 12),
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          shape: const StadiumBorder(),
        ),
        bottomNavigationBarTheme: const BottomNavigationBarThemeData(
          backgroundColor: Colors.white,
          selectedItemColor: AppColors.green,
          unselectedItemColor: AppColors.gray400,
          type: BottomNavigationBarType.fixed,
          elevation: 0,
          selectedLabelStyle:
              TextStyle(fontSize: 10, fontWeight: FontWeight.w500),
          unselectedLabelStyle: TextStyle(fontSize: 10),
        ),
        textTheme: const TextTheme(
          headlineLarge: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.w600,
              color: AppColors.gray900),
          headlineMedium: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.w500,
              color: AppColors.gray900),
          headlineSmall: TextStyle(
              fontSize: 17,
              fontWeight: FontWeight.w500,
              color: AppColors.gray900),
          bodyLarge: TextStyle(fontSize: 15, color: AppColors.gray900),
          bodyMedium: TextStyle(fontSize: 13, color: AppColors.gray600),
          bodySmall: TextStyle(fontSize: 11, color: AppColors.gray400),
          labelLarge: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w500,
              color: AppColors.gray900),
        ),
        cardTheme: CardThemeData(
          color: Colors.white,
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: BorderSide(color: Colors.black.withOpacity(0.07), width: 0.5),
          ),
        ),
      );

  static ThemeData get dark {
    const darkBg = Color(0xFF111110);
    const darkSurface = Color(0xFF1C1C1A);
    const darkBorder = Color(0xFF2A2A27);

    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      colorScheme: const ColorScheme.dark(
        primary: AppColors.green,
        secondary: AppColors.amber,
        error: AppColors.red,
        surface: darkSurface,
      ),
      scaffoldBackgroundColor: darkBg,
      fontFamily: 'Inter',
      appBarTheme: const AppBarTheme(
        backgroundColor: darkSurface,
        foregroundColor: Colors.white,
        elevation: 0,
      ),
      cardTheme: CardThemeData(
        color: darkSurface,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: const BorderSide(color: darkBorder, width: 0.5),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: darkSurface,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: const BorderSide(color: darkBorder, width: 0.5),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: const BorderSide(color: darkBorder, width: 0.5),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: const BorderSide(color: AppColors.green, width: 1.5),
        ),
      ),
      // bottomAppBarTheme: BottomAppBarTheme(
      //   color: darkSurface,
      //   surfaceTintColor: Colors.transparent,
      // ),
      bottomAppBarTheme: BottomAppBarThemeData(
        color: darkSurface,
        surfaceTintColor: Colors.transparent,
      ),
      textTheme: TextTheme(
        headlineLarge: TextStyle(
            fontSize: 24, fontWeight: FontWeight.w600, color: Colors.white),
        headlineMedium: TextStyle(
            fontSize: 20, fontWeight: FontWeight.w500, color: Colors.white),
        headlineSmall: TextStyle(
            fontSize: 17, fontWeight: FontWeight.w500, color: Colors.white),
        bodyLarge: TextStyle(fontSize: 15, color: Colors.white),
        bodyMedium: TextStyle(fontSize: 13, color: Color(0xFFB4B2A9)),
        bodySmall: TextStyle(fontSize: 11, color: Color(0xFF888780)),
        labelLarge: TextStyle(
            fontSize: 14, fontWeight: FontWeight.w500, color: Colors.white),
      ),
    );
  }
}

// ============================================================
// EXTENSIONS UI UTILES
// ============================================================

extension ScoreClientStyle on String {
  Color get scoreCouleur => switch (this) {
        'bon' => AppColors.green,
        'moyen' => AppColors.amber,
        'mauvais' => AppColors.red,
        _ => AppColors.gray400,
      };

  Color get scoreCouleurLight => switch (this) {
        'bon' => AppColors.greenLight,
        'moyen' => AppColors.amberLight,
        'mauvais' => AppColors.redLight,
        _ => AppColors.gray50,
      };
}

extension StatutDetteStyle on String {
  Color get statutCouleur => switch (this) {
        'paye' => AppColors.green,
        'partiel' => AppColors.amber,
        'non_paye' => AppColors.red,
        _ => AppColors.gray400,
      };
}
