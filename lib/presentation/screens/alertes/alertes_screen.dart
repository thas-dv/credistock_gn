import 'package:credistock_gn/core/di/injection.dart';
import 'package:credistock_gn/core/services/app_settings_service.dart';
import 'package:credistock_gn/core/theme/app_theme.dart';
import 'package:credistock_gn/data/local/database/app_database.dart';
import 'package:credistock_gn/domain/repositories/repositories.dart';
import 'package:credistock_gn/presentation/blocs/auth/auth_bloc.dart';
import 'package:drift/drift.dart' hide Column;
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

export '../screens.dart' show AlertesScreen;

class AlertesScreen extends StatelessWidget {
  const AlertesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final boutiqueId = context.read<AuthBloc>().state.boutiqueId;
    if (boutiqueId == null || boutiqueId.isEmpty) {
      return const Scaffold(
          body: Center(child: Text('Aucune boutique active')));
    }

    return FutureBuilder<_AlertesData>(
      future: _loadAlertes(boutiqueId),
      builder: (context, snapshot) {
        if (!snapshot.hasData) {
          return const Scaffold(
              body: Center(child: CircularProgressIndicator()));
        }
        final data = snapshot.data!;
        final settings = getIt<AppSettingsService>();

        return ValueListenableBuilder<AppSettings>(
          valueListenable: settings.settings,
          builder: (context, cfg, _) {
            return Scaffold(
              backgroundColor: AppColors.gray50,
              appBar: AppBar(title: const Text('Alertes')),
              body: ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  Card(
                    child: Column(
                      children: [
                        ...data.items,
                        if (data.items.isEmpty)
                          const Padding(
                            padding: EdgeInsets.all(16),
                            child: Text('Aucune alerte active'),
                          ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 20),
                  Text('Paramètres alertes',
                      style: Theme.of(context).textTheme.labelLarge),
                  const SizedBox(height: 8),
                  Card(
                    child: Column(
                      children: [
                        SwitchListTile(
                          title: const Text('Stock faible'),
                          value: cfg.alertStock,
                          onChanged: settings.setAlertStock,
                        ),
                        const Divider(height: 1),
                        SwitchListTile(
                          title: const Text('Rappel dettes · 1 jour'),
                          value: cfg.alertDette1j,
                          onChanged: settings.setAlert1j,
                        ),
                        const Divider(height: 1),
                        SwitchListTile(
                          title: const Text('Rappel dettes · 3 jours'),
                          value: cfg.alertDette3j,
                          onChanged: settings.setAlert3j,
                        ),
                        const Divider(height: 1),
                        SwitchListTile(
                          title: const Text('Rappel dettes · 7 jours'),
                          value: cfg.alertDette7j,
                          onChanged: settings.setAlert7j,
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            );
          },
        );
      },
    );
  }

  Future<_AlertesData> _loadAlertes(String boutiqueId) async {
    final db = getIt<AppDatabase>();
    final syncRepo = getIt<SyncRepository>();

    final produits = await (db.select(db.produits)
          ..where((p) =>
              p.boutiqueId.equals(boutiqueId) &
              p.quantite.isSmallerOrEqual(p.seuilAlerte))
          ..orderBy([(p) => OrderingTerm.asc(p.quantite)]))
        .get();

    final dettes = await (db.select(db.dettes)
          ..where((d) =>
              d.boutiqueId.equals(boutiqueId) & d.statut.equals('non_paye'))
          ..orderBy([(d) => OrderingTerm.asc(d.dateEcheance)]))
        .get();

    final clients = await (db.select(db.clients)
          ..where((c) => c.boutiqueId.equals(boutiqueId)))
        .get();
    final namesById = {for (final c in clients) c.id: c.nom};
    final pending = await syncRepo.getNombreElementsNonSynces();

    final widgets = <Widget>[];

    for (final p in produits.take(3)) {
      widgets.add(ListTile(
        leading: const Icon(Icons.inventory_2_outlined, color: AppColors.red),
        title: Text('Stock critique — ${p.nom}'),
        subtitle: Text('Seulement ${p.quantite} unités restantes'),
      ));
      widgets.add(const Divider(height: 1));
    }

    for (final d in dettes.take(3)) {
      final clientNom = namesById[d.clientId] ?? d.clientId;
      widgets.add(ListTile(
        leading: const Icon(Icons.access_time, color: AppColors.amber),
        title: Text('Échéance — $clientNom'),
        subtitle: Text('Montant: ${d.montant - d.montantPaye} GNF'),
      ));
      widgets.add(const Divider(height: 1));
    }

    if (pending > 0) {
      widgets.add(ListTile(
        leading: const Icon(Icons.cloud_upload_outlined, color: AppColors.blue),
        title: const Text('Synchronisation en attente'),
        subtitle: Text('$pending élément(s) hors ligne à envoyer au cloud'),
      ));
    }

    return _AlertesData(widgets);
  }
}

class _AlertesData {
  final List<Widget> items;
  _AlertesData(this.items);
}
