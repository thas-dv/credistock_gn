import 'dart:async';

import 'package:dartz/dartz.dart';
import 'package:injectable/injectable.dart';

import '../../core/errors/failures.dart';
import '../../domain/entities/entities.dart';
import '../../domain/repositories/repositories.dart';

@lazySingleton
class InMemoryStore {
  final List<Produit> produits = [];
  final List<Client> clients = [];
  final List<Vente> ventes = [];
  final List<Dette> dettes = [];

  final StreamController<List<Produit>> produitsCtrl =
      StreamController<List<Produit>>.broadcast();
  final StreamController<List<Client>> clientsCtrl =
      StreamController<List<Client>>.broadcast();
  final StreamController<List<Vente>> ventesCtrl =
      StreamController<List<Vente>>.broadcast();
  final StreamController<List<Dette>> dettesCtrl =
      StreamController<List<Dette>>.broadcast();

  void seedIfNeeded() {
    if (produits.isNotEmpty) return;

    final now = DateTime.now();
    final boutiqueId = 'demo-boutique';

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
      Produit(
        id: 'p2',
        boutiqueId: boutiqueId,
        nom: 'Huile 5L',
        categorie: CategorieProduit.alimentaire,
        prixVente: 185000,
        prixAchat: 160000,
        quantite: 7,
        seuilAlerte: 4,
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

    produitsCtrl.add(List.unmodifiable(produits));
    clientsCtrl.add(List.unmodifiable(clients));
    ventesCtrl.add(List.unmodifiable(ventes));
    dettesCtrl.add(List.unmodifiable(dettes));
  }

  void emitAll() {
    produitsCtrl.add(List.unmodifiable(produits));
    clientsCtrl.add(List.unmodifiable(clients));
    ventesCtrl.add(List.unmodifiable(ventes));
    dettesCtrl.add(List.unmodifiable(dettes));
  }
}

@LazySingleton(as: ProduitRepository)
class ProduitRepositoryImpl implements ProduitRepository {
  final InMemoryStore _store;

  ProduitRepositoryImpl(this._store) {
    _store.seedIfNeeded();
  }

  @override
  Future<Either<Failure, Produit>> ajouterProduit(Produit produit) async {
    _store.produits.add(produit);
    _store.emitAll();
    return Right(produit);
  }

  @override
  Future<Either<Failure, Produit>> getProduitById(String id) async {
    try {
      return Right(_store.produits.firstWhere((p) => p.id == id));
    } catch (_) {
      return const Left(DatabaseFailure(message: 'Produit introuvable'));
    }
  }

  @override
  Future<Either<Failure, Produit>> modifierProduit(Produit produit) async {
    final index = _store.produits.indexWhere((p) => p.id == produit.id);
    if (index == -1) return const Left(DatabaseFailure(message: 'Produit introuvable'));
    _store.produits[index] = produit;
    _store.emitAll();
    return Right(produit);
  }

  @override
  Future<Either<Failure, Unit>> mettreAJourStock(String produitId, int deltaQuantite) async {
    final index = _store.produits.indexWhere((p) => p.id == produitId);
    if (index == -1) return const Left(DatabaseFailure(message: 'Produit introuvable'));
    final produit = _store.produits[index];
    _store.produits[index] = produit.copyWith(
      quantite: (produit.quantite + deltaQuantite).clamp(0, 1 << 31),
      synced: false,
    );
    _store.emitAll();
    return const Right(unit);
  }

  @override
  Future<Either<Failure, List<Produit>>> searchProduits(String boutiqueId, String query) async {
    final q = query.toLowerCase();
    return Right(
      _store.produits
          .where((p) => p.boutiqueId == boutiqueId)
          .where((p) => p.nom.toLowerCase().contains(q))
          .toList(),
    );
  }

  @override
  Future<Either<Failure, Unit>> supprimerProduit(String id) async {
    _store.produits.removeWhere((p) => p.id == id);
    _store.emitAll();
    return const Right(unit);
  }

  @override
  Stream<List<Produit>> watchProduits(String boutiqueId) {
    return _store.produitsCtrl.stream.map(
      (items) => items.where((p) => p.boutiqueId == boutiqueId).toList(),
    );
  }

  @override
  Stream<List<Produit>> watchProduitsEnAlerte(String boutiqueId) {
    return watchProduits(boutiqueId)
        .map((produits) => produits.where((p) => p.estEnAlerteStock).toList());
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
    if (index == -1) return const Left(DatabaseFailure(message: 'Client introuvable'));
    _store.clients[index] = client;
    _store.emitAll();
    return Right(client);
  }

  @override
  Future<Either<Failure, Unit>> recalculerScore(String clientId) async {
    return const Right(unit);
  }

  @override
  Future<Either<Failure, List<Client>>> searchClients(String boutiqueId, String query) async {
    final q = query.toLowerCase();
    return Right(
      _store.clients
          .where((c) => c.boutiqueId == boutiqueId)
          .where((c) => c.nom.toLowerCase().contains(q) || (c.telephone?.contains(query) ?? false))
          .toList(),
    );
  }

