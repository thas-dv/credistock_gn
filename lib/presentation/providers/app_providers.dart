// lib/presentation/providers/app_providers.dart
import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../../data/local/database/app_database.dart';

// ── SharedPreferences ────────────────────────────────────────

final sharedPrefsProvider = Provider<SharedPreferences>((ref) {
  throw UnimplementedError('Initialize in main.dart');
});

// ── Base de données locale ───────────────────────────────────

final appDatabaseProvider = Provider<AppDatabase>((ref) {
  final db = AppDatabase();
  ref.onDispose(db.close);
  return db;
});

// ── Thème ────────────────────────────────────────────────────

class ThemeNotifier extends Notifier<ThemeMode> {
  @override
  ThemeMode build() {
    final prefs = ref.read(sharedPrefsProvider);
    final val   = prefs.getString('theme_mode') ?? 'system';
    return switch (val) {
      'light'  => ThemeMode.light,
      'dark'   => ThemeMode.dark,
      _        => ThemeMode.system,
    };
  }

  void setTheme(ThemeMode mode) {
    state = mode;
    final prefs = ref.read(sharedPrefsProvider);
    prefs.setString('theme_mode', switch (mode) {
      ThemeMode.light  => 'light',
      ThemeMode.dark   => 'dark',
      ThemeMode.system => 'system',
    });
  }
}

final themeProvider = NotifierProvider<ThemeNotifier, ThemeMode>(
  ThemeNotifier.new,
);

// ── Langue ───────────────────────────────────────────────────

class LocaleNotifier extends Notifier<Locale> {
  @override
  Locale build() {
    final prefs = ref.read(sharedPrefsProvider);
    final code  = prefs.getString('locale') ?? 'fr';
    return Locale(code);
  }

  void setLocale(String languageCode) {
    state = Locale(languageCode);
    ref.read(sharedPrefsProvider).setString('locale', languageCode);
  }
}

final localeProvider = NotifierProvider<LocaleNotifier, Locale>(
  LocaleNotifier.new,
);

// ── Connectivité ─────────────────────────────────────────────

final connectivityProvider = StreamProvider<bool>((ref) {
  return Connectivity().onConnectivityChanged.map(
    (results) => results.any((r) => r != ConnectivityResult.none),
  );
});

final isOnlineProvider = Provider<bool>((ref) {
  return ref.watch(connectivityProvider).when(
    data:    (online) => online,
    loading: ()       => false,
    error:   (_, __)  => false,
  );
});

// ── Session locale (boutique connectée) ──────────────────────

class SessionState {
  final String? boutiqueId;
  final String? utilisateurId;
  final String? utilisateurNom;
  final String? role;         // admin | employe
  final String? abonnement;   // gratuit | premium

  const SessionState({
    this.boutiqueId,
    this.utilisateurId,
    this.utilisateurNom,
    this.role,
    this.abonnement,
  });

  bool get isLoggedIn => boutiqueId != null && utilisateurId != null;
  bool get isAdmin    => role == 'admin';
  bool get isPremium  => abonnement == 'premium';

  SessionState copyWith({
    String? boutiqueId,
    String? utilisateurId,
    String? utilisateurNom,
    String? role,
    String? abonnement,
  }) => SessionState(
    boutiqueId:      boutiqueId      ?? this.boutiqueId,
    utilisateurId:   utilisateurId   ?? this.utilisateurId,
    utilisateurNom:  utilisateurNom  ?? this.utilisateurNom,
    role:            role            ?? this.role,
    abonnement:      abonnement      ?? this.abonnement,
  );
}

class SessionNotifier extends Notifier<SessionState> {
  @override
  SessionState build() {
    final prefs = ref.read(sharedPrefsProvider);
    return SessionState(
      boutiqueId:     prefs.getString('session_boutique_id'),
      utilisateurId:  prefs.getString('session_utilisateur_id'),
      utilisateurNom: prefs.getString('session_utilisateur_nom'),
      role:           prefs.getString('session_role'),
      abonnement:     prefs.getString('session_abonnement'),
    );
  }

  Future<void> saveSession({
    required String boutiqueId,
    required String utilisateurId,
    required String utilisateurNom,
    required String role,
    required String abonnement,
  }) async {
    state = SessionState(
      boutiqueId:     boutiqueId,
      utilisateurId:  utilisateurId,
      utilisateurNom: utilisateurNom,
      role:           role,
      abonnement:     abonnement,
    );
    final prefs = ref.read(sharedPrefsProvider);
    await prefs.setString('session_boutique_id',     boutiqueId);
    await prefs.setString('session_utilisateur_id',  utilisateurId);
    await prefs.setString('session_utilisateur_nom', utilisateurNom);
    await prefs.setString('session_role',            role);
    await prefs.setString('session_abonnement',      abonnement);
  }

