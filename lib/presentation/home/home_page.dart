// lib/presentation/home/home_page.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:intl/intl.dart';
import '../providers/app_providers.dart';
import '../../core/theme/app_theme.dart';
import '../../data/local/database/app_database.dart';

// Provider : statistiques du jour
final statsJourProvider = StreamProvider.autoDispose<Map<String, dynamic>>((ref) {
  final session = ref.watch(sessionProvider);
  if (!session.isLoggedIn) return Stream.value({});

  final db  = ref.watch(appDatabaseProvider);
  final bid = session.boutiqueId!;
  final now = DateTime.now();
  final debutJour = DateTime(now.year, now.month, now.day);

  // Écouter les ventes du jour
  return (db.select(db.creditStockVentes)
    ..where((v) => v.boutiqueId.equals(bid) & v.dateVente.isBiggerOrEqualValue(debutJour))
  ).watch().asyncMap((ventes) async {
    final totalVentes = ventes.fold<int>(0, (s, v) => s + v.montantTotal);

    final dettes = await (db.select(db.creditStockDettes)
      ..where((d) => d.boutiqueId.equals(bid) & d.statut.isNotIn(['paye']))
    ).get();
    final totalDettes = dettes.fold<int>(0, (s, d) => s + (d.montantInitial - d.montantPaye));

    final produitsAlerte = await (db.select(db.creditStockProduits)
      ..where((p) => p.boutiqueId.equals(bid) & p.actif.isValue(true))
    ).get().then((prods) => prods.where((p) => p.quantite <= p.seuilAlerte).length);

    final alertes = await (db.select(db.creditStockAlertes)
      ..where((a) => a.boutiqueId.equals(bid) & a.lu.isValue(false))
    ).get();

    final dettesRecentes = await (db.select(db.creditStockDettes)
      ..where((d) => d.boutiqueId.equals(bid) & d.statut.isNotIn(['paye']))
      ..orderBy([(d) => OrderingTerm.desc(d.createdAt)])
      ..limit(3)
    ).get();

    return {
      'total_ventes':      totalVentes,
      'nb_ventes':         ventes.length,
      'total_dettes':      totalDettes,
      'nb_dettes':         dettes.length,
      'stock_faible':      produitsAlerte,
      'alertes_non_lues':  alertes.length,
      'dettes_recentes':   dettesRecentes,
    };
  });
});

