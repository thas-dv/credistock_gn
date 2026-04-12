import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import 'package:injectable/injectable.dart';

import '../../../domain/repositories/repositories.dart';

abstract class AuthEvent extends Equatable {
  const AuthEvent();
  @override
  List<Object?> get props => [];
}

class AuthCheckRequested extends AuthEvent {}

class AuthPinSubmitted extends AuthEvent {
  final String pin;
  const AuthPinSubmitted(this.pin);

  @override
  List<Object?> get props => [pin];
}

class AuthLoginSubmitted extends AuthEvent {
  final String identifiant;
  final String motDePasse;

  const AuthLoginSubmitted({
    required this.identifiant,
    required this.motDePasse,
  });

  @override
  List<Object?> get props => [identifiant, motDePasse];
}

class AuthRegisterSubmitted extends AuthEvent {

  final String nom;
  final String role;
   final String prenom;
  final String telephone;
  final String motDePasse;
  final String boutiqueNom;
  final String boutiqueAdresse;
 

  const AuthRegisterSubmitted({
   
    required this.nom,
    required this.role,
     required this.prenom,
    required this.telephone,
    required this.motDePasse,
    required this.boutiqueNom,
    required this.boutiqueAdresse,

  });

  @override
  List<Object?> get props => [
        nom,
        prenom,
        telephone,
        role,
        motDePasse,
        boutiqueNom,
        boutiqueAdresse,

      ];
}

class AuthLogout extends AuthEvent {}

// ============================================================

enum AuthStatus { initial, checking, authenticated, unauthenticated, error }

class AuthState extends Equatable {
  final AuthStatus status;
  final String? boutiqueId;
  final String? errorMessage;

  const AuthState({
    this.status = AuthStatus.initial,
    this.boutiqueId,
    this.errorMessage,
  });

  bool get estAuthentifie => status == AuthStatus.authenticated;

  AuthState copyWith({
    AuthStatus? status,
    String? boutiqueId,
    String? errorMessage,
  }) {
    return AuthState(
      status: status ?? this.status,
      boutiqueId: boutiqueId ?? this.boutiqueId,
      errorMessage: errorMessage,
    );
  }

  @override
  List<Object?> get props => [status, boutiqueId, errorMessage];
}

// ============================================================

@singleton
@injectable
class AuthBloc extends Bloc<AuthEvent, AuthState> {
  final AuthRepository _authRepo;

  AuthBloc(this._authRepo) : super(const AuthState()) {
    on<AuthCheckRequested>(_onCheck);
    on<AuthPinSubmitted>(_onPinSubmitted);
    on<AuthLoginSubmitted>(_onLoginSubmitted);
    on<AuthRegisterSubmitted>(_onRegisterSubmitted);
    on<AuthLogout>(_onLogout);
  }

  // 🔍 Vérifie si boutique existe localement
  Future<void> _onCheck(AuthCheckRequested event, Emitter<AuthState> emit) async {
    emit(state.copyWith(status: AuthStatus.checking));

    final boutiqueIdResult = await _authRepo.getBoutiqueId();
    final estConnecte = await _authRepo.estConnecte();

    boutiqueIdResult.fold(
      (_) => emit(state.copyWith(status: AuthStatus.unauthenticated)),
      (id) => emit(state.copyWith(
        status: estConnecte ? AuthStatus.authenticated : AuthStatus.unauthenticated,
        boutiqueId: id,
        errorMessage: null,
      )),
    );
  }

  // 🔐 Vérification PIN
  Future<void> _onLoginSubmitted(AuthLoginSubmitted event, Emitter<AuthState> emit) async {
    emit(state.copyWith(status: AuthStatus.checking, errorMessage: null));

    final result = await _authRepo.seConnecter(
      identifiant: event.identifiant,
      motDePasse: event.motDePasse,
    );

    result.fold(
      (failure) => emit(state.copyWith(
        status: AuthStatus.error,
        errorMessage: failure.message,
      )),
      (_) => emit(state.copyWith(status: AuthStatus.authenticated, errorMessage: null)),
    );
  }

  Future<void> _onRegisterSubmitted(AuthRegisterSubmitted event, Emitter<AuthState> emit) async {
    emit(state.copyWith(status: AuthStatus.checking, errorMessage: null));

    final result = await _authRepo.creerCompte(
     
      nom: event.nom,
      role: event.role,
      prenom: event.prenom,
      telephone: event.telephone,
      motDePasse: event.motDePasse,
      boutiqueNom: event.boutiqueNom,
      boutiqueAdresse: event.boutiqueAdresse,

    );

    result.fold(
      (failure) => emit(state.copyWith(
        status: AuthStatus.error,
        errorMessage: failure.message,
      )),
      (_) => emit(state.copyWith(status: AuthStatus.authenticated, errorMessage: null)),
    );
  }

  Future<void> _onPinSubmitted(AuthPinSubmitted event, Emitter<AuthState> emit) async {
    if (state.boutiqueId == null) {
      emit(state.copyWith(
        status: AuthStatus.error,
        errorMessage: "Boutique introuvable",
      ));
      return;
    }

    emit(state.copyWith(status: AuthStatus.checking));

    final result = await _authRepo.verifierPin(state.boutiqueId!, event.pin.trim());

    result.fold(
       (_) => emit(state.copyWith(
        status: AuthStatus.error,
        errorMessage: 'Erreur serveur',
      )),
      (valide) {
        

        if (valide) {
          emit(state.copyWith(status: AuthStatus.authenticated, errorMessage: null));
        } else {
         emit(state.copyWith(status: AuthStatus.error, errorMessage: 'PIN incorrect'));
        }
      },
    );
  }

  Future<void> _onLogout(AuthLogout event, Emitter<AuthState> emit) async {
    await _authRepo.deconnecter();
    emit(state.copyWith(
      status: AuthStatus.unauthenticated,
      errorMessage: null,
    ));
  }
}
