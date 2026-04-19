import 'package:credistock_gn/widgets/app_badge.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_theme.dart';

import '../../../core/router/app_router.dart';

import '../../../domain/entities/entities.dart';
import '../../blocs/client/client_bloc.dart';
import '../../blocs/dette/dette_bloc.dart';
import '../../blocs/auth/auth_bloc.dart';

// ============================================================
// CLIENTS SCREEN
// ============================================================

class ClientsScreen extends StatelessWidget {
  const ClientsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocProvider.value(
      value: context.read<ClientBloc>()
        ..add(ClientWatchStarted(
            context.read<AuthBloc>().state.boutiqueId ?? '')),
      child: const _ClientsView(),
    );
  }
}

class _ClientsView extends StatelessWidget {
  const _ClientsView();

  @override
  Widget build(BuildContext context) {
    return BlocListener<ClientBloc, ClientState>(
      listenWhen: (previous, current) =>
          previous.status != current.status &&
          current.status == ClientStatus.error,
      listener: (context, state) {
        final msg =
            state.errorMessage ?? 'Erreur lors de l\'enregistrement du client';
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(msg)),
        );
      },
      child: Scaffold(
        backgroundColor: AppColors.gray50,
        body: SafeArea(
          child: Column(
            children: [
              _ClientsHeader(),
              _SearchField(),
              _ScoreFilter(),
              Expanded(child: _ClientsList()),
            ],
          ),
        ),
      ),
    );
  }
}

class _ClientsHeader extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.white,
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 12),
      child: Row(
        children: [
          Expanded(
            child: BlocBuilder<ClientBloc, ClientState>(
              buildWhen: (p, c) => p.totalClients != c.totalClients,
              builder: (_, state) => Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Clients',
                      style: Theme.of(context).textTheme.headlineSmall),
                  Text(
                    '${state.totalClients} enregistrés · ${state.clientsAvecDettes} avec dettes',
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                ],
              ),
            ),
          ),
          IconButton(
            onPressed: () => _showAjouterClientDialog(context),
            icon: const Icon(Icons.person_add_outlined),
            color: AppColors.green,
          ),
        ],
      ),
    );
  }

  void _showAjouterClientDialog(BuildContext context) {
    final nomCtrl = TextEditingController();
    final telCtrl = TextEditingController();
    final boutiqueId = context.read<AuthBloc>().state.boutiqueId ?? '';

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (_) => Padding(
        padding: EdgeInsets.only(
          bottom: MediaQuery.of(context).viewInsets.bottom + 16,
          left: 16,
          right: 16,
          top: 20,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(
              child: Container(
                width: 36,
                height: 4,
                decoration: BoxDecoration(
                  color: AppColors.gray200,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            const SizedBox(height: 16),
            Text('Nouveau client',
                style: Theme.of(context).textTheme.headlineSmall),
            const SizedBox(height: 16),
            TextField(
              controller: nomCtrl,
              textCapitalization: TextCapitalization.words,
              decoration: const InputDecoration(
                hintText: 'Nom complet',
                prefixIcon: Icon(Icons.person_outline, size: 18),
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: telCtrl,
              keyboardType: TextInputType.phone,
              decoration: const InputDecoration(
                hintText: '+224 6XX XX XX XX',
                prefixIcon: Icon(Icons.phone_outlined, size: 18),
              ),
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {
                if (nomCtrl.text.trim().isNotEmpty) {
                  context.read<ClientBloc>().add(ClientAjoute(
                        nom: nomCtrl.text.trim(),
                        telephone: telCtrl.text.trim().isEmpty
                            ? null
                            : telCtrl.text.trim(),
                        boutiqueId: boutiqueId,
                      ));
                  Navigator.pop(context);
                }
              },
              child: const Text('Ajouter le client'),
            ),
          ],
        ),
      ),
    );
  }
}

class _SearchField extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.white,
      padding: const EdgeInsets.fromLTRB(16, 0, 16, 10),
      child: TextField(
        onChanged: (v) =>
            context.read<ClientBloc>().add(ClientSearchChanged(v)),
        decoration: const InputDecoration(
          hintText: 'Rechercher un client...',
          prefixIcon: Icon(Icons.search, size: 18),
        ),
      ),
    );
  }
}

