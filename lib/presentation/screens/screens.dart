// ============================================================
// STATS SCREEN
// ============================================================

import 'package:credistock_gn/presentation/blocs/auth/auth_bloc.dart';
import 'package:credistock_gn/widgets/app_badge.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/app_theme.dart';
import '../../../core/router/app_router.dart';
import '../../../domain/usecases/usecases.dart';


class StatsScreen extends StatefulWidget {
  const StatsScreen({super.key});

  @override
  State<StatsScreen> createState() => _StatsScreenState();
}

class _StatsScreenState extends State<StatsScreen> {
  bool _semaineMode = true;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.gray50,
      body: SafeArea(
        child: CustomScrollView(
          slivers: [
            SliverToBoxAdapter(
              child: Container(
                color: Colors.white,
                padding: const EdgeInsets.fromLTRB(16, 12, 16, 12),
                child: Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Statistiques', style: Theme.of(context).textTheme.headlineSmall),
                          Text(
                            _semaineMode ? 'Cette semaine' : 'Ce mois',
                            style: Theme.of(context).textTheme.bodyMedium,
                          ),
                        ],
                      ),
                    ),
                    // Toggle semaine/mois
                    Container(
                      decoration: BoxDecoration(
                        color: AppColors.gray50,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: AppColors.gray200.withOpacity(0.5)),
                      ),
                      child: Row(
                        children: [
                          _ToggleBtn(label: 'Sem.', active: _semaineMode, onTap: () => setState(() => _semaineMode = true)),
                          _ToggleBtn(label: 'Mois', active: !_semaineMode, onTap: () => setState(() => _semaineMode = false)),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
            SliverPadding(
              padding: const EdgeInsets.all(16),
              sliver: SliverList(
                delegate: SliverChildListDelegate([
                  // Métriques clés
                  Row(
                    children: [
                      Expanded(child: _MetricBox(label: 'CA', value: '2 840 000', unit: 'GNF', color: AppColors.green, trend: '+18%')),
                      const SizedBox(width: 10),
                      Expanded(child: _MetricBox(label: 'Ventes crédit', value: '38%', unit: '', color: AppColors.amber, trend: '+5%')),
                    ],
                  ),
                  const SizedBox(height: 16),

                  // Graphique barres
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('Ventes par jour (GNF)',
                              style: TextStyle(fontSize: 13, fontWeight: FontWeight.w500)),
                          const SizedBox(height: 16),
                          SizedBox(
                            height: 140,
                            child: BarChart(
                              BarChartData(
                                alignment: BarChartAlignment.spaceAround,
                                maxY: 600000,
                                barTouchData: BarTouchData(enabled: false),
                                titlesData: FlTitlesData(
                                  leftTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                                  rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                                  topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                                  bottomTitles: AxisTitles(
                                    sideTitles: SideTitles(
                                      showTitles: true,
                                      getTitlesWidget: (value, _) {
                                        const jours = ['L', 'M', 'M', 'J', 'V', 'S', 'D'];
                                        return Text(
                                          jours[value.toInt()],
                                          style: const TextStyle(fontSize: 10, color: AppColors.gray400),
                                        );
                                      },
                                    ),
                                  ),
                                ),
                                gridData: FlGridData(show: false),
                                borderData: FlBorderData(show: false),
                                barGroups: [
                                  _barGroup(0, 270000),
                                  _barGroup(1, 420000),
                                  _barGroup(2, 330000),
                                  _barGroup(3, 540000, isMax: true),
                                  _barGroup(4, 390000),
                                  _barGroup(5, 480000),
                                  _barGroup(6, 360000),
                                ],
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),

                  // Top produits
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('Top produits', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w500)),
                          const SizedBox(height: 12),
                          _TopProduitRow(rang: '🥇', nom: 'Riz 25kg', montant: 920000, total: 2840000),
                          const Divider(height: 16, thickness: 0.5),
                          _TopProduitRow(rang: '🥈', nom: 'Huile Végétale 5L', montant: 480000, total: 2840000),
                          const Divider(height: 16, thickness: 0.5),
                          _TopProduitRow(rang: '🥉', nom: 'Sucre 1kg', montant: 310000, total: 2840000),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),

                  // Récupération dettes
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('Récupération dettes', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w500)),
                          const SizedBox(height: 12),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              const Text('Récupéré', style: TextStyle(fontSize: 13, color: AppColors.gray400)),
                              const Text('360 000 GNF', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w500, color: AppColors.green)),
                            ],
                          ),
                          const SizedBox(height: 8),
                          DetteProgressBar(montant: 580000, montantPaye: 360000, color: AppColors.green),
                          const SizedBox(height: 6),
                          Text('62% du total récupéré cette ${_semaineMode ? "semaine" : "mois"}',
                              style: const TextStyle(fontSize: 11, color: AppColors.gray400)),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 80),
                ]),
              ),
            ),
          ],
        ),
      ),
    );
  }

  BarChartGroupData _barGroup(int x, double y, {bool isMax = false}) {
    return BarChartGroupData(
      x: x,
      barRods: [
        BarChartRodData(
          toY: y,
          color: isMax ? AppColors.green : AppColors.greenLight,
          width: 28,
          borderRadius: const BorderRadius.vertical(top: Radius.circular(4)),
        ),
      ],
    );
  }
}

