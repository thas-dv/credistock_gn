import 'package:supabase_flutter/supabase_flutter.dart';

class SupabaseSyncService {
  final SupabaseClient _client;

  SupabaseSyncService(this._client);

  Future<void> upsertBatch({
    required String table,
    required List<Map<String, dynamic>> rows,
  }) async {
    if (rows.isEmpty) return;
     await _client.from(table).upsert(rows, onConflict: 'id');
  }
}
