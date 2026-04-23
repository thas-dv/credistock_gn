import 'package:drift/drift.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../core/theme/app_theme.dart';
import '../../data/local/database/app_database.dart';
import '../providers/app_providers.dart';

final produitsProvider = StreamProvider.autoDispose<List<CreditStockProduit>>((ref) {
  final session = ref.watch(sessionProvider);
  if (!session.isLoggedIn) return Stream.value(const []);

  final db = ref.watch(appDatabaseProvider);
  return (db.select(db.creditStockProduits)
        ..where((p) => p.boutiqueId.equals(session.boutiqueId!) & p.actif.isValue(true))
        ..orderBy([(p) => OrderingTerm.asc(p.nom)]))
      .watch();
});

class StockPage extends ConsumerWidget {
  const StockPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final colors = Theme.of(context).extension<CreditStockColors>()!;
    final produitsAsync = ref.watch(produitsProvider);
    final fmt = NumberFormat('#,###', 'fr_FR');

    return Scaffold(
      appBar: AppBar(title: const Text('Stock')),
      body: produitsAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (_, __) => const Center(child: Text('Erreur de chargement du stock')),
        data: (produits) {
          if (produits.isEmpty) return const _EmptyState(label: 'Aucun produit ajouté');

          return ListView.separated(
            padding: const EdgeInsets.all(16),
            itemCount: produits.length,
            separatorBuilder: (_, __) => const SizedBox(height: 10),
            itemBuilder: (_, i) {
              final p = produits[i];
              final faible = p.quantite <= p.seuilAlerte;
              return ListTile(
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                tileColor: Colors.white,
                title: Text(p.nom, style: const TextStyle(fontWeight: FontWeight.w600)),
                subtitle: Text('${fmt.format(p.prixVente)} GNF • ${p.quantite} ${p.unite}'),
                trailing: faible
                    ? Icon(Icons.warning_amber_rounded, color: colors.amber)
                    : Icon(Icons.check_circle_outline, color: colors.green),
              );
            },
          );
        },
      ),
    );
  }
}

class _EmptyState extends StatelessWidget {
  const _EmptyState({required this.label});
  final String label;

  @override
  Widget build(BuildContext context) {
    return Center(child: Text(label));
  }
}
