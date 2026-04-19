import 'dart:async';

import 'package:dartz/dartz.dart';
import 'package:drift/drift.dart';
import 'package:injectable/injectable.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import 'package:hive_flutter/hive_flutter.dart';
import '../../core/errors/failures.dart';
import '../../core/services/supabase_sync_service.dart';
import '../local/database/app_database.dart'
    hide Produit, Client, Dette, Vente, Abonnement;
import '../../domain/entities/entities.dart';
import '../../domain/repositories/repositories.dart';
import 'package:uuid/uuid.dart';

const _uuid = Uuid();
const _sessionBoxName = 'auth_session';
const _kSessionActive = 'active';
const _kBoutiqueId = 'boutique_id';

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
  final AppDatabase _db;

  ClientRepositoryImpl(this._db);

  Client _toEntity(dynamic row) {
    return Client(
      id: row.id,
      boutiqueId: row.boutiqueId,
      nom: row.nom,
      telephone: row.telephone,
      score: ScoreClient.values.firstWhere(
        (s) => s.name == row.score,
        orElse: () => ScoreClient.bon,
      ),
      totalDu: row.totalDu,
      nombreDettes: row.nombreDettes,
      nombresRemboursements: row.nombresRemboursements,
      synced: row.synced,
      createdAt: row.createdAt,
    );
  }

  @override
  Future<Either<Failure, Client>> ajouterClient(Client client) async {
    try {
      await _db.into(_db.clients).insert(
            ClientsCompanion.insert(
              id: client.id,
              boutiqueId: client.boutiqueId,
              nom: client.nom,
              telephone: Value(client.telephone),
              score: Value(client.score.name),
              totalDu: Value(client.totalDu),
              nombreDettes: Value(client.nombreDettes),
              nombresRemboursements: Value(client.nombresRemboursements),
              synced: Value(client.synced),
              createdAt: Value(client.createdAt),
            ),
          );
      return Right(client);
    } catch (e) {
      return Left(DatabaseFailure(message: 'Erreur ajout client: $e'));
    }
  }

  @override
  Future<Either<Failure, Client>> getClientById(String id) async {
    try {
      final row = await (_db.select(_db.clients)..where((c) => c.id.equals(id)))
          .getSingleOrNull();
      if (row == null) {
        return const Left(DatabaseFailure(message: 'Client introuvable'));
      }
      return Right(_toEntity(row));
    } catch (e) {
      return Left(DatabaseFailure(message: 'Erreur lecture client: $e'));
    }
  }

  @override
  Future<Either<Failure, Client>> modifierClient(Client client) async {
    try {
      final count = await (_db.update(_db.clients)
            ..where((c) => c.id.equals(client.id)))
          .write(
        ClientsCompanion(
          nom: Value(client.nom),
          telephone: Value(client.telephone),
          score: Value(client.score.name),
          totalDu: Value(client.totalDu),
          nombreDettes: Value(client.nombreDettes),
          nombresRemboursements: Value(client.nombresRemboursements),
          synced: Value(client.synced),
        ),
      );
      if (count == 0) {
        return const Left(DatabaseFailure(message: 'Client introuvable'));
      }
      return Right(client);
    } catch (e) {
      return Left(DatabaseFailure(message: 'Erreur modification client: $e'));
    }
  }

  @override
  Future<Either<Failure, Unit>> recalculerScore(String clientId) async {
    try {
      final clientRow = await (_db.select(_db.clients)
            ..where((c) => c.id.equals(clientId)))
          .getSingleOrNull();
      if (clientRow == null) {
        return const Left(DatabaseFailure(message: 'Client introuvable'));
      }

      final dettesRows = await (_db.select(_db.dettes)
            ..where((d) => d.clientId.equals(clientId)))
          .get();

      final nombreDettes = dettesRows.length;
      final totalDu = dettesRows.fold<int>(0, (sum, d) {
        final restant = (d.montant - d.montantPaye).clamp(0, d.montant);
        return sum + restant;
      });
      final remboursements = dettesRows.where((d) => d.statut == 'paye').length;

      ScoreClient score;
      if (totalDu == 0) {
        score = ScoreClient.bon;
      } else if (nombreDettes <= 2) {
        score = ScoreClient.moyen;
      } else {
        score = ScoreClient.mauvais;
      }

      await (_db.update(_db.clients)..where((c) => c.id.equals(clientId)))
          .write(
        ClientsCompanion(
          totalDu: Value(totalDu),
          nombreDettes: Value(nombreDettes),
          nombresRemboursements: Value(remboursements),
          score: Value(score.name),
          synced: const Value(false),
        ),
      );
      return const Right(unit);
    } catch (e) {
      return Left(DatabaseFailure(message: 'Erreur score client: $e'));
    }
  }

  @override
  Future<Either<Failure, List<Client>>> searchClients(
      String boutiqueId, String query) async {
    final q = query.toLowerCase().trim();
    try {
      final rows = await (_db.select(_db.clients)
            ..where((c) => c.boutiqueId.equals(boutiqueId)))
          .get();
      final items = rows
          .map(_toEntity)
          .where((c) =>
              c.nom.toLowerCase().contains(q) ||
              (c.telephone?.contains(query) ?? false))
          .toList();
      return Right(items);
    } catch (e) {
      return Left(DatabaseFailure(message: 'Erreur recherche client: $e'));
    }
  }

  @override
  Stream<List<Client>> watchClients(String boutiqueId) {
    final query = (_db.select(_db.clients)
      ..where((c) => c.boutiqueId.equals(boutiqueId))
      ..orderBy([(c) => OrderingTerm.asc(c.nom)]));
    return query.watch().map((rows) => rows.map(_toEntity).toList());
  }
}

