import 'package:flutter/material.dart';
import 'package:drift/drift.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../data/local/database/app_database.dart';
import '../providers/app_providers.dart';

final dettesProvider = StreamProvider.autoDispose<List<CreditStockDette>>((ref) {
  final session = ref.watch(sessionProvider);
  if (!session.isLoggedIn) return Stream.value(const []);

  final db = ref.watch(appDatabaseProvider);
  return (db.select(db.creditStockDettes)
        ..where((d) => d.boutiqueId.equals(session.boutiqueId!))
        ..orderBy([(d) => OrderingTerm.desc(d.createdAt)]))
      .watch();
});

class DettesPage extends ConsumerWidget {
  const DettesPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final dettesAsync = ref.watch(dettesProvider);
    final fmt = NumberFormat('#,###', 'fr_FR');

    return Scaffold(
          floatingActionButton: FloatingActionButton.extended(
        onPressed: () => Navigator.pushNamed(context, '/nouvelle-dette'),
        icon: const Icon(Icons.note_add_outlined),
        label: const Text('Dette'),
      ),
      appBar: AppBar(title: const Text('Dettes')),
      body: dettesAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (_, __) => const Center(child: Text('Erreur de chargement des dettes')),
        data: (dettes) {
          if (dettes.isEmpty) return const Center(child: Text('Aucune dette enregistrée'));

          return ListView.separated(
            padding: const EdgeInsets.all(16),
            itemCount: dettes.length,
            separatorBuilder: (_, __) => const SizedBox(height: 10),
            itemBuilder: (_, i) {
              final d = dettes[i];
              final restant = d.montantInitial - d.montantPaye;
              return ListTile(
                tileColor: Colors.white,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                title: Text('Dette #${i + 1}'),
                subtitle: Text('Statut: ${d.statut}'),
                trailing: Text('${fmt.format(restant)} GNF'),
              );
            },
          );
        },
      ),
    );
  }
}
