import 'package:credistock_gn/widgets/app_badge.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/app_theme.dart';
import '../../../core/router/app_router.dart';
import '../../../domain/entities/entities.dart';
import '../../blocs/stock/stock_bloc.dart';
import '../../blocs/auth/auth_bloc.dart';


class StockScreen extends StatelessWidget {
  const StockScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocProvider.value(
      value: context.read<StockBloc>()
        ..add(StockWatchStarted(context.read<AuthBloc>().state.boutiqueId ?? '')),
      child: const _StockView(),
    );
  }
}

class _StockView extends StatelessWidget {
  const _StockView();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.gray50,
      body: SafeArea(
        child: Column(
          children: [
            _StockHeader(),
            _SearchBar(),
            _CategorieFilter(),
            Expanded(child: _ProduitList()),
          ],
        ),
      ),
    );
  }
}

// ── Header ──────────────────────────────────────────────────

class _StockHeader extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.white,
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 12),
      child: Row(
        children: [
          Expanded(
            child: BlocBuilder<StockBloc, StockState>(
              buildWhen: (p, c) =>
                  p.totalProduits != c.totalProduits ||
                  p.nombreAlertes != c.nombreAlertes,
              builder: (_, state) => Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Stock', style: Theme.of(context).textTheme.headlineSmall),
                  Text(
                    '${state.totalProduits} produits · ${state.nombreAlertes} alertes',
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                ],
              ),
            ),
          ),
          IconButton(
            onPressed: () => context.push(AppRoutes.produitAjouter),
            icon: const Icon(Icons.add_circle_outline),
            color: AppColors.green,
          ),
        ],
      ),
    );
  }
}

// ── Search ──────────────────────────────────────────────────

class _SearchBar extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.white,
      padding: const EdgeInsets.fromLTRB(16, 0, 16, 10),
      child: TextField(
        onChanged: (v) => context.read<StockBloc>().add(StockSearchChanged(v)),
        decoration: const InputDecoration(
          hintText: 'Rechercher un produit...',
          prefixIcon: Icon(Icons.search, size: 18),
        ),
      ),
    );
  }
}

// ── Catégorie filtre ────────────────────────────────────────

class _CategorieFilter extends StatelessWidget {
  static const categories = [
    (null, 'Tous'),
    ('alimentaire', 'Alimentaire'),
    ('boisson', 'Boissons'),
    ('hygiene', 'Hygiène'),
    ('autre', 'Autre'),
  ];

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<StockBloc, StockState>(
      buildWhen: (p, c) => p.categorieFiltre != c.categorieFiltre,
      builder: (_, state) {
        return Container(
          color: Colors.white,
          height: 44,
          child: ListView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.fromLTRB(16, 6, 16, 6),
            children: categories.map((cat) {
              final (value, label) = cat;
              final selected = state.categorieFiltre == value;
              return Padding(
                padding: const EdgeInsets.only(right: 8),
                child: GestureDetector(
                  onTap: () => context
                      .read<StockBloc>()
                      .add(StockCategorieChanged(value)),
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 200),
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 4),
                    decoration: BoxDecoration(
                      color: selected ? AppColors.greenLight : AppColors.gray50,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(
                        color: selected ? AppColors.green : AppColors.gray200.withOpacity(0.5),
                        width: selected ? 1 : 0.5,
                      ),
                    ),
                    child: Text(
                      label,
                      style: TextStyle(
                        fontSize: 12,
                        color: selected ? AppColors.greenDark : AppColors.gray600,
                        fontWeight: selected ? FontWeight.w500 : FontWeight.w400,
                      ),
                    ),
                  ),
                ),
              );
            }).toList(),
          ),
        );
      },
    );
  }
}

// ── Liste produits ──────────────────────────────────────────

