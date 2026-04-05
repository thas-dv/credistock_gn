import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../../../core/theme/app_theme.dart';
import '../../../core/router/app_router.dart';
import '../../../domain/entities/entities.dart';
import '../../blocs/sync/sync_bloc.dart';
import '../../blocs/auth/auth_bloc.dart';
import '../../widgets/common/app_badge.dart';
import '../../widgets/common/metric_card.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final boutiqueId = context.read<AuthBloc>().state.boutiqueId ?? '';

    return Scaffold(
      backgroundColor: AppColors.gray50,
      body: SafeArea(
        child: CustomScrollView(
          slivers: [
            // ── Header ──────────────────────────────────────
            SliverToBoxAdapter(
              child: _Header(boutiqueId: boutiqueId),
            ),
            // ── Sync banner ─────────────────────────────────
            SliverToBoxAdapter(
              child: BlocBuilder<SyncBloc, SyncState>(
                buildWhen: (prev, curr) =>
                    prev.elementsEnAttente != curr.elementsEnAttente ||
                    prev.estConnecte != curr.estConnecte,
                builder: (_, state) {
                  if (!state.estConnecte) return _OfflineBanner(count: state.elementsEnAttente);
                  if (state.aSynchroniser && state.estConnecte) {
                    return _SyncBanner(count: state.elementsEnAttente, boutiqueId: boutiqueId);
                  }
                  return const SizedBox.shrink();
                },
              ),
            ),
            // ── Métriques ───────────────────────────────────
            SliverPadding(
              padding: const EdgeInsets.fromLTRB(16, 16, 16, 0),
              sliver: SliverToBoxAdapter(
                child: _MetriquesGrid(boutiqueId: boutiqueId),
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
    final now = DateFormat('EEEE d MMMM', 'fr_FR').format(DateTime.now());

    return Container(
      color: Colors.white,
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 12),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Bonjour 👋',
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
                const SizedBox(height: 2),
                Text(
                  now,
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
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
          const Icon(Icons.cloud_upload_outlined, color: AppColors.blue, size: 16),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              '$count élément(s) à synchroniser',
              style: const TextStyle(fontSize: 12, color: AppColors.blue),
            ),
          ),
          TextButton(
            onPressed: () => context.read<SyncBloc>().add(SyncManuel(boutiqueId)),
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
  const _MetriquesGrid({required this.boutiqueId});

  @override
  Widget build(BuildContext context) {
    // En prod: connecter à StockBloc + DetteBloc via BlocBuilder
    return const Column(
      children: [
        Row(
          children: [
            Expanded(
              child: MetricCard(
                label: 'Ventes du jour',
                value: '485 000',
                unit: 'GNF',
                trend: '+12%',
                trendPositive: true,
                color: AppColors.green,
              ),
            ),
            SizedBox(width: 10),
            Expanded(
              child: MetricCard(
                label: 'Dettes actives',
                value: '1 240 000',
                unit: 'GNF',
                trend: '8 clients',
                trendPositive: false,
                color: AppColors.red,
              ),
            ),
          ],
        ),
        SizedBox(height: 10),
        Row(
          children: [
            Expanded(
              child: MetricCard(
                label: 'Produits en stock',
                value: '47',
                unit: '',
                trend: '3 alertes',
                trendPositive: false,
                color: AppColors.amber,
              ),
            ),
            SizedBox(width: 10),
            Expanded(
              child: MetricCard(
                label: 'Non synchronisés',
                value: '5',
                unit: '',
                trend: 'offline',
                trendPositive: null,
                color: AppColors.gray400,
              ),
            ),
          ],
        ),
      ],
    );
  }
}

// ── Activité récente ─────────────────────────────────────────

class _ActiviteRecente extends StatelessWidget {
  final String boutiqueId;
  const _ActiviteRecente({required this.boutiqueId});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text('Activité récente', style: Theme.of(context).textTheme.labelLarge),
            TextButton(
              onPressed: () => context.go(AppRoutes.dettes),
              child: Text('Tout voir', style: TextStyle(fontSize: 12, color: AppColors.green)),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Card(
          child: Column(
            children: [
              _ActiviteItem(
                initiales: 'FA',
                nom: 'Fatou Diallo',
                detail: 'Riz 25kg · Crédit',
                montant: '75 000 GNF',
                temps: 'il y a 12min',
                couleur: AppColors.green,
                estPositif: false,
              ),
              const Divider(height: 1, thickness: 0.5),
              _ActiviteItem(
                initiales: 'AL',
                nom: 'Alpha Camara',
                detail: 'Huile 5L · Cash',
                montant: '45 000 GNF',
                temps: 'il y a 31min',
                couleur: AppColors.blue,
                estPositif: false,
              ),
              const Divider(height: 1, thickness: 0.5),
              _ActiviteItem(
                initiales: 'MB',
                nom: 'Mamadou Barry',
                detail: 'Paiement partiel',
                montant: '+30 000 GNF',
                temps: 'il y a 1h',
                couleur: AppColors.red,
                estPositif: true,
              ),
            ],
          ),
        ),
      ],
    );
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
            child: Text(
              initiales,
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w500,
                color: couleur,
              ),
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(nom, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w500)),
                Text(detail, style: const TextStyle(fontSize: 11, color: AppColors.gray400)),
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
              Text(temps, style: const TextStyle(fontSize: 11, color: AppColors.gray400)),
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
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Alertes', style: Theme.of(context).textTheme.labelLarge),
        const SizedBox(height: 8),
        _AlerteCard(
          icon: Icons.warning_amber_rounded,
          titre: 'Stock faible — Sucre 1kg',
          detail: 'Seulement 3 unités restantes',
          couleur: AppColors.red,
          couleurLight: AppColors.redLight,
        ),
        const SizedBox(height: 8),
        _AlerteCard(
          icon: Icons.access_time,
          titre: 'Rappel — Fatoumata Bah',
          detail: 'Echéance dans 2 jours · 120 000 GNF',
          couleur: AppColors.amber,
          couleurLight: AppColors.amberLight,
        ),
      ],
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
                Text(
                  titre,
                  style: TextStyle(fontSize: 13, fontWeight: FontWeight.w500, color: couleur),
                ),
                Text(
                  detail,
                  style: TextStyle(fontSize: 12, color: couleur.withOpacity(0.8)),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}