class _ScoreFilter extends StatelessWidget {
  static const filtres = [
    (null, 'Tous'),
    (ScoreClient.bon, 'Bon payeur'),
    (ScoreClient.moyen, 'Moyen'),
    (ScoreClient.mauvais, 'Mauvais'),
  ];

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<ClientBloc, ClientState>(
      buildWhen: (p, c) => p.filtreScore != c.filtreScore,
      builder: (_, state) {
        return Container(
          color: Colors.white,
          height: 44,
          child: ListView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.fromLTRB(16, 6, 16, 6),
            children: filtres.map((f) {
              final (score, label) = f;
              final selected = state.filtreScore == score;
              return Padding(
                padding: const EdgeInsets.only(right: 8),
                child: GestureDetector(
                  onTap: () => context
                      .read<ClientBloc>()
                      .add(ClientScoreFiltered(score)),
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

class _ClientsList extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return BlocBuilder<ClientBloc, ClientState>(
      buildWhen: (p, c) =>
          p.clientsFiltres != c.clientsFiltres || p.status != c.status,
      builder: (_, state) {
        if (state.status == ClientStatus.loading) {
          return const Center(child: CircularProgressIndicator());
        }
        if (state.clientsFiltres.isEmpty) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.people_outline, size: 48, color: AppColors.gray200),
                const SizedBox(height: 12),
                Text('Aucun client',
                    style: Theme.of(context).textTheme.bodyMedium),
              ],
            ),
          );
        }

        return ListView.separated(
          padding: const EdgeInsets.all(16),
          itemCount: state.clientsFiltres.length,
          separatorBuilder: (_, __) => const SizedBox(height: 1),
          itemBuilder: (_, i) {
            final client = state.clientsFiltres[i];
            return _ClientTile(
                client: client,
                isFirst: i == 0,
                isLast: i == state.clientsFiltres.length - 1);
          },
        );
      },
    );
  }
}

class _ClientTile extends StatelessWidget {
  final Client client;
  final bool isFirst;
  final bool isLast;

  const _ClientTile(
      {required this.client, required this.isFirst, required this.isLast});

  @override
  Widget build(BuildContext context) {
    final scoreColor = client.score.name.scoreCouleur;
    final scoreColorLight = client.score.name.scoreCouleurLight;

    return GestureDetector(
      onTap: () =>
          context.push('${AppRoutes.clientDetail}?clientId=${client.id}'),
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(
            top: isFirst ? const Radius.circular(14) : Radius.zero,
            bottom: isLast ? const Radius.circular(14) : Radius.zero,
          ),
          border: Border(
            left: BorderSide(color: Colors.black.withOpacity(0.06), width: 0.5),
            right:
                BorderSide(color: Colors.black.withOpacity(0.06), width: 0.5),
            top: isFirst
                ? BorderSide(color: Colors.black.withOpacity(0.06), width: 0.5)
                : BorderSide.none,
            bottom:
                BorderSide(color: Colors.black.withOpacity(0.06), width: 0.5),
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
          child: Row(
            children: [
              CircleAvatar(
                radius: 18,
                backgroundColor: scoreColorLight,
                child: Text(
                  client.nom.substring(0, 2).toUpperCase(),
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                    color: scoreColor,
                  ),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      client.nom,
                      style: const TextStyle(
                          fontSize: 14, fontWeight: FontWeight.w500),
                    ),
                    if (client.telephone != null)
                      Text(
                        client.telephone!,
                        style: const TextStyle(
                            fontSize: 11, color: AppColors.gray400),
                      ),
                  ],
                ),
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  AppBadge(label: client.score.name, type: client.score.name),
                  const SizedBox(height: 4),
                  Text(
                    client.aDesDetteEnCours
                        ? '${_formatGNF(client.totalDu)} GNF dû'
                        : 'Aucune dette',
                    style: TextStyle(
                      fontSize: 11,
                      color: client.aDesDetteEnCours
                          ? AppColors.red
                          : AppColors.gray400,
                    ),
                  ),
                ],
              ),
              const SizedBox(width: 4),
              const Icon(Icons.chevron_right,
                  size: 16, color: AppColors.gray200),
            ],
          ),
        ),
      ),
    );
  }
}

// ============================================================
// CLIENT DETAIL SCREEN
// ============================================================

