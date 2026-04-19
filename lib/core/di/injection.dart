import 'package:get_it/get_it.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../../data/local/database/app_database.dart';
import '../../data/repositories/repository_impls.dart';
import '../services/supabase_sync_service.dart';
import '../../domain/repositories/repositories.dart';
import '../../domain/usecases/usecases.dart';
import '../services/app_settings_service.dart';
import '../../presentation/blocs/auth/auth_bloc.dart';
import '../../presentation/blocs/client/client_bloc.dart';
import '../../presentation/blocs/dette/dette_bloc.dart';
import '../../presentation/blocs/stock/stock_bloc.dart';
import '../../presentation/blocs/sync/sync_bloc.dart';
import '../../presentation/blocs/vente/vente_bloc.dart';

final getIt = GetIt.instance;

Future<void> configureDependencies() async {
  if (getIt.isRegistered<AuthBloc>()) return;

  getIt.registerLazySingleton<AppDatabase>(() => AppDatabase());
  getIt.registerLazySingleton<SupabaseSyncService>(
    () => SupabaseSyncService(Supabase.instance.client),
  );

  getIt.registerLazySingleton<AppSettingsService>(() => AppSettingsService());
  getIt.registerLazySingleton<SyncRepository>(
    () => SyncRepositoryImpl(
      getIt<AppDatabase>(),
      getIt<SupabaseSyncService>(),
    ),
  );
  getIt.registerLazySingleton<AuthRepository>(
    () => AuthRepositoryImpl(getIt<AppDatabase>(), getIt<SyncRepository>()),
  );
  getIt.registerLazySingleton<ProduitRepository>(
    () => ProduitRepositoryImpl(getIt<AppDatabase>()),
  );
  getIt.registerLazySingleton<ClientRepository>(
    () => ClientRepositoryImpl(getIt<AppDatabase>()),
  );
  getIt.registerLazySingleton<VenteRepository>(
    () => VenteRepositoryImpl(getIt<AppDatabase>()),
  );
  getIt.registerLazySingleton<DetteRepository>(
    () => DetteRepositoryImpl(getIt<AppDatabase>()),
  );

  getIt.registerLazySingleton<AbonnementRepository>(
      () => AbonnementRepositoryImpl());

  getIt.registerFactory(
    () => EnregistrerVenteUseCase(
      getIt<VenteRepository>(),
      getIt<ProduitRepository>(),
      getIt<DetteRepository>(),
      getIt<ClientRepository>(),
      getIt<AbonnementRepository>(),
    ),
  );
  getIt.registerFactory(
    () => EnregistrerPaiementUseCase(
      getIt<DetteRepository>(),
      getIt<ClientRepository>(),
    ),
  );
  getIt.registerFactory(
    () => ParseCommandeVocaleUseCase(
      getIt<ProduitRepository>(),
      getIt<ClientRepository>(),
    ),
  );
  getIt.registerFactory(
    () => GetStatistiquesUseCase(
      getIt<VenteRepository>(),
      getIt<DetteRepository>(),
    ),
  );

  getIt.registerFactory(() => AuthBloc(getIt<AuthRepository>()));
  getIt.registerFactory(
     () => SyncBloc(getIt<SyncRepository>(), getIt<AuthRepository>(), getIt<AppSettingsService>()),
  );
  getIt.registerFactory(() => StockBloc(getIt<ProduitRepository>()));
  getIt.registerFactory(() => ClientBloc(getIt<ClientRepository>()));
  getIt.registerFactory(
    () => DetteBloc(
        getIt<DetteRepository>(), getIt<EnregistrerPaiementUseCase>()),
  );
  getIt.registerFactory(
    () => VenteBloc(
      getIt<EnregistrerVenteUseCase>(),
      getIt<ParseCommandeVocaleUseCase>(),
    ),
  );
}
