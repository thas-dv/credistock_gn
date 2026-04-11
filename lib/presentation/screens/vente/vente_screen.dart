import 'package:credistock_gn/widgets/app_badge.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/app_theme.dart';
import '../../../domain/entities/entities.dart';
import '../../blocs/vente/vente_bloc.dart';
import '../../blocs/auth/auth_bloc.dart';

class VenteScreen extends StatelessWidget {
  const VenteScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocProvider.value(
      value: context.read<VenteBloc>(),
      child: const _VenteView(),
    );
  }
}

class _VenteView extends StatelessWidget {
  const _VenteView();

  @override
  Widget build(BuildContext context) {
    return BlocListener<VenteBloc, VenteState>(
      listenWhen: (prev, curr) => prev.status != curr.status,
      listener: (context, state) {
        if (state.status == VenteStatus.success) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: const Text('Vente enregistrée ✓'),
              backgroundColor: AppColors.green,
              behavior: SnackBarBehavior.floating,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            ),
          );
          context.pop();
        }
        if (state.status == VenteStatus.error) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(state.errorMessage ?? 'Erreur'),
              backgroundColor: AppColors.red,
              behavior: SnackBarBehavior.floating,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            ),
          );
        }
      },
      child: Scaffold(
        backgroundColor: AppColors.gray50,
        appBar: AppBar(
          title: const Text('Nouvelle vente'),
          leading: IconButton(
            onPressed: () => context.pop(),
            icon: const Icon(Icons.close),
          ),
        ),
        body: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Type paiement
              _TypePaiementSelector(),
              const SizedBox(height: 20),
              // Bloc vocal
              _VocalSection(),
              const SizedBox(height: 20),
              // Produit
              _ProduitSection(),
              const SizedBox(height: 16),
              // Quantité
              _QuantiteSection(),
              const SizedBox(height: 16),
              // Client (si crédit)
              _ClientSection(),
              const SizedBox(height: 16),
              // Récapitulatif
              _RecapSection(),
              const SizedBox(height: 20),
              // Bouton enregistrer
              _EnregistrerButton(),
              const SizedBox(height: 32),
            ],
          ),
        ),
      ),
    );
  }
}

// ── Type paiement ──────────────────────────────────────────

class _TypePaiementSelector extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return BlocBuilder<VenteBloc, VenteState>(
      buildWhen: (p, c) => p.typePaiement != c.typePaiement,
      builder: (context, state) {
        return Row(
          children: [
            _Chip(
              label: '💵  Cash',
              selected: state.typePaiement == TypePaiement.cash,
              onTap: () => context
                  .read<VenteBloc>()
                  .add(const VenteChangerTypePaiement(TypePaiement.cash)),
            ),
            const SizedBox(width: 8),
            _Chip(
              label: '📋  Crédit',
              selected: state.typePaiement == TypePaiement.credit,
              onTap: () => context
                  .read<VenteBloc>()
                  .add(const VenteChangerTypePaiement(TypePaiement.credit)),
            ),
          ],
        );
      },
    );
  }
}

class _Chip extends StatelessWidget {
  final String label;
  final bool selected;
  final VoidCallback onTap;

  const _Chip({required this.label, required this.selected, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: selected ? AppColors.green : Colors.white,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: selected ? AppColors.green : AppColors.gray200,
            width: selected ? 1.5 : 0.5,
          ),
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.w500,
            color: selected ? Colors.white : AppColors.gray600,
          ),
        ),
      ),
    );
  }
}

// ── Section vocale ─────────────────────────────────────────

