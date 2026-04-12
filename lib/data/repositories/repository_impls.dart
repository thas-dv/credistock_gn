import 'dart:async';

import 'package:dartz/dartz.dart';
import 'package:drift/drift.dart';
import 'package:injectable/injectable.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import '../../core/errors/failures.dart';
import '../../core/services/supabase_sync_service.dart';
import '../local/database/app_database.dart'
    hide Produit, Client, Dette, Vente, Abonnement;
import '../../domain/entities/entities.dart';
import '../../domain/repositories/repositories.dart';
import 'package:uuid/uuid.dart';

const _uuid = Uuid();

@lazySingleton
class InMemoryStore {
  final List<Produit> produits = [];
  final List<Client> clients = [];
  final List<Vente> ventes = [];
  final List<Dette> dettes = [];

  final produitsCtrl = StreamController<List<Produit>>.broadcast();
  final clientsCtrl = StreamController<List<Client>>.broadcast();
  final ventesCtrl = StreamController<List<Vente>>.broadcast();
  final dettesCtrl = StreamController<List<Dette>>.broadcast();

  void seedIfNeeded() {
    if (produits.isNotEmpty) return;

    final now = DateTime.now();
    const boutiqueId = 'demo-boutique';

    produits.addAll([
      Produit(
        id: 'p1',
        boutiqueId: boutiqueId,
        nom: 'Riz 25kg',
        categorie: CategorieProduit.alimentaire,
        prixVente: 230000,
        prixAchat: 205000,
        quantite: 12,
        seuilAlerte: 5,
        synced: true,
        updatedAt: now,
      ),
    ]);

    clients.add(
      Client(
        id: 'c1',
        boutiqueId: boutiqueId,
        nom: 'Mamadou Barry',
        telephone: '+224620000000',
        score: ScoreClient.bon,
        totalDu: 0,
        nombreDettes: 0,
        nombresRemboursements: 0,
        synced: true,
        createdAt: now,
      ),
    );

    emitAll();
  }

  void emitAll() {
    produitsCtrl.add(List.unmodifiable(produits));
    clientsCtrl.add(List.unmodifiable(clients));
    ventesCtrl.add(List.unmodifiable(ventes));
    dettesCtrl.add(List.unmodifiable(dettes));
  }

  Stream<List<T>> withInitial<T>(
    List<T> current,
    Stream<List<T>> source,
  ) async* {
    yield List.unmodifiable(current);
    yield* source;
  }
}

@LazySingleton(as: ProduitRepository)
class ProduitRepositoryImpl implements ProduitRepository {
  final AppDatabase _db;

  ProduitRepositoryImpl(this._db);

  Produit _toEntity(dynamic row) {
    return Produit(
      id: row.id,
      boutiqueId: row.boutiqueId,
      nom: row.nom,
      categorie: CategorieProduit.values.firstWhere(
        (c) => c.name == row.categorie,
        orElse: () => CategorieProduit.general,
      ),
      prixVente: row.prixVente,
      prixAchat: row.prixAchat,
      quantite: row.quantite,
      seuilAlerte: row.seuilAlerte,
      synced: row.synced,
      updatedAt: row.updatedAt,
    );
  }

  @override
  Future<Either<Failure, Produit>> ajouterProduit(Produit produit) async {
    try {
      await _db.into(_db.produits).insert(
            ProduitsCompanion.insert(
              id: produit.id,
              boutiqueId: produit.boutiqueId,
              nom: produit.nom,
              categorie: Value(produit.categorie.name),
              prixVente: produit.prixVente,
              prixAchat: Value(produit.prixAchat),
              quantite: Value(produit.quantite),
              seuilAlerte: Value(produit.seuilAlerte),
              synced: Value(produit.synced),
              updatedAt: Value(produit.updatedAt),
            ),
          );
      return Right(produit);
    } catch (e) {
      return Left(DatabaseFailure(message: 'Erreur ajout produit: $e'));
    }
  }

