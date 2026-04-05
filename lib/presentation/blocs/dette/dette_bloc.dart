import 'dart:async';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import 'package:injectable/injectable.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../../domain/entities/entities.dart';
import '../../../domain/repositories/repositories.dart';
import '../../../domain/usecases/usecases.dart';

// ============================================================
// EVENTS
// ============================================================

abstract class DetteEvent extends Equatable {
  const DetteEvent();
  @override
  List<Object?> get props => [];
}

class DetteWatchStarted extends DetteEvent {
  final String boutiqueId;
  const DetteWatchStarted(this.boutiqueId);
  @override
  List<Object?> get props => [boutiqueId];
}

class DetteStatutFiltered extends DetteEvent {
  final StatutDette? statut;
  const DetteStatutFiltered(this.statut);
  @override
  List<Object?> get props => [statut];
}

class DettePaiementEnregistre extends DetteEvent {
  final String detteId;
  final String clientId;
  final int montant;
  final String modePaiement;
  const DettePaiementEnregistre({
    required this.detteId,
    required this.clientId,
    required this.montant,
    this.modePaiement = 'especes',
  });
  @override
  List<Object?> get props => [detteId, montant];
}

class DetteRappelWhatsApp extends DetteEvent {
  final Dette dette;
  final Client client;
  const DetteRappelWhatsApp(this.dette, this.client);
  @override
  List<Object?> get props => [dette.id];
}

class _DettesUpdated extends DetteEvent {
  final List<Dette> dettes;
  const _DettesUpdated(this.dettes);
  @override
  List<Object?> get props => [dettes];
}

// ============================================================
// STATE
// ============================================================

enum DetteStatus { initial, loading, loaded, paying, error }

class DetteState extends Equatable {
  final List<Dette> dettes;
  final List<Dette> dettesFiltrees;
  final StatutDette? filtreStatut;
  final DetteStatus status;
  final int totalDu;
  final int nombreDettesActives;
  final String? errorMessage;
  final String? successMessage;

  const DetteState({
    this.dettes = const [],
    this.dettesFiltrees = const [],
    this.filtreStatut,
    this.status = DetteStatus.initial,
    this.totalDu = 0,
    this.nombreDettesActives = 0,
    this.errorMessage,
    this.successMessage,
  });

  List<Dette> get dettesEchues =>
      dettes.where((d) => d.estEchue).toList();

  DetteState copyWith({
    List<Dette>? dettes,
    List<Dette>? dettesFiltrees,
    StatutDette? filtreStatut,
    DetteStatus? status,
    int? totalDu,
    int? nombreDettesActives,
    String? errorMessage,
    String? successMessage,
  }) {
    return DetteState(
      dettes: dettes ?? this.dettes,
      dettesFiltrees: dettesFiltrees ?? this.dettesFiltrees,
      filtreStatut: filtreStatut ?? this.filtreStatut,
      status: status ?? this.status,
      totalDu: totalDu ?? this.totalDu,
      nombreDettesActives: nombreDettesActives ?? this.nombreDettesActives,
      errorMessage: errorMessage,
      successMessage: successMessage,
    );
  }

  @override
  List<Object?> get props => [dettes, dettesFiltrees, filtreStatut, status, totalDu];
}

// ============================================================
// BLOC
// ============================================================

@injectable
class DetteBloc extends Bloc<DetteEvent, DetteState> {
  final DetteRepository _detteRepo;
  final EnregistrerPaiementUseCase _enregistrerPaiement;
  StreamSubscription<List<Dette>>? _dettesSubscription;

  DetteBloc(this._detteRepo, this._enregistrerPaiement)
      : super(const DetteState()) {
    on<DetteWatchStarted>(_onWatchStarted);
    on<DetteStatutFiltered>(_onFiltrer);
    on<DettePaiementEnregistre>(_onPaiement);
    on<DetteRappelWhatsApp>(_onRappelWhatsApp);
    on<_DettesUpdated>(_onDettesUpdated);
  }

  Future<void> _onWatchStarted(DetteWatchStarted event, Emitter<DetteState> emit) async {
    emit(state.copyWith(status: DetteStatus.loading));
    await _dettesSubscription?.cancel();
    _dettesSubscription = _detteRepo
        .watchDettes(event.boutiqueId)
        .listen((dettes) => add(_DettesUpdated(dettes)));
  }

  void _onDettesUpdated(_DettesUpdated event, Emitter<DetteState> emit) {
    final actives = event.dettes
        .where((d) => d.statut != StatutDette.paye)
        .toList();
    final totalDu = actives.fold(0, (sum, d) => sum + d.montantRestant);

    emit(state.copyWith(
      dettes: event.dettes,
      dettesFiltrees: _appliquerFiltre(event.dettes, state.filtreStatut),
      totalDu: totalDu,
      nombreDettesActives: actives.length,
      status: DetteStatus.loaded,
    ));
  }

  void _onFiltrer(DetteStatutFiltered event, Emitter<DetteState> emit) {
    emit(state.copyWith(
      filtreStatut: event.statut,
      dettesFiltrees: _appliquerFiltre(state.dettes, event.statut),
    ));
  }

  Future<void> _onPaiement(DettePaiementEnregistre event, Emitter<DetteState> emit) async {
    emit(state.copyWith(status: DetteStatus.paying));

    final result = await _enregistrerPaiement(
      detteId: event.detteId,
      montant: event.montant,
      clientId: event.clientId,
      modePaiement: event.modePaiement,
    );

    result.fold(
      (failure) => emit(state.copyWith(
        status: DetteStatus.error,
        errorMessage: failure.message,
      )),
      (_) => emit(state.copyWith(
        status: DetteStatus.loaded,
        successMessage: 'Paiement enregistré ✓',
      )),
    );
  }

  Future<void> _onRappelWhatsApp(
    DetteRappelWhatsApp event,
    Emitter<DetteState> emit,
  ) async {
    final client = event.client;
    final dette = event.dette;

    if (client.telephone == null) {
      emit(state.copyWith(errorMessage: 'Numéro de téléphone manquant'));
      return;
    }

    final tel = client.telephone!.replaceAll(RegExp(r'[^0-9]'), '');
    final montant = _formatGNF(dette.montantRestant);
    final message = Uri.encodeComponent(
      'Bonjour ${client.nom}, nous vous rappelons qu\'une dette de $montant GNF '
      'est en attente de règlement. Merci de contacter votre boutique. 🙏',
    );

    final url = Uri.parse('https://wa.me/$tel?text=$message');
    if (await canLaunchUrl(url)) {
      await launchUrl(url, mode: LaunchMode.externalApplication);
    } else {
      emit(state.copyWith(errorMessage: 'WhatsApp non disponible'));
    }
  }

  List<Dette> _appliquerFiltre(List<Dette> dettes, StatutDette? statut) {
    if (statut == null) return dettes;
    return dettes.where((d) => d.statut == statut).toList();
  }

  String _formatGNF(int montant) {
    final str = montant.toString();
    final buffer = StringBuffer();
    for (int i = 0; i < str.length; i++) {
      if (i > 0 && (str.length - i) % 3 == 0) buffer.write(' ');
      buffer.write(str[i]);
    }
    return buffer.toString();
  }

  @override
  Future<void> close() {
    _dettesSubscription?.cancel();
    return super.close();
  }
}