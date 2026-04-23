// lib/presentation/auth/register_page.dart
import 'package:drift/drift.dart' hide Column;
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:crypto/crypto.dart';
import 'dart:convert';
import 'package:uuid/uuid.dart';
import '../providers/app_providers.dart';
import '../../data/local/database/app_database.dart';
import '../../core/theme/app_theme.dart';

class RegisterPage extends ConsumerStatefulWidget {
  const RegisterPage({super.key});
  @override
  ConsumerState<RegisterPage> createState() => _RegisterPageState();
}

class _RegisterPageState extends ConsumerState<RegisterPage> {
  final _formKey    = GlobalKey<FormState>();
  final _nomBoutiqueCtrl     = TextEditingController();
  final _telephoneCtrl       = TextEditingController();
  final _nomProprietaireCtrl = TextEditingController();

  String _typeBoutique = 'general';
  String _pin          = '';
  String _pinConfirm   = '';
  int    _step         = 1; // 1 = infos, 2 = PIN
  bool   _loading      = false;
  String? _error;

  final _types = [
    ('general',      '🏪 Commerce général'),
    ('orange_money', '🟠 Orange Money'),
    ('pharmacie',    '💊 Pharmacie'),
    ('alimentaire',  '🛒 Alimentaire'),
    ('autre',        '📦 Autre'),
  ];

  String _hashPin(String pin) =>
      sha256.convert(utf8.encode(pin)).toString();

 String _normalizePhoneForLogin(String value) {
    final digits = value.replaceAll(RegExp(r'\D'), '');
    if (digits.startsWith('224')) return digits;
    return '224$digits';
  }

  String _friendlySupabaseError(Object error) {
    if (error is AuthException) {
      final message = error.message.toLowerCase();
      if (message.contains('already registered') ||
          message.contains('already been registered')) {
        return 'Ce numéro est déjà utilisé sur un autre compte.';
      }
      if (message.contains('invalid') && message.contains('email')) {
        return 'Impossible de créer le compte en ligne pour le moment.';
      }
      return 'Erreur d’authentification Supabase: ${error.message}';
    }
    if (error is PostgrestException) {
      return 'Erreur de synchronisation des données: ${error.message}';
    }
    return 'Erreur Supabase inattendue: $error';
  }