  @override
  Future<Either<Failure, Produit>> getProduitById(String id) async {
    try {
      final row = await (_db.select(_db.produits)
            ..where((p) => p.id.equals(id)))
          .getSingleOrNull();
      if (row == null) {
        return const Left(DatabaseFailure(message: 'Produit introuvable'));
      }
      return Right(_toEntity(row));
    } catch (e) {
      return Left(DatabaseFailure(message: 'Erreur lecture produit: $e'));
    }
  }

  @override
  Future<Either<Failure, Produit>> modifierProduit(Produit produit) async {
    try {
      final count = await (_db.update(_db.produits)
            ..where((p) => p.id.equals(produit.id)))
          .write(
        ProduitsCompanion(
          nom: Value(produit.nom),
          categorie: Value(produit.categorie.name),
          prixVente: Value(produit.prixVente),
          prixAchat: Value(produit.prixAchat),
          quantite: Value(produit.quantite),
          seuilAlerte: Value(produit.seuilAlerte),
          synced: Value(produit.synced),
          updatedAt: Value(produit.updatedAt),
        ),
      );
      if (count == 0) {
        return const Left(DatabaseFailure(message: 'Produit introuvable'));
      }
      return Right(produit);
    } catch (e) {
      return Left(DatabaseFailure(message: 'Erreur modification produit: $e'));
    }
  }

  @override
  Future<Either<Failure, Unit>> mettreAJourStock(String id, int delta) async {
    try {
      final row = await (_db.select(_db.produits)
            ..where((p) => p.id.equals(id)))
          .getSingleOrNull();
      if (row == null) {
        return const Left(DatabaseFailure(message: 'Produit introuvable'));
      }
      final nouvelleQuantite = (row.quantite + delta).clamp(0, 999999999);
      await (_db.update(_db.produits)..where((p) => p.id.equals(id))).write(
        ProduitsCompanion(
          quantite: Value(nouvelleQuantite),
          synced: const Value(false),
          updatedAt: Value(DateTime.now()),
        ),
      );
      return const Right(unit);
    } catch (e) {
      return Left(DatabaseFailure(message: 'Erreur mise à jour stock: $e'));
    }
  }

  @override
  Stream<List<Produit>> watchProduits(String boutiqueId) {
    final query = (_db.select(_db.produits)
      ..where((p) => p.boutiqueId.equals(boutiqueId))
      ..orderBy([(p) => OrderingTerm.asc(p.nom)]));
    return query.watch().map((rows) => rows.map(_toEntity).toList());
  }

  @override
  Stream<List<Produit>> watchProduitsEnAlerte(String boutiqueId) {
    return watchProduits(boutiqueId).map(
      (list) => list.where((p) => p.quantite <= p.seuilAlerte).toList(),
    );
  }

  @override
  Future<Either<Failure, Unit>> supprimerProduit(String id) async {
    try {
      await (_db.delete(_db.produits)..where((p) => p.id.equals(id))).go();
      return const Right(unit);
    } catch (e) {
      return Left(DatabaseFailure(message: 'Erreur suppression produit: $e'));
    }
  }

  @override
  Future<Either<Failure, List<Produit>>> searchProduits(
      String bId, String q) async {
    final query = q.toLowerCase().trim();
    try {
      final rows = await (_db.select(_db.produits)
            ..where((p) => p.boutiqueId.equals(bId)))
          .get();
      final items = rows
          .map(_toEntity)
          .where((p) => p.nom.toLowerCase().contains(query))
          .toList();
      return Right(items);
    } catch (e) {
      return Left(DatabaseFailure(message: 'Erreur recherche produit: $e'));
    }
  }
}

@LazySingleton(as: ClientRepository)
class ClientRepositoryImpl implements ClientRepository {
  final InMemoryStore _store;

  ClientRepositoryImpl(this._store) {
    _store.seedIfNeeded();
  }

  @override
  Future<Either<Failure, Client>> ajouterClient(Client client) async {
    _store.clients.add(client);
    _store.emitAll();
    return Right(client);
  }

