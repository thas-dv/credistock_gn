// ============================================================
// lib/core/observers/app_bloc_observer.dart
// ============================================================

import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:logger/logger.dart';

class AppBlocObserver extends BlocObserver {
  final _log = Logger(printer: PrettyPrinter(methodCount: 0));

  @override
  void onEvent(Bloc bloc, Object? event) {
    super.onEvent(bloc, event);
    _log.d('[${bloc.runtimeType}] EVENT: ${event.runtimeType}');
  }

  @override
  void onChange(BlocBase bloc, Change change) {
    super.onChange(bloc, change);
    _log.d('[${bloc.runtimeType}] STATE: ${change.nextState.runtimeType}');
  }

  @override
  void onError(BlocBase bloc, Object error, StackTrace stackTrace) {
    _log.e('[${bloc.runtimeType}] ERROR: $error');
    super.onError(bloc, error, stackTrace);
  }
}