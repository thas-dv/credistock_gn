import 'package:dartz/dartz.dart';
import 'package:injectable/injectable.dart';
import 'package:uuid/uuid.dart';

import '../entities/entities.dart';
import '../repositories/repositories.dart';
import '../../core/errors/failures.dart';

const _uuid = Uuid();

// ============================================================
// ENREGISTRER UNE VENTE (use case principal)
// ============================================================

@injectable
class EnregistrerVenteUseCase {
  final VenteRepository _venteRepo;
  final ProduitRepository _produitRepo;
  final DetteRepository _detteRepo;
  final ClientRepository _clientRepo;
  final AbonnementRepository _abonnementRepo;

  EnregistrerVenteUseCase(
    this._venteRepo,
    this._produitRepo,
    this._detteRepo,
    this._clientRepo,
    this._abonnementRepo,
  );

  Future<Either<Failure, Vente>> call({
    required String boutiqueId,
    required String utilisateurId,
    required String produitId,
    required int quantite,
    required TypePaiement typePaiement,
    String? clientId,
    DateTime? dateEcheance,
    SourceVente source = SourceVente.manuel,
  }) async {
    // 1. Vérifier le stock disponible
    final produitResult = await _produitRepo.getProduitById(produitId);
    if (produitResult.isLeft()) return Left(const StockInsuffisantFailure());

    final produit = produitResult.getOrElse(() => throw Exception());
    if (produit.quantite < quantite) {
      return Left(StockInsuffisantFailure(
        message: 'Stock insuffisant: ${produit.quantite} disponible(s), $quantite demandé(s)',
      ));
    }

    // 2. Vérifier limites du plan pour les crédits
    if (typePaiement == TypePaiement.credit) {
      final limitResult = await _abonnementRepo.verifierLimites(
        boutiqueId: boutiqueId,
        typeRessource: 'dettes',
      );
      final limitOk = limitResult.getOrElse(() => false);
      if (!limitOk) {
        return Left(const LimitePlanFailure(
          message: 'Limite de 10 dettes atteinte. Passez au plan Premium.',
        ));
      }
    }

    // 3. Créer la vente
    final vente = Vente(
      id: _uuid.v4(),
      boutiqueId: boutiqueId,
      produitId: produitId,
      clientId: clientId,
      utilisateurId: utilisateurId,
      nomProduit: produit.nom,
      quantite: quantite,
      prixUnitaire: produit.prixVente,
      montantTotal: produit.prixVente * quantite,
      typePaiement: typePaiement,
      source: source,
      synced: false,
      date: DateTime.now(),
    );

    final venteResult = await _venteRepo.enregistrerVente(vente);
    if (venteResult.isLeft()) return venteResult;

    // 4. Décrémenter le stock (offline-safe)
    await _produitRepo.mettreAJourStock(produitId, -quantite);

    // 5. Créer la dette si crédit
    if (typePaiement == TypePaiement.credit && clientId != null) {
      final clientResult = await _clientRepo.getClientById(clientId);
      final client = clientResult.getOrElse(() => throw Exception());

      final dette = Dette(
        id: _uuid.v4(),
        clientId: clientId,
        venteId: vente.id,
        boutiqueId: boutiqueId,
        nomClient: client.nom,
        montant: vente.montantTotal,
        montantPaye: 0,
        statut: StatutDette.nonPaye,
        dateEcheance: dateEcheance,
        synced: false,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );
      await _detteRepo.enregistrerDette(dette);

      // Recalculer score client
      await _clientRepo.recalculerScore(clientId);
    }

    return venteResult;
  }
}

// ============================================================
// ENREGISTRER UN PAIEMENT DE DETTE
// ============================================================

@injectable
class EnregistrerPaiementUseCase {
  final DetteRepository _detteRepo;
  final ClientRepository _clientRepo;

  EnregistrerPaiementUseCase(this._detteRepo, this._clientRepo);

  Future<Either<Failure, Dette>> call({
    required String detteId,
    required int montant,
    required String clientId,
    String modePaiement = 'especes',
  }) async {
    if (montant <= 0) {
      return Left(const ValidationFailure(message: 'Le montant doit être positif'));
    }

    final result = await _detteRepo.enregistrerPaiement(
      detteId: detteId,
      montant: montant,
      modePaiement: modePaiement,
    );

    if (result.isRight()) {
      await _clientRepo.recalculerScore(clientId);
    }

    return result;
  }
}

// ============================================================
// PARSER UNE COMMANDE VOCALE
// ============================================================

@injectable
class ParseCommandeVocaleUseCase {
  final ProduitRepository _produitRepo;
  final ClientRepository _clientRepo;

  ParseCommandeVocaleUseCase(this._produitRepo, this._clientRepo);

