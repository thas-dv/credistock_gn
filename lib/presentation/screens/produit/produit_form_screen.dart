import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'package:uuid/uuid.dart';

import '../../../core/theme/app_theme.dart';
import '../../../domain/entities/entities.dart';
import '../../blocs/stock/stock_bloc.dart';
import '../../blocs/auth/auth_bloc.dart';

class ProduitFormScreen extends StatefulWidget {
  final String? produitId;
  const ProduitFormScreen({super.key, this.produitId});

  @override
  State<ProduitFormScreen> createState() => _ProduitFormScreenState();
}

class _ProduitFormScreenState extends State<ProduitFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nomCtrl = TextEditingController();
  final _prixVenteCtrl = TextEditingController();
  final _prixAchatCtrl = TextEditingController();
  final _quantiteCtrl = TextEditingController(text: '0');
  final _seuilCtrl = TextEditingController(text: '5');
  CategorieProduit _categorie = CategorieProduit.alimentaire;

  bool get isEdit => widget.produitId != null;

  @override
  void dispose() {
    _nomCtrl.dispose();
    _prixVenteCtrl.dispose();
    _prixAchatCtrl.dispose();
    _quantiteCtrl.dispose();
    _seuilCtrl.dispose();
    super.dispose();
  }

  void _submit() {
    if (!_formKey.currentState!.validate()) return;

    final authState = context.read<AuthBloc>().state;
    final produit = Produit(
      id: isEdit ? widget.produitId! : const Uuid().v4(),
      boutiqueId: authState.boutiqueId ?? '',
      nom: _nomCtrl.text.trim(),
      categorie: _categorie,
      prixVente: int.parse(_prixVenteCtrl.text.replaceAll(' ', '')),
      prixAchat: int.tryParse(_prixAchatCtrl.text.replaceAll(' ', '')) ?? 0,
      quantite: int.parse(_quantiteCtrl.text),
      seuilAlerte: int.parse(_seuilCtrl.text),
      synced: false,
      updatedAt: DateTime.now(),
    );

    if (isEdit) {
      context.read<StockBloc>().add(StockProduitModifier(produit));
    } else {
      context.read<StockBloc>().add(StockProduitAjouter(produit));
    }

    context.pop();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.gray50,
      appBar: AppBar(
        title: Text(isEdit ? 'Modifier le produit' : 'Nouveau produit'),
        leading: IconButton(
          onPressed: () => context.pop(),
          icon: const Icon(Icons.close),
        ),
        actions: [
          if (isEdit)
            IconButton(
              onPressed: () {
                context.read<StockBloc>().add(
                      StockProduitSupprimer(widget.produitId!),
                    );
                context.pop();
              },
              icon: const Icon(Icons.delete_outline),
              color: AppColors.red,
            ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Nom
              _FormLabel('Nom du produit'),
              TextFormField(
                controller: _nomCtrl,
                textCapitalization: TextCapitalization.sentences,
                decoration: const InputDecoration(hintText: 'Ex: Riz 25kg'),
                validator: (v) => v == null || v.trim().isEmpty
                    ? 'Le nom est obligatoire'
                    : null,
              ),
              const SizedBox(height: 16),

              // Catégorie
              _FormLabel('Catégorie'),
              _CategorieSelector(
                selected: _categorie,
                onChanged: (c) => setState(() => _categorie = c),
              ),
              const SizedBox(height: 16),

              // Prix vente + achat
              Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        _FormLabel('Prix de vente (GNF)'),
                        TextFormField(
                          controller: _prixVenteCtrl,
                          keyboardType: TextInputType.number,
                          inputFormatters: [FilteringTextInputFormatter.digitsOnly],
                          decoration: const InputDecoration(hintText: '0'),
                          validator: (v) {
                            if (v == null || v.isEmpty) return 'Requis';
                            if (int.tryParse(v) == null) return 'Invalide';
                            return null;
                          },
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        _FormLabel('Prix d\'achat (GNF)'),
                        TextFormField(
                          controller: _prixAchatCtrl,
                          keyboardType: TextInputType.number,
                          inputFormatters: [FilteringTextInputFormatter.digitsOnly],
                          decoration: const InputDecoration(hintText: '0'),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),

              // Quantité + seuil
              Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        _FormLabel('Quantité initiale'),
                        TextFormField(
                          controller: _quantiteCtrl,
                          keyboardType: TextInputType.number,
                          inputFormatters: [FilteringTextInputFormatter.digitsOnly],
                          decoration: const InputDecoration(hintText: '0'),
                          validator: (v) =>
                              v == null || int.tryParse(v) == null ? 'Requis' : null,
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        _FormLabel('Seuil d\'alerte'),
                        TextFormField(
                          controller: _seuilCtrl,
                          keyboardType: TextInputType.number,
                          inputFormatters: [FilteringTextInputFormatter.digitsOnly],
                          decoration: const InputDecoration(hintText: '5'),
                          validator: (v) =>
                              v == null || int.tryParse(v) == null ? 'Requis' : null,
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                'Vous serez alerté quand le stock passe sous ce seuil',
                style: Theme.of(context).textTheme.bodySmall,
              ),
              const SizedBox(height: 32),

              ElevatedButton(
                onPressed: _submit,
                child: Text(isEdit ? 'Enregistrer les modifications' : 'Ajouter le produit'),
              ),
              const SizedBox(height: 32),
            ],
          ),
        ),
      ),
    );
  }
}

class _FormLabel extends StatelessWidget {
  final String text;
  const _FormLabel(this.text);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Text(
        text,
        style: const TextStyle(
          fontSize: 13,
          fontWeight: FontWeight.w500,
          color: AppColors.gray800,
        ),
      ),
    );
  }
}

class _CategorieSelector extends StatelessWidget {
  final CategorieProduit selected;
  final ValueChanged<CategorieProduit> onChanged;

  const _CategorieSelector({required this.selected, required this.onChanged});

  static const labels = {
    CategorieProduit.alimentaire: 'Alimentaire',
    CategorieProduit.boisson: 'Boissons',
    CategorieProduit.hygiene: 'Hygiène',
    CategorieProduit.general: 'Général',
    CategorieProduit.autre: 'Autre',
  };

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: 8,
      children: CategorieProduit.values.map((cat) {
        final isSelected = cat == selected;
        return GestureDetector(
          onTap: () => onChanged(cat),
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 150),
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: isSelected ? AppColors.green : Colors.white,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(
                color: isSelected ? AppColors.green : AppColors.gray200.withOpacity(0.5),
                width: 0.5,
              ),
            ),
            child: Text(
              labels[cat] ?? cat.name,
              style: TextStyle(
                fontSize: 12,
                color: isSelected ? Colors.white : AppColors.gray600,
                fontWeight: isSelected ? FontWeight.w500 : FontWeight.w400,
              ),
            ),
          ),
        );
      }).toList(),
    );
  }
}