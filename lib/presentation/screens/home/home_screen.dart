import 'package:credistock_gn/core/di/injection.dart';
import 'package:credistock_gn/domain/repositories/repositories.dart';

import 'package:credistock_gn/widgets/app_badge.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../../../core/theme/app_theme.dart';
import '../../../core/router/app_router.dart';
import '../../../domain/entities/entities.dart';

import '../../blocs/auth/auth_bloc.dart';
import '../../blocs/client/client_bloc.dart';
import '../../blocs/dette/dette_bloc.dart';
import '../../blocs/stock/stock_bloc.dart';
import '../../blocs/sync/sync_bloc.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  late final VenteRepository _venteRepository;

  @override
  void initState() {
    super.initState();
    _venteRepository = getIt<VenteRepository>();

    WidgetsBinding.instance.addPostFrameCallback((_) {
      final boutiqueId = context.read<AuthBloc>().state.boutiqueId;
      if (boutiqueId == null || boutiqueId.isEmpty) return;
      context.read<StockBloc>().add(StockWatchStarted(boutiqueId));
      context.read<ClientBloc>().add(ClientWatchStarted(boutiqueId));
      context.read<DetteBloc>().add(DetteWatchStarted(boutiqueId));
    });
  }

  @override
  Widget build(BuildContext context) {
    final boutiqueId = context.read<AuthBloc>().state.boutiqueId ?? '';

    return Scaffold(
      backgroundColor: AppColors.gray50,
      body: SafeArea(
        top: true,
        bottom: false,
        child: CustomScrollView(
          slivers: [
            // // ── Header ──────────────────────────────────────
            // SliverToBoxAdapter(
            //   child: _Header(boutiqueId: boutiqueId),
            // ),
            // // ── Sync banner ─────────────────────────────────
            SliverToBoxAdapter(child: _Header(boutiqueId: boutiqueId)),
            SliverToBoxAdapter(
              child: BlocBuilder<SyncBloc, SyncState>(
                buildWhen: (prev, curr) =>
                    prev.elementsEnAttente != curr.elementsEnAttente ||
                    prev.estConnecte != curr.estConnecte,
                builder: (_, state) {
                  if (!state.estConnecte) {
                    return _OfflineBanner(count: state.elementsEnAttente);
                  }
                  if (state.aSynchroniser && state.estConnecte) {
                    return _SyncBanner(
                      count: state.elementsEnAttente,
                      boutiqueId: boutiqueId,
                    );
                  }
                  return const SizedBox.shrink();
                },
              ),
            ),
            // ── Métriques ───────────────────────────────────
            SliverPadding(
              padding: const EdgeInsets.fromLTRB(16, 16, 16, 0),
              sliver: SliverToBoxAdapter(
                child: _MetriquesGrid(
                  boutiqueId: boutiqueId,
                  venteRepository: _venteRepository,
                ),
              ),
            ),
            // ── Activité récente ────────────────────────────
            SliverPadding(
              padding: const EdgeInsets.fromLTRB(16, 20, 16, 0),
              sliver: SliverToBoxAdapter(
                child: _ActiviteRecente(boutiqueId: boutiqueId),
              ),
            ),
            // ── Alertes stock ────────────────────────────────
            SliverPadding(
              padding: const EdgeInsets.fromLTRB(16, 20, 16, 80),
              sliver: SliverToBoxAdapter(
                child: _AlertesStock(boutiqueId: boutiqueId),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ── Header ──────────────────────────────────────────────────

class _Header extends StatelessWidget {
  final String boutiqueId;
  const _Header({required this.boutiqueId});

  @override
  Widget build(BuildContext context) {
    final locale = Localizations.localeOf(context).toLanguageTag();
    final now = DateFormat('EEEE d MMMM', locale).format(DateTime.now());

    return Container(
      color: Colors.white,
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 12),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Bonjour 👋',
                    style: Theme.of(context).textTheme.headlineSmall),
                const SizedBox(height: 2),
                Text(now, style: Theme.of(context).textTheme.bodyMedium),
              ],
            ),
          ),
          IconButton(
            onPressed: () => context.push(AppRoutes.alertes),
            icon: const Icon(Icons.notifications_outlined),
            color: AppColors.gray600,
          ),
          IconButton(
            onPressed: () => context.push(AppRoutes.settings),
            icon: const Icon(Icons.settings_outlined),
            color: AppColors.gray600,
          ),
        ],
      ),
    );
  }
}

// ── Banners ─────────────────────────────────────────────────

class _OfflineBanner extends StatelessWidget {
  final int count;
  const _OfflineBanner({required this.count});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.fromLTRB(16, 12, 16, 0),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: AppColors.amberLight,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: AppColors.amber.withOpacity(0.3), width: 0.5),
      ),
      child: Row(
        children: [
          const Icon(Icons.wifi_off, color: AppColors.amber, size: 16),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              count > 0
                  ? 'Hors ligne · $count opération(s) en attente de sync'
                  : 'Mode hors ligne actif',
              style: const TextStyle(fontSize: 12, color: AppColors.amber),
            ),
          ),
        ],
      ),
    );
  }
}