  /// Exemple: "Vendre 2 riz à crédit Mamadou"
  Future<Either<Failure, CommandeVocale>> call({
    required String boutiqueId,
    required String texte,
  }) async {
    final texteNormalise = texte.toLowerCase().trim();

    // Détecter le type de paiement
    final estCredit = texteNormalise.contains('crédit') ||
        texteNormalise.contains('credit') ||
        texteNormalise.contains('à crédit');

    // Extraire la quantité (regex: chiffre suivi d'un espace)
    final regexQuantite = RegExp(r'\b(\d+)\b');
    final matchQuantite = regexQuantite.firstMatch(texteNormalise);
    final quantite = matchQuantite != null ? int.tryParse(matchQuantite.group(1)!) : 1;

    // Rechercher le produit (mots clés)
    final mots = texteNormalise.split(' ')
        .where((m) => m.length > 2 && !_motsFiltres.contains(m))
        .toList();

    Produit? produitTrouve;
    for (final mot in mots) {
      final resultats = await _produitRepo.searchProduits(boutiqueId, mot);
      final liste = resultats.getOrElse(() => []);
      if (liste.isNotEmpty) {
        produitTrouve = liste.first;
        break;
      }
    }

    if (produitTrouve == null) {
      return Left(const ValidationFailure(message: 'Produit non reconnu dans la commande'));
    }

    // Rechercher le client si crédit
    Client? clientTrouve;
    if (estCredit) {
      for (final mot in mots) {
        if (mot == produitTrouve.nom.toLowerCase()) continue;
        final resultats = await _clientRepo.searchClients(boutiqueId, mot);
        final liste = resultats.getOrElse(() => []);
        if (liste.isNotEmpty) {
          clientTrouve = liste.first;
          break;
        }
      }
    }

    return Right(CommandeVocale(
      produit: produitTrouve,
      quantite: quantite ?? 1,
      typePaiement: estCredit ? TypePaiement.credit : TypePaiement.cash,
      client: clientTrouve,
      texteOriginal: texte,
    ));
  }

  static const _motsFiltres = {
    'vendre', 'vendu', 'vente', 'pour', 'avec', 'à', 'le', 'la', 'les',
    'un', 'une', 'des', 'du', 'de', 'en', 'au', 'aux', 'crédit', 'credit',
    'cash', 'et', 'ou',
  };
}

class CommandeVocale {
  final Produit produit;
  final int quantite;
  final TypePaiement typePaiement;
  final Client? client;
  final String texteOriginal;

  const CommandeVocale({
    required this.produit,
    required this.quantite,
    required this.typePaiement,
    this.client,
    required this.texteOriginal,
  });
}

// ============================================================
// OBTENIR STATISTIQUES
// ============================================================

@injectable
class GetStatistiquesUseCase {
  final VenteRepository _venteRepo;
  final DetteRepository _detteRepo;

  GetStatistiquesUseCase(this._venteRepo, this._detteRepo);

  Future<Either<Failure, StatistiquesData>> call({
    required String boutiqueId,
    required DateTime debut,
    required DateTime fin,
  }) async {
    final ventesResult = await _venteRepo.getVentesParPeriode(boutiqueId, debut, fin);

    return ventesResult.fold(
      (failure) => Left(failure),
      (ventes) async {
        final totalVentes = ventes.fold(0, (sum, v) => sum + v.montantTotal);
        final ventesCredit = ventes.where((v) => v.estCredit).toList();
        final totalCredit = ventesCredit.fold(0, (sum, v) => sum + v.montantTotal);
        final totalCash = totalVentes - totalCredit;

        final totalDettes = await _detteRepo.getTotalDettesActives(boutiqueId);
        final dettesTotal = totalDettes.getOrElse(() => 0);

        // Grouper par jour
        final Map<DateTime, int> parJour = {};
        for (final vente in ventes) {
          final jour = DateTime(vente.date.year, vente.date.month, vente.date.day);
          parJour[jour] = (parJour[jour] ?? 0) + vente.montantTotal;
        }

        // Top produits
        final Map<String, int> parProduit = {};
        for (final vente in ventes) {
          parProduit[vente.nomProduit] =
              (parProduit[vente.nomProduit] ?? 0) + vente.montantTotal;
        }
        final topProduits = parProduit.entries.toList()
          ..sort((a, b) => b.value.compareTo(a.value));

        return Right(StatistiquesData(
          totalVentes: totalVentes,
          nombreVentes: ventes.length,
          totalCash: totalCash,
          totalCredit: totalCredit,
          totalDettesActives: dettesTotal,
          ventesParJour: parJour,
          topProduits: topProduits.take(5).toList(),
        ));
      },
    );
  }
}

class StatistiquesData {
  final int totalVentes;
  final int nombreVentes;
  final int totalCash;
  final int totalCredit;
  final int totalDettesActives;
  final Map<DateTime, int> ventesParJour;
  final List<MapEntry<String, int>> topProduits;

  const StatistiquesData({
    required this.totalVentes,
    required this.nombreVentes,
    required this.totalCash,
    required this.totalCredit,
    required this.totalDettesActives,
    required this.ventesParJour,
    required this.topProduits,
  });

  double get pourcentageCredit =>
      totalVentes > 0 ? (totalCredit / totalVentes) * 100 : 0;
}