  @override
  Future<Either<Failure, Client>> getClientById(String id) async {
    try {
      return Right(_store.clients.firstWhere((c) => c.id == id));
    } catch (_) {
      return const Left(DatabaseFailure(message: 'Client introuvable'));
    }
  }

  @override
  Future<Either<Failure, Client>> modifierClient(Client client) async {
    final index = _store.clients.indexWhere((c) => c.id == client.id);
    if (index == -1)
      return const Left(DatabaseFailure(message: 'Client introuvable'));
    _store.clients[index] = client;
    _store.emitAll();
    return Right(client);
  }

  @override
  Future<Either<Failure, Unit>> recalculerScore(String clientId) async {
    return const Right(unit);
  }

  @override
  Future<Either<Failure, List<Client>>> searchClients(
      String boutiqueId, String query) async {
    final q = query.toLowerCase();
    return Right(
      _store.clients
          .where((c) => c.boutiqueId == boutiqueId)
          .where((c) =>
              c.nom.toLowerCase().contains(q) ||
              (c.telephone?.contains(query) ?? false))
          .toList(),
    );
  }

  @override
  Stream<List<Client>> watchClients(String boutiqueId) {
    return _store.withInitial(_store.clients, _store.clientsCtrl.stream).map(
          (items) => items.where((c) => c.boutiqueId == boutiqueId).toList(),
        );
  }
}

@LazySingleton(as: VenteRepository)
class VenteRepositoryImpl implements VenteRepository {
  final InMemoryStore _store;

  VenteRepositoryImpl(this._store) {
    _store.seedIfNeeded();
  }

  @override
  Future<Either<Failure, Vente>> enregistrerVente(Vente vente) async {
    _store.ventes.add(vente);
    _store.emitAll();
    return Right(vente);
  }

  @override
  Future<Either<Failure, int>> getTotalVentesJour(String boutiqueId) async {
    final today = DateTime.now();
    final total = _store.ventes
        .where((v) => v.boutiqueId == boutiqueId)
        .where((v) =>
            v.date.year == today.year &&
            v.date.month == today.month &&
            v.date.day == today.day)
        .fold<int>(0, (sum, v) => sum + v.montantTotal);
    return Right(total);
  }

  @override
  Future<Either<Failure, List<Vente>>> getVentesParJour(
      String boutiqueId, DateTime date) async {
    final ventes = _store.ventes
        .where((v) => v.boutiqueId == boutiqueId)
        .where((v) =>
            v.date.year == date.year &&
            v.date.month == date.month &&
            v.date.day == date.day)
        .toList();
    return Right(ventes);
  }

  @override
  Future<Either<Failure, List<Vente>>> getVentesParPeriode(
      String boutiqueId, DateTime debut, DateTime fin) async {
    final ventes = _store.ventes
        .where((v) => v.boutiqueId == boutiqueId)
        .where((v) => !v.date.isBefore(debut) && !v.date.isAfter(fin))
        .toList();
    return Right(ventes);
  }

  @override
  Stream<List<Vente>> watchVentes(String boutiqueId) {
    return _store.withInitial(_store.ventes, _store.ventesCtrl.stream).map(
          (items) => items.where((v) => v.boutiqueId == boutiqueId).toList(),
        );
  }
}

@LazySingleton(as: DetteRepository)
class DetteRepositoryImpl implements DetteRepository {
  final InMemoryStore _store;

  DetteRepositoryImpl(this._store) {
    _store.seedIfNeeded();
  }

  @override
  Future<Either<Failure, Dette>> enregistrerDette(Dette dette) async {
    _store.dettes.add(dette);
    _store.emitAll();
    return Right(dette);
  }

