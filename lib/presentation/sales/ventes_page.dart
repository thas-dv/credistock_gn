import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../data/local/database/app_database.dart';
import '../providers/app_providers.dart';

final ventesProvider = StreamProvider.autoDispose<List<CreditStockVente>>((ref) {
  final session = ref.watch(sessionProvider);
  if (!session.isLoggedIn) return Stream.value(const []);

  final db = ref.watch(appDatabaseProvider);
  return (db.select(db.creditStockVentes)
        ..where((v) => v.boutiqueId.equals(session.boutiqueId!))
        ..orderBy([(v) => OrderingTerm.desc(v.dateVente)]))
      .watch();
});

class VentesPage extends ConsumerWidget {
  const VentesPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final ventesAsync = ref.watch(ventesProvider);
    final money = NumberFormat('#,###', 'fr_FR');
    final date = DateFormat('dd/MM/yyyy HH:mm', 'fr_FR');

    return Scaffold(
      appBar: AppBar(title: const Text('Ventes')),
      body: ventesAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (_, __) => const Center(child: Text('Erreur de chargement des ventes')),
        data: (ventes) {
          if (ventes.isEmpty) return const Center(child: Text('Aucune vente enregistrée'));

          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: ventes.length,
            itemBuilder: (_, i) {
              final v = ventes[i];
              return Card(
                child: ListTile(
                  title: Text('${money.format(v.montantTotal)} GNF'),
                  subtitle: Text(date.format(v.dateVente)),
                  trailing: Text(v.typePaiement),
                ),
              );
            },
          );
        },
      ),
    );
  }
}
