import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import 'core/di/injection.dart';
import 'core/router/app_router.dart';
import 'core/theme/app_theme.dart';
import 'core/observers/app_bloc_observer.dart';

import 'presentation/blocs/sync/sync_bloc.dart';
import 'presentation/blocs/auth/auth_bloc.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Orientation portrait uniquement
  await SystemChrome.setPreferredOrientations([DeviceOrientation.portraitUp]);

 // Firebase (tolérant si config absente en dev)
  try {
    await Firebase.initializeApp();
  } catch (_) {
    // Ignore en environnement local non configuré.
  }
 
  // Supabase
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

  // Hive (cache rapide)
  await Hive.initFlutter();
  await Hive.openBox('preferences');
  await Hive.openBox('sync_queue');

  // Injection de dépendances
  await configureDependencies();

  // BLoC observer (logs dev)
  Bloc.observer = AppBlocObserver();

  runApp(const CrediStockApp());
}

class CrediStockApp extends StatelessWidget {
  const CrediStockApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiBlocProvider(
      providers: [
        BlocProvider(create: (_) => getIt<AuthBloc>()..add(AuthCheckRequested())),
        BlocProvider(create: (_) => getIt<SyncBloc>()..add(SyncStartWatching())),
      ],
      child: MaterialApp.router(
        title: 'CrédiStock GN',
        debugShowCheckedModeBanner: false,
        theme: AppTheme.light,
        darkTheme: AppTheme.dark,
        themeMode: ThemeMode.system,
        routerConfig: AppRouter.router,
      ),
    );
  }
}
