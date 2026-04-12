import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import 'package:injectable/injectable.dart';
import 'package:speech_to_text/speech_to_text.dart';

import '../../../domain/entities/entities.dart';
import '../../../domain/usecases/usecases.dart';

// ============================================================
// EVENTS
// ============================================================

abstract class VenteEvent extends Equatable {
  const VenteEvent();
  @override
  List<Object?> get props => [];
}

class VenteSelectionnerProduit extends VenteEvent {
  final Produit produit;
  const VenteSelectionnerProduit(this.produit);
  @override
  List<Object?> get props => [produit];
}

class VenteChangerQuantite extends VenteEvent {
  final int quantite;
  const VenteChangerQuantite(this.quantite);
  @override
  List<Object?> get props => [quantite];
}

class VenteChangerTypePaiement extends VenteEvent {
  final TypePaiement type;
  const VenteChangerTypePaiement(this.type);
  @override
  List<Object?> get props => [type];
}

class VenteSelectionnerClient extends VenteEvent {
  final Client client;
  const VenteSelectionnerClient(this.client);
  @override
  List<Object?> get props => [client];
}

class VenteEnregistrer extends VenteEvent {
  final String boutiqueId;
  final String utilisateurId;
  final DateTime? dateEcheance;
  const VenteEnregistrer({
    required this.boutiqueId,
    required this.utilisateurId,
    this.dateEcheance,
  });
}

class VenteDemarrerEcouteVocale extends VenteEvent {
 final String boutiqueId;
  const VenteDemarrerEcouteVocale(this.boutiqueId);

  @override
  List<Object?> get props => [boutiqueId];
}

class VenteArreterEcouteVocale extends VenteEvent {
  const VenteArreterEcouteVocale();
}

class VenteTexteVocalRecu extends VenteEvent {
  final String texte;
  final String boutiqueId;
  const VenteTexteVocalRecu(this.texte, this.boutiqueId);
  @override
  List<Object?> get props => [texte];
}

class VenteReinitialiser extends VenteEvent {
  const VenteReinitialiser();
}

// ============================================================
// STATE
// ============================================================

enum VenteStatus { initial, loading, success, error }
enum EcouteVocaleStatus { inactive, listening, processing, recognized }

class VenteState extends Equatable {
  final Produit? produitSelectionne;
  final int quantite;
  final TypePaiement typePaiement;
  final Client? clientSelectionne;
  final VenteStatus status;
  final EcouteVocaleStatus ecouteStatus;
  final String? texteVocal;
  final String? errorMessage;
  final Vente? venteEnregistree;

  const VenteState({
    this.produitSelectionne,
    this.quantite = 1,
    this.typePaiement = TypePaiement.cash,
    this.clientSelectionne,
    this.status = VenteStatus.initial,
    this.ecouteStatus = EcouteVocaleStatus.inactive,
    this.texteVocal,
    this.errorMessage,
    this.venteEnregistree,
  });

  int get montantTotal => (produitSelectionne?.prixVente ?? 0) * quantite;
  bool get peutEnregistrer =>
      produitSelectionne != null &&
      quantite > 0 &&
      (typePaiement == TypePaiement.cash || clientSelectionne != null);

  VenteState copyWith({
    Produit? produitSelectionne,
    int? quantite,
    TypePaiement? typePaiement,
    Client? clientSelectionne,
    VenteStatus? status,
    EcouteVocaleStatus? ecouteStatus,
    String? texteVocal,
    String? errorMessage,
    Vente? venteEnregistree,
  }) {
    return VenteState(
      produitSelectionne: produitSelectionne ?? this.produitSelectionne,
      quantite: quantite ?? this.quantite,
      typePaiement: typePaiement ?? this.typePaiement,
      clientSelectionne: clientSelectionne ?? this.clientSelectionne,
      status: status ?? this.status,
      ecouteStatus: ecouteStatus ?? this.ecouteStatus,
      texteVocal: texteVocal ?? this.texteVocal,
      errorMessage: errorMessage,
      venteEnregistree: venteEnregistree ?? this.venteEnregistree,
    );
  }

  @override
  List<Object?> get props => [
        produitSelectionne,
        quantite,
        typePaiement,
        clientSelectionne,
        status,
        ecouteStatus,
        texteVocal,
        errorMessage,
      ];
}

// ============================================================
// BLOC
// ============================================================

@injectable
class VenteBloc extends Bloc<VenteEvent, VenteState> {
  final EnregistrerVenteUseCase _enregistrerVente;
  final ParseCommandeVocaleUseCase _parseCommande;
  final SpeechToText _speechToText = SpeechToText();
  String? _boutiqueIdForVoice;

