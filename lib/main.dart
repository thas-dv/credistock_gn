// lib/main.dart
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'core/theme/app_theme.dart';
import 'core/constants/app_constants.dart';
import 'presentation/providers/app_providers.dart';
import 'presentation/auth/login_page.dart';
import 'presentation/auth/register_page.dart';
import 'presentation/home/home_page.dart';
import 'presentation/stock/stock_page.dart';
import 'presentation/clients/clients_page.dart';
import 'presentation/dettes/dettes_page.dart';
import 'presentation/settings/settings_page.dart';
import 'presentation/sales/nouvelle_vente_page.dart';
import 'presentation/sales/ventes_page.dart';
import 'presentation/alertes/alertes_page.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Orientation portrait uniquement (app mobile commerce)
  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);

  // SharedPreferences
  final prefs = await SharedPreferences.getInstance();

  // Supabase
  await Supabase.initialize(
    url: AppConstants.supabaseUrl,
    anonKey: AppConstants.supabaseAnonKey,
    authOptions: const FlutterAuthClientOptions(
      autoRefreshToken: true,
      // persistSession: true,
    ),
  );

  runApp(
    ProviderScope(
      overrides: [
        sharedPrefsProvider.overrideWithValue(prefs),
      ],
      child: const CreditStockApp(),
    ),
  );
}

class CreditStockApp extends ConsumerWidget {
  const CreditStockApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final themeMode = ref.watch(themeProvider);
    final locale = ref.watch(localeProvider);

    return MaterialApp(
      title: 'CrédiStock GN',
      debugShowCheckedModeBanner: false,

      // Thèmes
      theme: AppTheme.light,
      darkTheme: AppTheme.dark,
      themeMode: themeMode,

      // Localisation (FR / EN / AR)
      locale: locale,
      localizationsDelegates: const [
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [
        Locale('fr'),
        Locale('en'),
        Locale('ar'),
      ],

      // Routes
      initialRoute: '/',
      routes: {
        '/': (_) => const _SplashRouter(),
        '/login': (_) => const LoginPage(),
        '/register': (_) => const RegisterPage(),
        '/home': (_) => const MainShell(),
        '/nouvelle-vente': (_) => const NouvelleVentePage(),
        '/ventes': (_) => const VentesPage(),
        '/stock': (_) => const StockPage(),
        '/clients': (_) => const ClientsPage(),
        '/dettes': (_) => const DettesPage(),
        '/parametres': (_) => const SettingsPage(),
        '/alertes': (_) => const AlertesPage(),
      },
    );
  }
}

// ── Splash / Router ────────────────────────────────────────

class _SplashRouter extends ConsumerWidget {
  const _SplashRouter();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final session = ref.watch(sessionProvider);
    final colors = Theme.of(context).extension<CreditStockColors>()!;

    // Si session active → home, sinon → login
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!context.mounted) return;
      Navigator.pushReplacementNamed(
        context,
        session.isLoggedIn ? '/home' : '/login',
      );
    });

    // Écran de démarrage
    return Scaffold(
      backgroundColor: colors.green,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.15),
                borderRadius: BorderRadius.circular(24),
              ),
              child:
                  const Icon(Icons.storefront, color: Colors.white, size: 56),
            ),
            const SizedBox(height: 20),
            const Text(
              'CrédiStock GN',
              style: TextStyle(
                color: Colors.white,
                fontSize: 28,
                fontWeight: FontWeight.bold,
                fontFamily: 'Cairo',
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Gestion simple pour commerçants',
              style: TextStyle(
                color: Colors.white.withOpacity(0.8),
                fontSize: 14,
                fontFamily: 'Cairo',
              ),
            ),
            const SizedBox(height: 40),
            const CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation(Colors.white),
              strokeWidth: 2,
            ),
          ],
        ),
      ),
    );
  }
}

// ── Shell principal avec Bottom Navigation ─────────────────

class MainShell extends ConsumerStatefulWidget {
  const MainShell({super.key});
  @override
  ConsumerState<MainShell> createState() => _MainShellState();
}

class _MainShellState extends ConsumerState<MainShell> {
  int _selectedIndex = 0;

  final _pages = const [
    HomePage(),
    StockPage(),
    ClientsPage(),
    DettesPage(),
    SettingsPage(),
  ];

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).extension<CreditStockColors>()!;
    final alertes = ref.watch(alertesNonLuesProvider);

    return Scaffold(
      body: _pages[_selectedIndex],
      floatingActionButton: _selectedIndex == 0
          ? FloatingActionButton.extended(
              onPressed: () => Navigator.pushNamed(context, '/nouvelle-vente'),
              backgroundColor: colors.green,
              foregroundColor: Colors.white,
              icon: const Icon(Icons.add_shopping_cart),
              label: const Text('Vente',
                  style: TextStyle(fontWeight: FontWeight.w600)),
            )
          : null,
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: (i) => setState(() => _selectedIndex = i),
        items: [
          const BottomNavigationBarItem(
              icon: Icon(Icons.home_outlined),
              activeIcon: Icon(Icons.home),
              label: 'Accueil'),
          const BottomNavigationBarItem(
              icon: Icon(Icons.inventory_2_outlined),
              activeIcon: Icon(Icons.inventory_2),
              label: 'Stock'),
          const BottomNavigationBarItem(
              icon: Icon(Icons.people_outline),
              activeIcon: Icon(Icons.people),
              label: 'Clients'),
          const BottomNavigationBarItem(
              icon: Icon(Icons.account_balance_wallet_outlined),
              activeIcon: Icon(Icons.account_balance_wallet),
              label: 'Dettes'),
          BottomNavigationBarItem(
            icon: Stack(
              clipBehavior: Clip.none,
              children: [
                const Icon(Icons.settings_outlined),
                if ((alertes.value ?? 0) > 0)
                  Positioned(
                    right: -4,
                    top: -4,
                    child: Container(
                      width: 10,
                      height: 10,
                      decoration: BoxDecoration(
                          color: colors.red, shape: BoxShape.circle),
                    ),
                  ),
              ],
            ),
            activeIcon: const Icon(Icons.settings),
            label: 'Paramètres',
          ),
        ],
      ),
    );
  }
}
