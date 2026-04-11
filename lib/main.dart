import 'package:credistock_gn/pages/home_page.dart';
import 'package:credistock_gn/pages/login_page.dart';
import 'package:credistock_gn/pages/register_page.dart';
import 'package:flutter/material.dart';

import 'package:supabase_flutter/supabase_flutter.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

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

  await Supabase.initialize(url: supabaseUrl, anonKey: supabaseAnonKey);

  runApp(const CrediStockApp());
}

class CrediStockApp extends StatefulWidget {
  const CrediStockApp({super.key});

  @override
  State<CrediStockApp> createState() => _CrediStockAppState();
}

class _CrediStockAppState extends State<CrediStockApp> {
  bool _showRegister = false;

  void _openRegister() => setState(() => _showRegister = true);
  void _openLogin() => setState(() => _showRegister = false);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'CrédiStock',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.green),
        useMaterial3: true,
      ),
      home: StreamBuilder<AuthState>(
        stream: Supabase.instance.client.auth.onAuthStateChange,
        initialData: AuthState(
          AuthChangeEvent.initialSession,
          Supabase.instance.client.auth.currentSession,
        ),
        builder: (context, snapshot) {
          final session = snapshot.data?.session;

          if (session != null) {
            return const HomePage();
          }

          return _showRegister
              ? RegisterPage(onBackToLogin: _openLogin)
              : LoginPage(onGoToRegister: _openRegister);
        },
      ),
    );
  }
}
