import 'package:get_it/get_it.dart';
import '../../data/repositories/repository_impls.dart';
import '../../domain/repositories/repositories.dart';
import '../../domain/usecases/usecases.dart';
import '../../presentation/blocs/auth/auth_bloc.dart';
import '../../presentation/blocs/client/client_bloc.dart';
import '../../presentation/blocs/dette/dette_bloc.dart';
import '../../presentation/blocs/stock/stock_bloc.dart';
import '../../presentation/blocs/sync/sync_bloc.dart';
import '../../presentation/blocs/vente/vente_bloc.dart';

final getIt = GetIt.instance;

Future<void> configureDependencies() async {
  if (getIt.isRegistered<AuthBloc>()) return;

  getIt.registerLazySingleton<InMemoryStore>(() => InMemoryStore());

  getIt.registerLazySingleton<AuthRepository>(() => AuthRepositoryImpl());
  getIt.registerLazySingleton<ProduitRepository>(
    () => ProduitRepositoryImpl(getIt<InMemoryStore>()),
  );
  getIt.registerLazySingleton<ClientRepository>(
    () => ClientRepositoryImpl(getIt<InMemoryStore>()),
  );
  getIt.registerLazySingleton<VenteRepository>(
    () => VenteRepositoryImpl(getIt<InMemoryStore>()),
  );
  getIt.registerLazySingleton<DetteRepository>(
    () => DetteRepositoryImpl(getIt<InMemoryStore>()),
  );
  getIt.registerLazySingleton<SyncRepository>(() => SyncRepositoryImpl());
  getIt.registerLazySingleton<AbonnementRepository>(() => AbonnementRepositoryImpl());

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
  getIt.registerFactory(() => SyncBloc(getIt<SyncRepository>()));
  getIt.registerFactory(() => StockBloc(getIt<ProduitRepository>()));
  getIt.registerFactory(() => ClientBloc(getIt<ClientRepository>()));
  getIt.registerFactory(
    () => DetteBloc(getIt<DetteRepository>(), getIt<EnregistrerPaiementUseCase>()),
  );
  getIt.registerFactory(
    () => VenteBloc(
      getIt<EnregistrerVenteUseCase>(),
      getIt<ParseCommandeVocaleUseCase>(),
    ),
  );
}