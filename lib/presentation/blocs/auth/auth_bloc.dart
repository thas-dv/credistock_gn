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
    on<AuthLogout>(_onLogout);
  }

  // 🔍 Vérifie si boutique existe localement
  Future<void> _onCheck(
      AuthCheckRequested event, Emitter<AuthState> emit) async {
    emit(state.copyWith(status: AuthStatus.checking));

    final boutiqueIdResult = await _authRepo.getBoutiqueId();

    boutiqueIdResult.fold(
      (failure) {
        emit(state.copyWith(status: AuthStatus.unauthenticated));
      },
      (id) {
        print("Boutique ID récupéré: $id"); // DEBUG
        emit(state.copyWith(
          status: AuthStatus.unauthenticated,
          boutiqueId: id,
        ));
      },
    );
  }

  // 🔐 Vérification PIN
  Future<void> _onPinSubmitted(
      AuthPinSubmitted event, Emitter<AuthState> emit) async {
    if (state.boutiqueId == null) {
      emit(state.copyWith(
        status: AuthStatus.error,
        errorMessage: "Boutique introuvable",
      ));
      return;
    }

    emit(state.copyWith(status: AuthStatus.checking));

    final inputPin = event.pin.trim(); // 🔥 IMPORTANT

    print("PIN saisi: $inputPin"); // DEBUG
    print("Boutique ID: ${state.boutiqueId}");

    final result = await _authRepo.verifierPin(state.boutiqueId!, inputPin);

    result.fold(
      (failure) {
        emit(state.copyWith(
          status: AuthStatus.error,
          errorMessage: "Erreur serveur",
        ));
      },
      (valide) {
        print("PIN valide ? $valide"); // DEBUG

        if (valide) {
          emit(state.copyWith(
            status: AuthStatus.authenticated,
            errorMessage: null,
          ));
        } else {
          emit(state.copyWith(
            status: AuthStatus.error,
            errorMessage: "PIN incorrect",
          ));
        }
      },
    );
  }

  void _onLogout(AuthLogout event, Emitter<AuthState> emit) {
    emit(state.copyWith(
      status: AuthStatus.unauthenticated,
      errorMessage: null,
    ));
  }
}
