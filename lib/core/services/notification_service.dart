import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:injectable/injectable.dart';

@pragma('vm:entry-point')
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await NotificationService.instance.showLocalNotification(message);
}

@singleton
class NotificationService {
  static final NotificationService instance = NotificationService._();
  NotificationService._();

  final _fcm = FirebaseMessaging.instance;
  final _localNotif = FlutterLocalNotificationsPlugin();

  static const _channelId = 'credistock_alerts';
  static const _channelName = 'Alertes CrédiStock';

  Future<void> initialiser() async {
    // Permissions
    await _fcm.requestPermission(
      alert: true,
      badge: true,
      sound: true,
    );

    // Canal local Android
    const androidChannel = AndroidNotificationChannel(
      _channelId,
      _channelName,
      description: 'Stock faible, dettes, rappels',
      importance: Importance.high,
    );

    await _localNotif
        .resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>()
        ?.createNotificationChannel(androidChannel);

    // Init plugin local
    await _localNotif.initialize(
      settings: const InitializationSettings(
        android: AndroidInitializationSettings('@mipmap/ic_launcher'),
        iOS: DarwinInitializationSettings(),
      ),
    );

    // Handler messages en arrière-plan
    FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);

    // Handler messages au premier plan
    FirebaseMessaging.onMessage.listen((message) async {
      await showLocalNotification(message);
    });

    // Abonnement aux topics par boutique
    // await _fcm.subscribeToTopic('boutique_$boutiqueId');
  }

  Future<void> showLocalNotification(RemoteMessage message) async {
    final notif = message.notification;
    if (notif == null) return;

    await _localNotif.show(
     id: notif.hashCode,
      title: notif.title,
      body: notif.body,
      notificationDetails: NotificationDetails(
        android: AndroidNotificationDetails(
          _channelId,
          _channelName,
          icon: '@mipmap/ic_launcher',
          importance: Importance.high,
          priority: Priority.high,
        ),
        iOS: const DarwinNotificationDetails(
          presentAlert: true,
          presentBadge: true,
          presentSound: true,
        ),
      ),
    );
  }

  // === Notifications locales planifiées ===

  /// Alerte stock faible — déclenchée localement
  Future<void> alerterStockFaible({
    required String produitNom,
    required int quantiteRestante,
  }) async {
    await _localNotif.show(
     id: produitNom.hashCode,
      title: '⚠️ Stock faible — $produitNom',
      body: 'Seulement $quantiteRestante unité(s) restante(s). Pensez à réapprovisionner.',
      notificationDetails: NotificationDetails(
        android: AndroidNotificationDetails(
          _channelId,
          _channelName,
          importance: Importance.high,
          priority: Priority.high,
        ),
      ),
    );
  }

  /// Rappel dette échéance
  Future<void> rappelerDette({
    required String clientNom,
    required int montantRestant,
    required int joursAvantEcheance,
  }) async {
    final titre = joursAvantEcheance <= 0
        ? '🔴 Echéance dépassée — $clientNom'
        : '⏰ Rappel — $clientNom';

    final corps = joursAvantEcheance <= 0
        ? 'Dette de ${_formatGNF(montantRestant)} GNF dépassée depuis ${-joursAvantEcheance} jour(s)'
        : 'Echéance dans $joursAvantEcheance jour(s) · ${_formatGNF(montantRestant)} GNF';

    await _localNotif.show(
     id: clientNom.hashCode,
      title: titre,
      body: corps,
      notificationDetails: NotificationDetails(
        android: AndroidNotificationDetails(
          _channelId,
          _channelName,
          importance: joursAvantEcheance <= 0 ? Importance.max : Importance.high,
          priority: joursAvantEcheance <= 0 ? Priority.max : Priority.high,
        ),
      ),
    );
  }

  Future<String?> getToken() => _fcm.getToken();

  String _formatGNF(int montant) {
    final str = montant.toString();
    final buffer = StringBuffer();
    for (int i = 0; i < str.length; i++) {
      if (i > 0 && (str.length - i) % 3 == 0) buffer.write(' ');
      buffer.write(str[i]);
    }
    return buffer.toString();
  }
}