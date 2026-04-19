import 'package:credistock_gn/core/di/injection.dart';
import 'package:credistock_gn/core/observers/app_bloc_observer.dart';
import 'package:credistock_gn/core/router/app_router.dart';
import 'package:credistock_gn/core/theme/app_theme.dart';
import 'package:credistock_gn/core/services/app_settings_service.dart';
import 'package:credistock_gn/presentation/blocs/auth/auth_bloc.dart';
import 'package:credistock_gn/presentation/blocs/client/client_bloc.dart';
import 'package:credistock_gn/presentation/blocs/dette/dette_bloc.dart';
import 'package:credistock_gn/presentation/blocs/stock/stock_bloc.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:credistock_gn/presentation/blocs/sync/sync_bloc.dart';
import 'package:credistock_gn/presentation/blocs/vente/vente_bloc.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:intl/date_symbol_data_local.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_localizations/flutter_localizations.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  Bloc.observer = AppBlocObserver();
  await initializeDateFormatting('fr_FR');
  SystemChrome.setEnabledSystemUIMode(SystemUiMode.edgeToEdge);
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.dark,
      systemNavigationBarColor: Colors.white,
      systemNavigationBarIconBrightness: Brightness.dark,
    ),
  );
  // // Supabase
  const supabaseUrl = String.fromEnvironment(
    'SUPABASE_URL',
    defaultValue: 'https://gzaekbnodohycalquufi.supabase.co',
  );
  const supabaseAnonKey = String.fromEnvironment(
    'SUPABASE_ANON_KEY',
    defaultValue:
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd6YWVrYm5vZG9oeWNhbHF1dWZpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUxMjIxMTgsImV4cCI6MjA4MDY5ODExOH0.W-8-1PqUHN2FSaGzEWRuwky4ZbExuyB5mlW69gd1qbU',
  );

  await Supabase.initialize(url: supabaseUrl, anonKey: supabaseAnonKey);
  await configureDependencies();
  await Hive.initFlutter();
  await getIt<AppSettingsService>().init();

  runApp(const CrediStockApp());
}

class CrediStockApp extends StatelessWidget {
  const CrediStockApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiBlocProvider(
      providers: [
        BlocProvider<AuthBloc>(
          create: (_) => getIt<AuthBloc>()..add(AuthCheckRequested()),
        ),
        BlocProvider<SyncBloc>(
          create: (_) => getIt<SyncBloc>()..add(SyncStartWatching()),
        ),
        BlocProvider<StockBloc>(create: (_) => getIt<StockBloc>()),
        BlocProvider<ClientBloc>(create: (_) => getIt<ClientBloc>()),
        BlocProvider<DetteBloc>(create: (_) => getIt<DetteBloc>()),
        BlocProvider<VenteBloc>(create: (_) => getIt<VenteBloc>()),
      ],
      child: ValueListenableBuilder<AppSettings>(
        valueListenable: getIt<AppSettingsService>().settings,
        builder: (context, settings, _) {
          return MaterialApp.router(
            title: 'CrédiStock ',
            debugShowCheckedModeBanner: false,
            theme: AppTheme.light,
            darkTheme: AppTheme.dark,
            themeMode: ThemeMode.system,
            locale: settings.locale,
            supportedLocales: const [Locale('fr'), Locale('en'), Locale('ar')],
            localizationsDelegates: const [
              GlobalMaterialLocalizations.delegate,
              GlobalWidgetsLocalizations.delegate,
              GlobalCupertinoLocalizations.delegate,
            ],
            routerConfig: AppRouter.router,
          );
        },
      ),
    );
  }
}
