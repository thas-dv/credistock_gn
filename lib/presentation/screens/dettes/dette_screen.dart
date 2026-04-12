import 'package:credistock_gn/widgets/app_badge.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/app_theme.dart';
import '../../../core/router/app_router.dart';
import '../../../domain/entities/entities.dart';
import '../../blocs/dette/dette_bloc.dart';
import '../../blocs/auth/auth_bloc.dart';

// ============================================================
// DETTES SCREEN
// ============================================================

class DettesScreen extends StatelessWidget {
  const DettesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocProvider.value(
      value: context.read<DetteBloc>()
        ..add(
            DetteWatchStarted(context.read<AuthBloc>().state.boutiqueId ?? '')),
      child: const _DettesView(),
    );
  }
}

class _DettesView extends StatelessWidget {
  const _DettesView();

  @override
  Widget build(BuildContext context) {
    return BlocListener<DetteBloc, DetteState>(
      listenWhen: (p, c) =>
          p.successMessage != c.successMessage ||
          p.errorMessage != c.errorMessage,
      listener: (context, state) {
        if (state.successMessage != null) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(state.successMessage!),
              backgroundColor: AppColors.green,
              behavior: SnackBarBehavior.floating,
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(10)),
            ),
          );
        }
        if (state.errorMessage != null) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(state.errorMessage!),
              backgroundColor: AppColors.red,
              behavior: SnackBarBehavior.floating,
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(10)),
            ),
          );
        }
      },
      child: Scaffold(
        backgroundColor: AppColors.gray50,
        body: SafeArea(
          child: Column(
            children: [
              _DettesHeader(),
              _StatutFilter(),
              Expanded(child: _DettesList()),
            ],
          ),
        ),
      ),
    );
  }
}

// ── Header ──────────────────────────────────────────────────

class _DettesHeader extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.white,
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 12),
      child: Row(
        children: [
          Expanded(
            child: BlocBuilder<DetteBloc, DetteState>(
              buildWhen: (p, c) =>
                  p.totalDu != c.totalDu ||
                  p.nombreDettesActives != c.nombreDettesActives,
              builder: (_, state) => Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Dettes',
                      style: Theme.of(context).textTheme.headlineSmall),
                  Text(
                    '${_formatGNF(state.totalDu)} GNF à récupérer · ${state.nombreDettesActives} actives',
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                ],
              ),
            ),
          ),
          IconButton(
            onPressed: () {/* Export PDF */},
            icon: const Icon(Icons.download_outlined),
            color: AppColors.gray600,
          ),
        ],
      ),
    );
  }
}

// ── Statut filter ───────────────────────────────────────────

class _StatutFilter extends StatelessWidget {
  static const filtres = [
    (null, 'Toutes'),
    (StatutDette.nonPaye, 'Non payé'),
    (StatutDette.partiel, 'Partiel'),
    (StatutDette.paye, 'Payé'),
  ];

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<DetteBloc, DetteState>(
      buildWhen: (p, c) => p.filtreStatut != c.filtreStatut,
      builder: (_, state) {
        return Container(
          color: Colors.white,
          height: 44,
          child: ListView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.fromLTRB(16, 6, 16, 6),
            children: filtres.map((f) {
              final (statut, label) = f;
              final selected = state.filtreStatut == statut;
              return Padding(
                padding: const EdgeInsets.only(right: 8),
                child: GestureDetector(
                  onTap: () => context
                      .read<DetteBloc>()
                      .add(DetteStatutFiltered(statut)),
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 200),
                    padding:
                        const EdgeInsets.symmetric(horizontal: 14, vertical: 4),
                    decoration: BoxDecoration(
                      color: selected ? AppColors.greenLight : AppColors.gray50,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(
                        color: selected
                            ? AppColors.green
                            : AppColors.gray200.withOpacity(0.5),
                        width: selected ? 1 : 0.5,
                      ),
                    ),
                    child: Text(
                      label,
                      style: TextStyle(
                        fontSize: 12,
                        color:
                            selected ? AppColors.greenDark : AppColors.gray600,
                        fontWeight:
                            selected ? FontWeight.w500 : FontWeight.w400,
                      ),
                    ),
                  ),
                ),
              );
            }).toList(),
          ),
        );
      },
    );
  }
}

