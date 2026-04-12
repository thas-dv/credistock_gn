import 'package:dartz/dartz.dart';
import '../entities/entities.dart';
import '../../core/errors/failures.dart';

// ============================================================
// PRODUIT REPOSITORY
// ============================================================

abstract class ProduitRepository {
  Stream<List<Produit>> watchProduits(String boutiqueId);
  Stream<List<Produit>> watchProduitsEnAlerte(String boutiqueId);
  Future<Either<Failure, Produit>> getProduitById(String id);
  Future<Either<Failure, List<Produit>>> searchProduits(String boutiqueId, String query);
  Future<Either<Failure, Produit>> ajouterProduit(Produit produit);
  Future<Either<Failure, Produit>> modifierProduit(Produit produit);
  Future<Either<Failure, Unit>> supprimerProduit(String id);
  Future<Either<Failure, Unit>> mettreAJourStock(String produitId, int deltaQuantite);
}

// ============================================================
// CLIENT REPOSITORY
// ============================================================

abstract class ClientRepository {
  Stream<List<Client>> watchClients(String boutiqueId);
  Future<Either<Failure, Client>> getClientById(String id);
  Future<Either<Failure, List<Client>>> searchClients(String boutiqueId, String query);
  Future<Either<Failure, Client>> ajouterClient(Client client);
  Future<Either<Failure, Client>> modifierClient(Client client);
  Future<Either<Failure, Unit>> recalculerScore(String clientId);
}

// ============================================================
// VENTE REPOSITORY
// ============================================================

abstract class VenteRepository {
  Stream<List<Vente>> watchVentes(String boutiqueId);
  Future<Either<Failure, List<Vente>>> getVentesParJour(String boutiqueId, DateTime date);
  Future<Either<Failure, List<Vente>>> getVentesParPeriode(
    String boutiqueId,
    DateTime debut,
    DateTime fin,
  );
  Future<Either<Failure, Vente>> enregistrerVente(Vente vente);
  Future<Either<Failure, int>> getTotalVentesJour(String boutiqueId);
}

// ============================================================
// DETTE REPOSITORY
// ============================================================

abstract class DetteRepository {
  Stream<List<Dette>> watchDettes(String boutiqueId);
  Stream<List<Dette>> watchDettesClient(String clientId);
  Future<Either<Failure, Dette>> getDetteById(String id);
  Future<Either<Failure, List<Dette>>> getDettesEchues(String boutiqueId);
  Future<Either<Failure, Dette>> enregistrerDette(Dette dette);
  Future<Either<Failure, Dette>> enregistrerPaiement({
    required String detteId,
    required int montant,
    required String modePaiement,
  });
  Future<Either<Failure, int>> getTotalDettesActives(String boutiqueId);
}

// ============================================================
// SYNC REPOSITORY
// ============================================================

abstract class SyncRepository {
  Future<Either<Failure, Unit>> synchroniser(String boutiqueId);
  Future<int> getNombreElementsNonSynces();
  Stream<SyncStatus> watchSyncStatus();
}

enum SyncStatus { idle, syncing, success, error, offline }

// ============================================================
// AUTH REPOSITORY
// ============================================================

abstract class AuthRepository {
  Future<Either<Failure, bool>> verifierPin(String boutiqueId, String pin);
  Future<Either<Failure, Unit>> changerPin(String boutiqueId, String ancienPin, String nouveauPin);
  Future<Either<Failure, String>> getBoutiqueId();
  Future<bool> estConnecte();
  Future<Either<Failure, Unit>> creerCompte({
    required String identifiant,
    required String motDePasse,
     required String boutiqueId,
    required String nom,
    required String role,
  });
  Future<Either<Failure, Unit>> seConnecter({
    required String identifiant,
    required String motDePasse,
  });
  Future<void> deconnecter();
}

// ============================================================
// ABONNEMENT REPOSITORY
// ============================================================

abstract class AbonnementRepository {
  Future<Either<Failure, Abonnement>> getAbonnement(String boutiqueId);
  Future<Either<Failure, Abonnement>> souscrire({
    required String boutiqueId,
    required PlanAbonnement plan,
    required ModePaiementAbonnement modePaiement,
  });
  Future<Either<Failure, bool>> verifierLimites({
    required String boutiqueId,
    required String typeRessource,
  });
}