class _ToggleBtn extends StatelessWidget {
  final String label;
  final bool active;
  final VoidCallback onTap;

  const _ToggleBtn({required this.label, required this.active, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 150),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 5),
        decoration: BoxDecoration(
          color: active ? AppColors.green : Colors.transparent,
          borderRadius: BorderRadius.circular(7),
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: active ? Colors.white : AppColors.gray400,
            fontWeight: active ? FontWeight.w500 : FontWeight.w400,
          ),
        ),
      ),
    );
  }
}

class _MetricBox extends StatelessWidget {
  final String label;
  final String value;
  final String unit;
  final Color color;
  final String trend;

  const _MetricBox({
    required this.label,
    required this.value,
    required this.unit,
    required this.color,
    required this.trend,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.black.withOpacity(0.07), width: 0.5),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: const TextStyle(fontSize: 11, color: AppColors.gray400)),
          const SizedBox(height: 4),
          Text(value, style: TextStyle(fontSize: 22, fontWeight: FontWeight.w600, color: color)),
          if (unit.isNotEmpty)
            Text(unit, style: const TextStyle(fontSize: 10, color: AppColors.gray400)),
          const SizedBox(height: 4),
          Text(trend, style: TextStyle(fontSize: 11, color: color, fontWeight: FontWeight.w500)),
        ],
      ),
    );
  }
}

class _TopProduitRow extends StatelessWidget {
  final String rang;
  final String nom;
  final int montant;
  final int total;

  const _TopProduitRow({
    required this.rang,
    required this.nom,
    required this.montant,
    required this.total,
  });

  @override
  Widget build(BuildContext context) {
    final ratio = total > 0 ? montant / total : 0.0;
    return Column(
      children: [
        Row(
          children: [
            Text(rang, style: const TextStyle(fontSize: 16)),
            const SizedBox(width: 8),
            Expanded(
              child: Text(nom, style: const TextStyle(fontSize: 13)),
            ),
            Text(
              '${_formatGNF(montant)} GNF',
              style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w500, color: AppColors.green),
            ),
          ],
        ),
        const SizedBox(height: 6),
        DetteProgressBar(montant: total, montantPaye: montant, color: AppColors.green),
        const SizedBox(height: 2),
        Align(
          alignment: Alignment.centerRight,
          child: Text('${(ratio * 100).round()}%', style: const TextStyle(fontSize: 10, color: AppColors.gray400)),
        ),
      ],
    );
  }
}

// ============================================================
// ALERTES SCREEN
// ============================================================