  void _showErrorToUser(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Theme.of(context).extension<CreditStockColors>()?.red,
      ),
    );
  }

  Future<void> _creerCompte() async {
    if (_pin.length != 4) {
      setState(() => _error = 'Le PIN doit contenir 4 chiffres');
      return;
    }
    if (_pin != _pinConfirm) {
      setState(() => _error = 'Les PINs ne correspondent pas');
      return;
    }

    setState(() { _loading = true; _error = null; });

    try {
      final uuid     = const Uuid();
      final db       = ref.read(appDatabaseProvider);
      final isOnline = ref.read(isOnlineProvider);
      final pinHash  = _hashPin(_pin);

      final boutiqueId    = uuid.v4();
      final utilisateurId = uuid.v4();
      final now           = DateTime.now();

      // 1. Sauvegarder localement (toujours, même offline)
      await db.into(db.creditStockBoutiques).insert(
        CreditStockBoutiquesCompanion.insert(
          id:            boutiqueId,
          nom:           _nomBoutiqueCtrl.text.trim(),
          telephone:     _telephoneCtrl.text.trim(),
          typeBoutique:  Value(_typeBoutique),
          pinHash:       Value(pinHash),
          abonnement:    Value('gratuit'),
          createdAt:     Value(now),
          updatedAt:     Value(now),
        ),
      );

      await db.into(db.creditStockUtilisateurs).insert(
        CreditStockUtilisateursCompanion.insert(
          id:         utilisateurId,
          boutiqueId: boutiqueId,
          nom:        _nomProprietaireCtrl.text.trim(),
          telephone:  Value(_telephoneCtrl.text.trim()),
          role:       Value('admin'),
          pinHash:    Value(pinHash),
          createdAt:  Value(now),
          updatedAt:  Value(now),
        ),
      );

      // 2. Si en ligne → synchroniser vers Supabase immédiatement
      if (isOnline) {
        final supabase = Supabase.instance.client;

        // Identifiant technique (email/mdp) dérivé du téléphone + PIN.
        // L'utilisateur ne le voit jamais : il se connecte avec téléphone + PIN.
        final fakeEmail = '${_normalizePhoneForLogin(_telephoneCtrl.text.trim())}@credistock.local';
        final fakePassword = _pin + boutiqueId.substring(0, 8);
        String? authId;
        try {
          
              final authResponse = await supabase.auth.signUp(
            email: fakeEmail,
            password: fakePassword,
          );

          await supabase.from('credistock_boutiques').upsert({
            'id':           boutiqueId,
            'nom':          _nomBoutiqueCtrl.text.trim(),
            'telephone':    _telephoneCtrl.text.trim(),
            'type_boutique': _typeBoutique,
            'pin_hash':     pinHash,
            'abonnement':   'gratuit',
          });

          final authUser = supabase.auth.currentUser;
          await supabase.from('credistock_utilisateurs').upsert({
            'id':          utilisateurId,
            'auth_id':     authUser?.id,
            'boutique_id': boutiqueId,
            'nom':         _nomProprietaireCtrl.text.trim(),
            'telephone':   _telephoneCtrl.text.trim(),
            'role':        'admin',
            'pin_hash':    pinHash,
            'actif':       true,
          });

        } on AuthException catch (e) {
          // signUp a échoué côté Supabase Auth.
          final msg = e.message.toLowerCase();
          final alreadyExists = msg.contains('already registered') ||
              msg.contains('already exists') ||
              msg.contains('user already');

          await _rollbackLocal(db, boutiqueId, utilisateurId);

          if (!mounted) return;
          setState(() => _error = alreadyExists
              ? 'Ce numéro est déjà utilisé. Connectez-vous avec votre PIN existant.'
              : 'Erreur d\'authentification : ${e.message}');
          return;

        } on PostgrestException catch (e) {
          // Contrainte d'unicité (téléphone) ou RLS refusée côté base.
          final isUnique = e.code == '23505';

          await _rollbackLocal(db, boutiqueId, utilisateurId);

          if (!mounted) return;
          setState(() => _error = isUnique
              ? 'Ce numéro est déjà utilisé. Connectez-vous avec votre PIN existant.'
              : 'Erreur serveur : ${e.message}');
          return;

        } catch (e) {
          // Erreur réseau / timeout : on garde le compte local,
          // la sync se fera via la queue à la prochaine connexion.
          debugPrint('Sync Supabase échouée (non bloquant): $e');
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Compte créé localement. Synchronisation à la prochaine connexion.'),
                duration: Duration(seconds: 3),
              ),
            );
          }
        }
      }

      // 3. Ouvrir la session
      await ref.read(sessionProvider.notifier).saveSession(
        boutiqueId:     boutiqueId,
        utilisateurId:  utilisateurId,
        utilisateurNom: _nomProprietaireCtrl.text.trim(),
        role:            'admin',
        abonnement:      'gratuit',
      );

      if (mounted) {
        Navigator.pushReplacementNamed(context, '/home');
      }

    } catch (e) {
        final friendlyMessage = 'Erreur lors de la création du compte: $e';
      setState(() => _error = friendlyMessage);
      _showErrorToUser(friendlyMessage);
      debugPrint('Register error: $e');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  // Rollback des insertions locales quand le serveur refuse le compte
  // (numéro déjà utilisé, etc.) — évite de laisser un compte orphelin
  // qui ne pourrait jamais se synchroniser.
  Future<void> _rollbackLocal(
    AppDatabase db,
    String boutiqueId,
    String utilisateurId,
  ) async {
    await (db.delete(db.creditStockUtilisateurs)
      ..where((u) => u.id.equals(utilisateurId))
    ).go();
    await (db.delete(db.creditStockBoutiques)
      ..where((b) => b.id.equals(boutiqueId))
    ).go();
  }

  @override
  void dispose() {
    _nomBoutiqueCtrl.dispose();
    _telephoneCtrl.dispose();
    _nomProprietaireCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).extension<CreditStockColors>()!;
    final t      = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Créer mon compte'),
        backgroundColor: colors.green,
        foregroundColor: Colors.white,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: _step == 1 ? _buildStep1(colors, t) : _buildStep2(colors, t),
        ),
      ),
    );
  }

  // ── Étape 1 : Informations boutique ──────────────────────

  Widget _buildStep1(CreditStockColors colors, ThemeData t) {
    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Indicateur étape
          _StepBar(current: 1, total: 2, color: colors.green),
          const SizedBox(height: 28),

          Text('Votre boutique', style: t.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600)),
          const SizedBox(height: 16),

          TextFormField(
            controller: _nomBoutiqueCtrl,
            textCapitalization: TextCapitalization.words,
            decoration: const InputDecoration(
              labelText: 'Nom de la boutique',
              prefixIcon: Icon(Icons.storefront_outlined),
            ),
            validator: (v) => (v == null || v.trim().isEmpty) ? 'Champ obligatoire' : null,
          ).animate().slideY(begin: 0.05, duration: 250.ms),

          const SizedBox(height: 14),

          TextFormField(
            controller: _telephoneCtrl,
            keyboardType: TextInputType.phone,
            inputFormatters: [FilteringTextInputFormatter.allow(RegExp(r'[0-9+\s]'))],
            decoration: const InputDecoration(
              labelText: 'Téléphone',
              prefixIcon: Icon(Icons.phone_outlined),
              prefixText: '+224 ',
              helperText: 'Ce numéro sera votre identifiant de connexion',
            ),
            validator: (v) {
              if (v == null || v.trim().isEmpty) return 'Champ obligatoire';
              if (v.replaceAll(RegExp(r'\D'), '').length < 9) return 'Numéro invalide';
              return null;
            },
          ).animate().slideY(begin: 0.05, duration: 250.ms, delay: 50.ms),

          const SizedBox(height: 14),

          TextFormField(
            controller: _nomProprietaireCtrl,
            textCapitalization: TextCapitalization.words,
            decoration: const InputDecoration(
              labelText: 'Votre nom',
              prefixIcon: Icon(Icons.person_outline),
            ),
            validator: (v) => (v == null || v.trim().isEmpty) ? 'Champ obligatoire' : null,
          ).animate().slideY(begin: 0.05, duration: 250.ms, delay: 100.ms),

          const SizedBox(height: 20),

          Text('Type de boutique',
            style: t.textTheme.labelLarge?.copyWith(color: colors.textSecondary),
          ),
          const SizedBox(height: 10),

          Wrap(
            spacing: 8, runSpacing: 8,
            children: _types.map((type) => ChoiceChip(
              label: Text(type.$2, style: const TextStyle(fontSize: 13)),
              selected: _typeBoutique == type.$1,
              selectedColor: colors.greenLight,
              onSelected: (_) => setState(() => _typeBoutique = type.$1),
            )).toList(),
          ).animate().fadeIn(delay: 150.ms),

          const SizedBox(height: 32),

          ElevatedButton(
            onPressed: () {
              if (_formKey.currentState!.validate()) {
                setState(() => _step = 2);
              }
            },
            child: const Text('Continuer →'),
          ),
        ],
      ),
    );
  }

  // ── Étape 2 : Créer le PIN ────────────────────────────────

  Widget _buildStep2(CreditStockColors colors, ThemeData t) {
    final isPinConfirmStep = _pin.length == 4;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        _StepBar(current: 2, total: 2, color: colors.green),
        const SizedBox(height: 32),

        Icon(Icons.lock_outline, size: 48, color: colors.green),
        const SizedBox(height: 16),

        Text(
          isPinConfirmStep ? 'Confirmez votre PIN' : 'Créez votre code PIN',
          style: t.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600),
        ),

        Text(
          isPinConfirmStep
              ? 'Saisissez à nouveau votre PIN'
              : 'Ce code vous permettra de vous connecter sans internet',
          style: t.textTheme.bodySmall?.copyWith(color: colors.textSecondary),
          textAlign: TextAlign.center,
        ),

        const SizedBox(height: 28),

        // Dots PIN
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: List.generate(4, (i) {
            final filled = isPinConfirmStep
                ? i < _pinConfirm.length
                : i < _pin.length;
            return AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              margin:   const EdgeInsets.symmetric(horizontal: 10),
              width: 18, height: 18,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: filled ? colors.green : colors.textSecondary.withOpacity(0.25),
              ),
            );
          }),
        ),

        if (_error != null) ...[
          const SizedBox(height: 12),
          Text(_error!, style: TextStyle(color: colors.red, fontSize: 13)),
        ],

        const SizedBox(height: 28),

        // Pavé numérique
        if (!_loading) ...[
          ...[ ['1','2','3'], ['4','5','6'], ['7','8','9'], ['','0','⌫'] ].map((row) =>
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: row.map((k) {
                final onTap = k.isEmpty ? null : () {
                  setState(() => _error = null);
                  if (k == '⌫') {
                    if (isPinConfirmStep) {
                      setState(() => _pinConfirm = _pinConfirm.isEmpty ? '' : _pinConfirm.substring(0, _pinConfirm.length - 1));
                    } else {
                      setState(() => _pin = _pin.isEmpty ? '' : _pin.substring(0, _pin.length - 1));
                    }
                  } else {
                    if (isPinConfirmStep) {
                      if (_pinConfirm.length < 4) {
                        setState(() => _pinConfirm += k);
                        if (_pinConfirm.length == 4) _creerCompte();
                      }
                    } else {
                      if (_pin.length < 4) setState(() => _pin += k);
                    }
                  }
                };

                return GestureDetector(
                  onTap: onTap,
                  child: Container(
                    margin:   const EdgeInsets.all(8),
                    width: 70, height: 70,
                    decoration: BoxDecoration(
                      color:        onTap != null ? colors.cardBg : Colors.transparent,
                      borderRadius: BorderRadius.circular(16),
                      boxShadow:    onTap != null ? [
                        BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 6),
                      ] : null,
                    ),
                    child: Center(
                      child: Text(k,
                        style: TextStyle(
                          fontSize: k == '⌫' ? 22 : 24,
                          fontWeight: FontWeight.w500,
                          color: onTap != null ? t.textTheme.bodyLarge?.color : Colors.transparent,
                        ),
                      ),
                    ),
                  ),
                );
              }).toList(),
            ),
          ),
        ] else
          const Padding(
            padding: EdgeInsets.symmetric(vertical: 40),
            child: CircularProgressIndicator(),
          ),

        const SizedBox(height: 16),

        TextButton.icon(
          onPressed: () => setState(() { _step = 1; _pin = ''; _pinConfirm = ''; _error = null; }),
          icon: const Icon(Icons.arrow_back_ios, size: 14),
          label: const Text('Retour'),
        ),
      ],
    );
  }
}

// ── Indicateur d'étapes ──────────────────────────────────────

class _StepBar extends StatelessWidget {
  final int   current;
  final int   total;
  final Color color;
  const _StepBar({required this.current, required this.total, required this.color});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: List.generate(total, (i) {
        final done   = i + 1 < current;
        final active = i + 1 == current;
        return Expanded(
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 300),
            height: 4,
            margin: const EdgeInsets.symmetric(horizontal: 3),
            decoration: BoxDecoration(
              color:        done || active ? color : color.withOpacity(0.2),
              borderRadius: BorderRadius.circular(2),
            ),
          ),
        );
      }),
    );
  }
}