  @override
  Future<Either<Failure, Dette>> enregistrerPaiement(
      {required String detteId,
      required int montant,
      required String modePaiement}) async {
    final index = _store.dettes.indexWhere((d) => d.id == detteId);
    if (index == -1)
      return const Left(DatabaseFailure(message: 'Dette introuvable'));

    final current = _store.dettes[index];
    final nouveauPaye =
        (current.montantPaye + montant).clamp(0, current.montant);
    final statut = switch (nouveauPaye) {
      0 => StatutDette.nonPaye,
      _ when nouveauPaye >= current.montant => StatutDette.paye,
      _ => StatutDette.partiel,
    };

    final updated = Dette(
      id: current.id,
      clientId: current.clientId,
      venteId: current.venteId,
      boutiqueId: current.boutiqueId,
      nomClient: current.nomClient,
      montant: current.montant,
      montantPaye: nouveauPaye,
      statut: statut,
      dateEcheance: current.dateEcheance,
      synced: false,
      createdAt: current.createdAt,
      updatedAt: DateTime.now(),
    );

    _store.dettes[index] = updated;
    _store.emitAll();
    return Right(updated);
  }

  @override
  Future<Either<Failure, Dette>> getDetteById(String id) async {
    try {
      return Right(_store.dettes.firstWhere((d) => d.id == id));
    } catch (_) {
      return const Left(DatabaseFailure(message: 'Dette introuvable'));
    }
  }

  @override
  Future<Either<Failure, List<Dette>>> getDettesEchues(
      String boutiqueId) async {
    return Right(
      _store.dettes
          .where((d) => d.boutiqueId == boutiqueId && d.estEchue)
          .toList(),
    );
  }

  @override
  Future<Either<Failure, int>> getTotalDettesActives(String boutiqueId) async {
    final total = _store.dettes
        .where(
            (d) => d.boutiqueId == boutiqueId && d.statut != StatutDette.paye)
        .fold<int>(0, (sum, d) => sum + d.montantRestant);
    return Right(total);
  }

  @override
  Stream<List<Dette>> watchDettes(String boutiqueId) {
    return _store.withInitial(_store.dettes, _store.dettesCtrl.stream).map(
          (items) => items.where((d) => d.boutiqueId == boutiqueId).toList(),
        );
  }

  @override
  Stream<List<Dette>> watchDettesClient(String clientId) {
    return _store.withInitial(_store.dettes, _store.dettesCtrl.stream).map(
          (items) => items.where((d) => d.clientId == clientId).toList(),
        );
  }
}

@LazySingleton(as: AuthRepository)
class AuthRepositoryImpl implements AuthRepository {
  final AppDatabase _db;
  final SyncRepository _syncRepository;

  AuthRepositoryImpl(this._db, this._syncRepository);

  bool _sessionActive = false;
  String? _activeBoutiqueId;

  @override
  Future<Either<Failure, Unit>> changerPin(
      String boutiqueId, String ancienPin, String nouveauPin) async {
    return const Right(unit);
  }

  @override
  Future<Either<Failure, Unit>> creerCompte({
    required String nom,
    required String role,
    required String prenom,
    required String telephone,
    required String motDePasse,
    required String boutiqueNom,
    required String boutiqueAdresse,
  }) async {
    if (nom.trim().isEmpty ||
        prenom.trim().isEmpty ||
        telephone.trim().isEmpty ||
        motDePasse.trim().isEmpty ||
        boutiqueNom.trim().isEmpty ||
        boutiqueAdresse.trim().isEmpty) {
      return const Left(AuthFailure(message: 'Informations invalides'));
    }

    if (role != 'admin' && role != 'employe') {
      return const Left(AuthFailure(message: 'Rôle invalide'));
    }

    if (motDePasse.trim().length != 4) {
      return const Left(
          AuthFailure(message: 'Le code PIN doit avoir 4 chiffres'));
    }

    try {
      final utilisateurId = _uuid.v4();
      final boutiqueId = _uuid.v4();

      await _db.transaction(() async {
        await _db.into(_db.boutiques).insert(
              BoutiquesCompanion.insert(
                id: boutiqueId,
                nom: boutiqueNom.trim(),
                adresse: Value(boutiqueAdresse.trim()),
                telephone: telephone.trim(),
              ),
            );

        await _db.into(_db.utilisateurs).insert(
              UtilisateursCompanion.insert(
                id: utilisateurId,
                boutiqueId: boutiqueId,
                nom: '${nom.trim()} ${prenom.trim()}',
                role: Value(role),
                motDePasse: motDePasse.trim(),
                pinHash: Value(motDePasse.trim()),
              ),
            );
      });
      await _syncRepository.synchroniser(boutiqueId);
      _sessionActive = true;
      _activeBoutiqueId = boutiqueId;
      return const Right(unit);
    } catch (e) {
      return Left(AuthFailure(message: 'Erreur: ${e.toString()}'));
    }
  }

