import 'package:credistock_gn/core/router/app_router.dart';
import 'package:credistock_gn/core/theme/app_theme.dart';
import 'package:credistock_gn/presentation/blocs/auth/auth_bloc.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();

  final _nomCtrl = TextEditingController();
  final _prenomCtrl = TextEditingController();
  final _telephoneCtrl = TextEditingController();
  final _motDePasseCtrl = TextEditingController();
  final _confirmationCtrl = TextEditingController();

  String _role = 'employe';
  final _boutiqueNomCtrl = TextEditingController();
  final _boutiqueAdresseCtrl = TextEditingController();
  final _utilisateurIdCtrl = TextEditingController();
  @override
  void dispose() {
    _nomCtrl.dispose();
    _prenomCtrl.dispose();
    _telephoneCtrl.dispose();
    _motDePasseCtrl.dispose();
    _confirmationCtrl.dispose();
    _boutiqueNomCtrl.dispose();
    _boutiqueAdresseCtrl.dispose();
    _utilisateurIdCtrl.dispose();
    super.dispose();
  }

  void _submit() {
    final form = _formKey.currentState;
    if (form == null || !form.validate()) return;

    context.read<AuthBloc>().add(
          AuthRegisterSubmitted(
            nom: _nomCtrl.text.trim(),
            role: _role,
            prenom: _prenomCtrl.text.trim(),
            telephone: _telephoneCtrl.text.trim(),
            motDePasse: _motDePasseCtrl.text.trim(),
            boutiqueNom: _boutiqueNomCtrl.text.trim(),
            boutiqueAdresse: _boutiqueAdresseCtrl.text.trim(),
            utilisateurId: _utilisateurIdCtrl.text.trim(),
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
                            'Utilisateur',
                            style: TextStyle(
                                fontSize: 14, fontWeight: FontWeight.w600),
                          ),
                          const SizedBox(height: 10),
                          _simpleField(
                            controller: _nomCtrl,
                            label: 'Nom',
                            validatorMsg: 'Le nom est requis',
                          ),
                          const SizedBox(height: 10),
                          _simpleField(
                            controller: _prenomCtrl,
                            label: 'Prénom',
                            validatorMsg: 'Le prénom est requis',
                          ),
                          const SizedBox(height: 10),
                          _simpleField(
                            controller: _telephoneCtrl,
                            label: 'Téléphone',
                            keyboardType: TextInputType.phone,
                            validatorMsg: 'Le téléphone est requis',
                          ),
                          const SizedBox(height: 10),
                          TextFormField(
                            controller: _motDePasseCtrl,
                            obscureText: true,
                            keyboardType: TextInputType.number,
                            inputFormatters: [
                              FilteringTextInputFormatter.digitsOnly
                            ],
                            decoration: const InputDecoration(
                              labelText: 'Mot de passe (4 chiffres)',
                            ),
                            validator: (value) {
                              final v = value?.trim() ?? '';
                              if (v.isEmpty)
                                return 'Le mot de passe est requis';
                              if (v.length != 4) {
                                return 'Le mot de passe doit avoir 4 chiffres';
                              }
                              return null;
                            },
                          ),
                          const SizedBox(height: 10),
                          TextFormField(
                            controller: _confirmationCtrl,
                            obscureText: true,
                            keyboardType: TextInputType.number,
                            inputFormatters: [
                              FilteringTextInputFormatter.digitsOnly
                            ],
                            decoration: const InputDecoration(
                              labelText: 'Confirme mot de passe',
                            ),
                            validator: (value) {
                              if (value?.trim() !=
                                  _motDePasseCtrl.text.trim()) {
                                return 'Les mots de passe ne correspondent pas';
                              }
                              return null;
                            },
                          ),
                          const SizedBox(height: 20),
                          const Divider(),
                          const SizedBox(height: 12),
                          const Text(
                            'Boutique',
                            style: TextStyle(
                                fontSize: 16, fontWeight: FontWeight.w700),
                          ),
                          const SizedBox(height: 10),
                          _simpleField(
                            controller: _boutiqueNomCtrl,
                            label: 'Nom de la boutique',
                            validatorMsg: 'Le nom de la boutique est requis',
                          ),
                          const SizedBox(height: 10),
                          _simpleField(
                            controller: _boutiqueAdresseCtrl,
                            label: 'Adresse',
                            validatorMsg: 'L\'adresse est requise',
                          ),
                          const SizedBox(height: 10),
                          _simpleField(
                            controller: _utilisateurIdCtrl,
                            label: 'utilisateur_id',
                            validatorMsg: 'utilisateur_id est requis',
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

Widget _simpleField({
  required TextEditingController controller,
  required String label,
  required String validatorMsg,
  TextInputType? keyboardType,
}) {
  return TextFormField(
    controller: controller,
    keyboardType: keyboardType,
    decoration: InputDecoration(labelText: label),
    validator: (value) {
      if (value == null || value.trim().isEmpty) {
        return validatorMsg;
      }
      return null;
    },
  );
}