class _ProduitList extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return BlocBuilder<StockBloc, StockState>(
      buildWhen: (p, c) =>
          p.produitsFiltres != c.produitsFiltres ||
          p.produitsEnAlerte != c.produitsEnAlerte ||
          p.status != c.status,
      builder: (_, state) {
        if (state.status == StockStatus.loading) {
          return const Center(child: CircularProgressIndicator());
        }

        if (state.produitsFiltres.isEmpty) {
          return _EmptyState();
        }

        final enAlerte = state.produitsEnAlerte
            .where((p) => state.produitsFiltres.contains(p))
            .toList();
        final normaux = state.produitsFiltres
            .where((p) => !p.estEnAlerteStock)
            .toList();

        return ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Section alertes
            if (enAlerte.isNotEmpty) ...[
              _SectionTitle(
                icon: Icons.warning_amber_rounded,
                label: 'Stock faible',
                color: AppColors.red,
                count: enAlerte.length,
              ),
              const SizedBox(height: 8),
              ...enAlerte.map((p) => Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: _ProduitCard(produit: p, isAlerte: true),
                  )),
              const SizedBox(height: 12),
            ],
            // Section tous
            _SectionTitle(
              icon: Icons.inventory_2_outlined,
              label: 'Tous les produits',
              color: AppColors.gray600,
              count: normaux.length,
            ),
            const SizedBox(height: 8),
            ...normaux.map((p) => Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: _ProduitCard(produit: p, isAlerte: false),
                )),
            const SizedBox(height: 80),
          ],
        );
      },
    );
  }
}

class _SectionTitle extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final int count;

  const _SectionTitle({
    required this.icon,
    required this.label,
    required this.color,
    required this.count,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, size: 14, color: color),
        const SizedBox(width: 6),
        Text(
          label.toUpperCase(),
          style: TextStyle(
            fontSize: 11,
            fontWeight: FontWeight.w600,
            color: color,
            letterSpacing: 0.4,
          ),
        ),
        const SizedBox(width: 8),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 1),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Text(
            '$count',
            style: TextStyle(fontSize: 10, color: color, fontWeight: FontWeight.w600),
          ),
        ),
      ],
    );
  }
}

// ── Produit Card ────────────────────────────────────────────

class _ProduitCard extends StatelessWidget {
  final Produit produit;
  final bool isAlerte;

  const _ProduitCard({required this.produit, required this.isAlerte});

  @override
  Widget build(BuildContext context) {
    final couleur = isAlerte ? AppColors.red : AppColors.green;
    final ratio = produit.seuilAlerte > 0
        ? (produit.quantite / (produit.seuilAlerte * 3)).clamp(0.0, 1.0)
        : 1.0;

    return GestureDetector(
      onTap: () => context.push('/stock/${produit.id}'),
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            children: [
              Row(
                children: [
                  CircleAvatar(
                    radius: 18,
                    backgroundColor: couleur.withOpacity(0.1),
                    child: Text(
                      produit.nom.substring(0, 2).toUpperCase(),
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w600,
                        color: couleur,
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          produit.nom,
                          style: const TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                        Text(
                          produit.categorie.name,
                          style: const TextStyle(
                            fontSize: 11,
                            color: AppColors.gray400,
                          ),
                        ),
                      ],
                    ),
                  ),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      AppBadge(
                        label: '${produit.quantite} unités',
                        type: isAlerte ? 'mauvais' : 'bon',
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '${_formatGNF(produit.prixVente)} GNF/u',
                        style: const TextStyle(
                          fontSize: 11,
                          color: AppColors.gray400,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
              if (isAlerte) ...[
                const SizedBox(height: 8),
                DetteProgressBar(
                  montant: produit.seuilAlerte * 3,
                  montantPaye: produit.quantite,
                  color: isAlerte ? AppColors.red : AppColors.green,
                ),
                const SizedBox(height: 4),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Seuil d\'alerte: ${produit.seuilAlerte} unités',
                      style: const TextStyle(fontSize: 10, color: AppColors.gray400),
                    ),
                    Text(
                      '${(ratio * 100).round()}%',
                      style: TextStyle(
                        fontSize: 10,
                        color: isAlerte ? AppColors.red : AppColors.green,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class _EmptyState extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.inventory_2_outlined, size: 48, color: AppColors.gray200),
          const SizedBox(height: 12),
          Text(
            'Aucun produit trouvé',
            style: Theme.of(context).textTheme.bodyMedium,
          ),
          const SizedBox(height: 8),
          ElevatedButton.icon(
            onPressed: () => context.push(AppRoutes.produitAjouter),
            icon: const Icon(Icons.add, size: 16),
            label: const Text('Ajouter un produit'),
            style: ElevatedButton.styleFrom(
              minimumSize: const Size(0, 40),
              padding: const EdgeInsets.symmetric(horizontal: 20),
            ),
          ),
        ],
      ),
    );
  }
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