@LazySingleton(as: VenteRepository)
class VenteRepositoryImpl implements VenteRepository {
  final AppDatabase _db;

  VenteRepositoryImpl(this._db);

  TypePaiement _toTypePaiement(String value) {
    return TypePaiement.values.firstWhere(
      (t) => t.name == value,
      orElse: () => TypePaiement.cash,
    );
  }

  SourceVente _toSource(String value) {
    return SourceVente.values.firstWhere(
      (s) => s.name == value,
      orElse: () => SourceVente.manuel,
    );
  }

  Vente _toEntity(dynamic row, {required String nomProduit}) {
    return Vente(
      id: row.id,
      boutiqueId: row.boutiqueId,
      produitId: row.produitId,
      clientId: row.clientId,
      utilisateurId: row.utilisateurId,
      nomProduit: nomProduit,
      quantite: row.quantite,
      prixUnitaire: row.prixUnitaire,
      montantTotal: row.montantTotal,
      typePaiement: _toTypePaiement(row.typePaiement),
      source: _toSource(row.source),
      synced: row.synced,
      date: row.date,
    );
  }

  @override
  Future<Either<Failure, Vente>> enregistrerVente(Vente vente) async {
    try {
      await _db.into(_db.ventes).insert(
            VentesCompanion.insert(
              id: vente.id,
              boutiqueId: vente.boutiqueId,
              produitId: vente.produitId,
              clientId: Value(vente.clientId),
              utilisateurId: vente.utilisateurId,
              quantite: vente.quantite,
              prixUnitaire: vente.prixUnitaire,
              montantTotal: vente.montantTotal,
              typePaiement: vente.typePaiement.name,
              source: Value(vente.source.name),
              synced: Value(vente.synced),
              date: Value(vente.date),
            ),
          );
      return Right(vente);
    } catch (e) {
      return Left(DatabaseFailure(message: 'Erreur enregistrement vente: $e'));
    }
  }

  @override
  Future<Either<Failure, int>> getTotalVentesJour(String boutiqueId) async {
    try {
      final today = DateTime.now();
      final ventes = await getVentesParJour(boutiqueId, today);
      return ventes.fold((l) => Left(l), (list) {
        final total = list.fold<int>(0, (sum, v) => sum + v.montantTotal);
        return Right(total);
      });
    } catch (e) {
      return Left(DatabaseFailure(message: 'Erreur total ventes jour: $e'));
    }
  }