class _VocalSection extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return BlocBuilder<VenteBloc, VenteState>(
      buildWhen: (p, c) => p.ecouteStatus != c.ecouteStatus || p.texteVocal != c.texteVocal,
      builder: (context, state) {
        final isListening = state.ecouteStatus == EcouteVocaleStatus.listening;
        final isProcessing = state.ecouteStatus == EcouteVocaleStatus.processing;

        return GestureDetector(
          onTap: () {
            if (isListening) {
              context.read<VenteBloc>().add(const VenteArreterEcouteVocale());
            } else {
              context.read<VenteBloc>().add(const VenteDemarrerEcouteVocale());
            }
          },
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 300),
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: isListening ? AppColors.greenLight : Colors.white,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(
                color: isListening
                    ? AppColors.green.withOpacity(0.4)
                    : AppColors.gray200.withOpacity(0.5),
                width: isListening ? 1.5 : 0.5,
              ),
            ),
            child: Column(
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      isListening ? Icons.mic : Icons.mic_none,
                      color: isListening ? AppColors.green : AppColors.gray400,
                      size: 20,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      isListening
                          ? 'En écoute...'
                          : isProcessing
                              ? 'Analyse...'
                              : 'Appuyer pour dicter',
                      style: TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w500,
                        color: isListening ? AppColors.green : AppColors.gray400,
                      ),
                    ),
                  ],
                ),
                if (isListening) ...[
                  const SizedBox(height: 10),
                  _WaveAnimation(),
                ],
                if (state.texteVocal != null && !isListening) ...[
                  const SizedBox(height: 8),
                  Text(
                    '"${state.texteVocal}"',
                    style: TextStyle(
                      fontSize: 12,
                      color: AppColors.green,
                      fontStyle: FontStyle.italic,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ],
              ],
            ),
          ),
        );
      },
    );
  }
}

class _WaveAnimation extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: List.generate(5, (i) {
        return Container(
          margin: const EdgeInsets.symmetric(horizontal: 2),
          width: 4,
          height: 4,
          decoration: BoxDecoration(
            color: AppColors.green,
            borderRadius: BorderRadius.circular(2),
          ),
        )
            .animate(onPlay: (c) => c.repeat(reverse: true))
            .scaleY(
              begin: 1,
              end: 5,
              delay: Duration(milliseconds: i * 100),
              duration: const Duration(milliseconds: 400),
            );
      }),
    );
  }
}

// ── Produit ─────────────────────────────────────────────────

class _ProduitSection extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return BlocBuilder<VenteBloc, VenteState>(
      buildWhen: (p, c) => p.produitSelectionne != c.produitSelectionne,
      builder: (context, state) {
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Produit', style: Theme.of(context).textTheme.labelLarge),
            const SizedBox(height: 8),
            if (state.produitSelectionne != null)
              _ProduitCard(produit: state.produitSelectionne!)
            else
              _ProduitSearchField(),
          ],
        );
      },
    );
  }
}

class _ProduitCard extends StatelessWidget {
  final Produit produit;
  const _ProduitCard({required this.produit});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            CircleAvatar(
              radius: 18,
              backgroundColor: AppColors.greenLight,
              child: Text(
                produit.nom.substring(0, 2).toUpperCase(),
                style: const TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w600,
                  color: AppColors.greenDark,
                ),
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(produit.nom, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w500)),
                  Text(
                    '${produit.quantite} en stock · ${_formatGNF(produit.prixVente)} GNF',
                    style: const TextStyle(fontSize: 11, color: AppColors.gray400),
                  ),
                ],
              ),
            ),
            IconButton(
              onPressed: () => context.read<VenteBloc>().add(const VenteReinitialiser()),
              icon: const Icon(Icons.close, size: 16, color: AppColors.gray400),
            ),
          ],
        ),
      ),
    );
  }
}

class _ProduitSearchField extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return TextField(
      decoration: const InputDecoration(
        hintText: 'Rechercher un produit...',
        prefixIcon: Icon(Icons.search, size: 18),
      ),
      onChanged: (value) {
        // Déclencher recherche dans StockBloc
      },
    );
  }
}

// ── Quantité ───────────────────────────────────────────────

class _QuantiteSection extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return BlocBuilder<VenteBloc, VenteState>(
      buildWhen: (p, c) => p.quantite != c.quantite,
      builder: (context, state) {
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Quantité', style: Theme.of(context).textTheme.labelLarge),
            const SizedBox(height: 8),
            Row(
              children: [
                _QuantiteBtn(
                  icon: Icons.remove,
                  onTap: () => context
                      .read<VenteBloc>()
                      .add(VenteChangerQuantite(state.quantite - 1)),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Text(
                    '${state.quantite}',
                    textAlign: TextAlign.center,
                    style: const TextStyle(fontSize: 24, fontWeight: FontWeight.w500),
                  ),
                ),
                const SizedBox(width: 16),
                _QuantiteBtn(
                  icon: Icons.add,
                  onTap: () => context
                      .read<VenteBloc>()
                      .add(VenteChangerQuantite(state.quantite + 1)),
                ),
              ],
            ),
          ],
        );
      },
    );
  }
}

