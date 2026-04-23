import 'dart:convert';

import 'package:drift/drift.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:uuid/uuid.dart';

import '../../data/local/database/app_database.dart';
import '../providers/app_providers.dart';

final clientsDetteProvider = FutureProvider.autoDispose<List<CreditStockClient>>((ref) async {
  final session = ref.watch(sessionProvider);
  if (!session.isLoggedIn) return const [];

  final db = ref.watch(appDatabaseProvider);
  return (db.select(db.creditStockClients)
        ..where((c) => c.boutiqueId.equals(session.boutiqueId!))
        ..orderBy([(c) => OrderingTerm.asc(c.nom)]))
      .get();
});

class NouvelleDettePage extends ConsumerStatefulWidget {
  const NouvelleDettePage({super.key});

  @override
  ConsumerState<NouvelleDettePage> createState() => _NouvelleDettePageState();
}

class _NouvelleDettePageState extends ConsumerState<NouvelleDettePage> {
  final _formKey = GlobalKey<FormState>();
  final _montantCtrl = TextEditingController();
  final _noteCtrl = TextEditingController();
  String? _clientId;
  bool _saving = false;

  @override
  void dispose() {
    _montantCtrl.dispose();
    _noteCtrl.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    final session = ref.read(sessionProvider);
    if (!session.isLoggedIn || _clientId == null) return;

    setState(() => _saving = true);

    final db = ref.read(appDatabaseProvider);
    final id = const Uuid().v4();
    final now = DateTime.now();
    final montant = int.parse(_montantCtrl.text.trim());

    await db.into(db.creditStockDettes).insert(
          CreditStockDettesCompanion.insert(
            id: id,
            boutiqueId: session.boutiqueId!,
            clientId: _clientId!,
            montantInitial: Value(montant),
            montantPaye: const Value(0),
            statut: const Value('non_paye'),
            note: Value(_noteCtrl.text.trim().isEmpty ? null : _noteCtrl.text.trim()),
            synced: const Value(false),
            updatedAt: Value(now),
          ),
        );

    await (db.update(db.creditStockClients)..where((c) => c.id.equals(_clientId!))).write(
      CreditStockClientsCompanion.custom(totalDu: db.creditStockClients.totalDu + Constant(montant)),
    );

    final payload = {
      'id': id,
      'boutique_id': session.boutiqueId,
      'client_id': _clientId,
      'montant_initial': montant,
      'montant_paye': 0,
      'statut': 'non_paye',
      'note': _noteCtrl.text.trim().isEmpty ? null : _noteCtrl.text.trim(),
      'synced': false,
      'created_at': now.toIso8601String(),
      'updated_at': now.toIso8601String(),
    };

    await db.into(db.creditStockSyncQueue).insert(
          CreditStockSyncQueueCompanion.insert(
            id: const Uuid().v4(),
            boutiqueId: session.boutiqueId!,
            tableName_: 'credistock_dettes',
            operation: 'INSERT',
            recordId: id,
            payload: jsonEncode(payload),
          ),
        );

    if (mounted) {
      Navigator.pop(context);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Dette enregistrée avec succès')),
      );
    }

    setState(() => _saving = false);
  }

  @override
  Widget build(BuildContext context) {
    final clientsAsync = ref.watch(clientsDetteProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Nouvelle dette')),
      body: clientsAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (_, __) => const Center(child: Text('Impossible de charger les clients')),
        data: (clients) {
          if (clients.isEmpty) {
            return const Center(child: Text('Ajoutez d’abord un client pour créer une dette'));
          }

          _clientId ??= clients.first.id;

          return Form(
            key: _formKey,
            child: ListView(
              padding: const EdgeInsets.all(16),
              children: [
                DropdownButtonFormField<String>(
                  value: _clientId,
                  items: clients
                      .map((c) => DropdownMenuItem<String>(value: c.id, child: Text(c.nom)))
                      .toList(),
                  onChanged: (v) => setState(() => _clientId = v),
                  decoration: const InputDecoration(labelText: 'Client'),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _montantCtrl,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(labelText: 'Montant dû (GNF)'),
                  validator: (v) => (v == null || int.tryParse(v) == null || int.parse(v) <= 0)
                      ? 'Montant invalide'
                      : null,
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _noteCtrl,
                  minLines: 2,
                  maxLines: 4,
                  decoration: const InputDecoration(labelText: 'Note (optionnel)'),
                ),
                const SizedBox(height: 20),
                ElevatedButton.icon(
                  onPressed: _saving ? null : _save,
                  icon: _saving
                      ? const SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Icon(Icons.receipt_long_outlined),
                  label: const Text('Créer la dette'),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}