  @override
  Future<void> deconnecter() async {
    _sessionActive = false;
    _activeBoutiqueId = null;
  }

  @override
  Future<bool> estConnecte() async => _sessionActive;

  @override
  Future<Either<Failure, Unit>> seConnecter({
    required String identifiant,
    required String motDePasse,
  }) async {
    try {
      final utilisateur = await (_db.select(_db.utilisateurs)
            ..where((u) => u.nom.equals(identifiant.trim()))
            ..limit(1))
          .getSingleOrNull();

      if (utilisateur == null || utilisateur.motDePasse != motDePasse.trim()) {
        return const Left(AuthFailure(message: 'Identifiants invalides'));
      }

      _sessionActive = true;
      _activeBoutiqueId = utilisateur.boutiqueId;
      return const Right(unit);
    } catch (e) {
      return Left(AuthFailure(message: 'Erreur: ${e.toString()}'));
    }
  }

  @override
  Future<Either<Failure, String>> getBoutiqueId() async {
    if (_activeBoutiqueId != null && _activeBoutiqueId!.isNotEmpty) {
      return Right(_activeBoutiqueId!);
    }

    try {
      final boutique = await (_db.select(_db.boutiques)
            ..orderBy([(b) => OrderingTerm.desc(b.createdAt)])
            ..limit(1))
          .getSingleOrNull();

      if (boutique == null) {
        return const Left(AuthFailure(message: 'Aucune boutique enregistrée'));
      }

      return Right(boutique.id);
    } catch (e) {
      return Left(AuthFailure(message: 'Erreur: ${e.toString()}'));
    }
  }

  @override
  Future<Either<Failure, bool>> verifierPin(
      String boutiqueId, String pin) async {
    try {
      final utilisateur = await (_db.select(_db.utilisateurs)
            ..where((u) => u.boutiqueId.equals(boutiqueId))
            ..limit(1))
          .getSingleOrNull();

      if (utilisateur == null) {
        return const Left(AuthFailure(message: 'Boutique inconnue'));
      }

      return Right(utilisateur.pinHash == pin.trim());
    } catch (e) {
      return Left(AuthFailure(message: 'Erreur: ${e.toString()}'));
    }
  }
}

@LazySingleton(as: SyncRepository)
class SyncRepositoryImpl implements SyncRepository {
  final AppDatabase _db;
  final SupabaseSyncService _supabaseSyncService;

  SyncRepositoryImpl(this._db, this._supabaseSyncService);
  int _pending = 0;
  final StreamController<SyncStatus> _statusCtrl =
      StreamController<SyncStatus>.broadcast();

  @override
  Future<int> getNombreElementsNonSynces() async {
    final produits = await (_db.select(_db.produits)
          ..where((t) => t.synced.equals(false)))
        .get();
    final clients = await (_db.select(_db.clients)
          ..where((t) => t.synced.equals(false)))
        .get();
    final ventes = await (_db.select(_db.ventes)
          ..where((t) => t.synced.equals(false)))
        .get();
    final dettes = await (_db.select(_db.dettes)
          ..where((t) => t.synced.equals(false)))
        .get();
    final paiements = await (_db.select(_db.paiements)
          ..where((t) => t.synced.equals(false)))
        .get();
    _pending = produits.length +
        clients.length +
        ventes.length +
        dettes.length +
        paiements.length;
    return _pending;
  }