  VenteBloc(this._enregistrerVente, this._parseCommande)
      : super(const VenteState()) {
    on<VenteSelectionnerProduit>(_onSelectionnerProduit);
    on<VenteChangerQuantite>(_onChangerQuantite);
    on<VenteChangerTypePaiement>(_onChangerTypePaiement);
    on<VenteSelectionnerClient>(_onSelectionnerClient);
    on<VenteEnregistrer>(_onEnregistrer);
    on<VenteDemarrerEcouteVocale>(_onDemarrerEcoute);
    on<VenteArreterEcouteVocale>(_onArreterEcoute);
    on<VenteTexteVocalRecu>(_onTexteVocalRecu);
    on<VenteReinitialiser>(_onReinitialiser);
  }

  void _onSelectionnerProduit(VenteSelectionnerProduit event, Emitter<VenteState> emit) {
    emit(state.copyWith(produitSelectionne: event.produit));
  }

  void _onChangerQuantite(VenteChangerQuantite event, Emitter<VenteState> emit) {
    if (event.quantite < 1) return;
    final maxStock = state.produitSelectionne?.quantite ?? 999;
    final quantite = event.quantite.clamp(1, maxStock);
    emit(state.copyWith(quantite: quantite));
  }

  void _onChangerTypePaiement(VenteChangerTypePaiement event, Emitter<VenteState> emit) {
    emit(state.copyWith(typePaiement: event.type));
  }

  void _onSelectionnerClient(VenteSelectionnerClient event, Emitter<VenteState> emit) {
    emit(state.copyWith(clientSelectionne: event.client));
  }

  Future<void> _onEnregistrer(VenteEnregistrer event, Emitter<VenteState> emit) async {
    if (!state.peutEnregistrer) return;
    emit(state.copyWith(status: VenteStatus.loading));

    final result = await _enregistrerVente(
      boutiqueId: event.boutiqueId,
      utilisateurId: event.utilisateurId,
      produitId: state.produitSelectionne!.id,
      quantite: state.quantite,
      typePaiement: state.typePaiement,
      clientId: state.clientSelectionne?.id,
      dateEcheance: event.dateEcheance,
    );

    result.fold(
      (failure) => emit(state.copyWith(
        status: VenteStatus.error,
        errorMessage: failure.message,
      )),
      (vente) => emit(state.copyWith(
        status: VenteStatus.success,
        venteEnregistree: vente,
      )),
    );
  }

  Future<void> _onDemarrerEcoute(
    VenteDemarrerEcouteVocale event,
    Emitter<VenteState> emit,
  ) async {
    _boutiqueIdForVoice = event.boutiqueId;
    final available = await _speechToText.initialize(
      onError: (_) => add(const VenteArreterEcouteVocale()),
    );

    if (!available) {
      emit(state.copyWith(
        errorMessage: 'Microphone non disponible',
        status: VenteStatus.error,
      ));
      return;
    }

    emit(state.copyWith(ecouteStatus: EcouteVocaleStatus.listening));

    await _speechToText.listen(
      onResult: (result) {
        if (result.finalResult) {
          // Sera traité via VenteTexteVocalRecu
           final texte = result.recognizedWords.trim();
          final boutiqueId = _boutiqueIdForVoice;
          if (texte.isNotEmpty && boutiqueId != null) {
            add(VenteTexteVocalRecu(texte, boutiqueId));
          }
          add(const VenteArreterEcouteVocale());
        }
      },
      localeId: 'fr_FR',
      listenFor: const Duration(seconds: 10),
    );
  }

  Future<void> _onArreterEcoute(
    VenteArreterEcouteVocale event,
    Emitter<VenteState> emit,
  ) async {
    await _speechToText.stop();
    emit(state.copyWith(ecouteStatus: EcouteVocaleStatus.inactive));
  }

  Future<void> _onTexteVocalRecu(
    VenteTexteVocalRecu event,
    Emitter<VenteState> emit,
  ) async {
    emit(state.copyWith(
      ecouteStatus: EcouteVocaleStatus.processing,
      texteVocal: event.texte,
    ));

    final result = await _parseCommande(
      boutiqueId: event.boutiqueId,
      texte: event.texte,
    );

    result.fold(
      (failure) => emit(state.copyWith(
        ecouteStatus: EcouteVocaleStatus.inactive,
        errorMessage: failure.message,
      )),
      (commande) => emit(state.copyWith(
        ecouteStatus: EcouteVocaleStatus.recognized,
        produitSelectionne: commande.produit,
        quantite: commande.quantite,
        typePaiement: commande.typePaiement,
        clientSelectionne: commande.client,
      )),
    );
  }

  void _onReinitialiser(VenteReinitialiser event, Emitter<VenteState> emit) {
    emit(const VenteState());
  }
}