class AlertesScreen extends StatelessWidget {
  const AlertesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.gray50,
      appBar: AppBar(
        title: const Text('Alertes'),
        actions: [
          TextButton(
            onPressed: () {},
            child: const Text('Tout lire', style: TextStyle(fontSize: 12, color: AppColors.green)),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            child: Column(
              children: [
                _AlerteTile(
                  icon: Icons.inventory_2_outlined,
                  iconColor: AppColors.red,
                  titre: 'Stock critique — Sucre 1kg',
                  detail: 'Seulement 3 unités. Pensez à réapprovisionner.',
                  temps: 'Il y a 2h',
                  nonLu: true,
                  actions: [
                    _AlerteAction(label: 'Réapprovisionner', onTap: () => context.go(AppRoutes.stock)),
                  ],
                ),
                const Divider(height: 1, thickness: 0.5),
                _AlerteTile(
                  icon: Icons.access_time,
                  iconColor: AppColors.amber,
                  titre: 'Echéance — Ibrahima Bah',
                  detail: 'Dette de 345 000 GNF dépassée depuis 3 jours.',
                  temps: 'Il y a 5h',
                  nonLu: true,
                  actions: [
                    _AlerteAction(label: '💬 Rappel WA', onTap: () {}),
                    _AlerteAction(label: 'Voir dette', onTap: () => context.go(AppRoutes.dettes), isPrimary: true),
                  ],
                ),
                const Divider(height: 1, thickness: 0.5),
                _AlerteTile(
                  icon: Icons.check_circle_outline,
                  iconColor: AppColors.green,
                  titre: 'Paiement reçu — Fatou Diallo',
                  detail: '75 000 GNF remboursés. Score mis à jour : Bon ✓',
                  temps: 'Il y a 4h',
                  nonLu: false,
                ),
                const Divider(height: 1, thickness: 0.5),
                _AlerteTile(
                  icon: Icons.cloud_upload_outlined,
                  iconColor: AppColors.blue,
                  titre: 'Synchronisation terminée',
                  detail: '5 transactions offline envoyées vers le cloud.',
                  temps: 'Il y a 6h',
                  nonLu: false,
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),

          // Config alertes
          Text('Paramètres alertes', style: Theme.of(context).textTheme.labelLarge),
          const SizedBox(height: 8),
          Card(
            child: Column(
              children: [
                _AlerteToggle(label: 'Stock faible', detail: 'Notification immédiate', value: true),
                const Divider(height: 1, thickness: 0.5),
                _AlerteToggle(label: 'Rappel dettes · 1 jour', detail: 'Avant échéance', value: true),
                const Divider(height: 1, thickness: 0.5),
                _AlerteToggle(label: 'Rappel dettes · 3 jours', detail: 'Avant échéance', value: true),
                const Divider(height: 1, thickness: 0.5),
                _AlerteToggle(label: 'Rappel dettes · 7 jours', detail: 'Avant échéance', value: false),
                const Divider(height: 1, thickness: 0.5),
                _AlerteToggle(label: 'Baisse des ventes', detail: 'Si -20% vs semaine passée', value: false),
              ],
            ),
          ),
          const SizedBox(height: 80),
        ],
      ),
    );
  }
}

class _AlerteTile extends StatelessWidget {
  final IconData icon;
  final Color iconColor;
  final String titre;
  final String detail;
  final String temps;
  final bool nonLu;
  final List<_AlerteAction> actions;

  const _AlerteTile({
    required this.icon,
    required this.iconColor,
    required this.titre,
    required this.detail,
    required this.temps,
    required this.nonLu,
    this.actions = const [],
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(14),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 34,
            height: 34,
            decoration: BoxDecoration(
              color: iconColor.withOpacity(0.1),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, size: 16, color: iconColor),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(titre, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w500)),
                const SizedBox(height: 2),
                Text(detail, style: const TextStyle(fontSize: 12, color: AppColors.gray400)),
                const SizedBox(height: 4),
                Text(temps, style: const TextStyle(fontSize: 11, color: AppColors.gray200)),
                if (actions.isNotEmpty) ...[
                  const SizedBox(height: 10),
                  Row(
                    children: actions.map((a) => Padding(
                      padding: const EdgeInsets.only(right: 8),
                      child: GestureDetector(
                        onTap: a.onTap,
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                          decoration: BoxDecoration(
                            color: a.isPrimary ? AppColors.green : Colors.white,
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(
                              color: a.isPrimary ? AppColors.green : AppColors.gray200.withOpacity(0.5),
                              width: 0.5,
                            ),
                          ),
                          child: Text(
                            a.label,
                            style: TextStyle(
                              fontSize: 11,
                              color: a.isPrimary ? Colors.white : AppColors.gray600,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ),
                      ),
                    )).toList(),
                  ),
                ],
              ],
            ),
          ),
          if (nonLu)
            Container(
              width: 8,
              height: 8,
              decoration: BoxDecoration(color: iconColor, shape: BoxShape.circle),
            ),
        ],
      ),
    );
  }
}

