import 'package:flutter/material.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:injectable/injectable.dart';

class AppSettings {
  final ThemeMode themeMode;
  final Locale locale;
  final bool autoSync;
  final bool cloudBackup;
  final bool alertStock;
  final bool alertDette1j;
  final bool alertDette3j;
  final bool alertDette7j;

  const AppSettings({
    required this.themeMode,
    required this.locale,
    required this.autoSync,
    required this.cloudBackup,
    required this.alertStock,
    required this.alertDette1j,
    required this.alertDette3j,
    required this.alertDette7j,
  });

  AppSettings copyWith({
    ThemeMode? themeMode,
    Locale? locale,
    bool? autoSync,
    bool? cloudBackup,
    bool? alertStock,
    bool? alertDette1j,
    bool? alertDette3j,
    bool? alertDette7j,
  }) {
    return AppSettings(
      themeMode: themeMode ?? this.themeMode,
      locale: locale ?? this.locale,
      autoSync: autoSync ?? this.autoSync,
      cloudBackup: cloudBackup ?? this.cloudBackup,
      alertStock: alertStock ?? this.alertStock,
      alertDette1j: alertDette1j ?? this.alertDette1j,
      alertDette3j: alertDette3j ?? this.alertDette3j,
      alertDette7j: alertDette7j ?? this.alertDette7j,
    );
  }
}

@singleton
class AppSettingsService {
  static const _boxName = 'app_settings';

  static const _kTheme = 'theme_mode';
  static const _kLocale = 'locale';
  static const _kAutoSync = 'auto_sync';
  static const _kCloudBackup = 'cloud_backup';
  static const _kAlertStock = 'alert_stock';
  static const _kAlert1j = 'alert_1j';
  static const _kAlert3j = 'alert_3j';
  static const _kAlert7j = 'alert_7j';

  final ValueNotifier<AppSettings> settings = ValueNotifier(
    const AppSettings(
      themeMode: ThemeMode.light,
      locale: Locale('fr'),
      autoSync: true,
      cloudBackup: true,
      alertStock: true,
      alertDette1j: true,
      alertDette3j: true,
      alertDette7j: false,
    ),
  );

  Box<dynamic>? _box;

  Future<void> init() async {
    _box = await Hive.openBox<dynamic>(_boxName);
    settings.value = AppSettings(
      themeMode: _readTheme(_box?.get(_kTheme) as String?),
      locale: Locale((_box?.get(_kLocale) as String?) ?? 'fr'),
      autoSync: (_box?.get(_kAutoSync) as bool?) ?? true,
      cloudBackup: (_box?.get(_kCloudBackup) as bool?) ?? true,
      alertStock: (_box?.get(_kAlertStock) as bool?) ?? true,
      alertDette1j: (_box?.get(_kAlert1j) as bool?) ?? true,
      alertDette3j: (_box?.get(_kAlert3j) as bool?) ?? true,
      alertDette7j: (_box?.get(_kAlert7j) as bool?) ?? false,
    );
  }

  ThemeMode _readTheme(String? value) {
    return switch (value) {
      'dark' => ThemeMode.dark,
      'system' => ThemeMode.system,
      _ => ThemeMode.light,
    };
  }

  Future<void> setThemeMode(ThemeMode mode) async {
    settings.value = settings.value.copyWith(themeMode: mode);
    await _box?.put(_kTheme, mode.name);
  }

  Future<void> setLocale(String code) async {
    settings.value = settings.value.copyWith(locale: Locale(code));
    await _box?.put(_kLocale, code);
  }

  Future<void> setAutoSync(bool value) async {
    settings.value = settings.value.copyWith(autoSync: value);
    await _box?.put(_kAutoSync, value);
  }

  Future<void> setCloudBackup(bool value) async {
    settings.value = settings.value.copyWith(cloudBackup: value);
    await _box?.put(_kCloudBackup, value);
  }

  Future<void> setAlertStock(bool value) async {
    settings.value = settings.value.copyWith(alertStock: value);
    await _box?.put(_kAlertStock, value);
  }

  Future<void> setAlert1j(bool value) async {
    settings.value = settings.value.copyWith(alertDette1j: value);
    await _box?.put(_kAlert1j, value);
  }

  Future<void> setAlert3j(bool value) async {
    settings.value = settings.value.copyWith(alertDette3j: value);
    await _box?.put(_kAlert3j, value);
  }

  Future<void> setAlert7j(bool value) async {
    settings.value = settings.value.copyWith(alertDette7j: value);
    await _box?.put(_kAlert7j, value);
  }
}
