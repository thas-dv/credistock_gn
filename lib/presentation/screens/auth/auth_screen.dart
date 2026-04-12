import 'package:credistock_gn/core/router/app_router.dart';
import 'package:credistock_gn/core/theme/app_theme.dart';
import 'package:credistock_gn/presentation/blocs/auth/auth_bloc.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';

class AuthScreen extends StatefulWidget {
  const AuthScreen({super.key});

  @override
  State<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends State<AuthScreen> {
  final _identifiantCtrl = TextEditingController();
  final _motDePasseCtrl = TextEditingController();


  @override
  void dispose() {
    _identifiantCtrl.dispose();
    _motDePasseCtrl.dispose();
    super.dispose();
  }

  void _submit() {
    final identifiant = _identifiantCtrl.text.trim();
    final motDePasse = _motDePasseCtrl.text.trim();

    if (identifiant.isEmpty || motDePasse.isEmpty) return;

   

    context.read<AuthBloc>().add(
          AuthLoginSubmitted(
            identifiant: identifiant,
            motDePasse: motDePasse,
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
        body: SafeArea(
          child: Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(20),
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 420),
                child: Card(
                  child: Padding(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Container(
                          width: 64,
                          height: 64,
                          decoration: BoxDecoration(
                            color: AppColors.green,
                            borderRadius: BorderRadius.circular(18),
                          ),
                          child: const Icon(Icons.storefront,
                              color: Colors.white, size: 30),
                        ),
                        const SizedBox(height: 12),
                        const Text('CrédiStock GN',
                            style: TextStyle(
                                fontSize: 22, fontWeight: FontWeight.w600)),
                        const SizedBox(height: 18),
                        Align(
                          alignment: Alignment.centerRight,
                          child: TextButton(
                            onPressed: () => context.push(AppRoutes.register),
                            child: const Text('Créer un compte'),
                          ),),
                        const SizedBox(height: 8),
                        TextField(
                          controller: _identifiantCtrl,
                          decoration:
                              const InputDecoration(labelText: 'Identifiant'),
                        ),
                        const SizedBox(height: 12),
                        TextField(
                          controller: _motDePasseCtrl,
                          obscureText: true,
                          decoration:
                              const InputDecoration(labelText: 'Mot de passe'),
                        ),
                        const SizedBox(height: 16),
                        BlocBuilder<AuthBloc, AuthState>(
                          builder: (_, state) {
                            if (state.status == AuthStatus.error) {
                              return Padding(
                                padding: const EdgeInsets.only(bottom: 10),
                                child: Text(
                                  state.errorMessage ?? 'Erreur de connexion',
                                  style: const TextStyle(
                                      color: AppColors.red, fontSize: 12),
                                ),
                              );
                            }
                            return const SizedBox.shrink();
                          },
                        ),
                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton(
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
                                return const Text('Se connecter');
                              },
                            ),
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
    );
  }
}