class _AlerteAction {
  final String label;
  final VoidCallback onTap;
  final bool isPrimary;
  const _AlerteAction({required this.label, required this.onTap, this.isPrimary = false});
}

class _AlerteToggle extends StatefulWidget {
  final String label;
  final String detail;
  final bool value;

  const _AlerteToggle({required this.label, required this.detail, required this.value});

  @override
  State<_AlerteToggle> createState() => _AlerteToggleState();
}

class _AlerteToggleState extends State<_AlerteToggle> {
  late bool _value;

  @override
  void initState() {
    super.initState();
    _value = widget.value;
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(widget.label, style: const TextStyle(fontSize: 13)),
                Text(widget.detail, style: const TextStyle(fontSize: 11, color: AppColors.gray400)),
              ],
            ),
          ),
          Switch(
            value: _value,
            onChanged: (v) => setState(() => _value = v),
            activeColor: AppColors.green,
          ),
        ],
      ),
    );
  }
}

// ============================================================
// SETTINGS SCREEN
// ============================================================

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.gray50,
      appBar: AppBar(title: const Text('Paramètres')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Profil boutique
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  Container(
                    width: 56,
                    height: 56,
                    decoration: BoxDecoration(
                      color: AppColors.green,
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: const Icon(Icons.storefront, color: Colors.white, size: 28),
                  ),
                  const SizedBox(height: 10),
                  const Text('Boutique Al Nour', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w500)),
                  const Text('Conakry, Guinée · Admin', style: TextStyle(fontSize: 12, color: AppColors.gray400)),
                  const SizedBox(height: 10),
                  const AppBadge(label: 'Premium actif', type: 'bon'),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          Text('Compte', style: Theme.of(context).textTheme.labelLarge),
          const SizedBox(height: 8),
          _SettingsGroup(items: [
            _SettingsItem(icon: Icons.store_outlined, label: 'Nom de la boutique', value: 'Boutique Al Nour'),
            _SettingsItem(icon: Icons.phone_outlined, label: 'Téléphone', value: '+224 621 00 00 00'),
            _SettingsItem(icon: Icons.lock_outline, label: 'Changer le PIN', onTap: () {}),
          ]),

          const SizedBox(height: 16),
          Text('Utilisateurs', style: Theme.of(context).textTheme.labelLarge),
          const SizedBox(height: 8),
          Card(
            child: Column(
              children: [
                _UtilisateurTile(initiales: 'MK', nom: 'Moussa Kouyaté', role: 'Admin', color: AppColors.green),
                const Divider(height: 1, thickness: 0.5),
                _UtilisateurTile(initiales: 'AM', nom: 'Aminata Magassouba', role: 'Employée', color: AppColors.blue),
                const Divider(height: 1, thickness: 0.5),
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 12),
                  child: Center(
                    child: GestureDetector(
                      child: const Text('+ Ajouter un employé', style: TextStyle(fontSize: 13, color: AppColors.green, fontWeight: FontWeight.w500)),
                    ),
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 16),
          Text('Application', style: Theme.of(context).textTheme.labelLarge),
          const SizedBox(height: 8),
          Card(
            child: Column(
              children: [
                _ToggleItem(label: 'Synchronisation auto', detail: 'Dès connexion internet', value: true),
                const Divider(height: 1, thickness: 0.5),
                _ToggleItem(label: 'Sauvegarde cloud', detail: 'Quotidienne · chiffrée', value: true),
                const Divider(height: 1, thickness: 0.5),
                _ToggleItem(label: 'Mode sombre', detail: '', value: false),
              ],
            ),
          ),

          const SizedBox(height: 16),
          GestureDetector(
            onTap: () => context.push(AppRoutes.abonnement),
            child: Card(
              child: Padding(
                padding: const EdgeInsets.all(14),
                child: Row(
                  children: [
                    Container(
                      width: 34,
                      height: 34,
                      decoration: BoxDecoration(color: AppColors.greenLight, borderRadius: BorderRadius.circular(10)),
                      child: const Icon(Icons.workspace_premium, size: 18, color: AppColors.green),
                    ),
                    const SizedBox(width: 12),
                    const Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Mon abonnement Premium', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w500, color: AppColors.green)),
                          Text('Renouvellement le 5 mai 2025', style: TextStyle(fontSize: 11, color: AppColors.gray400)),
                        ],
                      ),
                    ),
                    const Icon(Icons.chevron_right, size: 16, color: AppColors.gray200),
                  ],
                ),
              ),
            ),
          ),

          const SizedBox(height: 16),
          // Déconnexion
          Card(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
              child: GestureDetector(
                onTap: () => context.read<AuthBloc>().add(AuthLogout()),
                child: const Row(
                  children: [
                    Icon(Icons.logout, size: 18, color: AppColors.red),
                    SizedBox(width: 10),
                    Text('Se déconnecter', style: TextStyle(fontSize: 13, color: AppColors.red)),
                  ],
                ),
              ),
            ),
          ),
          const SizedBox(height: 80),
        ],
      ),
    );
  }
}

