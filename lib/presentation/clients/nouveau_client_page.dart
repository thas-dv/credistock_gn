import 'dart:convert';

import 'package:drift/drift.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:uuid/uuid.dart';

import '../../data/local/database/app_database.dart';
import '../providers/app_providers.dart';

class NouveauClientPage extends ConsumerStatefulWidget {
  const NouveauClientPage({super.key});

  @override
  ConsumerState<NouveauClientPage> createState() => _NouveauClientPageState();
}

class _NouveauClientPageState extends ConsumerState<NouveauClientPage> {
  final _formKey = GlobalKey<FormState>();
  final _nomCtrl = TextEditingController();
  final _telephoneCtrl = TextEditingController();
  bool _saving = false;

  @override
  void dispose() {
    _nomCtrl.dispose();
    _telephoneCtrl.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    final session = ref.read(sessionProvider);
    if (!session.isLoggedIn) return;

    setState(() => _saving = true);
    final db = ref.read(appDatabaseProvider);
    final id = const Uuid().v4();
    final payload = {
      'id': id,
      'boutique_id': session.boutiqueId,
      'nom': _nomCtrl.text.trim(),
      'telephone': _telephoneCtrl.text.trim().isEmpty
          ? null
          : _telephoneCtrl.text.trim(),
      'score': 'moyen',
      'total_du': 0,
      'nb_achats': 0,
      'nb_retards': 0,
      'synced': false,
      'created_at': DateTime.now().toIso8601String(),
      'updated_at': DateTime.now().toIso8601String(),
    };

    await db.into(db.creditStockClients).insert(
          CreditStockClientsCompanion.insert(
            id: id,
            boutiqueId: session.boutiqueId!,
            nom: _nomCtrl.text.trim(),
            telephone: Value(_telephoneCtrl.text.trim().isEmpty
                ? null
                : _telephoneCtrl.text.trim()),
            synced: const Value(false),
          ),
        );

    await db.into(db.creditStockSyncQueue).insert(
          CreditStockSyncQueueCompanion.insert(
            id: const Uuid().v4(),
            boutiqueId: session.boutiqueId!,
            tableName_: 'credistock_clients',
            operation: 'INSERT',
            recordId: id,
            payload: jsonEncode(payload),
          ),
        );

    if (mounted) {
      Navigator.pop(context);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Client ajouté avec succès')),
      );
    }
    setState(() => _saving = false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Nouveau client')),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            TextFormField(
              controller: _nomCtrl,
              decoration: const InputDecoration(labelText: 'Nom complet'),
              validator: (v) =>
                  (v == null || v.trim().isEmpty) ? 'Champ requis' : null,
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _telephoneCtrl,
              keyboardType: TextInputType.phone,
              decoration:
                  const InputDecoration(labelText: 'Téléphone (optionnel)'),
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
                  : const Icon(Icons.person_add_alt_1),
              label: const Text('Enregistrer'),
            ),
          ],
        ),
      ),
    );
  }
}