  @override
  Future<Either<Failure, List<Vente>>> getVentesParJour(
      String boutiqueId, DateTime date) async {
    try {
      final start = DateTime(date.year, date.month, date.day);
      final end = start.add(const Duration(days: 1));
      return _getVentesBetween(boutiqueId, start, end);
    } catch (e) {
      return Left(DatabaseFailure(message: 'Erreur ventes du jour: $e'));
    }
  }

  @override
  Future<Either<Failure, List<Vente>>> getVentesParPeriode(
      String boutiqueId, DateTime debut, DateTime fin) async {
    try {
      return _getVentesBetween(
        boutiqueId,
        debut,
        fin.add(const Duration(milliseconds: 1)),
      );
    } catch (e) {
      return Left(DatabaseFailure(message: 'Erreur ventes période: $e'));
    }
  }

  @override
  Stream<List<Vente>> watchVentes(String boutiqueId) {
    final joined = (_db.select(_db.ventes).join([
      leftOuterJoin(
          _db.produits, _db.produits.id.equalsExp(_db.ventes.produitId)),
    ])
      ..where(_db.ventes.boutiqueId.equals(boutiqueId))
      ..orderBy([OrderingTerm.desc(_db.ventes.date)]));

    return joined.watch().map((rows) {
      return rows.map((row) {
        final vente = row.readTable(_db.ventes);
        final produit = row.readTableOrNull(_db.produits);
        return _toEntity(
          vente,
          nomProduit: produit?.nom ?? vente.produitId,
        );
      }).toList();
    });
  }

  Future<Either<Failure, List<Vente>>> _getVentesBetween(
    String boutiqueId,
    DateTime start,
    DateTime endExclusive,
  ) async {
    final joined = (_db.select(_db.ventes).join([
      leftOuterJoin(
          _db.produits, _db.produits.id.equalsExp(_db.ventes.produitId)),
    ])
      ..where(_db.ventes.boutiqueId.equals(boutiqueId))
      ..where(_db.ventes.date.isBiggerOrEqualValue(start))
      ..where(_db.ventes.date.isSmallerThanValue(endExclusive))
      ..orderBy([OrderingTerm.desc(_db.ventes.date)]));

    final rows = await joined.get();
    return Right(rows.map((row) {
      final vente = row.readTable(_db.ventes);
      final produit = row.readTableOrNull(_db.produits);
      return _toEntity(
        vente,
        nomProduit: produit?.nom ?? vente.produitId,
      );
    }).toList());
  }
}

@LazySingleton(as: DetteRepository)
class DetteRepositoryImpl implements DetteRepository {
  final AppDatabase _db;

  DetteRepositoryImpl(this._db);

  StatutDette _toStatut(String value) {
    if (value == 'non_paye') return StatutDette.nonPaye;
    if (value == 'partiel') return StatutDette.partiel;
    return StatutDette.paye;
  }

  String _fromStatut(StatutDette statut) {
    switch (statut) {
      case StatutDette.nonPaye:
        return 'non_paye';
      case StatutDette.partiel:
        return 'partiel';
      case StatutDette.paye:
        return 'paye';
    }
  }

  Dette _toEntity(dynamic row, {required String nomClient}) {
    return Dette(
      id: row.id,
      clientId: row.clientId,
      venteId: row.venteId,
      boutiqueId: row.boutiqueId,
      nomClient: nomClient,
      montant: row.montant,
      montantPaye: row.montantPaye,
      statut: _toStatut(row.statut),
      dateEcheance: row.dateEcheance,
      synced: row.synced,
      createdAt: row.createdAt,
      updatedAt: row.updatedAt,
    );
  }