class _QuantiteBtn extends StatelessWidget {
  final IconData icon;
  final VoidCallback onTap;
  const _QuantiteBtn({required this.icon, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(10),
      child: Container(
        width: 44,
        height: 44,
        decoration: BoxDecoration(
          border: Border.all(color: AppColors.gray200.withOpacity(0.5)),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Icon(icon, size: 20),
      ),
    );
  }
}

// ── Client ─────────────────────────────────────────────────

class _ClientSection extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return BlocBuilder<VenteBloc, VenteState>(
      buildWhen: (p, c) => p.typePaiement != c.typePaiement || p.clientSelectionne != c.clientSelectionne,
      builder: (context, state) {
        if (state.typePaiement != TypePaiement.credit) return const SizedBox.shrink();

        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Client', style: Theme.of(context).textTheme.labelLarge),
            const SizedBox(height: 8),
            if (state.clientSelectionne != null)
              _ClientChip(client: state.clientSelectionne!)
            else
              TextField(
                decoration: const InputDecoration(
                  hintText: 'Rechercher un client...',
                  prefixIcon: Icon(Icons.person_outline, size: 18),
                ),
              ),
          ],
        );
      },
    );
  }
}

class _ClientChip extends StatelessWidget {
  final Client client;
  const _ClientChip({required this.client});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: AppColors.blueLight,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: AppColors.blue.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          const Icon(Icons.person, size: 16, color: AppColors.blue),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              client.nom,
              style: const TextStyle(fontSize: 13, color: AppColors.blue, fontWeight: FontWeight.w500),
            ),
          ),
          AppBadge(label: client.score.name, type: client.score.name),
        ],
      ),
    );
  }
}

// ── Récap ──────────────────────────────────────────────────

class _RecapSection extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return BlocBuilder<VenteBloc, VenteState>(
      buildWhen: (p, c) =>
          p.montantTotal != c.montantTotal || p.produitSelectionne != c.produitSelectionne,
      builder: (context, state) {
        if (state.produitSelectionne == null) return const SizedBox.shrink();

        return Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: AppColors.greenLight,
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: AppColors.green.withOpacity(0.3)),
          ),
          child: Column(
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('Produit', style: TextStyle(fontSize: 13, color: AppColors.greenDark)),
                  Text(
                    '${state.produitSelectionne!.nom} × ${state.quantite}',
                    style: const TextStyle(fontSize: 13, color: AppColors.greenDark),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'Total',
                    style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600, color: AppColors.greenDark),
                  ),
                  Text(
                    '${_formatGNF(state.montantTotal)} GNF',
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w600,
                      color: AppColors.greenDark,
                    ),
                  ),
                ],
              ),
            ],
          ),
        );
      },
    );
  }
}

// ── Bouton enregistrer ─────────────────────────────────────

class _EnregistrerButton extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return BlocBuilder<VenteBloc, VenteState>(
      buildWhen: (p, c) =>
          p.peutEnregistrer != c.peutEnregistrer || p.status != c.status,
      builder: (context, state) {
        final isLoading = state.status == VenteStatus.loading;
        final authState = context.read<AuthBloc>().state;

        return ElevatedButton(
          onPressed: state.peutEnregistrer && !isLoading
              ? () => context.read<VenteBloc>().add(
                    VenteEnregistrer(
                      boutiqueId: authState.boutiqueId ?? '',
                      utilisateurId: 'current_user_id',
                    ),
                  )
              : null,
          style: ElevatedButton.styleFrom(
            backgroundColor: AppColors.green,
            disabledBackgroundColor: AppColors.gray200,
          ),
          child: isLoading
              ? const SizedBox(
                  height: 20,
                  width: 20,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    color: Colors.white,
                  ),
                )
              : const Text('Enregistrer la vente  ✓'),
        );
      },
    );
  }
}

// ── Helpers ────────────────────────────────────────────────

String _formatGNF(int montant) {
  final str = montant.toString();
  final buffer = StringBuffer();
  for (int i = 0; i < str.length; i++) {
    if (i > 0 && (str.length - i) % 3 == 0) buffer.write(' ');
    buffer.write(str[i]);
  }
  return buffer.toString();
}