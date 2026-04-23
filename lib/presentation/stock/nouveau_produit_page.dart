import 'dart:convert';

import 'package:drift/drift.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:uuid/uuid.dart';

import '../../data/local/database/app_database.dart';
import '../providers/app_providers.dart';

class NouveauProduitPage extends ConsumerStatefulWidget {
  const NouveauProduitPage({super.key});

  @override
  ConsumerState<NouveauProduitPage> createState() => _NouveauProduitPageState();
}

class _NouveauProduitPageState extends ConsumerState<NouveauProduitPage> {
  final _formKey = GlobalKey<FormState>();
  final _nomCtrl = TextEditingController();
  final _prixVenteCtrl = TextEditingController();
  final _prixAchatCtrl = TextEditingController();
  final _quantiteCtrl = TextEditingController(text: '0');
  final _seuilCtrl = TextEditingController(text: '5');
  bool _saving = false;

  @override
  void dispose() {
    _nomCtrl.dispose();
    _prixVenteCtrl.dispose();
    _prixAchatCtrl.dispose();
    _quantiteCtrl.dispose();
    _seuilCtrl.dispose();
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
      'prix_vente': int.parse(_prixVenteCtrl.text.trim()),
      'prix_achat': int.tryParse(_prixAchatCtrl.text.trim()) ?? 0,
      'quantite': int.parse(_quantiteCtrl.text.trim()),
      'seuil_alerte': int.parse(_seuilCtrl.text.trim()),
      'unite': 'unité',
      'actif': true,
      'synced': false,
      'created_at': DateTime.now().toIso8601String(),
      'updated_at': DateTime.now().toIso8601String(),
    };

    await db.into(db.creditStockProduits).insert(
          CreditStockProduitsCompanion.insert(
            id: id,
            boutiqueId: session.boutiqueId!,
            nom: _nomCtrl.text.trim(),
            prixVente: Value(int.parse(_prixVenteCtrl.text.trim())),
            prixAchat: Value(int.tryParse(_prixAchatCtrl.text.trim()) ?? 0),
            quantite: Value(int.parse(_quantiteCtrl.text.trim())),
            seuilAlerte: Value(int.parse(_seuilCtrl.text.trim())),
            synced: const Value(false),
          ),
        );

    await db.into(db.creditStockSyncQueue).insert(
          CreditStockSyncQueueCompanion.insert(
            id: const Uuid().v4(),
            boutiqueId: session.boutiqueId!,
            tableName_: 'credistock_produits',
            operation: 'INSERT',
            recordId: id,
            payload: jsonEncode(payload),
          ),
        );

    if (mounted) {
      Navigator.pop(context);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Produit ajouté avec succès')),
      );
    }

    setState(() => _saving = false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Nouveau produit')),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            TextFormField(
              controller: _nomCtrl,
              decoration: const InputDecoration(labelText: 'Nom du produit'),
              validator: (v) => (v == null || v.trim().isEmpty) ? 'Champ requis' : null,
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _prixVenteCtrl,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(labelText: 'Prix de vente (GNF)'),
              validator: (v) => (v == null || int.tryParse(v) == null) ? 'Prix invalide' : null,
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _prixAchatCtrl,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(labelText: 'Prix d\'achat (optionnel)'),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: TextFormField(
                    controller: _quantiteCtrl,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(labelText: 'Quantité'),
                    validator: (v) => (v == null || int.tryParse(v) == null) ? 'Valeur invalide' : null,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: TextFormField(
                    controller: _seuilCtrl,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(labelText: 'Seuil alerte'),
                    validator: (v) => (v == null || int.tryParse(v) == null) ? 'Valeur invalide' : null,
                  ),
                ),
              ],
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
                  : const Icon(Icons.save),
              label: const Text('Enregistrer'),
            ),
          ],
        ),
      ),
    );
  }
}