// ── Liste dettes ─────────────────────────────────────────────

class _DettesList extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return BlocBuilder<DetteBloc, DetteState>(
      buildWhen: (p, c) =>
          p.dettesFiltrees != c.dettesFiltrees || p.status != c.status,
      builder: (_, state) {
        if (state.status == DetteStatus.loading) {
          return const Center(child: CircularProgressIndicator());
        }
        if (state.dettesFiltrees.isEmpty) {
          return _EmptyDettes();
        }

        return ListView.separated(
          padding: const EdgeInsets.all(16),
          itemCount: state.dettesFiltrees.length,
          separatorBuilder: (_, __) => const SizedBox(height: 10),
          itemBuilder: (_, i) => _DetteCard(dette: state.dettesFiltrees[i]),
        );
      },
    );
  }
}

class _DetteCard extends StatelessWidget {
  final Dette dette;
  const _DetteCard({required this.dette});

  @override
  Widget build(BuildContext context) {
    final couleur = switch (dette.statut) {
      StatutDette.nonPaye => AppColors.red,
      StatutDette.partiel => AppColors.amber,
      StatutDette.paye => AppColors.green,
    };

    final badgeType = switch (dette.statut) {
      StatutDette.nonPaye => 'non_paye',
      StatutDette.partiel => 'partiel',
      StatutDette.paye => 'paye',
    };

    final badgeLabel = switch (dette.statut) {
      StatutDette.nonPaye => 'Non payé',
      StatutDette.partiel => 'Partiel',
      StatutDette.paye => 'Payé ✓',
    };

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // En-tête
            Row(
              children: [
                CircleAvatar(
                  radius: 18,
                  backgroundColor: couleur.withOpacity(0.1),
                  child: Text(
                    dette.nomClient.isNotEmpty
                        ? dette.nomClient.substring(0, 2).toUpperCase()
                        : '??',
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w600,
                      color: couleur,
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        dette.nomClient,
                        style: const TextStyle(
                            fontSize: 14, fontWeight: FontWeight.w500),
                      ),
                      Text(
                        _dateLabel(),
                        style: const TextStyle(
                            fontSize: 11, color: AppColors.gray400),
                      ),
                    ],
                  ),
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    AppBadge(label: badgeLabel, type: badgeType),
                    const SizedBox(height: 4),
                    Text(
                      '${_formatGNF(dette.statut == StatutDette.partiel ? dette.montantRestant : dette.montant)} GNF',
                      style: TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                        color: couleur,
                      ),
                    ),
                  ],
                ),
              ],
            ),

            // Barre de progression si partiel
            if (dette.statut == StatutDette.partiel) ...[
              const SizedBox(height: 10),
              DetteProgressBar(
                montant: dette.montant,
                montantPaye: dette.montantPaye,
                color: AppColors.amber,
              ),
              const SizedBox(height: 4),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Payé: ${_formatGNF(dette.montantPaye)} / ${_formatGNF(dette.montant)} GNF',
                    style:
                        const TextStyle(fontSize: 10, color: AppColors.gray400),
                  ),
                  Text(
                    '${dette.tauxRemboursement.round()}%',
                    style: const TextStyle(
                      fontSize: 10,
                      color: AppColors.amber,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
            ],

            // Badge retard
            if (dette.estEchue) ...[
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: AppColors.redLight,
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Text(
                  'En retard de ${dette.joursDeRetard} jour(s)',
                  style: const TextStyle(fontSize: 11, color: AppColors.red),
                ),
              ),
            ],

            // Actions
            if (dette.statut != StatutDette.paye) ...[
              const SizedBox(height: 10),
              Row(
                children: [
                  // WhatsApp
                  OutlinedButton.icon(
                    onPressed: () {
                      // TODO: passer le vrai objet Client
                    },
                    icon: const Icon(Icons.message_outlined, size: 14),
                    label: const Text('WA', style: TextStyle(fontSize: 12)),
                    style: OutlinedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 10, vertical: 6),
                      minimumSize: Size.zero,
                      tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                    ),
                  ),
                  const SizedBox(width: 8),
                  // Payer
                  Expanded(
                    child: ElevatedButton(
                      onPressed: () => context
                          .push('${AppRoutes.paiement}?detteId=${dette.id}'),
                      style: ElevatedButton.styleFrom(
                        minimumSize: const Size(0, 36),
                        padding: const EdgeInsets.symmetric(horizontal: 12),
                      ),
                      child: Text(
                        dette.statut == StatutDette.partiel
                            ? 'Payer le reste'
                            : 'Enregistrer paiement',
                        style: const TextStyle(fontSize: 12),
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }

  String _dateLabel() {
    if (dette.dateEcheance != null) {
      final diff = dette.dateEcheance!.difference(DateTime.now()).inDays;
      if (diff < 0) return 'Echéance dépassée';
      if (diff == 0) return 'Echéance aujourd\'hui';
      return 'Echéance dans $diff jour(s)';
    }
    return 'Créé le ${dette.createdAt.day}/${dette.createdAt.month}';
  }
}

class _EmptyDettes extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.account_balance_wallet_outlined,
              size: 48, color: AppColors.gray200),
          const SizedBox(height: 12),
          Text(
            'Aucune dette trouvée',
            style: Theme.of(context).textTheme.bodyMedium,
          ),
          const SizedBox(height: 4),
          Text(
            'Les dettes crédit apparaîtront ici',
            style: Theme.of(context).textTheme.bodySmall,
          ),
        ],
      ),
    );
  }
}

