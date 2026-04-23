import 'dart:convert';

import 'package:drift/drift.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:uuid/uuid.dart';

import '../../data/local/database/app_database.dart';
import '../providers/app_providers.dart';

final produitsVenteProvider =
    FutureProvider.autoDispose<List<CreditStockProduit>>((ref) async {
  final session = ref.watch(sessionProvider);
  if (!session.isLoggedIn) return const [];

  final db = ref.watch(appDatabaseProvider);
  return (db.select(db.creditStockProduits)
        ..where((p) =>
            p.boutiqueId.equals(session.boutiqueId!) & p.actif.equals(true))
        ..orderBy([(p) => OrderingTerm.asc(p.nom)]))
      .get();
});

final clientsVenteProvider =
    FutureProvider.autoDispose<List<CreditStockClient>>((ref) async {
  final session = ref.watch(sessionProvider);
  if (!session.isLoggedIn) return const [];

  final db = ref.watch(appDatabaseProvider);
  return (db.select(db.creditStockClients)
        ..where((c) => c.boutiqueId.equals(session.boutiqueId!))
        ..orderBy([(c) => OrderingTerm.asc(c.nom)]))
      .get();
});

class NouvelleVentePage extends ConsumerStatefulWidget {
  const NouvelleVentePage({super.key});
  @override
  ConsumerState<NouvelleVentePage> createState() => _NouvelleVentePageState();
}

class _NouvelleVentePageState extends ConsumerState<NouvelleVentePage> {
  String _typePaiement = 'cash';
  String? _clientId;
  bool _saving = false;
  final Map<String, int> _quantites = {};

  int _total(List<CreditStockProduit> produits) {
    var sum = 0;
    for (final p in produits) {
      final q = _quantites[p.id] ?? 0;
      sum += q * p.prixVente;
    }
    return sum;
  }