class _SettingsGroup extends StatelessWidget {
  final List<_SettingsItem> items;
  const _SettingsGroup({required this.items});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Column(
        children: items.asMap().entries.map((e) {
          return Column(
            children: [
              if (e.key > 0) const Divider(height: 1, thickness: 0.5),
              e.value,
            ],
          );
        }).toList(),
      ),
    );
  }
}

class _SettingsItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final String? value;
  final VoidCallback? onTap;

  const _SettingsItem({required this.icon, required this.label, this.value, this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
        child: Row(
          children: [
            Icon(icon, size: 16, color: AppColors.gray400),
            const SizedBox(width: 10),
            Expanded(child: Text(label, style: const TextStyle(fontSize: 13))),
            if (value != null)
              Text(value!, style: const TextStyle(fontSize: 12, color: AppColors.gray400)),
            const SizedBox(width: 4),
            const Icon(Icons.chevron_right, size: 14, color: AppColors.gray200),
          ],
        ),
      ),
    );
  }
}

class _UtilisateurTile extends StatelessWidget {
  final String initiales;
  final String nom;
  final String role;
  final Color color;

  const _UtilisateurTile({
    required this.initiales,
    required this.nom,
    required this.role,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      child: Row(
        children: [
          CircleAvatar(
            radius: 16,
            backgroundColor: color.withOpacity(0.1),
            child: Text(initiales, style: TextStyle(fontSize: 10, fontWeight: FontWeight.w600, color: color)),
          ),
          const SizedBox(width: 10),
          Expanded(child: Text(nom, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w500))),
          AppBadge(label: role, type: role == 'Admin' ? 'info' : 'moyen'),
        ],
      ),
    );
  }
}

class _ToggleItem extends StatefulWidget {
  final String label;
  final String detail;
  final bool value;

  const _ToggleItem({required this.label, required this.detail, required this.value});

  @override
  State<_ToggleItem> createState() => _ToggleItemState();
}

class _ToggleItemState extends State<_ToggleItem> {
  late bool _value;

  @override
  void initState() {
    super.initState();
    _value = widget.value;
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(widget.label, style: const TextStyle(fontSize: 13)),
                if (widget.detail.isNotEmpty)
                  Text(widget.detail, style: const TextStyle(fontSize: 11, color: AppColors.gray400)),
              ],
            ),
          ),
          Switch(value: _value, onChanged: (v) => setState(() => _value = v), activeColor: AppColors.green),
        ],
      ),
    );
  }
}

// ============================================================
// ABONNEMENT SCREEN
// ============================================================

class AbonnementScreen extends StatefulWidget {
  const AbonnementScreen({super.key});

  @override
  State<AbonnementScreen> createState() => _AbonnementScreenState();
}

