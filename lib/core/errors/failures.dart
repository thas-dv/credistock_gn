// ============================================================
// lib/core/errors/failures.dart
// ============================================================

abstract class Failure {
  final String message;
  const Failure({this.message = 'Une erreur est survenue'});
}

class DatabaseFailure extends Failure {
  const DatabaseFailure({super.message = 'Erreur base de données locale'});
}

class NetworkFailure extends Failure {
  const NetworkFailure({super.message = 'Connexion internet requise'});
}

class SyncFailure extends Failure {
  const SyncFailure({super.message = 'Erreur de synchronisation'});
}

class StockInsuffisantFailure extends Failure {
  const StockInsuffisantFailure({super.message = 'Stock insuffisant'});
}

class ValidationFailure extends Failure {
  const ValidationFailure({required super.message});
}

class AuthFailure extends Failure {
  const AuthFailure({super.message = 'Authentification échouée'});
}

class LimitePlanFailure extends Failure {
  const LimitePlanFailure({super.message = 'Limite du plan atteinte'});
}