  Future<void> _save(List<CreditStockProduit> produits) async {
    final session = ref.read(sessionProvider);
    if (!session.isLoggedIn) return;

    final lignes = produits.where((p) => (_quantites[p.id] ?? 0) > 0).toList();
    if (lignes.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Sélectionnez au moins un produit')),
      );
      return;
    }
    if (_typePaiement == 'credit' && _clientId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
            content: Text('Choisissez un client pour une vente à crédit')),
      );
      return;
    }

    setState(() => _saving = true);

    final db = ref.read(appDatabaseProvider);
    final now = DateTime.now();
    final venteId = const Uuid().v4();
    final total = _total(produits);

    await db.into(db.creditStockVentes).insert(
          CreditStockVentesCompanion.insert(
            id: venteId,
            boutiqueId: session.boutiqueId!,
            utilisateurId: Value(session.utilisateurId),
            clientId: Value(_clientId),
            typePaiement: Value(_typePaiement),
            montantTotal: Value(total),
            synced: const Value(false),
            dateVente: Value(now),
          ),
        );

    final ventePayload = {
      'id': venteId,
      'boutique_id': session.boutiqueId,
      'utilisateur_id': session.utilisateurId,
      'client_id': _clientId,
      'type_paiement': _typePaiement,
      'montant_total': total,
      'synced': false,
      'date_vente': now.toIso8601String(),
      'created_at': now.toIso8601String(),
    };

    await db.into(db.creditStockSyncQueue).insert(
          CreditStockSyncQueueCompanion.insert(
            id: const Uuid().v4(),
            boutiqueId: session.boutiqueId!,
            tableName_: 'credistock_ventes',
            operation: 'INSERT',
            recordId: venteId,
            payload: jsonEncode(ventePayload),
          ),
        );

    for (final p in lignes) {
      final q = _quantites[p.id] ?? 0;
      final lineId = const Uuid().v4();
      await db.into(db.creditStockLignesVente).insert(
            CreditStockLignesVenteCompanion.insert(
              id: lineId,
              venteId: venteId,
              produitId: p.id,
              boutiqueId: session.boutiqueId!,
              nomProduit: p.nom,
              quantite: Value(q),
              prixUnitaire: Value(p.prixVente),
              sousTotal: Value(q * p.prixVente),
              synced: const Value(false),
            ),
          );

      await (db.update(db.creditStockProduits)
            ..where((it) => it.id.equals(p.id)))
          .write(
        CreditStockProduitsCompanion.custom(
          quantite: db.creditStockProduits.quantite - Constant(q),
          updatedAt: Constant(now),
          synced: const Constant(false),
        ),
      );

      final linePayload = {
        'id': lineId,
        'vente_id': venteId,
        'produit_id': p.id,
        'boutique_id': session.boutiqueId,
        'nom_produit': p.nom,
        'quantite': q,
        'prix_unitaire': p.prixVente,
        'sous_total': q * p.prixVente,
        'synced': false,
        'created_at': now.toIso8601String(),
      };

      await db.into(db.creditStockSyncQueue).insert(
            CreditStockSyncQueueCompanion.insert(
              id: const Uuid().v4(),
              boutiqueId: session.boutiqueId!,
              tableName_: 'credistock_lignes_vente',
              operation: 'INSERT',
              recordId: lineId,
              payload: jsonEncode(linePayload),
            ),
          );
    }

    if (_typePaiement == 'credit' && _clientId != null) {
      final detteId = const Uuid().v4();
      await db.into(db.creditStockDettes).insert(
            CreditStockDettesCompanion.insert(
              id: detteId,
              boutiqueId: session.boutiqueId!,
              clientId: _clientId!,
              venteId: Value(venteId),
              montantInitial: Value(total),
              montantPaye: const Value(0),
              statut: const Value('non_paye'),
              synced: const Value(false),
              updatedAt: Value(now),
            ),
          );

      await (db.update(db.creditStockClients)
            ..where((c) => c.id.equals(_clientId!)))
          .write(
        CreditStockClientsCompanion.custom(
            totalDu: db.creditStockClients.totalDu + Constant(total)),
      );

      final dettePayload = {
        'id': detteId,
        'boutique_id': session.boutiqueId,
        'client_id': _clientId,
        'vente_id': venteId,
        'montant_initial': total,
        'montant_paye': 0,
        'statut': 'non_paye',
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
              recordId: detteId,
              payload: jsonEncode(dettePayload),
            ),
          );
    }

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Vente enregistrée avec succès')),
      );
      Navigator.pop(context);
    }

    setState(() => _saving = false);
  }

  @override
  Widget build(BuildContext context) {
    final produitsAsync = ref.watch(produitsVenteProvider);
    final clientsAsync = ref.watch(clientsVenteProvider);
    final money = NumberFormat('#,###', 'fr_FR');

    return Scaffold(
      appBar: AppBar(title: const Text('Nouvelle vente')),
      body: produitsAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (_, __) =>
            const Center(child: Text('Erreur de chargement des produits')),
        data: (produits) {
          if (produits.isEmpty) {
            return const Center(
                child: Text('Ajoutez des produits avant de faire une vente'));
          }

          final total = _total(produits);

          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              SegmentedButton<String>(
                segments: const [
                  ButtonSegment(
                      value: 'cash',
                      icon: Icon(Icons.payments_outlined),
                      label: Text('Cash')),
                  ButtonSegment(
                      value: 'credit',
                      icon: Icon(Icons.credit_card_outlined),
                      label: Text('Crédit')),
                ],
                selected: {_typePaiement},
                onSelectionChanged: (s) =>
                    setState(() => _typePaiement = s.first),
              ),
              const SizedBox(height: 12),
              if (_typePaiement == 'credit')
                clientsAsync.when(
                  loading: () => const LinearProgressIndicator(),
                  error: (_, __) =>
                      const Text('Impossible de charger les clients'),
                  data: (clients) {
                    if (clients.isEmpty) {
                      return const Text(
                          'Ajoutez un client pour la vente à crédit');
                    }
                    _clientId ??= clients.first.id;
                    return DropdownButtonFormField<String>(
                      value: _clientId,
                      items: clients
                          .map((c) => DropdownMenuItem<String>(
                              value: c.id, child: Text(c.nom)))
                          .toList(),
                      onChanged: (v) => setState(() => _clientId = v),
                      decoration: const InputDecoration(labelText: 'Client'),
                    );
                  },
                ),
              const SizedBox(height: 16),
              Text('Produits', style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(height: 8),
              ...produits.map((p) {
                final q = _quantites[p.id] ?? 0;
                return Card(
                  child: ListTile(
                    title: Text(p.nom),
                    subtitle: Text(
                        '${money.format(p.prixVente)} GNF • Stock: ${p.quantite}'),
                    trailing: SizedBox(
                      width: 112,
                      child: Row(
                        children: [
                          IconButton(
                            onPressed: q > 0
                                ? () => setState(() => _quantites[p.id] = q - 1)
                                : null,
                            icon: const Icon(Icons.remove_circle_outline),
                          ),
                          Text('$q'),
                          IconButton(
                            onPressed: q < p.quantite
                                ? () => setState(() => _quantites[p.id] = q + 1)
                                : null,
                            icon: const Icon(Icons.add_circle_outline),
                          ),
                        ],
                      ),
                    ),
                  ),
                );
              }),
              const SizedBox(height: 10),
              Card(
                child: ListTile(
                  title: const Text('Total'),
                  trailing: Text(
                    '${money.format(total)} GNF',
                    style: const TextStyle(
                        fontWeight: FontWeight.bold, fontSize: 18),
                  ),
                ),
              ),
              const SizedBox(height: 10),
              ElevatedButton.icon(
                onPressed: _saving ? null : () => _save(produits),
                icon: _saving
                    ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.save_outlined),
                label: const Text('Valider la vente'),
              ),
            ],
          );
        },
      ),
    );
  }
}
