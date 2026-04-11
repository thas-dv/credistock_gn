import 'package:flutter/material.dart';

import '../service/supabase_service_login.dart';

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('CrédiStock GN'),
        actions: [
          IconButton(
            onPressed: () async {
              await SupabaseServiceLogin().signOut();
            },
            icon: const Icon(Icons.logout),
          ),
        ],
      ),
      body: const Center(child: Text('Architecture simple Flutter + Supabase')),
    );
  }
}
