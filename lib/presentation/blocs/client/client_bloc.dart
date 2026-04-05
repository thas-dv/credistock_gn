import 'dart:async';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import 'package:injectable/injectable.dart';

import '../../../domain/entities/entities.dart';
import '../../../domain/repositories/repositories.dart';

// ============================================================
// EVENTS
// ============================================================

abstract class ClientEvent extends Equatable {
  const ClientEvent();
  @override
  List<Object?> get props => [];
}

class ClientWatchStarted extends ClientEvent {
  final String boutiqueId;
  const ClientWatchStarted(this.boutiqueId);
  @override
  List<Object?> get props => [boutiqueId];
}

class ClientSearchChanged extends ClientEvent {
  final String query;
  const ClientSearchChanged(this.query);
  @override
  List<Object?> get props => [query];
}

class ClientScoreFiltered extends ClientEvent {
  final ScoreClient? score;
  const ClientScoreFiltered(this.score);
  @override
  List<Object?> get props => [score];
}

class ClientAjoute extends ClientEvent {
  final String nom;
  final String? telephone;
  final String boutiqueId;
  const ClientAjoute({required this.nom, this.telephone, required this.boutiqueId});
  @override
  List<Object?> get props => [nom, telephone];
}

class _ClientsUpdated extends ClientEvent {
  final List<Client> clients;
  const _ClientsUpdated(this.clients);
  @override
  List<Object?> get props => [clients];
}

// ============================================================
// STATE
// ============================================================

enum ClientStatus { initial, loading, loaded, saving, error }

class ClientState extends Equatable {
  final List<Client> clients;
  final List<Client> clientsFiltres;
  final ClientStatus status;
  final String query;
  final ScoreClient? filtreScore;
  final String? errorMessage;

  const ClientState({
    this.clients = const [],
    this.clientsFiltres = const [],
    this.status = ClientStatus.initial,
    this.query = '',
    this.filtreScore,
    this.errorMessage,
  });

  int get totalClients => clients.length;
  int get clientsAvecDettes => clients.where((c) => c.aDesDetteEnCours).length;

  ClientState copyWith({
    List<Client>? clients,
    List<Client>? clientsFiltres,
    ClientStatus? status,
    String? query,
    ScoreClient? filtreScore,
    String? errorMessage,
  }) {
    return ClientState(
      clients: clients ?? this.clients,
      clientsFiltres: clientsFiltres ?? this.clientsFiltres,
      status: status ?? this.status,
      query: query ?? this.query,
      filtreScore: filtreScore ?? this.filtreScore,
      errorMessage: errorMessage,
    );
  }

  @override
  List<Object?> get props => [clients, clientsFiltres, status, query, filtreScore];
}

// ============================================================
// BLOC
// ============================================================

@injectable
class ClientBloc extends Bloc<ClientEvent, ClientState> {
  final ClientRepository _clientRepo;
  StreamSubscription<List<Client>>? _clientsSubscription;

  ClientBloc(this._clientRepo) : super(const ClientState()) {
    on<ClientWatchStarted>(_onWatchStarted);
    on<ClientSearchChanged>(_onSearch);
    on<ClientScoreFiltered>(_onFiltrer);
    on<ClientAjoute>(_onAjouter);
    on<_ClientsUpdated>(_onClientsUpdated);
  }

  Future<void> _onWatchStarted(ClientWatchStarted event, Emitter<ClientState> emit) async {
    emit(state.copyWith(status: ClientStatus.loading));
    await _clientsSubscription?.cancel();
    _clientsSubscription = _clientRepo
        .watchClients(event.boutiqueId)
        .listen((clients) => add(_ClientsUpdated(clients)));
  }

  void _onClientsUpdated(_ClientsUpdated event, Emitter<ClientState> emit) {
    emit(state.copyWith(
      clients: event.clients,
      clientsFiltres: _appliquerFiltres(event.clients, state.query, state.filtreScore),
      status: ClientStatus.loaded,
    ));
  }

  void _onSearch(ClientSearchChanged event, Emitter<ClientState> emit) {
    emit(state.copyWith(
      query: event.query,
      clientsFiltres: _appliquerFiltres(state.clients, event.query, state.filtreScore),
    ));
  }

  void _onFiltrer(ClientScoreFiltered event, Emitter<ClientState> emit) {
    emit(state.copyWith(
      filtreScore: event.score,
      clientsFiltres: _appliquerFiltres(state.clients, state.query, event.score),
    ));
  }

  Future<void> _onAjouter(ClientAjoute event, Emitter<ClientState> emit) async {
    emit(state.copyWith(status: ClientStatus.saving));

    final client = Client(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      boutiqueId: event.boutiqueId,
      nom: event.nom,
      telephone: event.telephone,
      score: ScoreClient.bon,
      totalDu: 0,
      nombreDettes: 0,
      nombresRemboursements: 0,
      synced: false,
      createdAt: DateTime.now(),
    );

    final result = await _clientRepo.ajouterClient(client);
    result.fold(
      (failure) => emit(state.copyWith(
        status: ClientStatus.error,
        errorMessage: failure.message,
      )),
      (_) => emit(state.copyWith(status: ClientStatus.loaded)),
    );
  }

  List<Client> _appliquerFiltres(
    List<Client> clients,
    String query,
    ScoreClient? score,
  ) {
    return clients.where((c) {
      final matchQuery = query.isEmpty ||
          c.nom.toLowerCase().contains(query.toLowerCase()) ||
          (c.telephone?.contains(query) ?? false);
      final matchScore = score == null || c.score == score;
      return matchQuery && matchScore;
    }).toList();
  }

  @override
  Future<void> close() {
    _clientsSubscription?.cancel();
    return super.close();
  }
}