class _AbonnementScreenState extends State<AbonnementScreen> {
  String _modePaiement = 'orange_money';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.gray50,
      appBar: AppBar(title: const Text('Abonnement')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Plan gratuit
          _PlanCard(
            titre: 'Gratuit',
            prix: 0,
            isPremium: false,
            features: [
              _Feature('Jusqu\'à 10 dettes', true),
              _Feature('Jusqu\'à 20 clients', true),
              _Feature('Ventes illimitées', true),
              _Feature('Multi-utilisateurs', false),
              _Feature('Alertes intelligentes', false),
              _Feature('Sauvegarde cloud', false),
              _Feature('Statistiques avancées', false),
            ],
          ),
          const SizedBox(height: 12),
          // Plan Premium
          _PlanCard(
            titre: 'Premium',
            prix: 25000,
            isPremium: true,
            isCurrent: true,
            features: [
              _Feature('Dettes illimitées', true),
              _Feature('Clients illimités', true),
              _Feature('Multi-utilisateurs', true),
              _Feature('Alertes intelligentes FCM', true),
              _Feature('Sauvegarde cloud chiffrée', true),
              _Feature('Statistiques avancées + export', true),
              _Feature('Commandes vocales', true),
            ],
          ),
          const SizedBox(height: 20),

          Text('Payer avec', style: Theme.of(context).textTheme.labelLarge),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(child: _ModePaiementBtn(
                icon: Icons.phone_android,
                label: 'Orange Money',
                value: 'orange_money',
                color: Colors.orange,
                selected: _modePaiement == 'orange_money',
                onTap: () => setState(() => _modePaiement = 'orange_money'),
              )),
              const SizedBox(width: 10),
              Expanded(child: _ModePaiementBtn(
                icon: Icons.phone_android,
                label: 'MTN MoMo',
                value: 'mtn_momo',
                color: Colors.amber.shade700,
                selected: _modePaiement == 'mtn_momo',
                onTap: () => setState(() => _modePaiement = 'mtn_momo'),
              )),
            ],
          ),
          const SizedBox(height: 20),
          ElevatedButton(
            onPressed: () {},
            child: const Text('Passer au Premium — 25 000 GNF/mois'),
          ),
          const SizedBox(height: 8),
          const Center(
            child: Text('Annulation possible à tout moment', style: TextStyle(fontSize: 12, color: AppColors.gray400)),
          ),
          const SizedBox(height: 32),
        ],
      ),
    );
  }
}

class _Feature {
  final String label;
  final bool inclus;
  const _Feature(this.label, this.inclus);
}

class _PlanCard extends StatelessWidget {
  final String titre;
  final int prix;
  final bool isPremium;
  final bool isCurrent;
  final List<_Feature> features;

  const _PlanCard({
    required this.titre,
    required this.prix,
    required this.isPremium,
    this.isCurrent = false,
    required this.features,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: isPremium ? AppColors.green : Colors.black.withOpacity(0.08),
          width: isPremium ? 1.5 : 0.5,
        ),
      ),
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(titre, style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w500)),
              const Spacer(),
              if (isCurrent) const AppBadge(label: 'Plan actuel', type: 'bon'),
              if (!isCurrent && isPremium) const AppBadge(label: 'Recommandé', type: 'bon'),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                prix > 0 ? '${_formatGNF(prix)}' : '0',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.w600,
                  color: isPremium ? AppColors.green : AppColors.gray900,
                ),
              ),
              const SizedBox(width: 4),
              Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Text(
                  'GNF/mois',
                  style: const TextStyle(fontSize: 12, color: AppColors.gray400),
                ),
              ),
            ],
          ),
          const Divider(height: 16, thickness: 0.5),
          ...features.map((f) => Padding(
            padding: const EdgeInsets.symmetric(vertical: 4),
            child: Row(
              children: [
                Icon(
                  f.inclus ? Icons.check : Icons.close,
                  size: 14,
                  color: f.inclus ? AppColors.green : AppColors.gray200,
                ),
                const SizedBox(width: 8),
                Text(
                  f.label,
                  style: TextStyle(
                    fontSize: 12,
                    color: f.inclus ? AppColors.gray900 : AppColors.gray200,
                  ),
                ),
              ],
            ),
          )),
        ],
      ),
    );
  }
}

class _ModePaiementBtn extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color color;
  final bool selected;
  final VoidCallback onTap;

  const _ModePaiementBtn({
    required this.icon,
    required this.label,
    required this.value,
    required this.color,
    required this.selected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 150),
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: selected ? AppColors.green : Colors.black.withOpacity(0.08),
            width: selected ? 1.5 : 0.5,
          ),
        ),
        child: Column(
          children: [
            Icon(icon, color: color, size: 24),
            const SizedBox(height: 6),
            Text(label, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w500), textAlign: TextAlign.center),
          ],
        ),
      ),
    );
  }
}