  @override
  Future<Either<Failure, Unit>> synchroniser(String boutiqueId) async {
    try {
      _statusCtrl.add(SyncStatus.syncing);

      final boutiques = await (_db.select(_db.boutiques)
            ..where((b) => b.id.equals(boutiqueId)))
          .get();
      final utilisateurs = await (_db.select(_db.utilisateurs)
            ..where((u) => u.boutiqueId.equals(boutiqueId)))
          .get();
      final produits = await (_db.select(_db.produits)
            ..where((t) => t.boutiqueId.equals(boutiqueId)))
          .get();
      final clients = await (_db.select(_db.clients)
            ..where((t) => t.boutiqueId.equals(boutiqueId)))
          .get();
      final ventes = await (_db.select(_db.ventes)
            ..where((t) => t.boutiqueId.equals(boutiqueId)))
          .get();
      final dettes = await (_db.select(_db.dettes)
            ..where((t) => t.boutiqueId.equals(boutiqueId)))
          .get();
      final paiements = await (_db.select(_db.paiements)
            ..where((t) => t.boutiqueId.equals(boutiqueId)))
          .get();
      final abonnements = await (_db.select(_db.abonnements)
            ..where((t) => t.boutiqueId.equals(boutiqueId)))
          .get();

      await _supabaseSyncService.upsertBatch(
        table: 'boutiques',
        rows: boutiques
            .map((b) => {
                  'id': b.id,
                  'nom': b.nom,
                  'adresse': b.adresse,
                  'telephone': b.telephone,
                  'created_at': b.createdAt.toIso8601String()
                })
            .toList(),
      );
      await _supabaseSyncService.upsertBatch(
        table: 'utilisateurs',
        rows: utilisateurs
            .map((u) => {
                  'id': u.id,
                  'boutique_id': u.boutiqueId,
                  'nom': u.nom,
                  'role': u.role,
                  'mot_de_passe': u.motDePasse,
                  'pin_hash': u.pinHash,
                  'created_at': u.createdAt.toIso8601String(),
                })
            .toList(),
      );
      await _supabaseSyncService.upsertBatch(
        table: 'produits',
        rows: produits
            .map((p) => {
                  'id': p.id,
                  'boutique_id': p.boutiqueId,
                  'nom': p.nom,
                  'categorie': p.categorie,
                  'prix_vente': p.prixVente,
                  'prix_achat': p.prixAchat,
                  'quantite': p.quantite,
                  'seuil_alerte': p.seuilAlerte,
                  'synced': true,
                  'updated_at': p.updatedAt.toIso8601String(),
                })
            .toList(),
      );
      await _supabaseSyncService.upsertBatch(
        table: 'clients',
        rows: clients
            .map((c) => {
                  'id': c.id,
                  'boutique_id': c.boutiqueId,
                  'nom': c.nom,
                  'telephone': c.telephone,
                  'score': c.score,
                  'total_du': c.totalDu,
                  'nombre_dettes': c.nombreDettes,
                  'nombres_remboursements': c.nombresRemboursements,
                  'synced': true,
                  'created_at': c.createdAt.toIso8601String(),
                })
            .toList(),
      );
      await _supabaseSyncService.upsertBatch(
        table: 'ventes',
        rows: ventes
            .map((v) => {
                  'id': v.id,
                  'boutique_id': v.boutiqueId,
                  'produit_id': v.produitId,
                  'client_id': v.clientId,
                  'utilisateur_id': v.utilisateurId,
                  'quantite': v.quantite,
                  'prix_unitaire': v.prixUnitaire,
                  'montant_total': v.montantTotal,
                  'type_paiement': v.typePaiement,
                  'source': v.source,
                  'synced': true,
                  'date': v.date.toIso8601String(),
                })
            .toList(),
      );
      await _supabaseSyncService.upsertBatch(
        table: 'dettes',
        rows: dettes
            .map((d) => {
                  'id': d.id,
                  'client_id': d.clientId,
                  'vente_id': d.venteId,
                  'boutique_id': d.boutiqueId,
                  'montant': d.montant,
                  'montant_paye': d.montantPaye,
                  'statut': d.statut,
                  'date_echeance': d.dateEcheance?.toIso8601String(),
                  'rappel1_jour_envoye': d.rappel1JourEnvoye,
                  'rappel3_jours_envoye': d.rappel3JoursEnvoye,
                  'rappel7_jours_envoye': d.rappel7JoursEnvoye,
                  'synced': true,
                  'created_at': d.createdAt.toIso8601String(),
                  'updated_at': d.updatedAt.toIso8601String(),
                })
            .toList(),
      );
      await _supabaseSyncService.upsertBatch(
        table: 'paiements',
        rows: paiements
            .map((p) => {
                  'id': p.id,
                  'dette_id': p.detteId,
                  'boutique_id': p.boutiqueId,
                  'montant': p.montant,
                  'mode_paiement': p.modePaiement,
                  'synced': true,
                  'date': p.date.toIso8601String(),
                })
            .toList(),
      );
      await _supabaseSyncService.upsertBatch(
        table: 'abonnements',
        rows: abonnements
            .map((a) => {
                  'id': a.id,
                  'boutique_id': a.boutiqueId,
                  'plan': a.plan,
                  'statut': a.statut,
                  'mode_paiement': a.modePaiement,
                  'montant': a.montant,
                  'date_debut': a.dateDebut.toIso8601String(),
                  'date_fin': a.dateFin?.toIso8601String(),
                  'synced': true,
                })
            .toList(),
      );

      await (_db.update(_db.produits)
            ..where((t) => t.boutiqueId.equals(boutiqueId)))
          .write(const ProduitsCompanion(synced: Value(true)));
      await (_db.update(_db.clients)
            ..where((t) => t.boutiqueId.equals(boutiqueId)))
          .write(const ClientsCompanion(synced: Value(true)));
      await (_db.update(_db.ventes)
            ..where((t) => t.boutiqueId.equals(boutiqueId)))
          .write(const VentesCompanion(synced: Value(true)));
      await (_db.update(_db.dettes)
            ..where((t) => t.boutiqueId.equals(boutiqueId)))
          .write(const DettesCompanion(synced: Value(true)));
      await (_db.update(_db.paiements)
            ..where((t) => t.boutiqueId.equals(boutiqueId)))
          .write(const PaiementsCompanion(synced: Value(true)));

      _pending = await getNombreElementsNonSynces();
      _statusCtrl.add(SyncStatus.success);
      return const Right(unit);
    } on PostgrestException catch (e) {
      _statusCtrl.add(SyncStatus.error);
      return Left(SyncFailure(message: e.message));
    } catch (e) {
      _statusCtrl.add(SyncStatus.error);
      return Left(SyncFailure(message: e.toString()));
    }
  }