class HomePage extends ConsumerWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final colors  = Theme.of(context).extension<CreditStockColors>()!;
    final session = ref.watch(sessionProvider);
    final stats   = ref.watch(statsJourProvider);
    final isOnline = ref.watch(isOnlineProvider);
    final syncStt  = ref.watch(syncProvider);

    final fmt = NumberFormat('#,###', 'fr_FR');

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(session.utilisateurNom ?? 'Accueil',
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            Text(session.boutiqueId != null ? 'Ma boutique' : '',
              style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w300),
            ),
          ],
        ),
        actions: [
          // Badge alertes
          if ((stats.value?['alertes_non_lues'] ?? 0) > 0)
            Stack(
              children: [
                IconButton(
                  icon: const Icon(Icons.notifications_outlined),
                  onPressed: () => Navigator.pushNamed(context, '/alertes'),
                ),
                Positioned(
                  right: 8, top: 8,
                  child: Container(
                    width: 16, height: 16,
                    decoration: BoxDecoration(color: colors.red, shape: BoxShape.circle),
                    child: Center(
                      child: Text('${stats.value!['alertes_non_lues']}',
                        style: const TextStyle(color: Colors.white, fontSize: 9, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ),
                ),
              ],
            ),

          // Indicateur sync / connexion
          Padding(
            padding: const EdgeInsets.only(right: 12),
            child: Icon(
              syncStt == SyncStatus.syncing ? Icons.sync : (isOnline ? Icons.cloud_done_outlined : Icons.cloud_off_outlined),
              color: syncStt == SyncStatus.syncing ? colors.amber : (isOnline ? Colors.white70 : colors.amber),
              size: 20,
            ),
          ),
        ],
      ),

      body: RefreshIndicator(
        onRefresh: () async {
          if (isOnline) await ref.read(syncProvider.notifier).syncAll();
        },
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [

            // Banner hors ligne
            if (!isOnline) Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
              margin:  const EdgeInsets.only(bottom: 12),
              decoration: BoxDecoration(
                color:        colors.amberLight,
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: colors.amber.withOpacity(0.3)),
              ),
              child: Row(
                children: [
                  Icon(Icons.wifi_off, color: colors.amber, size: 16),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Mode hors ligne — données locales uniquement',
                      style: TextStyle(color: colors.amber, fontSize: 12),
                    ),
                  ),
                ],
              ),
            ).animate().fadeIn(),

            // ── Métriques du jour ───────────────────────

            stats.when(
              loading: () => _LoadingMetrics(),
              error:   (_, __) => const SizedBox.shrink(),
              data:    (data) => Column(
                children: [
                  // Ventes du jour — carte principale
                  _MetricCard(
                    label: 'Ventes aujourd\'hui',
                    value: '${fmt.format(data['total_ventes'] ?? 0)} GNF',
                    sub:   '${data['nb_ventes'] ?? 0} transaction(s)',
                    icon:  Icons.trending_up,
                    color: colors.green,
                    bg:    colors.greenLight,
                    onTap: () => Navigator.pushNamed(context, '/ventes'),
                  ).animate().slideX(begin: -0.05, duration: 300.ms),

                  const SizedBox(height: 10),

                  Row(children: [
                    Expanded(
                      child: _MetricCard(
                        label: 'Dettes',
                        value: '${data['nb_dettes'] ?? 0}',
                        sub:   '${fmt.format(data['total_dettes'] ?? 0)} GNF',
                        icon:  Icons.account_balance_wallet_outlined,
                        color: colors.red,
                        bg:    colors.redLight,
                        onTap: () => Navigator.pushNamed(context, '/dettes'),
                      ).animate().slideX(begin: -0.05, duration: 300.ms, delay: 50.ms),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: _MetricCard(
                        label: 'Stock faible',
                        value: '${data['stock_faible'] ?? 0}',
                        sub:   'produit(s)',
                        icon:  Icons.inventory_2_outlined,
                        color: colors.amber,
                        bg:    colors.amberLight,
                        onTap: () => Navigator.pushNamed(context, '/stock'),
                      ).animate().slideX(begin: 0.05, duration: 300.ms, delay: 100.ms),
                    ),
                  ]),
                ],
              ),
            ),

            const SizedBox(height: 20),

            // ── Actions rapides ──────────────────────────

            Text('Actions rapides',
              style: Theme.of(context).textTheme.labelMedium?.copyWith(
                color: colors.textSecondary, letterSpacing: 0.5,
              ),
            ),
            const SizedBox(height: 10),

            GridView.count(
              crossAxisCount:      2,
              shrinkWrap:          true,
              physics:             const NeverScrollableScrollPhysics(),
              crossAxisSpacing:    10,
              mainAxisSpacing:     10,
              childAspectRatio:    1.6,
              children: [
                _ActionCard(
                  emoji: '💰',
                  label: 'Nouvelle vente',
                  color: colors.green,
                  onTap: () => Navigator.pushNamed(context, '/nouvelle-vente'),
                ),
                _ActionCard(
                  emoji: '📦',
                  label: 'Stock',
                  color: colors.blue,
                  onTap: () => Navigator.pushNamed(context, '/stock'),
                ),
                _ActionCard(
                  emoji: '👥',
                  label: 'Clients',
                  color: colors.amber,
                  onTap: () => Navigator.pushNamed(context, '/clients'),
                ),
                _ActionCard(
                  emoji: '💸',
                  label: 'Dettes',
                  color: colors.red,
                  onTap: () => Navigator.pushNamed(context, '/dettes'),
                ),
              ],
            ).animate().fadeIn(delay: 150.ms),

            const SizedBox(height: 20),

            // ── Dettes récentes ──────────────────────────

            stats.whenData((data) {
              final dettes = data['dettes_recentes'] as List<dynamic>? ?? [];
              if (dettes.isEmpty) return const SizedBox.shrink();

              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Text('Dettes récentes',
                        style: Theme.of(context).textTheme.labelMedium?.copyWith(
                          color: colors.textSecondary, letterSpacing: 0.5,
                        ),
                      ),
                      const Spacer(),
                      TextButton(
                        onPressed: () => Navigator.pushNamed(context, '/dettes'),
                        child: Text('Voir tout', style: TextStyle(color: colors.green, fontSize: 12)),
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  ...dettes.map((d) {
                    final dette = d as CreditStockDette;
                    final restant = dette.montantInitial - dette.montantPaye;
                    return Card(
                      margin: const EdgeInsets.only(bottom: 8),
                      child: ListTile(
                        dense: true,
                        leading: CircleAvatar(
                          radius:     18,
                          backgroundColor: colors.redLight,
                          child: Text('💸', style: const TextStyle(fontSize: 14)),
                        ),
                        title: Text(dette.clientId, style: const TextStyle(fontSize: 14)),
                        subtitle: Text(dette.statut, style: TextStyle(fontSize: 11, color: colors.textSecondary)),
                        trailing: Text(
                          '${fmt.format(restant)} GNF',
                          style: TextStyle(color: colors.red, fontWeight: FontWeight.bold, fontSize: 13),
                        ),
                        onTap: () => Navigator.pushNamed(context, '/dettes'),
                      ),
                    );
                  }),
                ],
              );
            }).value ?? const SizedBox.shrink(),
          ],
        ),
      ),
    );
  }
}

// ── Widgets home ─────────────────────────────────────────────

class _MetricCard extends StatelessWidget {
  final String label, value, sub;
  final IconData icon;
  final Color color, bg;
  final VoidCallback onTap;
  const _MetricCard({required this.label, required this.value, required this.sub,
    required this.icon, required this.color, required this.bg, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(14),
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(color: bg, borderRadius: BorderRadius.circular(10)),
                child: Icon(icon, color: color, size: 22),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(label, style: TextStyle(fontSize: 11, color: Theme.of(context).extension<CreditStockColors>()!.textSecondary)),
                    Text(value, style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: color)),
                    Text(sub,   style: TextStyle(fontSize: 11, color: Theme.of(context).extension<CreditStockColors>()!.textSecondary)),
                  ],
                ),
              ),
              Icon(Icons.chevron_right, size: 16, color: Theme.of(context).extension<CreditStockColors>()!.textSecondary),
            ],
          ),
        ),
      ),
    );
  }
}

class _ActionCard extends StatelessWidget {
  final String emoji, label;
  final Color color;
  final VoidCallback onTap;
  const _ActionCard({required this.emoji, required this.label, required this.color, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(14),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(emoji, style: const TextStyle(fontSize: 26)),
              const SizedBox(height: 6),
              Text(label, style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: color)),
            ],
          ),
        ),
      ),
    );
  }
}

class _LoadingMetrics extends StatelessWidget {
  @override
  Widget build(BuildContext context) => Column(
    children: List.generate(2, (_) => Container(
      height: 80, margin: const EdgeInsets.only(bottom: 10),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(14),
      ),
    )),
  );
}