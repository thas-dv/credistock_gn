import 'dart:async';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import 'package:injectable/injectable.dart';

import '../../../domain/entities/entities.dart';
import '../../../domain/repositories/repositories.dart';
import '../../../core/errors/failures.dart';

// ============================================================
// EVENTS
// ============================================================

abstract class StockEvent extends Equatable {
  const StockEvent();
  @override
  List<Object?> get props => [];
}

class StockWatchStarted extends StockEvent {
  final String boutiqueId;
  const StockWatchStarted(this.boutiqueId);
  @override
  List<Object?> get props => [boutiqueId];
}

class StockSearchChanged extends StockEvent {
  final String query;
  const StockSearchChanged(this.query);
  @override
  List<Object?> get props => [query];
}

class StockCategorieChanged extends StockEvent {
  final String? categorie;
  const StockCategorieChanged(this.categorie);
  @override
  List<Object?> get props => [categorie];
}

class StockProduitAjouter extends StockEvent {
  final Produit produit;
  const StockProduitAjouter(this.produit);
  @override
  List<Object?> get props => [produit];
}

class StockProduitModifier extends StockEvent {
  final Produit produit;
  const StockProduitModifier(this.produit);
  @override
  List<Object?> get props => [produit];
}

class StockProduitSupprimer extends StockEvent {
  final String produitId;
  const StockProduitSupprimer(this.produitId);
  @override
  List<Object?> get props => [produitId];
}

class _ProduitsUpdated extends StockEvent {
  final List<Produit> produits;
  const _ProduitsUpdated(this.produits);
  @override
  List<Object?> get props => [produits];
}

// ============================================================
// STATE
// ============================================================

enum StockStatus { initial, loading, loaded, error }

class StockState extends Equatable {
  final List<Produit> produits;
  final List<Produit> produitsFiltres;
  final List<Produit> produitsEnAlerte;
  final StockStatus status;
  final String query;
  final String? categorieFiltre;
  final String? errorMessage;

  const StockState({
    this.produits = const [],
    this.produitsFiltres = const [],
    this.produitsEnAlerte = const [],
    this.status = StockStatus.initial,
    this.query = '',
    this.categorieFiltre,
    this.errorMessage,
  });

  int get totalProduits => produits.length;
  int get nombreAlertes => produitsEnAlerte.length;

  StockState copyWith({
    List<Produit>? produits,
    List<Produit>? produitsFiltres,
    List<Produit>? produitsEnAlerte,
    StockStatus? status,
    String? query,
    String? categorieFiltre,
    String? errorMessage,
  }) {
    return StockState(
      produits: produits ?? this.produits,
      produitsFiltres: produitsFiltres ?? this.produitsFiltres,
      produitsEnAlerte: produitsEnAlerte ?? this.produitsEnAlerte,
      status: status ?? this.status,
      query: query ?? this.query,
      categorieFiltre: categorieFiltre ?? this.categorieFiltre,
      errorMessage: errorMessage,
    );
  }

  @override
  List<Object?> get props => [produits, produitsFiltres, produitsEnAlerte, status, query, categorieFiltre];
}

// ============================================================
// BLOC
// ============================================================

@injectable
class StockBloc extends Bloc<StockEvent, StockState> {
  final ProduitRepository _produitRepo;
  StreamSubscription<List<Produit>>? _produitsSubscription;

  StockBloc(this._produitRepo) : super(const StockState()) {
    on<StockWatchStarted>(_onWatchStarted);
    on<StockSearchChanged>(_onSearchChanged);
    on<StockCategorieChanged>(_onCategorieChanged);
    on<StockProduitAjouter>(_onAjouter);
    on<StockProduitModifier>(_onModifier);
    on<StockProduitSupprimer>(_onSupprimer);
    on<_ProduitsUpdated>(_onProduitsUpdated);
  }

  Future<void> _onWatchStarted(StockWatchStarted event, Emitter<StockState> emit) async {
    emit(state.copyWith(status: StockStatus.loading));
    await _produitsSubscription?.cancel();
    _produitsSubscription = _produitRepo
        .watchProduits(event.boutiqueId)
        .listen((produits) => add(_ProduitsUpdated(produits)));
  }

  void _onProduitsUpdated(_ProduitsUpdated event, Emitter<StockState> emit) {
    final enAlerte = event.produits.where((p) => p.estEnAlerteStock).toList();
    emit(state.copyWith(
      produits: event.produits,
      produitsFiltres: _appliquerFiltres(event.produits, state.query, state.categorieFiltre),
      produitsEnAlerte: enAlerte,
      status: StockStatus.loaded,
    ));
  }

  void _onSearchChanged(StockSearchChanged event, Emitter<StockState> emit) {
    emit(state.copyWith(
      query: event.query,
      produitsFiltres: _appliquerFiltres(state.produits, event.query, state.categorieFiltre),
    ));
  }

  void _onCategorieChanged(StockCategorieChanged event, Emitter<StockState> emit) {
    emit(state.copyWith(
      categorieFiltre: event.categorie,
      produitsFiltres: _appliquerFiltres(state.produits, state.query, event.categorie),
    ));
  }

  Future<void> _onAjouter(StockProduitAjouter event, Emitter<StockState> emit) async {
    final result = await _produitRepo.ajouterProduit(event.produit);
    result.fold(
      (failure) => emit(state.copyWith(errorMessage: failure.message)),
      (_) {}, // Stream met à jour automatiquement
    );
  }

  Future<void> _onModifier(StockProduitModifier event, Emitter<StockState> emit) async {
    final result = await _produitRepo.modifierProduit(event.produit);
    result.fold(
      (failure) => emit(state.copyWith(errorMessage: failure.message)),
      (_) {},
    );
  }

  Future<void> _onSupprimer(StockProduitSupprimer event, Emitter<StockState> emit) async {
    final result = await _produitRepo.supprimerProduit(event.produitId);
    result.fold(
      (failure) => emit(state.copyWith(errorMessage: failure.message)),
      (_) {},
    );
  }

  List<Produit> _appliquerFiltres(
    List<Produit> produits,
    String query,
    String? categorie,
  ) {
    return produits.where((p) {
      final matchQuery = query.isEmpty ||
          p.nom.toLowerCase().contains(query.toLowerCase());
      final matchCat = categorie == null ||
          p.categorie.name == categorie;
      return matchQuery && matchCat;
    }).toList();
  }

  @override
  Future<void> close() {
    _produitsSubscription?.cancel();
    return super.close();
  }
}