  @override
  Future<Either<Failure, Dette>> enregistrerDette(Dette dette) async {
    try {
      await _db.into(_db.dettes).insert(
            DettesCompanion.insert(
              id: dette.id,
              clientId: dette.clientId,
              venteId: dette.venteId,
              boutiqueId: dette.boutiqueId,
              montant: dette.montant,
              montantPaye: Value(dette.montantPaye),
              statut: Value(_fromStatut(dette.statut)),
              dateEcheance: Value(dette.dateEcheance),
              synced: Value(dette.synced),
              createdAt: Value(dette.createdAt),
              updatedAt: Value(dette.updatedAt),
            ),
          );
      return Right(dette);
    } catch (e) {
      return Left(DatabaseFailure(message: 'Erreur enregistrement dette: $e'));
    }
  }

  @override
  Future<Either<Failure, Dette>> enregistrerPaiement(
      {required String detteId,
      required int montant,
      required String modePaiement}) async {
    try {
      final currentRow = await (_db.select(_db.dettes)
            ..where((d) => d.id.equals(detteId)))
          .getSingleOrNull();
      if (currentRow == null) {
        return const Left(DatabaseFailure(message: 'Dette introuvable'));
      }

      final nouveauPaye =
          (currentRow.montantPaye + montant).clamp(0, currentRow.montant);
      final statut = switch (nouveauPaye) {
        0 => StatutDette.nonPaye,
        _ when nouveauPaye >= currentRow.montant => StatutDette.paye,
        _ => StatutDette.partiel,
      };

      await (_db.update(_db.dettes)..where((d) => d.id.equals(detteId))).write(
        DettesCompanion(
          montantPaye: Value(nouveauPaye),
          statut: Value(_fromStatut(statut)),
          synced: const Value(false),
          updatedAt: Value(DateTime.now()),
        ),
      );

      await _db.into(_db.paiements).insert(
            PaiementsCompanion.insert(
              id: _uuid.v4(),
              detteId: detteId,
              boutiqueId: currentRow.boutiqueId,
              montant: montant,
              modePaiement: Value(modePaiement),
              synced: const Value(false),
              date: Value(DateTime.now()),
            ),
          );

      final clientRow = await (_db.select(_db.clients)
            ..where((c) => c.id.equals(currentRow.clientId)))
          .getSingleOrNull();

      final updated = _toEntity(
        currentRow.copyWith(
          montantPaye: nouveauPaye,
          statut: _fromStatut(statut),
          synced: false,
          updatedAt: DateTime.now(),
        ),
        nomClient: clientRow?.nom ?? currentRow.clientId,
      );
      return Right(updated);
    } catch (e) {
      return Left(DatabaseFailure(message: 'Erreur paiement dette: $e'));
    }
  }

  @override
  Future<Either<Failure, Dette>> getDetteById(String id) async {
    try {
      final joined = _db.select(_db.dettes).join([
        leftOuterJoin(
            _db.clients, _db.clients.id.equalsExp(_db.dettes.clientId)),
      ])
        ..where(_db.dettes.id.equals(id))
        ..limit(1);

      final row = await joined.getSingleOrNull();
      if (row == null) {
        return const Left(DatabaseFailure(message: 'Dette introuvable'));
      }
      final dette = row.readTable(_db.dettes);
      final client = row.readTableOrNull(_db.clients);
      return Right(_toEntity(dette, nomClient: client?.nom ?? dette.clientId));
    } catch (e) {
      return Left(DatabaseFailure(message: 'Erreur lecture dette: $e'));
    }
  }

  @override
  Future<Either<Failure, List<Dette>>> getDettesEchues(
      String boutiqueId) async {
    try {
      final now = DateTime.now();
      final joined = (_db.select(_db.dettes).join([
        leftOuterJoin(
            _db.clients, _db.clients.id.equalsExp(_db.dettes.clientId)),
      ])
        ..where(_db.dettes.boutiqueId.equals(boutiqueId))
        ..where(_db.dettes.dateEcheance.isSmallerThanValue(now))
        ..where(_db.dettes.statut.isNotValue('paye'))
        ..orderBy([OrderingTerm.desc(_db.dettes.updatedAt)]));

      final rows = await joined.get();
      return Right(rows.map((row) {
        final dette = row.readTable(_db.dettes);
        final client = row.readTableOrNull(_db.clients);
        return _toEntity(dette, nomClient: client?.nom ?? dette.clientId);
      }).toList());
    } catch (e) {
      return Left(DatabaseFailure(message: 'Erreur dettes échues: $e'));
    }
  }