class _SyncBanner extends StatelessWidget {
  final int count;
  final String boutiqueId;
  const _SyncBanner({required this.count, required this.boutiqueId});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.fromLTRB(16, 12, 16, 0),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: AppColors.blueLight,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: AppColors.blue.withOpacity(0.3), width: 0.5),
      ),
      child: Row(
        children: [
          const Icon(Icons.cloud_upload_outlined,
              color: AppColors.blue, size: 16),
          const SizedBox(width: 8),
          Expanded(
            child: Text('$count élément(s) à synchroniser',
                style: const TextStyle(fontSize: 12, color: AppColors.blue)),
          ),
          TextButton(
            onPressed: () =>
                context.read<SyncBloc>().add(SyncManuel(boutiqueId)),
            style: TextButton.styleFrom(
              foregroundColor: AppColors.blue,
              padding: const EdgeInsets.symmetric(horizontal: 8),
              minimumSize: Size.zero,
              tapTargetSize: MaterialTapTargetSize.shrinkWrap,
            ),
            child: const Text('Sync', style: TextStyle(fontSize: 12)),
          ),
        ],
      ),
    );
  }
}

// ── Métriques ───────────────────────────────────────────────

class _MetriquesGrid extends StatelessWidget {
  final String boutiqueId;
  final VenteRepository venteRepository;

  const _MetriquesGrid(
      {required this.boutiqueId, required this.venteRepository});

  String _fmt(int v) =>
      NumberFormat.decimalPattern('fr_FR').format(v).replaceAll(',', ' ');

  @override
  Widget build(BuildContext context) {
    // En prod: connecter à StockBloc + DetteBloc via BlocBuilder
    return BlocBuilder<StockBloc, StockState>(
      builder: (context, stockState) {
        return BlocBuilder<DetteBloc, DetteState>(
          builder: (context, detteState) {
            return BlocBuilder<SyncBloc, SyncState>(
              builder: (context, syncState) {
                return FutureBuilder(
                  future: venteRepository.getTotalVentesJour(boutiqueId),
                  builder: (context, snapshot) {
                    final totalVentes =
                        snapshot.data?.fold((_) => 0, (v) => v) ?? 0;

                    return Column(
                      children: [
                        Row(
                          children: [
                            Expanded(
                              child: MetricCard(
                                label: 'Ventes du jour',
                                value: _fmt(totalVentes),
                                unit: 'GNF',
                                trend: '${detteState.dettes.length} opérations',
                                trendPositive: totalVentes > 0,
                                color: AppColors.green,
                              ),
                            ),
                            const SizedBox(width: 10),
                            Expanded(
                              child: MetricCard(
                                label: 'Dettes actives',
                                value: _fmt(detteState.totalDu),
                                unit: 'GNF',
                                trend:
                                    '${detteState.nombreDettesActives} clients',
                                trendPositive: false,
                                color: AppColors.red,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 10),
                        Row(
                          children: [
                            Expanded(
                              child: MetricCard(
                                label: 'Produits en stock',
                                value: '${stockState.totalProduits}',
                                unit: '',
                                trend: '${stockState.nombreAlertes} alertes',
                                trendPositive: stockState.nombreAlertes == 0,
                                color: AppColors.amber,
                              ),
                            ),
                            const SizedBox(width: 10),
                            Expanded(
                              child: MetricCard(
                                label: 'Non synchronisés',
                                value: '${syncState.elementsEnAttente}',
                                unit: '',
                                trend: syncState.estConnecte
                                    ? 'en ligne'
                                    : 'offline',
                                trendPositive: syncState.estConnecte,
                                color: AppColors.gray400,
                              ),
                            ),
                          ],
                        ),
                      ],
                    );
                  },
                );
              },
            );
          },
        );
      },
    );
  }
}

// ── Activité récente ─────────────────────────────────────────

class _ActiviteRecente extends StatelessWidget {
  final String boutiqueId;
  const _ActiviteRecente({required this.boutiqueId});

  String _fmtMontant(int value) =>
      '${NumberFormat.decimalPattern('fr_FR').format(value).replaceAll(',', ' ')} GNF';

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<DetteBloc, DetteState>(
      builder: (context, state) {
        final recent = [...state.dettes]
          ..sort((a, b) => b.updatedAt.compareTo(a.updatedAt));
        final items = recent.take(3).toList();

        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('Activité récente',
                    style: Theme.of(context).textTheme.labelLarge),
                TextButton(
                  onPressed: () => context.go(AppRoutes.dettes),
                  child: const Text('Tout voir',
                      style: TextStyle(fontSize: 12, color: AppColors.green)),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Card(
              child: items.isEmpty
                  ? const Padding(
                      padding: EdgeInsets.all(16),
                      child: Text('Aucune activité récente'),
                    )
                  : Column(
                      children: [
                        for (int i = 0; i < items.length; i++) ...[
                          _ActiviteItem(
                            initiales: _initiales(items[i].nomClient),
                            nom: items[i].nomClient,
                            detail: items[i].statut.name,
                            montant: _fmtMontant(items[i].montantRestant),
                            temps: _tempsRelatif(items[i].updatedAt),
                            couleur: items[i].statut == StatutDette.paye
                                ? AppColors.green
                                : AppColors.red,
                            estPositif: items[i].statut == StatutDette.paye,
                          ),
                          if (i < items.length - 1)
                            const Divider(height: 1, thickness: 0.5),
                        ]
                      ],
                    ),
            ),
          ],
        );
      },
    );
  }

  String _initiales(String nom) {
    final parts = nom.trim().split(RegExp(r'\s+'));
    return parts
        .take(2)
        .map((p) => p.isNotEmpty ? p[0].toUpperCase() : '')
        .join();
  }

  String _tempsRelatif(DateTime date) {
    final diff = DateTime.now().difference(date);
    if (diff.inMinutes < 1) return 'à l\'instant';
    if (diff.inMinutes < 60) return 'il y a ${diff.inMinutes} min';
    if (diff.inHours < 24) return 'il y a ${diff.inHours} h';
    return 'il y a ${diff.inDays} j';
  }
}

class _ActiviteItem extends StatelessWidget {
  final String initiales;
  final String nom;
  final String detail;
  final String montant;
  final String temps;
  final Color couleur;
  final bool estPositif;