// ============================================================
// PIN SCREEN
// ============================================================

class PinScreen extends StatefulWidget {
  const PinScreen({super.key});

  @override
  State<PinScreen> createState() => _PinScreenState();
}

class _PinScreenState extends State<PinScreen> {
  String _pin = '';
  static const _pinLength = 4;

  void _onTap(String digit) {
    if (_pin.length >= _pinLength) return;
    setState(() => _pin += digit);
    if (_pin.length == _pinLength) {
      Future.delayed(const Duration(milliseconds: 100), () {
        context.read<AuthBloc>().add(AuthPinSubmitted(_pin));
        setState(() => _pin = '');
      });
    }
  }

  void _onDelete() {
    if (_pin.isEmpty) return;
    setState(() => _pin = _pin.substring(0, _pin.length - 1));
  }

  @override
  Widget build(BuildContext context) {
    return BlocListener<AuthBloc, AuthState>(
      listener: (context, state) {
        if (state.status == AuthStatus.authenticated) {
          context.go(AppRoutes.home);
        }
      },
      child: Scaffold(
        backgroundColor: AppColors.gray50,
        body: SafeArea(
          child: Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // Logo
                Container(
                  width: 72,
                  height: 72,
                  decoration: BoxDecoration(
                    color: AppColors.green,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: const Icon(Icons.storefront, color: Colors.white, size: 34),
                ),
                const SizedBox(height: 16),
                const Text('CrédiStock GN', style: TextStyle(fontSize: 22, fontWeight: FontWeight.w500)),
                const SizedBox(height: 4),
                const Text('Boutique Al Nour · Conakry', style: TextStyle(fontSize: 13, color: AppColors.gray400)),
                const SizedBox(height: 40),
                const Text('Entrez votre code PIN', style: TextStyle(fontSize: 14, color: AppColors.gray400)),
                const SizedBox(height: 16),
                // Points PIN
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: List.generate(_pinLength, (i) {
                    final filled = i < _pin.length;
                    return AnimatedContainer(
                      duration: const Duration(milliseconds: 150),
                      margin: const EdgeInsets.symmetric(horizontal: 7),
                      width: 14,
                      height: 14,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: filled ? AppColors.green : Colors.transparent,
                        border: Border.all(color: AppColors.green, width: 1.5),
                      ),
                    );
                  }),
                ),
                // Erreur
                BlocBuilder<AuthBloc, AuthState>(
                  builder: (_, state) {
                    if (state.status == AuthStatus.error) {
                      return Padding(
                        padding: const EdgeInsets.only(top: 12),
                        child: Text(state.errorMessage ?? 'PIN incorrect',
                            style: const TextStyle(fontSize: 12, color: AppColors.red)),
                      );
                    }
                    return const SizedBox(height: 28);
                  },
                ),
                const SizedBox(height: 24),
                // Clavier
                SizedBox(
                  width: 240,
                  child: GridView.count(
                    crossAxisCount: 3,
                    shrinkWrap: true,
                    mainAxisSpacing: 10,
                    crossAxisSpacing: 10,
                    childAspectRatio: 1.4,
                    children: [
                      ...['1','2','3','4','5','6','7','8','9'].map((d) => _PinBtn(label: d, onTap: () => _onTap(d))),
                      const SizedBox(),
                      _PinBtn(label: '0', onTap: () => _onTap('0')),
                      _PinBtn(label: '⌫', onTap: _onDelete, isDelete: true),
                    ],
                  ),
                ),
                const SizedBox(height: 24),
                // Offline badge
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: AppColors.greenLight,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: const Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.circle, size: 8, color: AppColors.green),
                      SizedBox(width: 6),
                      Text('Mode hors ligne disponible', style: TextStyle(fontSize: 12, color: AppColors.greenDark)),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _PinBtn extends StatelessWidget {
  final String label;
  final VoidCallback onTap;
  final bool isDelete;

  const _PinBtn({required this.label, required this.onTap, this.isDelete = false});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        decoration: BoxDecoration(
          color: isDelete ? Colors.transparent : Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: isDelete ? null : Border.all(color: Colors.black.withOpacity(0.08), width: 0.5),
        ),
        child: Center(
          child: Text(
            label,
            style: TextStyle(
              fontSize: isDelete ? 18 : 22,
              fontWeight: FontWeight.w500,
              color: isDelete ? AppColors.gray400 : AppColors.gray900,
            ),
          ),
        ),
      ),
    );
  }
}

