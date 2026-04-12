import 'package:credistock_gn/core/router/app_router.dart';
import 'package:credistock_gn/core/theme/app_theme.dart';
import 'package:credistock_gn/presentation/blocs/auth/auth_bloc.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _boutiqueIdCtrl = TextEditingController();
  final _nomCtrl = TextEditingController();
  final _motDePasseCtrl = TextEditingController();
  final _confirmationCtrl = TextEditingController();

  String _role = 'employe';

  @override
  void dispose() {
    _boutiqueIdCtrl.dispose();
    _nomCtrl.dispose();
    _motDePasseCtrl.dispose();
    _confirmationCtrl.dispose();
    super.dispose();
  }

  void _submit() {
    final form = _formKey.currentState;
    if (form == null || !form.validate()) return;

    context.read<AuthBloc>().add(
          AuthRegisterSubmitted(
            identifiant: _nomCtrl.text.trim(),
            motDePasse: _motDePasseCtrl.text.trim(),
            boutiqueId: _boutiqueIdCtrl.text.trim(),
            nom: _nomCtrl.text.trim(),
            role: _role,
          ),
        );
  }

  @override
  Widget build(BuildContext context) {
    return BlocListener<AuthBloc, AuthState>(
      listener: (context, state) {
        if (state.status == AuthStatus.authenticated) {
          context.go(AppRoutes.home);
        }
      },
      child: Scaffold(
        backgroundColor: AppColors.gray50,
        appBar: AppBar(
          backgroundColor: AppColors.gray50,
          title: const Text('Créer un compte'),
        ),
        body: SafeArea(
          child: Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(20),
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 420),
                child: Card(
                  child: Padding(
                    padding: const EdgeInsets.all(20),
                    child: Form(
                      key: _formKey,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          const Text(
                            'Structure utilisateur',
                            style: TextStyle(
                                fontSize: 14, fontWeight: FontWeight.w600),
                          ),
                          const SizedBox(height: 12),
                          TextFormField(
                            controller: _boutiqueIdCtrl,
                            decoration:
                                const InputDecoration(labelText: 'boutique_id'),
                            validator: (value) {
                              if (value == null || value.trim().isEmpty) {
                                return 'boutique_id est requis';
                              }
                              return null;
                            },
                          ),
                          const SizedBox(height: 12),
                          TextFormField(
                            controller: _nomCtrl,
                            decoration: const InputDecoration(labelText: 'nom'),
                            validator: (value) {
                              if (value == null || value.trim().isEmpty) {
                                return 'nom est requis';
                              }
                              return null;
                            },
                          ),
                          const SizedBox(height: 12),
                          DropdownButtonFormField<String>(
                            value: _role,
                            decoration:
                                const InputDecoration(labelText: 'role'),
                            items: const [
                              DropdownMenuItem(
                                  value: 'admin', child: Text('admin')),
                              DropdownMenuItem(
                                  value: 'employe', child: Text('employe')),
                            ],
                            onChanged: (value) {
                              if (value != null) {
                                setState(() => _role = value);
                              }
                            },
                          ),
                          const SizedBox(height: 12),
                          TextFormField(
                            controller: _motDePasseCtrl,
                            obscureText: true,
                            decoration: const InputDecoration(
                                labelText: 'mot_de_passe'),
                            validator: (value) {
                              if (value == null || value.trim().isEmpty) {
                                return 'mot_de_passe est requis';
                              }
                              if (value.trim().length < 6) {
                                return 'Minimum 6 caractères';
                              }
                              return null;
                            },
                          ),
                          const SizedBox(height: 12),
                          TextFormField(
                            controller: _confirmationCtrl,
                            obscureText: true,
                            decoration: const InputDecoration(
                                labelText: 'confirmation mot_de_passe'),
                            validator: (value) {
                              if (value?.trim() !=
                                  _motDePasseCtrl.text.trim()) {
                                return 'Les mots de passe ne correspondent pas';
                              }
                              return null;
                            },
                          ),
                          const SizedBox(height: 18),
                          BlocBuilder<AuthBloc, AuthState>(
                            builder: (_, state) {
                              if (state.status != AuthStatus.error) {
                                return const SizedBox.shrink();
                              }

                              return Padding(
                                padding: const EdgeInsets.only(bottom: 12),
                                child: Text(
                                  state.errorMessage ??
                                      'Erreur de création de compte',
                                  style: const TextStyle(
                                      color: AppColors.red, fontSize: 12),
                                ),
                              );
                            },
                          ),
                          ElevatedButton(
                            onPressed: _submit,
                            child: BlocBuilder<AuthBloc, AuthState>(
                              builder: (_, state) {
                                if (state.status == AuthStatus.checking) {
                                  return const SizedBox(
                                    width: 18,
                                    height: 18,
                                    child: CircularProgressIndicator(
                                        strokeWidth: 2),
                                  );
                                }
                                return const Text('Créer le compte');
                              },
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
