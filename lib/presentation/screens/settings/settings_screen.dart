import 'package:credistock_gn/core/di/injection.dart';
import 'package:credistock_gn/core/services/app_settings_service.dart';
import 'package:credistock_gn/core/theme/app_theme.dart';
import 'package:credistock_gn/data/local/database/app_database.dart';
import 'package:credistock_gn/presentation/blocs/auth/auth_bloc.dart';
import 'package:credistock_gn/widgets/app_badge.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
export '../screens.dart' show SettingsScreen;

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final db = getIt<AppDatabase>();
    final settings = getIt<AppSettingsService>();
    final boutiqueId = context.read<AuthBloc>().state.boutiqueId;

    if (boutiqueId == null || boutiqueId.isEmpty) {
      return const Scaffold(
          body: Center(child: Text('Aucune boutique active')));
    }

    return FutureBuilder<_SettingsData>(
      future: _loadData(db, boutiqueId),
      builder: (context, snapshot) {
        final data = snapshot.data;
        if (data == null) {
          return const Scaffold(
              body: Center(child: CircularProgressIndicator()));
        }

        return ValueListenableBuilder<AppSettings>(
          valueListenable: settings.settings,
          builder: (context, cfg, _) {
            return Scaffold(
              backgroundColor: AppColors.gray50,
              appBar: AppBar(title: const Text('Paramètres')),
              body: ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        children: [
                          Container(
                            width: 56,
                            height: 56,
                            decoration: BoxDecoration(
                              color: AppColors.green,
                              borderRadius: BorderRadius.circular(16),
                            ),
                            child: const Icon(Icons.storefront,
                                color: Colors.white, size: 28),
                          ),
                          const SizedBox(height: 10),
                          Text(data.boutique.nom,
                              style: const TextStyle(
                                  fontSize: 16, fontWeight: FontWeight.w500)),
                          Text(
                              '${data.boutique.adresse ?? ""} · ${data.currentUserRole}',
                              style: const TextStyle(
                                  fontSize: 12, color: AppColors.gray400)),
                          const SizedBox(height: 10),
                          const AppBadge(label: 'Premium actif', type: 'bon'),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text('Compte', style: Theme.of(context).textTheme.labelLarge),
                  const SizedBox(height: 8),
                  Card(
                    child: Column(
                      children: [
                        _Item(
                            icon: Icons.store_outlined,
                            label: 'Nom de la boutique',
                            value: data.boutique.nom),
                        const Divider(height: 1),
                        _Item(
                            icon: Icons.phone_outlined,
                            label: 'Téléphone',
                            value: data.boutique.telephone),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text('Utilisateurs',
                      style: Theme.of(context).textTheme.labelLarge),
                  const SizedBox(height: 8),
                  Card(
                    child: Column(
                      children: data.users
                          .map((u) => Column(
                                children: [
                                  ListTile(
                                    leading: CircleAvatar(
                                      backgroundColor: AppColors.greenLight,
                                      child: Text(
                                        u.nom
                                            .split(' ')
                                            .map(
                                                (p) => p.isNotEmpty ? p[0] : '')
                                            .take(2)
                                            .join()
                                            .toUpperCase(),
                                        style: const TextStyle(
                                            color: AppColors.green),
                                      ),
                                    ),
                                    title: Text(u.nom),
                                    trailing: AppBadge(
                                        label: u.role == 'admin'
                                            ? 'Admin'
                                            : 'Employé',
                                        type: u.role == 'admin'
                                            ? 'info'
                                            : 'moyen'),
                                  ),
                                  if (u != data.users.last)
                                    const Divider(height: 1),
                                ],
                              ))
                          .toList(),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text('Application',
                      style: Theme.of(context).textTheme.labelLarge),
                  const SizedBox(height: 8),
                  Card(
                    child: Column(
                      children: [
                        SwitchListTile(
                          title: const Text('Synchronisation auto'),
                          subtitle: const Text('Dès connexion internet'),
                          value: cfg.autoSync,
                          onChanged: settings.setAutoSync,
                        ),
                        const Divider(height: 1),
                        SwitchListTile(
                          title: const Text('Sauvegarde cloud'),
                          subtitle: const Text(
                              'Sauvegarder pour restaurer si téléphone perdu'),
                          value: cfg.cloudBackup,
                          onChanged: settings.setCloudBackup,
                        ),
                        const Divider(height: 1),
                        SwitchListTile(
                          title: const Text('Mode sombre'),
                          value: cfg.themeMode == ThemeMode.dark,
                          onChanged: (v) => settings.setThemeMode(
                              v ? ThemeMode.dark : ThemeMode.light),
                        ),
                        const Divider(height: 1),
                        ListTile(
                          title: const Text('Langue'),
                          subtitle: Text(cfg.locale.languageCode == 'ar'
                              ? 'العربية'
                              : cfg.locale.languageCode == 'en'
                                  ? 'English'
                                  : 'Français'),
                          trailing: DropdownButton<String>(
                            value: cfg.locale.languageCode,
                            onChanged: (v) {
                              if (v != null) settings.setLocale(v);
                            },
                            items: const [
                              DropdownMenuItem(value: 'fr', child: Text('FR')),
                              DropdownMenuItem(value: 'en', child: Text('EN')),
                              DropdownMenuItem(value: 'ar', child: Text('AR')),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),
                  Card(
                    child: ListTile(
                      onTap: () {
                        context.read<AuthBloc>().add(AuthLogout());
                      },
                      leading: const Icon(Icons.logout, color: AppColors.red),
                      title: const Text('Se déconnecter',
                          style: TextStyle(color: AppColors.red)),
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

  Future<_SettingsData> _loadData(AppDatabase db, String boutiqueId) async {
    final boutique = await (db.select(db.boutiques)
          ..where((b) => b.id.equals(boutiqueId)))
        .getSingle();
    final users = await (db.select(db.utilisateurs)
          ..where((u) => u.boutiqueId.equals(boutiqueId)))
        .get();
    return _SettingsData(
      boutique: boutique,
      users: users,
      currentUserRole: users
          .firstWhere((u) => u.role == 'admin', orElse: () => users.first)
          .role,
    );
  }
}

class _SettingsData {
  final Boutique boutique;
  final List<Utilisateur> users;
  final String currentUserRole;

  _SettingsData(
      {required this.boutique,
      required this.users,
      required this.currentUserRole});
}

class _Item extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _Item({required this.icon, required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Icon(icon, size: 18, color: AppColors.gray400),
      title: Text(label),
      subtitle: Text(value),
    );
  }
}
