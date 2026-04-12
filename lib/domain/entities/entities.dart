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

  Produit copyWith({
    String? id,
    String? boutiqueId,
    String? nom,
    CategorieProduit? categorie,
    int? prixVente,
    int? prixAchat,
    int? quantite,
    int? seuilAlerte,
    bool? synced,
    DateTime? updatedAt,
  }) {
    return Produit(
      id: id ?? this.id,
      boutiqueId: boutiqueId ?? this.boutiqueId,
      nom: nom ?? this.nom,
      categorie: categorie ?? this.categorie,
      prixVente: prixVente ?? this.prixVente,
      prixAchat: prixAchat ?? this.prixAchat,
      quantite: quantite ?? this.quantite,
      seuilAlerte: seuilAlerte ?? this.seuilAlerte,
      synced: synced ?? this.synced,
      updatedAt: updatedAt ?? DateTime.now(),
    );
  }

  @override
  List<Object?> get props => [id, nom, quantite, prixVente, synced];
}

// ============================================================
// CLIENT
// ============================================================

enum ScoreClient { bon, moyen, mauvais }

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

  Client copyWith({
    String? nom,
    String? telephone,
    ScoreClient? score,
    int? totalDu,
    int? nombreDettes,
    int? nombresRemboursements,
    bool? synced,
  }) {
    return Client(
      id: id,
      boutiqueId: boutiqueId,
      nom: nom ?? this.nom,
      telephone: telephone ?? this.telephone,
      score: score ?? this.score,
      totalDu: totalDu ?? this.totalDu,
      nombreDettes: nombreDettes ?? this.nombreDettes,
      nombresRemboursements:
          nombresRemboursements ?? this.nombresRemboursements,
      synced: synced ?? this.synced,
      createdAt: createdAt,
    );
  }

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
  final String nomProduit;
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

class Dette extends Equatable {
  final String id;
  final String clientId;
  final String venteId;
  final String boutiqueId;
  final String nomClient;
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

  bool get estEchue =>
      dateEcheance != null &&
      DateTime.now().isAfter(dateEcheance!) &&
      statut != StatutDette.paye;

double get tauxRemboursement =>
    montant > 0 ? (montantPaye / montant) * 100 : 0;

int get joursDeRetard {
  if (dateEcheance == null) return 0;
  final diff = DateTime.now().difference(dateEcheance!).inDays;
  return diff > 0 ? diff : 0;
}
  Dette copyWith({
    int? montantPaye,
    StatutDette? statut,
    bool? synced,
    DateTime? updatedAt,
  }) {
    return Dette(
      id: id,
      clientId: clientId,
      venteId: venteId,
      boutiqueId: boutiqueId,
      nomClient: nomClient,
      montant: montant,
      montantPaye: montantPaye ?? this.montantPaye,
      statut: statut ?? this.statut,
      dateEcheance: dateEcheance,
      synced: synced ?? this.synced,
      createdAt: createdAt,
      updatedAt: updatedAt ?? DateTime.now(),
    );
  }

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

  @override
  List<Object?> get props => [id, plan, statut];
}