// ============================================================
// ONBOARDING SCREEN
// ============================================================

class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key});

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  int _page = 0;

  static const pages = [
    _OnboardPage(icon: Icons.inventory_2_outlined, titre: 'Gérez votre stock',
        detail: 'Suivez vos produits en temps réel et recevez des alertes quand le stock est faible.'),
    _OnboardPage(icon: Icons.people_outline, titre: 'Suivez vos clients',
        detail: 'Enregistrez vos clients, suivez leurs dettes et calculez automatiquement leur score de paiement.'),
    _OnboardPage(icon: Icons.mic_outlined, titre: 'Vendez en 3 clics',
        detail: 'Enregistrez une vente en 3 clics ou dictez-la vocalement. CrédiStock fonctionne même sans internet.'),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: SafeArea(
        child: Column(
          children: [
            const SizedBox(height: 20),
            Expanded(
              child: PageView.builder(
                onPageChanged: (i) => setState(() => _page = i),
                itemCount: pages.length,
                itemBuilder: (_, i) {
                  final p = pages[i];
                  return Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 32),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Container(
                          width: double.infinity,
                          height: 200,
                          decoration: BoxDecoration(
                            color: AppColors.greenLight,
                            borderRadius: BorderRadius.circular(24),
                          ),
                          child: Icon(p.icon, size: 80, color: AppColors.green),
                        ),
                        const SizedBox(height: 32),
                        Text(p.titre, style: Theme.of(context).textTheme.headlineMedium, textAlign: TextAlign.center),
                        const SizedBox(height: 12),
                        Text(p.detail, style: Theme.of(context).textTheme.bodyMedium, textAlign: TextAlign.center),
                      ],
                    ),
                  );
                },
              ),
            ),
            // Dots
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: List.generate(pages.length, (i) {
                return AnimatedContainer(
                  duration: const Duration(milliseconds: 200),
                  margin: const EdgeInsets.symmetric(horizontal: 4),
                  width: _page == i ? 20 : 8,
                  height: 8,
                  decoration: BoxDecoration(
                    color: _page == i ? AppColors.green : AppColors.gray200,
                    borderRadius: BorderRadius.circular(4),
                  ),
                );
              }),
            ),
            const SizedBox(height: 32),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24),
              child: Column(
                children: [
                  ElevatedButton(
                    onPressed: () {
                      if (_page < pages.length - 1) {
                        setState(() => _page++);
                      } else {
                        context.go(AppRoutes.auth);
                      }
                    },
                    child: Text(_page < pages.length - 1 ? 'Suivant →' : 'Commencer'),
                  ),
                  if (_page < pages.length - 1) ...[
                    const SizedBox(height: 10),
                    TextButton(
                      onPressed: () => context.go(AppRoutes.auth),
                      child: const Text('Passer', style: TextStyle(fontSize: 13, color: AppColors.gray400)),
                    ),
                  ],
                ],
              ),
            ),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }
}

class _OnboardPage {
  final IconData icon;
  final String titre;
  final String detail;
  const _OnboardPage({required this.icon, required this.titre, required this.detail});
}

// Screens stub pour compilation (à extraire en fichiers séparés)
class ClientDetailScreen extends StatelessWidget {
  final String clientId;
  const ClientDetailScreen({super.key, required this.clientId});

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Détail client')),
    body: Center(child: Text(clientId)),
  );
}

class PaiementScreen extends StatelessWidget {
  final String detteId;
  const PaiementScreen({super.key, required this.detteId});

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Paiement')),
    body: Center(child: Text(detteId)),
  );
}

String _formatGNF(int montant) {
  final str = montant.toString();
  final buffer = StringBuffer();
  for (int i = 0; i < str.length; i++) {
    if (i > 0 && (str.length - i) % 3 == 0) buffer.write(' ');
    buffer.write(str[i]);
  }
  return buffer.toString();
}