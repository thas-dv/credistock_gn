import 'package:credistock_gn/presentation/blocs/auth/auth_bloc.dart';
import 'package:credistock_gn/presentation/screens/clients/client_screen.dart';
import 'package:credistock_gn/presentation/screens/dettes/dette_screen.dart';
import 'package:credistock_gn/presentation/screens/home/home_screen.dart';
import 'package:credistock_gn/presentation/screens/produit/produit_form_screen.dart';
import 'package:credistock_gn/presentation/screens/screens.dart'
    hide PaiementScreen, ClientDetailScreen;
import 'package:credistock_gn/presentation/screens/stock/stock_screen.dart';
import 'package:credistock_gn/presentation/screens/auth/auth_screen.dart';
import 'package:credistock_gn/presentation/screens/vente/vente_screen.dart';
import 'package:credistock_gn/widgets/main_shell.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';

abstract class AppRoutes {
  static const auth = '/auth';
  static const home = '/';
  static const stock = '/stock';
  static const produitForm = '/produit-form';
  static const vente = '/vente';
  static const clients = '/clients';
  static const clientDetail = '/client-detail';
  static const dettes = '/dettes';
  static const paiement = '/paiement';
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
    initialLocation: AppRoutes.auth,
    redirect: (context, state) {
      final estAuth = context.read<AuthBloc>().state.estAuthentifie;
      final estSurAuth = state.matchedLocation == AppRoutes.auth;

      if (!estAuth && !estSurAuth) return AppRoutes.auth;
      if (estAuth && estSurAuth) return AppRoutes.home;

      return null;
    },
    routes: [
      // ── Auth ──────────────────────────────────────────────

      GoRoute(
        path: AppRoutes.auth,
        builder: (_, __) => const AuthScreen(),
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
            pageBuilder: (_, __) =>
                const NoTransitionPage(child: StockScreen()),
          ),
          GoRoute(
            path: AppRoutes.clients,
            pageBuilder: (_, __) =>
                const NoTransitionPage(child: ClientsScreen()),
          ),
          GoRoute(
            path: AppRoutes.dettes,
            pageBuilder: (_, __) =>
                const NoTransitionPage(child: DettesScreen()),
          ),
          GoRoute(
            path: AppRoutes.stats,
            pageBuilder: (_, __) =>
                const NoTransitionPage(child: StatsScreen()),
          ),
          GoRoute(
            path: AppRoutes.alertes,
            pageBuilder: (_, __) =>
                const NoTransitionPage(child: AlertesScreen()),
          ),
          GoRoute(
            path: AppRoutes.settings,
            pageBuilder: (_, __) =>
                const NoTransitionPage(child: SettingsScreen()),
          ),
        ],
      ),

      // ── Vente (modal plein écran) ─────────────────────────
      GoRoute(
        path: AppRoutes.produitForm,
        parentNavigatorKey: _rootNavigatorKey,
        builder: (_, state) => ProduitFormScreen(
          produitId: state.uri.queryParameters['produitId'],
        ),
      ),
      GoRoute(
        path: AppRoutes.clientDetail,
        parentNavigatorKey: _rootNavigatorKey,
        builder: (_, state) => ClientDetailScreen(
          clientId: state.uri.queryParameters['clientId'] ?? '',
        ),
      ),
      GoRoute(
        path: AppRoutes.paiement,
        parentNavigatorKey: _rootNavigatorKey,
        builder: (_, state) => PaiementScreen(
          detteId: state.uri.queryParameters['detteId'] ?? '',
        ),
      ),
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