  @override
  Future<Either<Failure, int>> getTotalDettesActives(String boutiqueId) async {
    try {
      final rows = await (_db.select(_db.dettes)
            ..where((d) => d.boutiqueId.equals(boutiqueId))
            ..where((d) => d.statut.isNotValue('paye')))
          .get();
      final total = rows.fold<int>(
        0,
        (sum, d) => sum + (d.montant - d.montantPaye).clamp(0, d.montant),
      );
      return Right(total);
    } catch (e) {
      return Left(DatabaseFailure(message: 'Erreur total dettes: $e'));
    }
  }

  @override
  Stream<List<Dette>> watchDettes(String boutiqueId) {
    final joined = (_db.select(_db.dettes).join([
      leftOuterJoin(_db.clients, _db.clients.id.equalsExp(_db.dettes.clientId)),
    ])
      ..where(_db.dettes.boutiqueId.equals(boutiqueId))
      ..orderBy([OrderingTerm.desc(_db.dettes.updatedAt)]));

    return joined.watch().map((rows) {
      return rows.map((row) {
        final dette = row.readTable(_db.dettes);
        final client = row.readTableOrNull(_db.clients);
        return _toEntity(dette, nomClient: client?.nom ?? dette.clientId);
      }).toList();
    });
  }

  @override
  Stream<List<Dette>> watchDettesClient(String clientId) {
    final joined = (_db.select(_db.dettes).join([
      leftOuterJoin(_db.clients, _db.clients.id.equalsExp(_db.dettes.clientId)),
    ])
      ..where(_db.dettes.clientId.equals(clientId))
      ..orderBy([OrderingTerm.desc(_db.dettes.updatedAt)]));

    return joined.watch().map((rows) {
      return rows.map((row) {
        final dette = row.readTable(_db.dettes);
        final client = row.readTableOrNull(_db.clients);
        return _toEntity(dette, nomClient: client?.nom ?? dette.clientId);
      }).toList();
    });
  }
}

@LazySingleton(as: AuthRepository)
class AuthRepositoryImpl implements AuthRepository {
  final AppDatabase _db;
  final SyncRepository _syncRepository;

  AuthRepositoryImpl(this._db, this._syncRepository);

  bool _sessionActive = false;
  String? _activeBoutiqueId;

  Future<Box<dynamic>> _sessionBox() => Hive.openBox<dynamic>(_sessionBoxName);

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
      final box = await _sessionBox();
      await box.put(_kSessionActive, true);
      await box.put(_kBoutiqueId, boutiqueId);
      return const Right(unit);
    } catch (e) {
      return Left(AuthFailure(message: 'Erreur: ${e.toString()}'));
    }
  }

  @override
  Future<void> deconnecter() async {
    _sessionActive = false;
    _activeBoutiqueId = null;
    final box = await _sessionBox();
    await box.put(_kSessionActive, false);
    await box.delete(_kBoutiqueId);
  }

  @override
  Future<bool> estConnecte() async {
    if (_sessionActive) return true;
    final box = await _sessionBox();
    final active = box.get(_kSessionActive) as bool? ?? false;
    _sessionActive = active;
    _activeBoutiqueId = box.get(_kBoutiqueId) as String? ?? _activeBoutiqueId;
    return active;
  }

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
      final box = await _sessionBox();
      await box.put(_kSessionActive, true);
      await box.put(_kBoutiqueId, utilisateur.boutiqueId);
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

    final box = await _sessionBox();
    final cachedBoutiqueId = box.get(_kBoutiqueId) as String?;
    if (cachedBoutiqueId != null && cachedBoutiqueId.isNotEmpty) {
      _activeBoutiqueId = cachedBoutiqueId;
      return Right(cachedBoutiqueId);
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
        table: 'creditstock_boutiques',
        rows: boutiques
            .map((b) => {
                  'id': b.id,
                  'nom': b.nom,
                  'adresse': b.adresse,
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