// ============================================================
// PAIEMENT SCREEN
// ============================================================

class PaiementScreen extends StatefulWidget {
  final String detteId;
  const PaiementScreen({super.key, required this.detteId});

  @override
  State<PaiementScreen> createState() => _PaiementScreenState();
}

class _PaiementScreenState extends State<PaiementScreen> {
  final _montantCtrl = TextEditingController();
  String _modePaiement = 'especes';

  static const modesPaiement = [
    ('especes', 'Espèces', Icons.payments_outlined),
    ('orange_money', 'Orange Money', Icons.phone_android),
    ('mtn_momo', 'MTN MoMo', Icons.phone_android),
  ];

  @override
  void dispose() {
    _montantCtrl.dispose();
    super.dispose();
  }

  void _submit(Dette dette) {
    final montant = int.tryParse(_montantCtrl.text.replaceAll(' ', ''));

    if (montant == null || montant <= 0) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Montant invalide')),
      );
      return;
    }

    if (montant > dette.montantRestant) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Montant supérieur au reste à payer')),
      );
      return;
    }

    context.read<DetteBloc>().add(
          DettePaiementEnregistre(
            detteId: dette.id,
            clientId: dette.clientId,
            montant: montant,
            modePaiement: _modePaiement,
          ),
        );

    context.pop();
  }

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<DetteBloc, DetteState>(
      builder: (context, state) {
        final dette =
            state.dettes.where((d) => d.id == widget.detteId).isNotEmpty
                ? state.dettes.firstWhere((d) => d.id == widget.detteId)
                : null;
        if (dette == null)
          return const Scaffold(
              body: Center(child: CircularProgressIndicator()));

        return Scaffold(
          backgroundColor: AppColors.gray50,
          appBar: AppBar(
            title: const Text('Enregistrer un paiement'),
            leading: IconButton(
                onPressed: () => context.pop(), icon: const Icon(Icons.close)),
          ),
          body: SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Recap dette
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(14),
                    child: Column(
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text('Client',
                                style: Theme.of(context).textTheme.bodyMedium),
                            Text(dette.nomClient,
                                style: const TextStyle(
                                    fontWeight: FontWeight.w500)),
                          ],
                        ),
                        const SizedBox(height: 6),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text('Montant total',
                                style: Theme.of(context).textTheme.bodyMedium),
                            Text('${_formatGNF(dette.montant)} GNF'),
                          ],
                        ),
                        const SizedBox(height: 6),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text('Déjà payé',
                                style: Theme.of(context).textTheme.bodyMedium),
                            Text('${_formatGNF(dette.montantPaye)} GNF',
                                style: const TextStyle(color: AppColors.green)),
                          ],
                        ),
                        const Divider(height: 16),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            const Text('Reste à payer',
                                style: TextStyle(fontWeight: FontWeight.w600)),
                            Text(
                              '${_formatGNF(dette.montantRestant)} GNF',
                              style: const TextStyle(
                                fontWeight: FontWeight.w600,
                                color: AppColors.red,
                                fontSize: 16,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        DetteProgressBar(
                          montant: dette.montant,
                          montantPaye: dette.montantPaye,
                          color: AppColors.amber,
                        ),
                      ],
                    ),
                  ),
                ),

                const SizedBox(height: 20),

                // Montant à payer
                const Text('Montant reçu (GNF)',
                    style:
                        TextStyle(fontSize: 13, fontWeight: FontWeight.w500)),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: _montantCtrl,
                        keyboardType: TextInputType.number,
                        inputFormatters: [
                          FilteringTextInputFormatter.digitsOnly
                        ],
                        style: const TextStyle(
                            fontSize: 20, fontWeight: FontWeight.w500),
                        decoration: const InputDecoration(
                          hintText: '0',
                          suffixText: 'GNF',
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    // Bouton "Tout payer"
                    OutlinedButton(
                      onPressed: () =>
                          _montantCtrl.text = '${dette.montantRestant}',
                      child: const Text('Tout', style: TextStyle(fontSize: 12)),
                    ),
                  ],
                ),

                const SizedBox(height: 20),

                // Mode paiement
                const Text('Mode de paiement',
                    style:
                        TextStyle(fontSize: 13, fontWeight: FontWeight.w500)),
                const SizedBox(height: 8),
                ...modesPaiement.map((m) {
                  final (value, label, icon) = m;
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: GestureDetector(
                      onTap: () => setState(() => _modePaiement = value),
                      child: AnimatedContainer(
                        duration: const Duration(milliseconds: 150),
                        padding: const EdgeInsets.symmetric(
                            horizontal: 14, vertical: 12),
                        decoration: BoxDecoration(
                          color: _modePaiement == value
                              ? AppColors.greenLight
                              : Colors.white,
                          borderRadius: BorderRadius.circular(10),
                          border: Border.all(
                            color: _modePaiement == value
                                ? AppColors.green
                                : AppColors.gray200.withOpacity(0.5),
                            width: _modePaiement == value ? 1.5 : 0.5,
                          ),
                        ),
                        child: Row(
                          children: [
                            Icon(icon,
                                size: 18,
                                color: _modePaiement == value
                                    ? AppColors.green
                                    : AppColors.gray400),
                            const SizedBox(width: 10),
                            Text(
                              label,
                              style: TextStyle(
                                fontSize: 13,
                                fontWeight: _modePaiement == value
                                    ? FontWeight.w500
                                    : FontWeight.w400,
                                color: _modePaiement == value
                                    ? AppColors.greenDark
                                    : AppColors.gray600,
                              ),
                            ),
                            const Spacer(),
                            if (_modePaiement == value)
                              const Icon(Icons.check_circle,
                                  size: 16, color: AppColors.green),
                          ],
                        ),
                      ),
                    ),
                  );
                }),

                const SizedBox(height: 24),
                ElevatedButton(
                  onPressed: () => _submit(dette),
                  child: const Text('Confirmer le paiement'),
                ),
                const SizedBox(height: 32),
              ],
            ),
          ),
        );
      },
    );
  }
}

String _formatGNF(int montant) {
  final str = montant.toString();
  final buffer = StringBuffer();
  for (int i = 0; i < str.length; i++) {
    if (i > 0 && (str.length - i) % 3 == 0) buffer.write(' ');
    buffer.write(str[i]);
  }
  return buffer.toString();
}
