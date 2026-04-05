import 'package:equatable/equatable.dart';

// ============================================================
// PRODUIT
// ============================================================

enum CategorieProduit { general, alimentaire, boisson, hygiene, autre }

class Produit extends Equatable {
  final String id;
  final String boutiqueId;
  final String nom;
  final CategorieProduit categorie;
  final int prixVente;
  final int prixAchat;
  final int quantite;
  final int seuilAlerte;
  final bool synced;
  final DateTime updatedAt;

  const Produit({
    required this.id,
    required this.boutiqueId,
    required this.nom,
    required this.categorie,
    required this.prixVente,
    required this.prixAchat,
    required this.quantite,
    required this.seuilAlerte,
    required this.synced,
    required this.updatedAt,
  });

  bool get estEnAlerteStock => quantite <= seuilAlerte;
  bool get estEnRuptureStock => quantite == 0;
  int get margeGNF => prixVente - prixAchat;
  double get margePourcent => prixAchat > 0 ? (margeGNF / prixAchat) * 100 : 0;

  Produit copyWith({
    String? nom,
    int? prixVente,
    int? prixAchat,
    int? quantite,
    int? seuilAlerte,
    bool? synced,
  }) {
    return Produit(
      id: id,
      boutiqueId: boutiqueId,
      nom: nom ?? this.nom,
      categorie: categorie,
      prixVente: prixVente ?? this.prixVente,
      prixAchat: prixAchat ?? this.prixAchat,
      quantite: quantite ?? this.quantite,
      seuilAlerte: seuilAlerte ?? this.seuilAlerte,
      synced: synced ?? this.synced,
      updatedAt: DateTime.now(),
    );
  }

  @override
  List<Object?> get props => [id, nom, quantite, prixVente, synced];
}

// ============================================================
// CLIENT
// ============================================================

enum ScoreClient { bon, moyen, mauvais }

extension ScoreClientExt on ScoreClient {
  String get label => switch (this) {
    ScoreClient.bon => 'Bon payeur',
    ScoreClient.moyen => 'Payeur moyen',
    ScoreClient.mauvais => 'Mauvais payeur',
  };

  // Score calculé automatiquement selon le comportement
  static ScoreClient calculer({
    required int nombreDettes,
    required int nombreRemboursements,
    required int joursRetardMoyen,
  }) {
    if (nombreDettes == 0) return ScoreClient.bon;
    final tauxRemboursement = nombreRemboursements / nombreDettes;
    if (tauxRemboursement >= 0.8 && joursRetardMoyen <= 7) return ScoreClient.bon;
    if (tauxRemboursement >= 0.5 && joursRetardMoyen <= 30) return ScoreClient.moyen;
    return ScoreClient.mauvais;
  }
}

class Client extends Equatable {
  final String id;
  final String boutiqueId;
  final String nom;
  final String? telephone;
  final ScoreClient score;
  final int totalDu;
  final int nombreDettes;
  final int nombresRemboursements;
  final bool synced;
  final DateTime createdAt;

  const Client({
    required this.id,
    required this.boutiqueId,
    required this.nom,
    this.telephone,
    required this.score,
    required this.totalDu,
    required this.nombreDettes,
    required this.nombresRemboursements,
    required this.synced,
    required this.createdAt,
  });

  bool get aDesDetteEnCours => totalDu > 0;
  String? get whatsappUrl => telephone != null
      ? 'https://wa.me/${telephone!.replaceAll(RegExp(r'[^0-9]'), '')}'
      : null;

  @override
  List<Object?> get props => [id, nom, score, totalDu];
}

// ============================================================
// VENTE
// ============================================================

enum TypePaiement { cash, credit }
enum SourceVente { manuel, vocal }

class Vente extends Equatable {
  final String id;
  final String boutiqueId;
  final String produitId;
  final String? clientId;
  final String utilisateurId;
  final String nomProduit; // snapshot
  final int quantite;
  final int prixUnitaire;
  final int montantTotal;
  final TypePaiement typePaiement;
  final SourceVente source;
  final bool synced;
  final DateTime date;

