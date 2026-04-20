// lib/data/local/database/app_database.dart
// ============================================================
// Base de données SQLite locale (Drift)
// Toutes les tables locales correspondent aux tables Supabase
// avec le même préfixe credistock_
// ============================================================

import 'dart:io';
import 'package:drift/drift.dart';
import 'package:drift/native.dart';
import 'package:drift_flutter/drift_flutter.dart';
import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as p;

part 'app_database.g.dart';

// ── Tables ──────────────────────────────────────────────────

/// credistock_boutiques
class CreditStockBoutiques extends Table {
  TextColumn get id            => text()();
  TextColumn get nom           => text()();
  TextColumn get telephone     => text()();
  TextColumn get adresse       => text().nullable()();
  TextColumn get typeBoutique  => text().withDefault(const Constant('general'))();
  TextColumn get logoUrl       => text().nullable()();
  TextColumn get pinHash       => text().nullable()();
  TextColumn get abonnement    => text().withDefault(const Constant('gratuit'))();
  DateTimeColumn get premiumExpireAt => dateTime().nullable()();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();
  DateTimeColumn get updatedAt => dateTime().withDefault(currentDateAndTime)();

  @override
  String get tableName => 'credistock_boutiques';
  @override
  Set<Column> get primaryKey => {id};
}

