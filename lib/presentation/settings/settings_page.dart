import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../providers/app_providers.dart';

class SettingsPage extends ConsumerWidget {
  const SettingsPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final themeMode = ref.watch(themeProvider);
    final locale = ref.watch(localeProvider);
    final autoSyncEnabled = ref.watch(autoSyncEnabledProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('Paramètres')),
      body: ListView(
        children: [
          ListTile(
            title: const Text('Thème'),
            subtitle: Text(themeMode.name),
            trailing: DropdownButton<ThemeMode>(
              value: themeMode,
              items: const [
                DropdownMenuItem(
                    value: ThemeMode.system, child: Text('Système')),
                DropdownMenuItem(value: ThemeMode.light, child: Text('Clair')),
                DropdownMenuItem(value: ThemeMode.dark, child: Text('Sombre')),
              ],
              onChanged: (value) {
                if (value != null)
                  ref.read(themeProvider.notifier).setTheme(value);
              },
            ),
          ),
          ListTile(
            title: const Text('Langue'),
            subtitle: Text(locale.languageCode.toUpperCase()),
            trailing: DropdownButton<String>(
              value: locale.languageCode,
              items: const [
                DropdownMenuItem(value: 'fr', child: Text('FR')),
                DropdownMenuItem(value: 'en', child: Text('EN')),
                DropdownMenuItem(value: 'ar', child: Text('AR')),
              ],
              onChanged: (value) {
                if (value != null)
                  ref.read(localeProvider.notifier).setLocale(value);
              },
            ),
          ),
          SwitchListTile(
            title: const Text('Synchronisation automatique'),
            subtitle: const Text(
              'Synchroniser dès que la connexion revient',
            ),
            value: autoSyncEnabled,
            onChanged: (value) {
              ref.read(autoSyncEnabledProvider.notifier).setEnabled(value);
            },
          ),
          ListTile(
            title: const Text('Déconnexion'),
            leading: const Icon(Icons.logout),
            onTap: () async {
              await ref.read(sessionProvider.notifier).clearSession();
              if (context.mounted) {
                Navigator.pushNamedAndRemoveUntil(
                    context, '/login', (_) => false);
              }
            },
          ),
        ],
      ),
    );
  }
}
