import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/local/database/app_database.dart';
import '../providers/app_providers.dart';

final alertesProvider = StreamProvider.autoDispose<List<CreditStockAlerte>>((ref) {
  final session = ref.watch(sessionProvider);
  if (!session.isLoggedIn) return Stream.value(const []);

  final db = ref.watch(appDatabaseProvider);
  return (db.select(db.creditStockAlertes)
        ..where((a) => a.boutiqueId.equals(session.boutiqueId!))
        ..orderBy([(a) => OrderingTerm.desc(a.createdAt)]))
      .watch();
});

class AlertesPage extends ConsumerWidget {
  const AlertesPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final alertesAsync = ref.watch(alertesProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Alertes')),
      body: alertesAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (_, __) => const Center(child: Text('Erreur de chargement des alertes')),
        data: (alertes) {
          if (alertes.isEmpty) return const Center(child: Text('Aucune alerte'));

          return ListView.separated(
            padding: const EdgeInsets.all(16),
            itemCount: alertes.length,
            separatorBuilder: (_, __) => const SizedBox(height: 8),
            itemBuilder: (_, i) {
              final a = alertes[i];
              return ListTile(
                tileColor: Colors.white,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                title: Text(a.titre),
                subtitle: Text(a.message ?? ''),
                trailing: Icon(a.lu ? Icons.mark_email_read_outlined : Icons.mark_email_unread_outlined),
              );
            },
          );
        },
      ),
    );
  }
}
