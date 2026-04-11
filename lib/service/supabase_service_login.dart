import 'package:supabase_flutter/supabase_flutter.dart';

class SupabaseServiceLogin {
  final SupabaseClient _client = Supabase.instance.client;

  Future<void> signIn({required String email, required String password}) async {
    await _client.auth.signInWithPassword(email: email, password: password);
  }

  Future<void> signOut() async {
    await _client.auth.signOut();
  }
}