  const _ActiviteItem({
    required this.initiales,
    required this.nom,
    required this.detail,
    required this.montant,
    required this.temps,
    required this.couleur,
    required this.estPositif,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      child: Row(
        children: [
          CircleAvatar(
            radius: 18,
            backgroundColor: couleur.withOpacity(0.1),
            child: Text(initiales,
                style: TextStyle(
                    fontSize: 11, fontWeight: FontWeight.w500, color: couleur)),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(nom,
                    style: const TextStyle(
                        fontSize: 13, fontWeight: FontWeight.w500)),
                Text(detail,
                    style: const TextStyle(
                        fontSize: 11, color: AppColors.gray400)),
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                montant,
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w500,
                  color: estPositif ? AppColors.green : AppColors.gray900,
                ),
              ),
              Text(temps,
                  style:
                      const TextStyle(fontSize: 11, color: AppColors.gray400)),
            ],
          ),
        ],
      ),
    );
  }
}

// ── Alertes stock ────────────────────────────────────────────

class _AlertesStock extends StatelessWidget {
  final String boutiqueId;
  const _AlertesStock({required this.boutiqueId});

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<StockBloc, StockState>(
      builder: (context, stockState) {
        return BlocBuilder<DetteBloc, DetteState>(
          builder: (context, detteState) {
            final lowStock = stockState.produitsEnAlerte.take(1).toList();
            final detteEchue = [...detteState.dettesEchues]
              ..sort((a, b) => b.updatedAt.compareTo(a.updatedAt));

            return Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Alertes', style: Theme.of(context).textTheme.labelLarge),
                const SizedBox(height: 8),
                if (lowStock.isNotEmpty)
                  _AlerteCard(
                    icon: Icons.warning_amber_rounded,
                    titre: 'Stock faible — ${lowStock.first.nom}',
                    detail:
                        'Seulement ${lowStock.first.quantite} unité(s) restantes',
                    couleur: AppColors.red,
                    couleurLight: AppColors.redLight,
                  ),
                if (detteEchue.isNotEmpty) ...[
                  const SizedBox(height: 8),
                  _AlerteCard(
                    icon: Icons.access_time,
                    titre: 'Rappel — ${detteEchue.first.nomClient}',
                    detail:
                        'Échéance dépassée · ${detteEchue.first.montantRestant} GNF',
                    couleur: AppColors.amber,
                    couleurLight: AppColors.amberLight,
                  ),
                ],
                if (lowStock.isEmpty && detteEchue.isEmpty)
                  const Card(
                    child: Padding(
                      padding: EdgeInsets.all(14),
                      child: Text('Aucune alerte active'),
                    ),
                  ),
              ],
            );
          },
        );
      },
    );
  }
}

class _AlerteCard extends StatelessWidget {
  final IconData icon;
  final String titre;
  final String detail;
  final Color couleur;
  final Color couleurLight;

  const _AlerteCard({
    required this.icon,
    required this.titre,
    required this.detail,
    required this.couleur,
    required this.couleurLight,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: couleurLight,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: couleur.withOpacity(0.2), width: 0.5),
      ),
      child: Row(
        children: [
          Icon(icon, color: couleur, size: 20),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(titre,
                    style: TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w500,
                        color: couleur)),
                Text(detail,
                    style: TextStyle(
                        fontSize: 12, color: couleur.withOpacity(0.8))),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
