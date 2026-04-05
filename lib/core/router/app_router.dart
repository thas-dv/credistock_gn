import 'package:credistock_gn/presentation/blocs/auth/auth_bloc.dart';
import 'package:credistock_gn/presentation/screens/clients/client_screen.dart';
import 'package:credistock_gn/presentation/screens/dettes/dette_screen.dart';
import 'package:credistock_gn/presentation/screens/home/home_screen.dart';
import 'package:credistock_gn/presentation/screens/produit/produit_form_screen.dart';
import 'package:credistock_gn/presentation/screens/screens.dart' hide PaiementScreen, ClientDetailScreen;
import 'package:credistock_gn/presentation/screens/stock/stock_screen.dart';
import 'package:credistock_gn/presentation/screens/vente/vente_screen.dart';
import 'package:credistock_gn/widgets/main_shell.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';


abstract class AppRoutes {
  static const onboarding = '/onboarding';
  static const pin = '/pin';
  static const home = '/';
  static const stock = '/stock';
  static const produitAjouter = '/stock/ajouter';
  static const produitModifier = '/stock/:produitId';
  static const vente = '/vente';
  static const clients = '/clients';
  static const clientDetail = '/clients/:clientId';
  static const dettes = '/dettes';
  static const paiement = '/dettes/:detteId/payer';
  static const stats = '/stats';
  static const alertes = '/alertes';
  static const settings = '/settings';
  static const abonnement = '/abonnement';
}

class AppRouter {
  static final _rootNavigatorKey = GlobalKey<NavigatorState>();
  static final _shellNavigatorKey = GlobalKey<NavigatorState>();

  static final router = GoRouter(
    navigatorKey: _rootNavigatorKey,
    initialLocation: AppRoutes.pin,
    redirect: (context, state) {
      final authState = context.read<AuthBloc>().state;
      final estAuth = authState.estAuthentifie;
      final estSurPin = state.matchedLocation == AppRoutes.pin;
      final estSurOnboarding = state.matchedLocation == AppRoutes.onboarding;

      // Pas encore de boutique configurée → onboarding
      if (authState.boutiqueId == null &&
          !estSurOnboarding &&
          authState.status == AuthStatus.unauthenticated) {
        return AppRoutes.onboarding;
      }

      // Non authentifié → PIN
      if (!estAuth && !estSurPin && !estSurOnboarding) {
        return AppRoutes.pin;
      }

      // Déjà authentifié → accueil
      if (estAuth && estSurPin) return AppRoutes.home;

      return null;
    },
    routes: [
      // ── Auth ──────────────────────────────────────────────
      GoRoute(
        path: AppRoutes.onboarding,
        builder: (_, __) => const OnboardingScreen(),
      ),
      GoRoute(
        path: AppRoutes.pin,
        builder: (_, __) => const PinScreen(),
      ),

      // ── Shell avec bottom nav ─────────────────────────────
      ShellRoute(
        navigatorKey: _shellNavigatorKey,
        builder: (context, state, child) => MainShell(child: child),
        routes: [
          GoRoute(
            path: AppRoutes.home,
            pageBuilder: (_, __) => const NoTransitionPage(child: HomeScreen()),
          ),
          GoRoute(
            path: AppRoutes.stock,
            pageBuilder: (_, __) => const NoTransitionPage(child: StockScreen()),
            routes: [
              GoRoute(
                path: 'ajouter',
                parentNavigatorKey: _rootNavigatorKey,
                builder: (_, __) => const ProduitFormScreen(),
              ),
              GoRoute(
                path: ':produitId',
                parentNavigatorKey: _rootNavigatorKey,
                builder: (_, state) => ProduitFormScreen(
                  produitId: state.pathParameters['produitId'],
                ),
              ),
            ],
          ),
          GoRoute(
            path: AppRoutes.clients,
            pageBuilder: (_, __) => const NoTransitionPage(child: ClientsScreen()),
            routes: [
              GoRoute(
                path: ':clientId',
                parentNavigatorKey: _rootNavigatorKey,
                builder: (_, state) => ClientDetailScreen(
                  clientId: state.pathParameters['clientId']!,
                ),
              ),
            ],
          ),
          GoRoute(
            path: AppRoutes.dettes,
            pageBuilder: (_, __) => const NoTransitionPage(child: DettesScreen()),
            routes: [
              GoRoute(
                path: ':detteId/payer',
                parentNavigatorKey: _rootNavigatorKey,
                builder: (_, state) => PaiementScreen(
                  detteId: state.pathParameters['detteId']!,
                ),
              ),
            ],
          ),
          GoRoute(
            path: AppRoutes.stats,
            pageBuilder: (_, __) => const NoTransitionPage(child: StatsScreen()),
          ),
          GoRoute(
            path: AppRoutes.alertes,
            pageBuilder: (_, __) => const NoTransitionPage(child: AlertesScreen()),
          ),
          GoRoute(
            path: AppRoutes.settings,
            pageBuilder: (_, __) => const NoTransitionPage(child: SettingsScreen()),
          ),
        ],
      ),

      // ── Vente (modal plein écran) ─────────────────────────
      GoRoute(
        path: AppRoutes.vente,
        parentNavigatorKey: _rootNavigatorKey,
        builder: (_, __) => const VenteScreen(),
      ),

      // ── Abonnement ────────────────────────────────────────
      GoRoute(
        path: AppRoutes.abonnement,
        parentNavigatorKey: _rootNavigatorKey,
        builder: (_, __) => const AbonnementScreen(),
      ),
    ],
  );
}