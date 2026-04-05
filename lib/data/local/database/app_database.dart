import 'package:drift/drift.dart';
import 'package:drift_flutter/drift_flutter.dart';
import 'package:injectable/injectable.dart';

part 'app_database.g.dart';

// ============================================================
// TABLES
// ============================================================

class Boutiques extends Table {
  TextColumn get id => text().withLength(min: 36, max: 36)();
  TextColumn get nom => text().withLength(max: 100)();
  TextColumn get adresse => text().withLength(max: 200).nullable()();
  TextColumn get telephone => text().withLength(max: 20)();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();

  @override
  Set<Column> get primaryKey => {id};
}

class Utilisateurs extends Table {
  TextColumn get id => text().withLength(min: 36, max: 36)();
  TextColumn get boutiqueId => text().references(Boutiques, #id)();
  TextColumn get nom => text().withLength(max: 100)();
  TextColumn get role => text().withDefault(const Constant('employe'))(); // admin | employe
  TextColumn get motDePasse => text()(); // hashé bcrypt
  TextColumn get pinHash => text().nullable()(); // PIN local hashé
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();

  @override
  Set<Column> get primaryKey => {id};
}

class Produits extends Table {
  TextColumn get id => text().withLength(min: 36, max: 36)();
  TextColumn get boutiqueId => text().references(Boutiques, #id)();
  TextColumn get nom => text().withLength(max: 100)();
  TextColumn get categorie => text().withDefault(const Constant('general'))();
  IntColumn get prixVente => integer()(); // GNF
  IntColumn get prixAchat => integer().withDefault(const Constant(0))(); // GNF
  IntColumn get quantite => integer().withDefault(const Constant(0))();
  IntColumn get seuilAlerte => integer().withDefault(const Constant(5))();
  BoolColumn get synced => boolean().withDefault(const Constant(true))();
  DateTimeColumn get updatedAt => dateTime().withDefault(currentDateAndTime)();

  @override
  Set<Column> get primaryKey => {id};
}

class Clients extends Table {
  TextColumn get id => text().withLength(min: 36, max: 36)();
  TextColumn get boutiqueId => text().references(Boutiques, #id)();
  TextColumn get nom => text().withLength(max: 100)();
  TextColumn get telephone => text().withLength(max: 20).nullable()();
  TextColumn get score => text().withDefault(const Constant('bon'))(); // bon | moyen | mauvais
  IntColumn get totalDu => integer().withDefault(const Constant(0))(); // GNF
  IntColumn get nombreDettes => integer().withDefault(const Constant(0))();
  IntColumn get nombresRemboursements => integer().withDefault(const Constant(0))();
  BoolColumn get synced => boolean().withDefault(const Constant(true))();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();

  @override
  Set<Column> get primaryKey => {id};
}

class Ventes extends Table {
  TextColumn get id => text().withLength(min: 36, max: 36)();
  TextColumn get boutiqueId => text().references(Boutiques, #id)();
  TextColumn get produitId => text().references(Produits, #id)();
  TextColumn get clientId => text().nullable()(); // nullable si cash
  TextColumn get utilisateurId => text().references(Utilisateurs, #id)();
  IntColumn get quantite => integer()();
  IntColumn get prixUnitaire => integer()(); // snapshot prix au moment de la vente
  IntColumn get montantTotal => integer()();
  TextColumn get typePaiement => text()(); // cash | credit
  TextColumn get source => text().withDefault(const Constant('manuel'))(); // manuel | vocal
  BoolColumn get synced => boolean().withDefault(const Constant(false))();
  DateTimeColumn get date => dateTime().withDefault(currentDateAndTime)();

  @override
  Set<Column> get primaryKey => {id};
}

class Dettes extends Table {
  TextColumn get id => text().withLength(min: 36, max: 36)();
  TextColumn get clientId => text().references(Clients, #id)();
  TextColumn get venteId => text().references(Ventes, #id)();
  TextColumn get boutiqueId => text()();
  IntColumn get montant => integer()(); // GNF total
  IntColumn get montantPaye => integer().withDefault(const Constant(0))(); // paiement partiel
  TextColumn get statut => text().withDefault(const Constant('non_paye'))(); // non_paye | partiel | paye
  DateTimeColumn get dateEcheance => dateTime().nullable()();
  BoolColumn get rappel1JourEnvoye => boolean().withDefault(const Constant(false))();
  BoolColumn get rappel3JoursEnvoye => boolean().withDefault(const Constant(false))();
  BoolColumn get rappel7JoursEnvoye => boolean().withDefault(const Constant(false))();
  BoolColumn get synced => boolean().withDefault(const Constant(false))();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();
  DateTimeColumn get updatedAt => dateTime().withDefault(currentDateAndTime)();

  @override
  Set<Column> get primaryKey => {id};
}

class Paiements extends Table {
  TextColumn get id => text().withLength(min: 36, max: 36)();
  TextColumn get detteId => text().references(Dettes, #id)();
  TextColumn get boutiqueId => text()();
  IntColumn get montant => integer()();
  TextColumn get modePaiement => text().withDefault(const Constant('especes'))(); // especes | orange_money | mtn_momo
  BoolColumn get synced => boolean().withDefault(const Constant(false))();
  DateTimeColumn get date => dateTime().withDefault(currentDateAndTime)();

  @override
  Set<Column> get primaryKey => {id};
}

class SyncQueue extends Table {
  TextColumn get id => text().withLength(min: 36, max: 36)();
  TextColumn get tableName => text()();
  TextColumn get recordId => text()();
  TextColumn get operation => text()(); // insert | update | delete
  TextColumn get payload => text()(); // JSON
  IntColumn get retryCount => integer().withDefault(const Constant(0))();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();

  @override
  Set<Column> get primaryKey => {id};
}

class Abonnements extends Table {
  TextColumn get id => text().withLength(min: 36, max: 36)();
  TextColumn get boutiqueId => text().references(Boutiques, #id)();
  TextColumn get plan => text().withDefault(const Constant('gratuit'))(); // gratuit | premium
  TextColumn get statut => text().withDefault(const Constant('actif'))(); // actif | expire | suspendu
  TextColumn get modePaiement => text().nullable()(); // orange_money | mtn_momo
  IntColumn get montant => integer().withDefault(const Constant(0))();
  DateTimeColumn get dateDebut => dateTime().withDefault(currentDateAndTime)();
  DateTimeColumn get dateFin => dateTime().nullable()();
  BoolColumn get synced => boolean().withDefault(const Constant(false))();

  @override
  Set<Column> get primaryKey => {id};
}

// ============================================================
// DATABASE
// ============================================================

@singleton
@DriftDatabase(tables: [
  Boutiques,
  Utilisateurs,
  Produits,
  Clients,
  Ventes,
  Dettes,
  Paiements,
  SyncQueue,
  Abonnements,
])
class AppDatabase extends _$AppDatabase {
  AppDatabase() : super(_openConnection());

  @override
  int get schemaVersion => 1;

  @override
  MigrationStrategy get migration => MigrationStrategy(
    onCreate: (Migrator m) async {
      await m.createAll();
    },
    onUpgrade: (Migrator m, int from, int to) async {
      // Migrations futures ici
    },
  );

  static QueryExecutor _openConnection() {
    return driftDatabase(name: 'credistock_gn.db');
  }
}