  const Vente({
    required this.id,
    required this.boutiqueId,
    required this.produitId,
    this.clientId,
    required this.utilisateurId,
    required this.nomProduit,
    required this.quantite,
    required this.prixUnitaire,
    required this.montantTotal,
    required this.typePaiement,
    required this.source,
    required this.synced,
    required this.date,
  });

  bool get estCredit => typePaiement == TypePaiement.credit;

  @override
  List<Object?> get props => [id, montantTotal, typePaiement, synced];
}

// ============================================================
// DETTE
// ============================================================

enum StatutDette { nonPaye, partiel, paye }

extension StatutDetteExt on StatutDette {
  String get label => switch (this) {
    StatutDette.nonPaye => 'Non payé',
    StatutDette.partiel => 'Partiel',
    StatutDette.paye => 'Payé',
  };
}

class Dette extends Equatable {
  final String id;
  final String clientId;
  final String venteId;
  final String boutiqueId;
  final String nomClient; // dénormalisé pour affichage rapide
  final int montant;
  final int montantPaye;
  final StatutDette statut;
  final DateTime? dateEcheance;
  final bool synced;
  final DateTime createdAt;
  final DateTime updatedAt;

  const Dette({
    required this.id,
    required this.clientId,
    required this.venteId,
    required this.boutiqueId,
    required this.nomClient,
    required this.montant,
    required this.montantPaye,
    required this.statut,
    this.dateEcheance,
    required this.synced,
    required this.createdAt,
    required this.updatedAt,
  });

  int get montantRestant => montant - montantPaye;
  double get tauxRemboursement => montant > 0 ? (montantPaye / montant) * 100 : 0;
  bool get estEchue => dateEcheance != null && DateTime.now().isAfter(dateEcheance!) && statut != StatutDette.paye;
  int get joursDeRetard => estEchue ? DateTime.now().difference(dateEcheance!).inDays : 0;

  @override
  List<Object?> get props => [id, montantRestant, statut, synced];
}

// ============================================================
// ABONNEMENT
// ============================================================

enum PlanAbonnement { gratuit, premium }
enum StatutAbonnement { actif, expire, suspendu }
enum ModePaiementAbonnement { orangeMoney, mtnMomo }

class Abonnement extends Equatable {
  final String id;
  final String boutiqueId;
  final PlanAbonnement plan;
  final StatutAbonnement statut;
  final ModePaiementAbonnement? modePaiement;
  final int montant;
  final DateTime dateDebut;
  final DateTime? dateFin;

  const Abonnement({
    required this.id,
    required this.boutiqueId,
    required this.plan,
    required this.statut,
    this.modePaiement,
    required this.montant,
    required this.dateDebut,
    this.dateFin,
  });

  bool get estActif => statut == StatutAbonnement.actif;
  bool get estPremium => plan == PlanAbonnement.premium && estActif;

  // Limites selon le plan
  int? get maxDettes => plan == PlanAbonnement.gratuit ? 10 : null;
  int? get maxClients => plan == PlanAbonnement.gratuit ? 20 : null;
  bool get multiUtilisateurs => plan == PlanAbonnement.premium;
  bool get alertesIntelligentes => plan == PlanAbonnement.premium;
  bool get sauvegardeCloud => plan == PlanAbonnement.premium;

  @override
  List<Object?> get props => [id, plan, statut];
}

// ============================================================
// STATISTIQUES (value objects)
// ============================================================

class StatJour extends Equatable {
  final DateTime date;
  final int totalVentes;
  final int nombreVentes;
  final int totalCredit;
  final int totalCash;

  const StatJour({
    required this.date,
    required this.totalVentes,
    required this.nombreVentes,
    required this.totalCredit,
    required this.totalCash,
  });

  @override
  List<Object?> get props => [date, totalVentes];
}
