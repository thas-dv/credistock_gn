import 'package:flutter/material.dart';
import 'package:drift/drift.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../data/local/database/app_database.dart';
import '../providers/app_providers.dart';

final clientsProvider =
    StreamProvider.autoDispose<List<CreditStockClient>>((ref) {
  final session = ref.watch(sessionProvider);
  if (!session.isLoggedIn) return Stream.value(const []);

  final db = ref.watch(appDatabaseProvider);
  return (db.select(db.creditStockClients)
        ..where((c) => c.boutiqueId.equals(session.boutiqueId!))
        ..orderBy([(c) => OrderingTerm.asc(c.nom)]))
      .watch();
});

class ClientsPage extends ConsumerWidget {
  const ClientsPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final clientsAsync = ref.watch(clientsProvider);
    final fmt = NumberFormat('#,###', 'fr_FR');

    return Scaffold(
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => Navigator.pushNamed(context, '/nouveau-client'),
        icon: const Icon(Icons.person_add_alt_1),
        label: const Text('Client'),
      ),
      appBar: AppBar(title: const Text('Clients')),
      body: clientsAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (_, __) =>
            const Center(child: Text('Erreur de chargement des clients')),
        data: (clients) {
          if (clients.isEmpty)
            return const Center(child: Text('Aucun client enregistré'));

          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: clients.length,
            itemBuilder: (_, i) {
              final c = clients[i];
              return Card(
                child: ListTile(
                  title: Text(c.nom),
                  subtitle: Text(c.telephone ?? 'Téléphone non renseigné'),
                  trailing: Text('${fmt.format(c.totalDu)} GNF'),
                ),
              );
            },
          );
        },
      ),
    );
  }
}