  @override
  Stream<List<Client>> watchClients(String boutiqueId) {
    return _store.clientsCtrl.stream.map(
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
        .where((v) => v.date.year == today.year && v.date.month == today.month && v.date.day == today.day)
        .fold<int>(0, (sum, v) => sum + v.montantTotal);
    return Right(total);
  }

  @override
  Future<Either<Failure, List<Vente>>> getVentesParJour(String boutiqueId, DateTime date) async {
    final ventes = _store.ventes
        .where((v) => v.boutiqueId == boutiqueId)
        .where((v) => v.date.year == date.year && v.date.month == date.month && v.date.day == date.day)
        .toList();
    return Right(ventes);
  }

  @override
  Future<Either<Failure, List<Vente>>> getVentesParPeriode(String boutiqueId, DateTime debut, DateTime fin) async {
    final ventes = _store.ventes
        .where((v) => v.boutiqueId == boutiqueId)
        .where((v) => !v.date.isBefore(debut) && !v.date.isAfter(fin))
        .toList();
    return Right(ventes);
  }

  @override
  Stream<List<Vente>> watchVentes(String boutiqueId) {
    return _store.ventesCtrl.stream.map(
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
  Future<Either<Failure, Dette>> enregistrerPaiement({required String detteId, required int montant, required String modePaiement}) async {
    final index = _store.dettes.indexWhere((d) => d.id == detteId);
    if (index == -1) return const Left(DatabaseFailure(message: 'Dette introuvable'));

    final current = _store.dettes[index];
    final nouveauPaye = (current.montantPaye + montant).clamp(0, current.montant);
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
  Future<Either<Failure, List<Dette>>> getDettesEchues(String boutiqueId) async {
    return Right(
      _store.dettes.where((d) => d.boutiqueId == boutiqueId && d.estEchue).toList(),
    );
  }

  @override
  Future<Either<Failure, int>> getTotalDettesActives(String boutiqueId) async {
    final total = _store.dettes
        .where((d) => d.boutiqueId == boutiqueId && d.statut != StatutDette.paye)
        .fold<int>(0, (sum, d) => sum + d.montantRestant);
    return Right(total);
  }

  @override
  Stream<List<Dette>> watchDettes(String boutiqueId) {
    return _store.dettesCtrl.stream.map(
      (items) => items.where((d) => d.boutiqueId == boutiqueId).toList(),
    );
  }

  @override
  Stream<List<Dette>> watchDettesClient(String clientId) {
    return _store.dettesCtrl.stream.map(
      (items) => items.where((d) => d.clientId == clientId).toList(),
    );
  }
}

@LazySingleton(as: AuthRepository)
class AuthRepositoryImpl implements AuthRepository {
  String? _boutiqueId = 'demo-boutique';
  static const _pin = '0000';

final Map<String, String> _comptes = {
    'admin': 'admin1234',
  };
  final Map<String, Map<String, String>> _utilisateurs = {};
  bool _sessionActive = false;
  @override
  Future<Either<Failure, Unit>> changerPin(String boutiqueId, String ancienPin, String nouveauPin) async {
    return const Right(unit);
  }

  @override
  Future<Either<Failure, Unit>> creerCompte({
    required String identifiant,
    required String motDePasse,
    required String boutiqueId,
    required String nom,
    required String role,
  }) async {
   if (identifiant.trim().isEmpty ||
        motDePasse.trim().isEmpty ||
        boutiqueId.trim().isEmpty ||
        nom.trim().isEmpty) {
      return const Left(AuthFailure(message: 'Informations invalides'));
    }
     if (role != 'admin' && role != 'employe') {
      return const Left(AuthFailure(message: 'Rôle invalide'));
    }
    if (_comptes.containsKey(identifiant.trim())) {
      return const Left(AuthFailure(message: 'Ce compte existe déjà'));
    }

    _comptes[identifiant.trim()] = motDePasse.trim();
    _utilisateurs[identifiant.trim()] = {
      'id': identifiant.trim(),
      'boutique_id': boutiqueId.trim(),
      'nom': nom.trim(),
      'role': role,
      'mot_de_passe': motDePasse.trim(),
    };
    _boutiqueId = boutiqueId.trim();
    _sessionActive = true;
    return const Right(unit);
  }

  @override
  Future<void> deconnecter() async {
    _sessionActive = false;
  }

  @override
  Future<bool> estConnecte() async => _sessionActive;

 @override
  Future<Either<Failure, Unit>> seConnecter({
    required String identifiant,
    required String motDePasse,
  }) async {
    final existing = _comptes[identifiant.trim()];
    if (existing == null || existing != motDePasse.trim()) {
      return const Left(AuthFailure(message: 'Identifiants invalides'));
    }

    _sessionActive = true;
    return const Right(unit);
  }

  @override
  Future<Either<Failure, String>> getBoutiqueId() async {
    if (_boutiqueId == null) return const Left(AuthFailure());
    return Right(_boutiqueId!);
  }

  @override
  Future<Either<Failure, bool>> verifierPin(String boutiqueId, String pin) async {
    if (boutiqueId != _boutiqueId) return const Left(AuthFailure(message: 'Boutique inconnue'));
    return Right(pin == _pin);
  }
}

@LazySingleton(as: SyncRepository)
class SyncRepositoryImpl implements SyncRepository {
  int _pending = 0;
  final StreamController<SyncStatus> _statusCtrl =
      StreamController<SyncStatus>.broadcast();

  @override
  Future<int> getNombreElementsNonSynces() async => _pending;

  @override
  Future<Either<Failure, Unit>> synchroniser(String boutiqueId) async {
    _statusCtrl.add(SyncStatus.syncing);
    _pending = 0;
    _statusCtrl.add(SyncStatus.success);
    return const Right(unit);
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
  Future<Either<Failure, Abonnement>> souscrire({required String boutiqueId, required PlanAbonnement plan, required ModePaiementAbonnement modePaiement}) async {
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
  Future<Either<Failure, bool>> verifierLimites({required String boutiqueId, required String typeRessource}) async {
    return const Right(true);
  }
}