  @override
  Stream<SyncStatus> watchSyncStatus() => _statusCtrl.stream;
}

@LazySingleton(as: AbonnementRepository)
class AbonnementRepositoryImpl implements AbonnementRepository {
  @override
  Future<Either<Failure, Abonnement>> getAbonnement(String boutiqueId) async {
    return Right(
      Abonnement(
        id: 'abonnement-demo',
        boutiqueId: boutiqueId,
        plan: PlanAbonnement.gratuit,
        statut: StatutAbonnement.actif,
        montant: 0,
        dateDebut: DateTime.now().subtract(const Duration(days: 10)),
      ),
    );
  }

  @override
  Future<Either<Failure, Abonnement>> souscrire(
      {required String boutiqueId,
      required PlanAbonnement plan,
      required ModePaiementAbonnement modePaiement}) async {
    return Right(
      Abonnement(
        id: 'abonnement-${DateTime.now().millisecondsSinceEpoch}',
        boutiqueId: boutiqueId,
        plan: plan,
        statut: StatutAbonnement.actif,
        modePaiement: modePaiement,
        montant: plan == PlanAbonnement.gratuit ? 0 : 100000,
        dateDebut: DateTime.now(),
      ),
    );
  }

  @override
  Future<Either<Failure, bool>> verifierLimites(
      {required String boutiqueId, required String typeRessource}) async {
    return const Right(true);
  }
}