/// credistock_utilisateurs
class CreditStockUtilisateurs extends Table {
  TextColumn get id          => text()();
  TextColumn get authId      => text().nullable()();
  TextColumn get boutiqueId  => text().references(CreditStockBoutiques, #id)();
  TextColumn get nom         => text()();
  TextColumn get telephone   => text().nullable()();
  TextColumn get role        => text().withDefault(const Constant('employe'))(); // admin | employe
  TextColumn get pinHash     => text().nullable()();
  BoolColumn get actif       => boolean().withDefault(const Constant(true))();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();
  DateTimeColumn get updatedAt => dateTime().withDefault(currentDateAndTime)();

  @override
  String get tableName => 'credistock_utilisateurs';
  @override
  Set<Column> get primaryKey => {id};
}

/// credistock_produits
class CreditStockProduits extends Table {
  TextColumn get id           => text()();
  TextColumn get boutiqueId   => text().references(CreditStockBoutiques, #id)();
  TextColumn get nom          => text()();
  TextColumn get description  => text().nullable()();
  TextColumn get codeBarre    => text().nullable()();
  IntColumn  get prixVente    => integer().withDefault(const Constant(0))();  // GNF
  IntColumn  get prixAchat    => integer().withDefault(const Constant(0))();
  IntColumn  get quantite     => integer().withDefault(const Constant(0))();
  IntColumn  get seuilAlerte  => integer().withDefault(const Constant(5))();
  TextColumn get unite        => text().withDefault(const Constant('unité'))();
  TextColumn get categorie    => text().nullable()();
  TextColumn get imageUrl     => text().nullable()();
  BoolColumn get actif        => boolean().withDefault(const Constant(true))();
  BoolColumn get synced       => boolean().withDefault(const Constant(false))();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();
  DateTimeColumn get updatedAt => dateTime().withDefault(currentDateAndTime)();

  @override
  String get tableName => 'credistock_produits';
  @override
  Set<Column> get primaryKey => {id};
}

/// credistock_clients
class CreditStockClients extends Table {
  TextColumn get id          => text()();
  TextColumn get boutiqueId  => text().references(CreditStockBoutiques, #id)();
  TextColumn get nom         => text()();
  TextColumn get telephone   => text().nullable()();
  TextColumn get adresse     => text().nullable()();
  TextColumn get photoUrl    => text().nullable()();
  TextColumn get score       => text().withDefault(const Constant('moyen'))(); // bon|moyen|mauvais
  IntColumn  get totalDu     => integer().withDefault(const Constant(0))();
  IntColumn  get nbAchats    => integer().withDefault(const Constant(0))();
  IntColumn  get nbRetards   => integer().withDefault(const Constant(0))();
  BoolColumn get synced      => boolean().withDefault(const Constant(false))();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();
  DateTimeColumn get updatedAt => dateTime().withDefault(currentDateAndTime)();

  @override
  String get tableName => 'credistock_clients';
  @override
  Set<Column> get primaryKey => {id};
}

/// credistock_ventes
class CreditStockVentes extends Table {
  TextColumn get id             => text()();
  TextColumn get boutiqueId     => text().references(CreditStockBoutiques, #id)();
  TextColumn get utilisateurId  => text().nullable()();
  TextColumn get clientId       => text().nullable()();
  TextColumn get typePaiement   => text().withDefault(const Constant('cash'))();
  IntColumn  get montantTotal   => integer().withDefault(const Constant(0))();
  TextColumn get note           => text().nullable()();
  BoolColumn get synced         => boolean().withDefault(const Constant(false))();
  DateTimeColumn get dateVente  => dateTime().withDefault(currentDateAndTime)();
  DateTimeColumn get createdAt  => dateTime().withDefault(currentDateAndTime)();

  @override
  String get tableName => 'credistock_ventes';
  @override
  Set<Column> get primaryKey => {id};
}

/// credistock_lignes_vente
class CreditStockLignesVente extends Table {
  TextColumn get id           => text()();
  TextColumn get venteId      => text().references(CreditStockVentes, #id)();
  TextColumn get produitId    => text()();
  TextColumn get boutiqueId   => text()();
  TextColumn get nomProduit   => text()();
  IntColumn  get quantite     => integer().withDefault(const Constant(1))();
  IntColumn  get prixUnitaire => integer().withDefault(const Constant(0))();
  IntColumn  get sousTotal    => integer().withDefault(const Constant(0))();
  BoolColumn get synced       => boolean().withDefault(const Constant(false))();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();

  @override
  String get tableName => 'credistock_lignes_vente';
  @override
  Set<Column> get primaryKey => {id};
}

/// credistock_dettes
class CreditStockDettes extends Table {
  TextColumn get id              => text()();
  TextColumn get boutiqueId      => text().references(CreditStockBoutiques, #id)();
  TextColumn get clientId        => text().references(CreditStockClients, #id)();
  TextColumn get venteId         => text().nullable()();
  IntColumn  get montantInitial  => integer().withDefault(const Constant(0))();
  IntColumn  get montantPaye     => integer().withDefault(const Constant(0))();
  TextColumn get statut          => text().withDefault(const Constant('non_paye'))();
  DateTimeColumn get dateEcheance => dateTime().nullable()();
  TextColumn get note            => text().nullable()();
  BoolColumn get synced          => boolean().withDefault(const Constant(false))();
  DateTimeColumn get createdAt   => dateTime().withDefault(currentDateAndTime)();
  DateTimeColumn get updatedAt   => dateTime().withDefault(currentDateAndTime)();

  // Calculé localement
  int get montantRestant => 0; // override dans la couche data

  @override
  String get tableName => 'credistock_dettes';
  @override
  Set<Column> get primaryKey => {id};
}

/// credistock_paiements
class CreditStockPaiements extends Table {
  TextColumn get id            => text()();
  TextColumn get boutiqueId    => text()();
  TextColumn get detteId       => text().references(CreditStockDettes, #id)();
  TextColumn get clientId      => text()();
  IntColumn  get montant       => integer().withDefault(const Constant(0))();
  TextColumn get modePaiement  => text().withDefault(const Constant('cash'))();
  TextColumn get note          => text().nullable()();
  BoolColumn get synced        => boolean().withDefault(const Constant(false))();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();

  @override
  String get tableName => 'credistock_paiements';
  @override
  Set<Column> get primaryKey => {id};
}

/// credistock_sync_queue
class CreditStockSyncQueue extends Table {
  TextColumn get id          => text()();
  TextColumn get boutiqueId  => text()();
  TextColumn get tableName_  => text().named('table_name')();
  TextColumn get operation   => text()(); // INSERT | UPDATE | DELETE
  TextColumn get recordId    => text()();
  TextColumn get payload     => text()();  // JSON
  TextColumn get statut      => text().withDefault(const Constant('pending'))();
  IntColumn  get tentatives  => integer().withDefault(const Constant(0))();
  TextColumn get errorMsg    => text().nullable()();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();
  DateTimeColumn get syncedAt  => dateTime().nullable()();

  @override
  String get tableName => 'credistock_sync_queue';
  @override
  Set<Column> get primaryKey => {id};
}

/// credistock_alertes
class CreditStockAlertes extends Table {
  TextColumn get id          => text()();
  TextColumn get boutiqueId  => text()();
  TextColumn get typeAlerte  => text()(); // stock_faible | dette_echue | dette_rappel
  TextColumn get referenceId => text().nullable()();
  TextColumn get titre       => text()();
  TextColumn get message     => text().nullable()();
  BoolColumn get lu          => boolean().withDefault(const Constant(false))();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();

  @override
  String get tableName => 'credistock_alertes';
  @override
  Set<Column> get primaryKey => {id};
}

// ── Database ─────────────────────────────────────────────────

@DriftDatabase(tables: [
  CreditStockBoutiques,
  CreditStockUtilisateurs,
  CreditStockProduits,
  CreditStockClients,
  CreditStockVentes,
  CreditStockLignesVente,
  CreditStockDettes,
  CreditStockPaiements,
  CreditStockSyncQueue,
  CreditStockAlertes,
])
class AppDatabase extends _$AppDatabase {
  AppDatabase() : super(_openConnection());

  @override
  int get schemaVersion => 1;

  @override
  MigrationStrategy get migration => MigrationStrategy(
    onCreate: (m) => m.createAll(),
    onUpgrade: (m, from, to) async {
      // Migrations futures ici
    },
  );

  static QueryExecutor _openConnection() {
    return driftDatabase(name: 'credistock_local.db');
  }
}