  Future<void> clearSession() async {
    state = const SessionState();
    final prefs = ref.read(sharedPrefsProvider);
    await prefs.remove('session_boutique_id');
    await prefs.remove('session_utilisateur_id');
    await prefs.remove('session_utilisateur_nom');
    await prefs.remove('session_role');
    await prefs.remove('session_abonnement');
    await Supabase.instance.client.auth.signOut();
  }
}

final sessionProvider = NotifierProvider<SessionNotifier, SessionState>(
  SessionNotifier.new,
);

// ── Sync status ──────────────────────────────────────────────

enum SyncStatus { idle, syncing, success, error }

class SyncNotifier extends Notifier<SyncStatus> {
  @override
  SyncStatus build() => SyncStatus.idle;

  Future<void> syncAll() async {
    final session = ref.read(sessionProvider);
    if (!session.isLoggedIn) return;

    final isOnline = ref.read(isOnlineProvider);
    if (!isOnline) return;

    state = SyncStatus.syncing;

    try {
      final db        = ref.read(appDatabaseProvider);
      final supabase  = Supabase.instance.client;
      final boutiqueId = session.boutiqueId!;

      // Synchroniser dans l'ordre : produits → clients → ventes → dettes → paiements
      await _syncTable(db, supabase, boutiqueId, 'credistock_produits');
      await _syncTable(db, supabase, boutiqueId, 'credistock_clients');
      await _syncTable(db, supabase, boutiqueId, 'credistock_ventes');
      await _syncTable(db, supabase, boutiqueId, 'credistock_lignes_vente');
      await _syncTable(db, supabase, boutiqueId, 'credistock_dettes');
      await _syncTable(db, supabase, boutiqueId, 'credistock_paiements');

      state = SyncStatus.success;

      // Reset to idle after 3s
      await Future.delayed(const Duration(seconds: 3));
      if (state == SyncStatus.success) state = SyncStatus.idle;
    } catch (e) {
      state = SyncStatus.error;
      debugPrint('Sync error: $e');
    }
  }

  Future<void> _syncTable(
    AppDatabase db,
    SupabaseClient supabase,
    String boutiqueId,
    String tableName,
  ) async {
    // Récupérer tous les enregistrements non synchronisés depuis la queue
    final queue = await (db.select(db.creditStockSyncQueue)
      ..where((q) => q.boutiqueId.equals(boutiqueId) & q.statut.equals('pending') & q.tableName_.equals(tableName))
    ).get();

    for (final item in queue) {
      try {
        final payload = Map<String, dynamic>.from(
          json.decode(item.payload) as Map,
        );

        switch (item.operation) {
          case 'INSERT':
          case 'UPDATE':
            await supabase.from(tableName).upsert(payload);
          case 'DELETE':
            await supabase.from(tableName).delete().eq('id', item.recordId);
        }

        // Marquer comme synchronisé
        await (db.update(db.creditStockSyncQueue)
          ..where((q) => q.id.equals(item.id))
        ).write(
          CreditStockSyncQueueCompanion(
            statut:    const Value('synced'),
            syncedAt:  Value(DateTime.now()),
          ),
        );
      } catch (e) {
        // Incrémenter les tentatives
        await (db.update(db.creditStockSyncQueue)
          ..where((q) => q.id.equals(item.id))
        ).write(
          CreditStockSyncQueueCompanion(
            tentatives: Value(item.tentatives + 1),
            statut:     Value(item.tentatives >= 5 ? 'error' : 'pending'),
            errorMsg:   Value(e.toString()),
          ),
        );
      }
    }
  }
}

final syncProvider = NotifierProvider<SyncNotifier, SyncStatus>(
  SyncNotifier.new,
);

// ── Alertes non lues ─────────────────────────────────────────

final alertesNonLuesProvider = StreamProvider.autoDispose<int>((ref) {
  final session = ref.watch(sessionProvider);
  if (!session.isLoggedIn) return Stream.value(0);

  final db = ref.watch(appDatabaseProvider);
  return (db.select(db.creditStockAlertes)
    ..where((a) => a.boutiqueId.equals(session.boutiqueId!) & a.lu.equals(false))
  ).watch().map((list) => list.length);
});