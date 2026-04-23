// lib/presentation/auth/login_page.dart
import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:crypto/crypto.dart';
import '../providers/app_providers.dart';
import '../../data/local/database/app_database.dart';
import '../../core/theme/app_theme.dart';
import 'register_page.dart';

class LoginPage extends ConsumerStatefulWidget {
  const LoginPage({super.key});
  @override
  ConsumerState<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends ConsumerState<LoginPage> {
  final _phoneCtrl = TextEditingController();
  String _pin      = '';
  bool   _loading  = false;
  String? _error;

  // Hash du PIN
  String _hashPin(String pin) =>
      sha256.convert(utf8.encode(pin)).toString();

  Future<void> _login() async {
    if (_phoneCtrl.text.trim().isEmpty) {
      setState(() => _error = 'Entrez votre numéro de téléphone');
      return;
    }
    if (_pin.length != 4) {
      setState(() => _error = 'Le PIN doit contenir 4 chiffres');
      return;
    }

    setState(() { _loading = true; _error = null; });

    try {
      final db       = ref.read(appDatabaseProvider);
      final phone    = _phoneCtrl.text.trim();
      final pinHash  = _hashPin(_pin);

      // 1. Vérifier localement d'abord (offline-first)
      final boutique = await (db.select(db.creditStockBoutiques)
        ..where((b) => b.telephone.equals(phone))
        ..limit(1)
      ).getSingleOrNull();

      if (boutique != null) {
        final utilisateur = await (db.select(db.creditStockUtilisateurs)
          ..where((u) => u.boutiqueId.equals(boutique.id) & u.pinHash.equals(pinHash) & u.actif.isValue(true))
          ..limit(1)
        ).getSingleOrNull();

        if (utilisateur != null) {
          // Connexion locale réussie
          await ref.read(sessionProvider.notifier).saveSession(
            boutiqueId:     boutique.id,
            utilisateurId:  utilisateur.id,
            utilisateurNom: utilisateur.nom,
            role:            utilisateur.role,
            abonnement:      boutique.abonnement,
          );

          // Tenter sync en arrière-plan si connecté
          final isOnline = ref.read(isOnlineProvider);
          if (isOnline) unawaited(ref.read(syncProvider.notifier).syncAll());

          if (mounted) Navigator.pushReplacementNamed(context, '/home');
          return;
        }
      }

      // 2. Essayer via Supabase si en ligne
      final isOnline = ref.read(isOnlineProvider);
      if (!isOnline) {
        setState(() => _error = 'Téléphone ou PIN incorrect');
        return;
      }

      // Rechercher la boutique sur Supabase par téléphone
      final supabase = Supabase.instance.client;
      final boutiqueData = await supabase
          .from('credistock_boutiques')
          .select('id, nom, abonnement, premium_expire_at')
          .eq('telephone', phone)
          .maybeSingle();

      if (boutiqueData == null) {
        setState(() => _error = 'Aucun compte trouvé pour ce numéro');
        return;
      }

      // Vérifier utilisateur avec PIN hashé
      final userData = await supabase
          .from('credistock_utilisateurs')
          .select('id, nom, role, actif')
          .eq('boutique_id', boutiqueData['id'])
          .eq('pin_hash', pinHash)
          .eq('actif', true)
          .maybeSingle();

      if (userData == null) {
        setState(() => _error = 'PIN incorrect');
        return;
      }

      // Sauvegarder localement pour usage offline futur
      await db.into(db.creditStockBoutiques).insertOnConflictUpdate(
        CreditStockBoutiquesCompanion.insert(
          id:         boutiqueData['id'],
          nom:        boutiqueData['nom'],
          telephone:  phone,
          abonnement: Value(boutiqueData['abonnement'] ?? 'gratuit'),
        ),
      );

      await db.into(db.creditStockUtilisateurs).insertOnConflictUpdate(
        CreditStockUtilisateursCompanion.insert(
          id:         userData['id'],
          boutiqueId: boutiqueData['id'],
          nom:        userData['nom'],
          role:       Value(userData['role'] ?? 'employe'),
          pinHash:    Value(pinHash),
        ),
      );

      await ref.read(sessionProvider.notifier).saveSession(
        boutiqueId:     boutiqueData['id'],
        utilisateurId:  userData['id'],
        utilisateurNom: userData['nom'],
        role:            userData['role'],
        abonnement:      boutiqueData['abonnement'] ?? 'gratuit',
      );

      // Déclencher sync complète
      unawaited(ref.read(syncProvider.notifier).syncAll());

      if (mounted) Navigator.pushReplacementNamed(context, '/home');

    } catch (e) {
      setState(() => _error = 'Erreur de connexion. Réessayez.');
      debugPrint('Login error: $e');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  void _onPinDigit(String digit) {
    if (_pin.length >= 4) return;
    setState(() { _pin += digit; _error = null; });
    if (_pin.length == 4) _login();
  }

  void _onPinDelete() {
    if (_pin.isEmpty) return;
    setState(() => _pin = _pin.substring(0, _pin.length - 1));
  }

  @override
  void dispose() {
    _phoneCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).extension<CreditStockColors>()!;
    final t      = Theme.of(context);

    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              const SizedBox(height: 32),

              // Logo
              Container(
                width: 72, height: 72,
                decoration: BoxDecoration(
                  color:        colors.green,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: const Icon(Icons.storefront, color: Colors.white, size: 38),
              ).animate().scale(duration: 400.ms),

              const SizedBox(height: 16),

              Text('CrédiStock GN',
                style: t.textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold),
              ).animate().fadeIn(delay: 200.ms),

              Text('Gérez votre boutique simplement',
                style: t.textTheme.bodyMedium?.copyWith(color: colors.textSecondary),
              ).animate().fadeIn(delay: 300.ms),

              const SizedBox(height: 40),

              // Champ téléphone
              TextField(
                controller: _phoneCtrl,
                keyboardType: TextInputType.phone,
                inputFormatters: [FilteringTextInputFormatter.allow(RegExp(r'[0-9+\s]'))],
                decoration: InputDecoration(
                  labelText: 'Numéro de téléphone',
                  prefixIcon: const Icon(Icons.phone_outlined),
                  prefixText: '+224 ',
                ),
                onChanged: (_) => setState(() => _pin = ''),
              ).animate().slideY(begin: 0.1, duration: 300.ms, delay: 100.ms),

              const SizedBox(height: 28),

              // PIN dots
              Text('Code PIN', style: t.textTheme.labelLarge),
              const SizedBox(height: 12),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: List.generate(4, (i) => AnimatedContainer(
                  duration: const Duration(milliseconds: 200),
                  margin: const EdgeInsets.symmetric(horizontal: 8),
                  width: 16, height: 16,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: i < _pin.length ? colors.green : colors.textSecondary.withOpacity(0.3),
                  ),
                )),
              ),

              if (_error != null) ...[
                const SizedBox(height: 12),
                Text(_error!, style: TextStyle(color: colors.red, fontSize: 13)),
              ],

              const SizedBox(height: 28),

              // Pavé numérique
              _PinPad(
                onDigit:  _onPinDigit,
                onDelete: _onPinDelete,
                loading:  _loading,
              ).animate().fadeIn(delay: 400.ms),

              const SizedBox(height: 32),

              // Lien inscription
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text("Pas de compte ? ", style: TextStyle(color: colors.textSecondary)),
                  GestureDetector(
                    onTap: () => Navigator.push(
                      context,
                      MaterialPageRoute(builder: (_) => const RegisterPage()),
                    ),
                    child: Text('Créer un compte',
                      style: TextStyle(color: colors.green, fontWeight: FontWeight.bold),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ── Pavé numérique ───────────────────────────────────────────

class _PinPad extends StatelessWidget {
  final void Function(String) onDigit;
  final VoidCallback onDelete;
  final bool loading;

  const _PinPad({
    required this.onDigit,
    required this.onDelete,
    required this.loading,
  });

  @override
  Widget build(BuildContext context) {
    if (loading) {
      return const SizedBox(
        height: 200,
        child: Center(child: CircularProgressIndicator()),
      );
    }

    const keys = [
      ['1','2','3'],
      ['4','5','6'],
      ['7','8','9'],
      ['','0','⌫'],
    ];

    return Column(
      children: keys.map((row) => Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: row.map((k) => _PinKey(
          label:   k,
          onTap:   k.isEmpty ? null : () => k == '⌫' ? onDelete() : onDigit(k),
        )).toList(),
      )).toList(),
    );
  }
}

class _PinKey extends StatelessWidget {
  final String label;
  final VoidCallback? onTap;
  const _PinKey({required this.label, this.onTap});

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).extension<CreditStockColors>()!;

    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 100),
        margin:   const EdgeInsets.all(8),
        width: 70, height: 70,
        decoration: BoxDecoration(
          color:        onTap != null ? colors.cardBg : Colors.transparent,
          borderRadius: BorderRadius.circular(16),
          boxShadow: onTap != null ? [
            BoxShadow(color: Colors.black.withOpacity(0.06), blurRadius: 8, offset: const Offset(0, 2)),
          ] : null,
        ),
        child: Center(
          child: Text(
            label,
            style: TextStyle(
              fontSize:   label == '⌫' ? 22 : 24,
              fontWeight: FontWeight.w500,
              color:      onTap != null ? Theme.of(context).textTheme.bodyLarge?.color : Colors.transparent,
            ),
          ),
        ),
      ),
    );
  }
}