import 'package:flutter/material.dart';

class NouvelleVentePage extends StatelessWidget {
  const NouvelleVentePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Nouvelle vente')),
      body: const Center(
        child: Text(
          'Formulaire de vente à compléter',
          textAlign: TextAlign.center,
        ),
      ),
    );
  }
}
