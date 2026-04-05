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

  AuthState copyWith({AuthStatus? status, String? boutiqueId, String? errorMessage}) {
    return AuthState(
      status: status ?? this.status,
      boutiqueId: boutiqueId ?? this.boutiqueId,
      errorMessage: errorMessage,
    );
  }

  @override
  List<Object?> get props => [status, boutiqueId];
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

  Future<void> _onCheck(AuthCheckRequested event, Emitter<AuthState> emit) async {
    emit(state.copyWith(status: AuthStatus.checking));
    final boutiqueId = await _authRepo.getBoutiqueId();
    boutiqueId.fold(
      (_) => emit(state.copyWith(status: AuthStatus.unauthenticated)),
      (id) => emit(state.copyWith(
        status: AuthStatus.unauthenticated, // Toujours demander le PIN
        boutiqueId: id,
      )),
    );
  }

  Future<void> _onPinSubmitted(AuthPinSubmitted event, Emitter<AuthState> emit) async {
    if (state.boutiqueId == null) return;
    emit(state.copyWith(status: AuthStatus.checking));

    final result = await _authRepo.verifierPin(state.boutiqueId!, event.pin);
    result.fold(
      (failure) => emit(state.copyWith(
        status: AuthStatus.error,
        errorMessage: 'PIN incorrect',
      )),
      (valide) => emit(state.copyWith(
        status: valide ? AuthStatus.authenticated : AuthStatus.error,
        errorMessage: valide ? null : 'PIN incorrect',
      )),
    );
  }

  void _onLogout(AuthLogout event, Emitter<AuthState> emit) {
    emit(state.copyWith(status: AuthStatus.unauthenticated));
  }
}