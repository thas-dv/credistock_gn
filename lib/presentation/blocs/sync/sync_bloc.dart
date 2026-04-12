import 'dart:async';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import 'package:injectable/injectable.dart';

import '../../../domain/repositories/repositories.dart';

// ============================================================
// EVENTS
// ============================================================

abstract class SyncEvent extends Equatable {
  const SyncEvent();
  @override
  List<Object?> get props => [];
}

class SyncStartWatching extends SyncEvent {}
class SyncManuel extends SyncEvent {
  final String boutiqueId;
  const SyncManuel(this.boutiqueId);
}
class _ConnectivityChanged extends SyncEvent {
  final bool estConnecte;
  const _ConnectivityChanged(this.estConnecte);
  @override
  List<Object?> get props => [estConnecte];
}

class _AutoSyncTick extends SyncEvent {}

// ============================================================
// STATE
// ============================================================

class SyncState extends Equatable {
  final bool estConnecte;
  final SyncStatus status;
  final int elementsEnAttente;
  final DateTime? derniereSyncReussie;
  final String? errorMessage;

  const SyncState({
    this.estConnecte = false,
    this.status = SyncStatus.idle,
    this.elementsEnAttente = 0,
    this.derniereSyncReussie,
    this.errorMessage,
  });

  bool get aSynchroniser => elementsEnAttente > 0;

  SyncState copyWith({
    bool? estConnecte,
    SyncStatus? status,
    int? elementsEnAttente,
    DateTime? derniereSyncReussie,
    String? errorMessage,
  }) {
    return SyncState(
      estConnecte: estConnecte ?? this.estConnecte,
      status: status ?? this.status,
      elementsEnAttente: elementsEnAttente ?? this.elementsEnAttente,
      derniereSyncReussie: derniereSyncReussie ?? this.derniereSyncReussie,
      errorMessage: errorMessage,
    );
  }

  @override
  List<Object?> get props => [estConnecte, status, elementsEnAttente];
}

// ============================================================
// BLOC
// ============================================================

@singleton
@injectable
class SyncBloc extends Bloc<SyncEvent, SyncState> {
  final SyncRepository _syncRepo;
  final AuthRepository _authRepository;
  final Connectivity _connectivity = Connectivity();
  StreamSubscription? _connectivitySub;
  Timer? _syncTimer;

   SyncBloc(this._syncRepo, this._authRepository) : super(const SyncState()) {
    on<SyncStartWatching>(_onStartWatching);
    on<SyncManuel>(_onManuel);
    on<_ConnectivityChanged>(_onConnectivityChanged);
    on<_AutoSyncTick>(_onAutoSyncTick);
  }

  Future<void> _onStartWatching(SyncStartWatching event, Emitter<SyncState> emit) async {
    // Vérifier l'état initial
    final result = await _connectivity.checkConnectivity();
    final estConnecte = !result.contains(ConnectivityResult.none);
    emit(state.copyWith(estConnecte: estConnecte));

    // Écouter les changements de connectivité
    _connectivitySub = _connectivity.onConnectivityChanged.listen((results) {
      add(_ConnectivityChanged(!results.contains(ConnectivityResult.none)));
    });

    // Sync périodique toutes les 5 minutes si connecté
    _syncTimer = Timer.periodic(const Duration(minutes: 5), (_) {
      if (state.estConnecte && state.aSynchroniser) {
        // Le boutiqueId sera injecté depuis le contexte
        // add(SyncManuel(boutiqueId));
        add(_AutoSyncTick());
      }
    });

    // Compter les éléments en attente
    final count = await _syncRepo.getNombreElementsNonSynces();
    emit(state.copyWith(elementsEnAttente: count));

    await _synchroniserSiPossible(emit);
  }

  Future<void> _onAutoSyncTick(
    _AutoSyncTick event,
    Emitter<SyncState> emit,
  ) async {
    await _synchroniserSiPossible(emit);
  }

  Future<void> _onConnectivityChanged(
    _ConnectivityChanged event,
    Emitter<SyncState> emit,
  ) async {
    emit(state.copyWith(estConnecte: event.estConnecte));

    // Déclencher sync automatique dès reconnexion
    if (event.estConnecte && state.aSynchroniser) {
      emit(state.copyWith(status: SyncStatus.syncing));
      // Sync déclenchée — boutiqueId depuis les prefs
      await _synchroniserSiPossible(emit);
    }
  }

  Future<void> _onManuel(SyncManuel event, Emitter<SyncState> emit) async {
    if (!state.estConnecte) return;
    emit(state.copyWith(status: SyncStatus.syncing));

    final result = await _syncRepo.synchroniser(event.boutiqueId);

    result.fold(
      (failure) => emit(state.copyWith(
        status: SyncStatus.error,
        errorMessage: failure.message,
      )),
      (_) async {
        final count = await _syncRepo.getNombreElementsNonSynces();
        emit(state.copyWith(
          status: SyncStatus.success,
          elementsEnAttente: count,
          derniereSyncReussie: DateTime.now(),
        ));
      },
    );
  }

 Future<void> _synchroniserSiPossible(Emitter<SyncState> emit) async {
    if (!state.estConnecte) return;

    final boutiqueIdResult = await _authRepository.getBoutiqueId();
    await boutiqueIdResult.fold(
      (_) async {},
      (boutiqueId) async {
        final result = await _syncRepo.synchroniser(boutiqueId);
        result.fold(
          (failure) => emit(state.copyWith(
            status: SyncStatus.error,
            errorMessage: failure.message,
          )),
          (_) async {
            final count = await _syncRepo.getNombreElementsNonSynces();
            emit(state.copyWith(
              status: SyncStatus.success,
              elementsEnAttente: count,
              derniereSyncReussie: DateTime.now(),
            ));
          },
        );
      },
    );
  }
  @override
  Future<void> close() {
    _connectivitySub?.cancel();
    _syncTimer?.cancel();
    return super.close();
  }
}