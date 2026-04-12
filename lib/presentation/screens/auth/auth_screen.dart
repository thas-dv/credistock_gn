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
   static const _pinLength = 4;
  String _pin = '';

void _onTapDigit(String digit) {
    if (_pin.length >= _pinLength) return;

  setState(() => _pin += digit);

    if (_pin.length == _pinLength) {
      Future.delayed(const Duration(milliseconds: 100), () {
        context.read<AuthBloc>().add(AuthPinSubmitted(_pin));
        setState(() => _pin = '');
      });
    }
  }

    void _onDelete() {
    if (_pin.isEmpty) return;
    setState(() => _pin = _pin.substring(0, _pin.length - 1));
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
                          width: 72,
                          height: 72,
                          decoration: BoxDecoration(
                            color: AppColors.green,
                            borderRadius: BorderRadius.circular(18),
                          ),
                          child: const Icon(Icons.storefront,
                              color: Colors.white, size: 30),
                        ),
                         const SizedBox(height: 16),
                        const Text(
                          'CrédiStock GN',
                          style: TextStyle(
                              fontSize: 24, fontWeight: FontWeight.w600),
                        ),
                       const SizedBox(height: 8),
                        const Text(
                          'Entrez votre code PIN (4 chiffres)',
                          style:
                              TextStyle(fontSize: 14, color: AppColors.gray400),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 16),
                         Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: List.generate(_pinLength, (i) {
                            final filled = i < _pin.length;
                            return AnimatedContainer(
                              duration: const Duration(milliseconds: 150),
                              margin:
                                  const EdgeInsets.symmetric(horizontal: 7),
                              width: 14,
                              height: 14,
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                color:
                                    filled ? AppColors.green : Colors.transparent,
                                border: Border.all(
                                    color: AppColors.green, width: 1.5),
                              ),
                            );
                          }),
                        ),
                        BlocBuilder<AuthBloc, AuthState>(
                          builder: (_, state) {
                            if (state.status == AuthStatus.error) {
                              return Padding(
                                padding: const EdgeInsets.only(top: 12),
                                child: Text(
                                  state.errorMessage ?? 'PIN incorrect',
                                  style: const TextStyle(
                                      fontSize: 12, color: AppColors.red),
                                ),
                              );
                            }
                            return const SizedBox(height: 28);
                          },
                        ),
                         SizedBox(
                          width: 240,
                          child: GridView.count(
                            crossAxisCount: 3,
                            shrinkWrap: true,
                            mainAxisSpacing: 10,
                            crossAxisSpacing: 10,
                            childAspectRatio: 1.4,
                            children: [
                              ...['1', '2', '3', '4', '5', '6', '7', '8', '9']
                                  .map((d) => _PinBtn(
                                      label: d,
                                      onTap: () => _onTapDigit(d))),
                              const SizedBox(),
                              _PinBtn(label: '0', onTap: () => _onTapDigit('0')),
                              _PinBtn(
                                  label: '⌫', onTap: _onDelete, isDelete: true),
                            ],
                          ),
                        ),
                        const SizedBox(height: 16),
                        SizedBox(
                          width: double.infinity,
                          child: OutlinedButton.icon(
                            onPressed: () => context.push(AppRoutes.register),
                            icon: const Icon(Icons.person_add_alt_1),
                            label: const Text('Créer un compte'),
                          ),
                        ),
                         const SizedBox(height: 10),
                        const Text(
                          'Simple et rapide pour tous les commerçants.',
                          style: TextStyle(fontSize: 12, color: AppColors.gray400),
                          textAlign: TextAlign.center,
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

class _PinBtn extends StatelessWidget {
  final String label;
  final VoidCallback onTap;
  final bool isDelete;

  const _PinBtn({
    required this.label,
    required this.onTap,
    this.isDelete = false,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.white,
      borderRadius: BorderRadius.circular(14),
      child: InkWell(
        borderRadius: BorderRadius.circular(14),
        onTap: onTap,
        child: Center(
          child: isDelete
              ? const Icon(Icons.backspace_outlined, color: AppColors.gray200)
              : Text(
                  label,
                  style: const TextStyle(
                    fontSize: 30,
                    fontWeight: FontWeight.w500,
                    color: AppColors.gray900,
                  ),
                ),
        ),
      ),
    );
  }
}
