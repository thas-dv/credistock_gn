// lib/core/constants/app_constants.dart

class AppConstants {
  // ── Supabase ─────────────────────────────────────────────
  // Remplacer par vos vraies valeurs depuis le Dashboard Supabase
  static const String supabaseUrl    = 'https://gzaekbnodohycalquufi.supabase.co';
  static const String supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd6YWVrYm5vZG9oeWNhbHF1dWZpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjUxMjIxMTgsImV4cCI6MjA4MDY5ODExOH0.W-8-1PqUHN2FSaGzEWRuwky4ZbExuyB5mlW69gd1qbU';

  // ── App ──────────────────────────────────────────────────
  static const String appName    = 'CrédiStock GN';
  static const String appVersion = '1.0.0';

  // ── Abonnement (GNF) ─────────────────────────────────────
  static const int prixPremiumMois = 25000;  // 25 000 GNF / mois

  // ── Limites plan gratuit ──────────────────────────────────
  static const int maxDettesGratuit  = 10;
  static const int maxClientsGratuit = 20;

  // ── Langues supportées ────────────────────────────────────
  static const List<Map<String, String>> langues = [
    {'code': 'fr', 'label': 'Français',  'flag': '🇫🇷'},
    {'code': 'en', 'label': 'English',   'flag': '🇬🇧'},
    {'code': 'ar', 'label': 'العربية',   'flag': '🇸🇦'},
  ];

  // ── Types de boutique ─────────────────────────────────────
  static const List<Map<String, String>> typesBoutique = [
    {'code': 'general',      'label': 'Commerce général', 'emoji': '🏪'},
    {'code': 'orange_money', 'label': 'Orange Money',     'emoji': '🟠'},
    {'code': 'pharmacie',    'label': 'Pharmacie',        'emoji': '💊'},
    {'code': 'alimentaire',  'label': 'Alimentaire',      'emoji': '🛒'},
    {'code': 'autre',        'label': 'Autre',             'emoji': '📦'},
  ];

  // ── Modes de paiement ─────────────────────────────────────
  static const List<Map<String, String>> modesPaiement = [
    {'code': 'cash',         'label': 'Cash',         'emoji': '💵'},
    {'code': 'credit',       'label': 'Crédit',       'emoji': '📋'},
    {'code': 'orange_money', 'label': 'Orange Money', 'emoji': '🟠'},
    {'code': 'mtn_momo',     'label': 'MTN MoMo',     'emoji': '🟡'},
  ];

  // ── Tables Supabase (préfixe credistock_) ─────────────────
  static const String tableBoutiques    = 'credistock_boutiques';
  static const String tableUtilisateurs = 'credistock_utilisateurs';
  static const String tableProduits     = 'credistock_produits';
  static const String tableClients      = 'credistock_clients';
  static const String tableVentes       = 'credistock_ventes';
  static const String tableLignesVente  = 'credistock_lignes_vente';
  static const String tableDettes       = 'credistock_dettes';
  static const String tablePaiements    = 'credistock_paiements';
  static const String tableSyncQueue    = 'credistock_sync_queue';
  static const String tableAlertes      = 'credistock_alertes';
}