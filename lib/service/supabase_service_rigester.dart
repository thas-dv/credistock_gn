import 'package:supabase_flutter/supabase_flutter.dart';

class SupabaseServiceRigester {
  final SupabaseClient _client = Supabase.instance.client;

  Future<void> registerUserAndShop({
    required String email,
    required String password,
    required String fullName,
    required String shopName,
    required String shopPhone,
    required String shopAddress,
  }) async {
    final authResponse = await _client.auth.signUp(
      email: email,
      password: password,
      data: {
        'full_name': fullName,
      },
    );

    final userId = authResponse.user?.id;
    if (userId == null) {
      throw Exception('Impossible de créer le compte utilisateur.');
    }

    await _client.from('boutiques').insert({
      'owner_id': userId,
      'name': shopName,
      'phone': shopPhone,
      'address': shopAddress,
    });
  }
}