class ClientDetailScreen extends StatelessWidget {
  final String clientId;
  const ClientDetailScreen({super.key, required this.clientId});

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<ClientBloc, ClientState>(
      builder: (context, state) {
        final client = state.clients.where((c) => c.id == clientId).firstOrNull;
        if (client == null) {
          return Scaffold(
            appBar: AppBar(),
            body: const Center(child: CircularProgressIndicator()),
          );
        }

        final scoreColor = client.score.name.scoreCouleur;
        final scoreColorLight = client.score.name.scoreCouleurLight;

        return Scaffold(
          backgroundColor: AppColors.gray50,
          appBar: AppBar(
            title: Text(client.nom),
            actions: [
              IconButton(
                onPressed: () {/* WhatsApp */},
                icon: const Icon(Icons.message_outlined),
                color: AppColors.green,
              ),
            ],
          ),
          body: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              // Fiche client
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    children: [
                      CircleAvatar(
                        radius: 32,
                        backgroundColor: scoreColorLight,
                        child: Text(
                          client.nom.substring(0, 2).toUpperCase(),
                          style: TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.w600,
                            color: scoreColor,
                          ),
                        ),
                      ),
                      const SizedBox(height: 10),
                      Text(client.nom,
                          style: Theme.of(context).textTheme.headlineSmall),
                      if (client.telephone != null) ...[
                        const SizedBox(height: 4),
                        Text(client.telephone!,
                            style: Theme.of(context).textTheme.bodyMedium),
                      ],
                      const SizedBox(height: 12),
                      AppBadge(
                          label: client.score.name, type: client.score.name),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 12),

              // Stats
              Row(
                children: [
                  Expanded(
                    child: _StatCard(
                      label: 'Total dû',
                      value: '${_formatGNF(client.totalDu)} GNF',
                      color:
                          client.totalDu > 0 ? AppColors.red : AppColors.green,
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: _StatCard(
                      label: 'Dettes',
                      value: '${client.nombreDettes}',
                      color: AppColors.amber,
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: _StatCard(
                      label: 'Remboursés',
                      value: '${client.nombresRemboursements}',
                      color: AppColors.green,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 20),

              // Historique dettes
              Text('Historique des dettes',
                  style: Theme.of(context).textTheme.labelLarge),
              const SizedBox(height: 8),
              BlocBuilder<DetteBloc, DetteState>(
                builder: (_, detteState) {
                  final dettesClient = detteState.dettes
                      .where((d) => d.clientId == clientId)
                      .toList();

                  if (dettesClient.isEmpty) {
                    return Card(
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Center(
                          child: Text(
                            'Aucune dette enregistrée',
                            style: Theme.of(context).textTheme.bodyMedium,
                          ),
                        ),
                      ),
                    );
                  }

                  return Card(
                    child: Column(
                      children: dettesClient.asMap().entries.map((entry) {
                        final i = entry.key;
                        final d = entry.value;
                        final couleur = switch (d.statut) {
                          StatutDette.nonPaye => AppColors.red,
                          StatutDette.partiel => AppColors.amber,
                          StatutDette.paye => AppColors.green,
                        };
                        return Column(
                          children: [
                            if (i > 0) const Divider(height: 1, thickness: 0.5),
                            Padding(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 14, vertical: 10),
                              child: Row(
                                children: [
                                  Container(
                                    width: 6,
                                    height: 6,
                                    decoration: BoxDecoration(
                                      color: couleur,
                                      shape: BoxShape.circle,
                                    ),
                                  ),
                                  const SizedBox(width: 10),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment:
                                          CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          '${_formatGNF(d.montant)} GNF',
                                          style: const TextStyle(
                                              fontSize: 13,
                                              fontWeight: FontWeight.w500),
                                        ),
                                        Text(
                                          '${d.createdAt.day}/${d.createdAt.month}/${d.createdAt.year}',
                                          style: const TextStyle(
                                              fontSize: 11,
                                              color: AppColors.gray400),
                                        ),
                                      ],
                                    ),
                                  ),
                                  AppBadge(
                                    label: d.statut.name,
                                    type: d.statut == StatutDette.nonPaye
                                        ? 'non_paye'
                                        : d.statut == StatutDette.partiel
                                            ? 'partiel'
                                            : 'paye',
                                  ),
                                ],
                              ),
                            ),
                          ],
                        );
                      }).toList(),
                    ),
                  );
                },
              ),
              const SizedBox(height: 80),
            ],
          ),
        );
      },
    );
  }
}

class _StatCard extends StatelessWidget {
  final String label;
  final String value;
  final Color color;

  const _StatCard(
      {required this.label, required this.value, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.08),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          Text(
            value,
            style: TextStyle(
                fontSize: 16, fontWeight: FontWeight.w600, color: color),
          ),
          const SizedBox(height: 2),
          Text(label,
              style: const TextStyle(fontSize: 10, color: AppColors.gray400)),
        ],
      ),
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

extension on ScoreClient {
  String get label => switch (this) {
        ScoreClient.bon => 'Bon payeur',
        ScoreClient.moyen => 'Payeur moyen',
        ScoreClient.mauvais => 'Mauvais payeur',
      };
}

extension on StatutDette {
  String get label => switch (this) {
        StatutDette.nonPaye => 'Non payé',
        StatutDette.partiel => 'Partiel',
        StatutDette.paye => 'Payé',
      };
}
