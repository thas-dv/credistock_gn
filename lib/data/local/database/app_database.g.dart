// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'app_database.dart';

// ignore_for_file: type=lint
class $CreditStockBoutiquesTable extends CreditStockBoutiques
    with TableInfo<$CreditStockBoutiquesTable, CreditStockBoutique> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $CreditStockBoutiquesTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<String> id = GeneratedColumn<String>(
      'id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _nomMeta = const VerificationMeta('nom');
  @override
  late final GeneratedColumn<String> nom = GeneratedColumn<String>(
      'nom', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _telephoneMeta =
      const VerificationMeta('telephone');
  @override
  late final GeneratedColumn<String> telephone = GeneratedColumn<String>(
      'telephone', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _adresseMeta =
      const VerificationMeta('adresse');
  @override
  late final GeneratedColumn<String> adresse = GeneratedColumn<String>(
      'adresse', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _typeBoutiqueMeta =
      const VerificationMeta('typeBoutique');
  @override
  late final GeneratedColumn<String> typeBoutique = GeneratedColumn<String>(
      'type_boutique', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: false,
      defaultValue: const Constant('general'));
  static const VerificationMeta _logoUrlMeta =
      const VerificationMeta('logoUrl');
  @override
  late final GeneratedColumn<String> logoUrl = GeneratedColumn<String>(
      'logo_url', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _pinHashMeta =
      const VerificationMeta('pinHash');
  @override
  late final GeneratedColumn<String> pinHash = GeneratedColumn<String>(
      'pin_hash', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _abonnementMeta =
      const VerificationMeta('abonnement');
  @override
  late final GeneratedColumn<String> abonnement = GeneratedColumn<String>(
      'abonnement', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: false,
      defaultValue: const Constant('gratuit'));
  static const VerificationMeta _premiumExpireAtMeta =
      const VerificationMeta('premiumExpireAt');
  @override
  late final GeneratedColumn<DateTime> premiumExpireAt =
      GeneratedColumn<DateTime>('premium_expire_at', aliasedName, true,
          type: DriftSqlType.dateTime, requiredDuringInsert: false);
  static const VerificationMeta _createdAtMeta =
      const VerificationMeta('createdAt');
  @override
  late final GeneratedColumn<DateTime> createdAt = GeneratedColumn<DateTime>(
      'created_at', aliasedName, false,
      type: DriftSqlType.dateTime,
      requiredDuringInsert: false,
      defaultValue: currentDateAndTime);
  static const VerificationMeta _updatedAtMeta =
      const VerificationMeta('updatedAt');
  @override
  late final GeneratedColumn<DateTime> updatedAt = GeneratedColumn<DateTime>(
      'updated_at', aliasedName, false,
      type: DriftSqlType.dateTime,
      requiredDuringInsert: false,
      defaultValue: currentDateAndTime);
  @override
  List<GeneratedColumn> get $columns => [
        id,
        nom,
        telephone,
        adresse,
        typeBoutique,
        logoUrl,
        pinHash,
        abonnement,
        premiumExpireAt,
        createdAt,
        updatedAt
      ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'credistock_boutiques';
  @override
  VerificationContext validateIntegrity(
      Insertable<CreditStockBoutique> instance,
      {bool isInserting = false}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    } else if (isInserting) {
      context.missing(_idMeta);
    }
    if (data.containsKey('nom')) {
      context.handle(
          _nomMeta, nom.isAcceptableOrUnknown(data['nom']!, _nomMeta));
    } else if (isInserting) {
      context.missing(_nomMeta);
    }
    if (data.containsKey('telephone')) {
      context.handle(_telephoneMeta,
          telephone.isAcceptableOrUnknown(data['telephone']!, _telephoneMeta));
    } else if (isInserting) {
      context.missing(_telephoneMeta);
    }
    if (data.containsKey('adresse')) {
      context.handle(_adresseMeta,
          adresse.isAcceptableOrUnknown(data['adresse']!, _adresseMeta));
    }
    if (data.containsKey('type_boutique')) {
      context.handle(
          _typeBoutiqueMeta,
          typeBoutique.isAcceptableOrUnknown(
              data['type_boutique']!, _typeBoutiqueMeta));
    }
    if (data.containsKey('logo_url')) {
      context.handle(_logoUrlMeta,
          logoUrl.isAcceptableOrUnknown(data['logo_url']!, _logoUrlMeta));
    }
    if (data.containsKey('pin_hash')) {
      context.handle(_pinHashMeta,
          pinHash.isAcceptableOrUnknown(data['pin_hash']!, _pinHashMeta));
    }
    if (data.containsKey('abonnement')) {
      context.handle(
          _abonnementMeta,
          abonnement.isAcceptableOrUnknown(
              data['abonnement']!, _abonnementMeta));
    }
    if (data.containsKey('premium_expire_at')) {
      context.handle(
          _premiumExpireAtMeta,
          premiumExpireAt.isAcceptableOrUnknown(
              data['premium_expire_at']!, _premiumExpireAtMeta));
    }
    if (data.containsKey('created_at')) {
      context.handle(_createdAtMeta,
          createdAt.isAcceptableOrUnknown(data['created_at']!, _createdAtMeta));
    }
    if (data.containsKey('updated_at')) {
      context.handle(_updatedAtMeta,
          updatedAt.isAcceptableOrUnknown(data['updated_at']!, _updatedAtMeta));
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  CreditStockBoutique map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return CreditStockBoutique(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}id'])!,
      nom: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}nom'])!,
      telephone: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}telephone'])!,
      adresse: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}adresse']),
      typeBoutique: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}type_boutique'])!,
      logoUrl: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}logo_url']),
      pinHash: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}pin_hash']),
      abonnement: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}abonnement'])!,
      premiumExpireAt: attachedDatabase.typeMapping.read(
          DriftSqlType.dateTime, data['${effectivePrefix}premium_expire_at']),
      createdAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}created_at'])!,
      updatedAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}updated_at'])!,
    );
  }

  @override
  $CreditStockBoutiquesTable createAlias(String alias) {
    return $CreditStockBoutiquesTable(attachedDatabase, alias);
  }
}

class CreditStockBoutique extends DataClass
    implements Insertable<CreditStockBoutique> {
  final String id;
  final String nom;
  final String telephone;
  final String? adresse;
  final String typeBoutique;
  final String? logoUrl;
  final String? pinHash;
  final String abonnement;
  final DateTime? premiumExpireAt;
  final DateTime createdAt;
  final DateTime updatedAt;
  const CreditStockBoutique(
      {required this.id,
      required this.nom,
      required this.telephone,
      this.adresse,
      required this.typeBoutique,
      this.logoUrl,
      this.pinHash,
      required this.abonnement,
      this.premiumExpireAt,
      required this.createdAt,
      required this.updatedAt});
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<String>(id);
    map['nom'] = Variable<String>(nom);
    map['telephone'] = Variable<String>(telephone);
    if (!nullToAbsent || adresse != null) {
      map['adresse'] = Variable<String>(adresse);
    }
    map['type_boutique'] = Variable<String>(typeBoutique);
    if (!nullToAbsent || logoUrl != null) {
      map['logo_url'] = Variable<String>(logoUrl);
    }
    if (!nullToAbsent || pinHash != null) {
      map['pin_hash'] = Variable<String>(pinHash);
    }
    map['abonnement'] = Variable<String>(abonnement);
    if (!nullToAbsent || premiumExpireAt != null) {
      map['premium_expire_at'] = Variable<DateTime>(premiumExpireAt);
    }
    map['created_at'] = Variable<DateTime>(createdAt);
    map['updated_at'] = Variable<DateTime>(updatedAt);
    return map;
  }

  CreditStockBoutiquesCompanion toCompanion(bool nullToAbsent) {
    return CreditStockBoutiquesCompanion(
      id: Value(id),
      nom: Value(nom),
      telephone: Value(telephone),
      adresse: adresse == null && nullToAbsent
          ? const Value.absent()
          : Value(adresse),
      typeBoutique: Value(typeBoutique),
      logoUrl: logoUrl == null && nullToAbsent
          ? const Value.absent()
          : Value(logoUrl),
      pinHash: pinHash == null && nullToAbsent
          ? const Value.absent()
          : Value(pinHash),
      abonnement: Value(abonnement),
      premiumExpireAt: premiumExpireAt == null && nullToAbsent
          ? const Value.absent()
          : Value(premiumExpireAt),
      createdAt: Value(createdAt),
      updatedAt: Value(updatedAt),
    );
  }

  factory CreditStockBoutique.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return CreditStockBoutique(
      id: serializer.fromJson<String>(json['id']),
      nom: serializer.fromJson<String>(json['nom']),
      telephone: serializer.fromJson<String>(json['telephone']),
      adresse: serializer.fromJson<String?>(json['adresse']),
      typeBoutique: serializer.fromJson<String>(json['typeBoutique']),
      logoUrl: serializer.fromJson<String?>(json['logoUrl']),
      pinHash: serializer.fromJson<String?>(json['pinHash']),
      abonnement: serializer.fromJson<String>(json['abonnement']),
      premiumExpireAt: serializer.fromJson<DateTime?>(json['premiumExpireAt']),
      createdAt: serializer.fromJson<DateTime>(json['createdAt']),
      updatedAt: serializer.fromJson<DateTime>(json['updatedAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<String>(id),
      'nom': serializer.toJson<String>(nom),
      'telephone': serializer.toJson<String>(telephone),
      'adresse': serializer.toJson<String?>(adresse),
      'typeBoutique': serializer.toJson<String>(typeBoutique),
      'logoUrl': serializer.toJson<String?>(logoUrl),
      'pinHash': serializer.toJson<String?>(pinHash),
      'abonnement': serializer.toJson<String>(abonnement),
      'premiumExpireAt': serializer.toJson<DateTime?>(premiumExpireAt),
      'createdAt': serializer.toJson<DateTime>(createdAt),
      'updatedAt': serializer.toJson<DateTime>(updatedAt),
    };
  }

  CreditStockBoutique copyWith(
          {String? id,
          String? nom,
          String? telephone,
          Value<String?> adresse = const Value.absent(),
          String? typeBoutique,
          Value<String?> logoUrl = const Value.absent(),
          Value<String?> pinHash = const Value.absent(),
          String? abonnement,
          Value<DateTime?> premiumExpireAt = const Value.absent(),
          DateTime? createdAt,
          DateTime? updatedAt}) =>
      CreditStockBoutique(
        id: id ?? this.id,
        nom: nom ?? this.nom,
        telephone: telephone ?? this.telephone,
        adresse: adresse.present ? adresse.value : this.adresse,
        typeBoutique: typeBoutique ?? this.typeBoutique,
        logoUrl: logoUrl.present ? logoUrl.value : this.logoUrl,
        pinHash: pinHash.present ? pinHash.value : this.pinHash,
        abonnement: abonnement ?? this.abonnement,
        premiumExpireAt: premiumExpireAt.present
            ? premiumExpireAt.value
            : this.premiumExpireAt,
        createdAt: createdAt ?? this.createdAt,
        updatedAt: updatedAt ?? this.updatedAt,
      );
  CreditStockBoutique copyWithCompanion(CreditStockBoutiquesCompanion data) {
    return CreditStockBoutique(
      id: data.id.present ? data.id.value : this.id,
      nom: data.nom.present ? data.nom.value : this.nom,
      telephone: data.telephone.present ? data.telephone.value : this.telephone,
      adresse: data.adresse.present ? data.adresse.value : this.adresse,
      typeBoutique: data.typeBoutique.present
          ? data.typeBoutique.value
          : this.typeBoutique,
      logoUrl: data.logoUrl.present ? data.logoUrl.value : this.logoUrl,
      pinHash: data.pinHash.present ? data.pinHash.value : this.pinHash,
      abonnement:
          data.abonnement.present ? data.abonnement.value : this.abonnement,
      premiumExpireAt: data.premiumExpireAt.present
          ? data.premiumExpireAt.value
          : this.premiumExpireAt,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
      updatedAt: data.updatedAt.present ? data.updatedAt.value : this.updatedAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('CreditStockBoutique(')
          ..write('id: $id, ')
          ..write('nom: $nom, ')
          ..write('telephone: $telephone, ')
          ..write('adresse: $adresse, ')
          ..write('typeBoutique: $typeBoutique, ')
          ..write('logoUrl: $logoUrl, ')
          ..write('pinHash: $pinHash, ')
          ..write('abonnement: $abonnement, ')
          ..write('premiumExpireAt: $premiumExpireAt, ')
          ..write('createdAt: $createdAt, ')
          ..write('updatedAt: $updatedAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(id, nom, telephone, adresse, typeBoutique,
      logoUrl, pinHash, abonnement, premiumExpireAt, createdAt, updatedAt);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is CreditStockBoutique &&
          other.id == this.id &&
          other.nom == this.nom &&
          other.telephone == this.telephone &&
          other.adresse == this.adresse &&
          other.typeBoutique == this.typeBoutique &&
          other.logoUrl == this.logoUrl &&
          other.pinHash == this.pinHash &&
          other.abonnement == this.abonnement &&
          other.premiumExpireAt == this.premiumExpireAt &&
          other.createdAt == this.createdAt &&
          other.updatedAt == this.updatedAt);
}

class CreditStockBoutiquesCompanion
    extends UpdateCompanion<CreditStockBoutique> {
  final Value<String> id;
  final Value<String> nom;
  final Value<String> telephone;
  final Value<String?> adresse;
  final Value<String> typeBoutique;
  final Value<String?> logoUrl;
  final Value<String?> pinHash;
  final Value<String> abonnement;
  final Value<DateTime?> premiumExpireAt;
  final Value<DateTime> createdAt;
  final Value<DateTime> updatedAt;
  final Value<int> rowid;
  const CreditStockBoutiquesCompanion({
    this.id = const Value.absent(),
    this.nom = const Value.absent(),
    this.telephone = const Value.absent(),
    this.adresse = const Value.absent(),
    this.typeBoutique = const Value.absent(),
    this.logoUrl = const Value.absent(),
    this.pinHash = const Value.absent(),
    this.abonnement = const Value.absent(),
    this.premiumExpireAt = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  CreditStockBoutiquesCompanion.insert({
    required String id,
    required String nom,
    required String telephone,
    this.adresse = const Value.absent(),
    this.typeBoutique = const Value.absent(),
    this.logoUrl = const Value.absent(),
    this.pinHash = const Value.absent(),
    this.abonnement = const Value.absent(),
    this.premiumExpireAt = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  })  : id = Value(id),
        nom = Value(nom),
        telephone = Value(telephone);
  static Insertable<CreditStockBoutique> custom({
    Expression<String>? id,
    Expression<String>? nom,
    Expression<String>? telephone,
    Expression<String>? adresse,
    Expression<String>? typeBoutique,
    Expression<String>? logoUrl,
    Expression<String>? pinHash,
    Expression<String>? abonnement,
    Expression<DateTime>? premiumExpireAt,
    Expression<DateTime>? createdAt,
    Expression<DateTime>? updatedAt,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (nom != null) 'nom': nom,
      if (telephone != null) 'telephone': telephone,
      if (adresse != null) 'adresse': adresse,
      if (typeBoutique != null) 'type_boutique': typeBoutique,
      if (logoUrl != null) 'logo_url': logoUrl,
      if (pinHash != null) 'pin_hash': pinHash,
      if (abonnement != null) 'abonnement': abonnement,
      if (premiumExpireAt != null) 'premium_expire_at': premiumExpireAt,
      if (createdAt != null) 'created_at': createdAt,
      if (updatedAt != null) 'updated_at': updatedAt,
      if (rowid != null) 'rowid': rowid,
    });
  }

  CreditStockBoutiquesCompanion copyWith(
      {Value<String>? id,
      Value<String>? nom,
      Value<String>? telephone,
      Value<String?>? adresse,
      Value<String>? typeBoutique,
      Value<String?>? logoUrl,
      Value<String?>? pinHash,
      Value<String>? abonnement,
      Value<DateTime?>? premiumExpireAt,
      Value<DateTime>? createdAt,
      Value<DateTime>? updatedAt,
      Value<int>? rowid}) {
    return CreditStockBoutiquesCompanion(
      id: id ?? this.id,
      nom: nom ?? this.nom,
      telephone: telephone ?? this.telephone,
      adresse: adresse ?? this.adresse,
      typeBoutique: typeBoutique ?? this.typeBoutique,
      logoUrl: logoUrl ?? this.logoUrl,
      pinHash: pinHash ?? this.pinHash,
      abonnement: abonnement ?? this.abonnement,
      premiumExpireAt: premiumExpireAt ?? this.premiumExpireAt,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<String>(id.value);
    }
    if (nom.present) {
      map['nom'] = Variable<String>(nom.value);
    }
    if (telephone.present) {
      map['telephone'] = Variable<String>(telephone.value);
    }
    if (adresse.present) {
      map['adresse'] = Variable<String>(adresse.value);
    }
    if (typeBoutique.present) {
      map['type_boutique'] = Variable<String>(typeBoutique.value);
    }
    if (logoUrl.present) {
      map['logo_url'] = Variable<String>(logoUrl.value);
    }
    if (pinHash.present) {
      map['pin_hash'] = Variable<String>(pinHash.value);
    }
    if (abonnement.present) {
      map['abonnement'] = Variable<String>(abonnement.value);
    }
    if (premiumExpireAt.present) {
      map['premium_expire_at'] = Variable<DateTime>(premiumExpireAt.value);
    }
    if (createdAt.present) {
      map['created_at'] = Variable<DateTime>(createdAt.value);
    }
    if (updatedAt.present) {
      map['updated_at'] = Variable<DateTime>(updatedAt.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('CreditStockBoutiquesCompanion(')
          ..write('id: $id, ')
          ..write('nom: $nom, ')
          ..write('telephone: $telephone, ')
          ..write('adresse: $adresse, ')
          ..write('typeBoutique: $typeBoutique, ')
          ..write('logoUrl: $logoUrl, ')
          ..write('pinHash: $pinHash, ')
          ..write('abonnement: $abonnement, ')
          ..write('premiumExpireAt: $premiumExpireAt, ')
          ..write('createdAt: $createdAt, ')
          ..write('updatedAt: $updatedAt, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $CreditStockUtilisateursTable extends CreditStockUtilisateurs
    with TableInfo<$CreditStockUtilisateursTable, CreditStockUtilisateur> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $CreditStockUtilisateursTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<String> id = GeneratedColumn<String>(
      'id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _authIdMeta = const VerificationMeta('authId');
  @override
  late final GeneratedColumn<String> authId = GeneratedColumn<String>(
      'auth_id', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _boutiqueIdMeta =
      const VerificationMeta('boutiqueId');
  @override
  late final GeneratedColumn<String> boutiqueId = GeneratedColumn<String>(
      'boutique_id', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: true,
      defaultConstraints: GeneratedColumn.constraintIsAlways(
          'REFERENCES credistock_boutiques (id)'));
  static const VerificationMeta _nomMeta = const VerificationMeta('nom');
  @override
  late final GeneratedColumn<String> nom = GeneratedColumn<String>(
      'nom', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _telephoneMeta =
      const VerificationMeta('telephone');
  @override
  late final GeneratedColumn<String> telephone = GeneratedColumn<String>(
      'telephone', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _roleMeta = const VerificationMeta('role');
  @override
  late final GeneratedColumn<String> role = GeneratedColumn<String>(
      'role', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: false,
      defaultValue: const Constant('employe'));
  static const VerificationMeta _pinHashMeta =
      const VerificationMeta('pinHash');
  @override
  late final GeneratedColumn<String> pinHash = GeneratedColumn<String>(
      'pin_hash', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _actifMeta = const VerificationMeta('actif');
  @override
  late final GeneratedColumn<bool> actif = GeneratedColumn<bool>(
      'actif', aliasedName, false,
      type: DriftSqlType.bool,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('CHECK ("actif" IN (0, 1))'),
      defaultValue: const Constant(true));
  static const VerificationMeta _createdAtMeta =
      const VerificationMeta('createdAt');
  @override
  late final GeneratedColumn<DateTime> createdAt = GeneratedColumn<DateTime>(
      'created_at', aliasedName, false,
      type: DriftSqlType.dateTime,
      requiredDuringInsert: false,
      defaultValue: currentDateAndTime);
  static const VerificationMeta _updatedAtMeta =
      const VerificationMeta('updatedAt');
  @override
  late final GeneratedColumn<DateTime> updatedAt = GeneratedColumn<DateTime>(
      'updated_at', aliasedName, false,
      type: DriftSqlType.dateTime,
      requiredDuringInsert: false,
      defaultValue: currentDateAndTime);
  @override
  List<GeneratedColumn> get $columns => [
        id,
        authId,
        boutiqueId,
        nom,
        telephone,
        role,
        pinHash,
        actif,
        createdAt,
        updatedAt
      ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'credistock_utilisateurs';
  @override
  VerificationContext validateIntegrity(
      Insertable<CreditStockUtilisateur> instance,
      {bool isInserting = false}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    } else if (isInserting) {
      context.missing(_idMeta);
    }
    if (data.containsKey('auth_id')) {
      context.handle(_authIdMeta,
          authId.isAcceptableOrUnknown(data['auth_id']!, _authIdMeta));
    }
    if (data.containsKey('boutique_id')) {
      context.handle(
          _boutiqueIdMeta,
          boutiqueId.isAcceptableOrUnknown(
              data['boutique_id']!, _boutiqueIdMeta));
    } else if (isInserting) {
      context.missing(_boutiqueIdMeta);
    }
    if (data.containsKey('nom')) {
      context.handle(
          _nomMeta, nom.isAcceptableOrUnknown(data['nom']!, _nomMeta));
    } else if (isInserting) {
      context.missing(_nomMeta);
    }
    if (data.containsKey('telephone')) {
      context.handle(_telephoneMeta,
          telephone.isAcceptableOrUnknown(data['telephone']!, _telephoneMeta));
    }
    if (data.containsKey('role')) {
      context.handle(
          _roleMeta, role.isAcceptableOrUnknown(data['role']!, _roleMeta));
    }
    if (data.containsKey('pin_hash')) {
      context.handle(_pinHashMeta,
          pinHash.isAcceptableOrUnknown(data['pin_hash']!, _pinHashMeta));
    }
    if (data.containsKey('actif')) {
      context.handle(
          _actifMeta, actif.isAcceptableOrUnknown(data['actif']!, _actifMeta));
    }
    if (data.containsKey('created_at')) {
      context.handle(_createdAtMeta,
          createdAt.isAcceptableOrUnknown(data['created_at']!, _createdAtMeta));
    }
    if (data.containsKey('updated_at')) {
      context.handle(_updatedAtMeta,
          updatedAt.isAcceptableOrUnknown(data['updated_at']!, _updatedAtMeta));
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  CreditStockUtilisateur map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return CreditStockUtilisateur(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}id'])!,
      authId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}auth_id']),
      boutiqueId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}boutique_id'])!,
      nom: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}nom'])!,
      telephone: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}telephone']),
      role: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}role'])!,
      pinHash: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}pin_hash']),
      actif: attachedDatabase.typeMapping
          .read(DriftSqlType.bool, data['${effectivePrefix}actif'])!,
      createdAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}created_at'])!,
      updatedAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}updated_at'])!,
    );
  }

  @override
  $CreditStockUtilisateursTable createAlias(String alias) {
    return $CreditStockUtilisateursTable(attachedDatabase, alias);
  }
}

class CreditStockUtilisateur extends DataClass
    implements Insertable<CreditStockUtilisateur> {
  final String id;
  final String? authId;
  final String boutiqueId;
  final String nom;
  final String? telephone;
  final String role;
  final String? pinHash;
  final bool actif;
  final DateTime createdAt;
  final DateTime updatedAt;
  const CreditStockUtilisateur(
      {required this.id,
      this.authId,
      required this.boutiqueId,
      required this.nom,
      this.telephone,
      required this.role,
      this.pinHash,
      required this.actif,
      required this.createdAt,
      required this.updatedAt});
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<String>(id);
    if (!nullToAbsent || authId != null) {
      map['auth_id'] = Variable<String>(authId);
    }
    map['boutique_id'] = Variable<String>(boutiqueId);
    map['nom'] = Variable<String>(nom);
    if (!nullToAbsent || telephone != null) {
      map['telephone'] = Variable<String>(telephone);
    }
    map['role'] = Variable<String>(role);
    if (!nullToAbsent || pinHash != null) {
      map['pin_hash'] = Variable<String>(pinHash);
    }
    map['actif'] = Variable<bool>(actif);
    map['created_at'] = Variable<DateTime>(createdAt);
    map['updated_at'] = Variable<DateTime>(updatedAt);
    return map;
  }

  CreditStockUtilisateursCompanion toCompanion(bool nullToAbsent) {
    return CreditStockUtilisateursCompanion(
      id: Value(id),
      authId:
          authId == null && nullToAbsent ? const Value.absent() : Value(authId),
      boutiqueId: Value(boutiqueId),
      nom: Value(nom),
      telephone: telephone == null && nullToAbsent
          ? const Value.absent()
          : Value(telephone),
      role: Value(role),
      pinHash: pinHash == null && nullToAbsent
          ? const Value.absent()
          : Value(pinHash),
      actif: Value(actif),
      createdAt: Value(createdAt),
      updatedAt: Value(updatedAt),
    );
  }

  factory CreditStockUtilisateur.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return CreditStockUtilisateur(
      id: serializer.fromJson<String>(json['id']),
      authId: serializer.fromJson<String?>(json['authId']),
      boutiqueId: serializer.fromJson<String>(json['boutiqueId']),
      nom: serializer.fromJson<String>(json['nom']),
      telephone: serializer.fromJson<String?>(json['telephone']),
      role: serializer.fromJson<String>(json['role']),
      pinHash: serializer.fromJson<String?>(json['pinHash']),
      actif: serializer.fromJson<bool>(json['actif']),
      createdAt: serializer.fromJson<DateTime>(json['createdAt']),
      updatedAt: serializer.fromJson<DateTime>(json['updatedAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<String>(id),
      'authId': serializer.toJson<String?>(authId),
      'boutiqueId': serializer.toJson<String>(boutiqueId),
      'nom': serializer.toJson<String>(nom),
      'telephone': serializer.toJson<String?>(telephone),
      'role': serializer.toJson<String>(role),
      'pinHash': serializer.toJson<String?>(pinHash),
      'actif': serializer.toJson<bool>(actif),
      'createdAt': serializer.toJson<DateTime>(createdAt),
      'updatedAt': serializer.toJson<DateTime>(updatedAt),
    };
  }

  CreditStockUtilisateur copyWith(
          {String? id,
          Value<String?> authId = const Value.absent(),
          String? boutiqueId,
          String? nom,
          Value<String?> telephone = const Value.absent(),
          String? role,
          Value<String?> pinHash = const Value.absent(),
          bool? actif,
          DateTime? createdAt,
          DateTime? updatedAt}) =>
      CreditStockUtilisateur(
        id: id ?? this.id,
        authId: authId.present ? authId.value : this.authId,
        boutiqueId: boutiqueId ?? this.boutiqueId,
        nom: nom ?? this.nom,
        telephone: telephone.present ? telephone.value : this.telephone,
        role: role ?? this.role,
        pinHash: pinHash.present ? pinHash.value : this.pinHash,
        actif: actif ?? this.actif,
        createdAt: createdAt ?? this.createdAt,
        updatedAt: updatedAt ?? this.updatedAt,
      );
  CreditStockUtilisateur copyWithCompanion(
      CreditStockUtilisateursCompanion data) {
    return CreditStockUtilisateur(
      id: data.id.present ? data.id.value : this.id,
      authId: data.authId.present ? data.authId.value : this.authId,
      boutiqueId:
          data.boutiqueId.present ? data.boutiqueId.value : this.boutiqueId,
      nom: data.nom.present ? data.nom.value : this.nom,
      telephone: data.telephone.present ? data.telephone.value : this.telephone,
      role: data.role.present ? data.role.value : this.role,
      pinHash: data.pinHash.present ? data.pinHash.value : this.pinHash,
      actif: data.actif.present ? data.actif.value : this.actif,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
      updatedAt: data.updatedAt.present ? data.updatedAt.value : this.updatedAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('CreditStockUtilisateur(')
          ..write('id: $id, ')
          ..write('authId: $authId, ')
          ..write('boutiqueId: $boutiqueId, ')
          ..write('nom: $nom, ')
          ..write('telephone: $telephone, ')
          ..write('role: $role, ')
          ..write('pinHash: $pinHash, ')
          ..write('actif: $actif, ')
          ..write('createdAt: $createdAt, ')
          ..write('updatedAt: $updatedAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(id, authId, boutiqueId, nom, telephone, role,
      pinHash, actif, createdAt, updatedAt);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is CreditStockUtilisateur &&
          other.id == this.id &&
          other.authId == this.authId &&
          other.boutiqueId == this.boutiqueId &&
          other.nom == this.nom &&
          other.telephone == this.telephone &&
          other.role == this.role &&
          other.pinHash == this.pinHash &&
          other.actif == this.actif &&
          other.createdAt == this.createdAt &&
          other.updatedAt == this.updatedAt);
}

class CreditStockUtilisateursCompanion
    extends UpdateCompanion<CreditStockUtilisateur> {
  final Value<String> id;
  final Value<String?> authId;
  final Value<String> boutiqueId;
  final Value<String> nom;
  final Value<String?> telephone;
  final Value<String> role;
  final Value<String?> pinHash;
  final Value<bool> actif;
  final Value<DateTime> createdAt;
  final Value<DateTime> updatedAt;
  final Value<int> rowid;
  const CreditStockUtilisateursCompanion({
    this.id = const Value.absent(),
    this.authId = const Value.absent(),
    this.boutiqueId = const Value.absent(),
    this.nom = const Value.absent(),
    this.telephone = const Value.absent(),
    this.role = const Value.absent(),
    this.pinHash = const Value.absent(),
    this.actif = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  CreditStockUtilisateursCompanion.insert({
    required String id,
    this.authId = const Value.absent(),
    required String boutiqueId,
    required String nom,
    this.telephone = const Value.absent(),
    this.role = const Value.absent(),
    this.pinHash = const Value.absent(),
    this.actif = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  })  : id = Value(id),
        boutiqueId = Value(boutiqueId),
        nom = Value(nom);
  static Insertable<CreditStockUtilisateur> custom({
    Expression<String>? id,
    Expression<String>? authId,
    Expression<String>? boutiqueId,
    Expression<String>? nom,
    Expression<String>? telephone,
    Expression<String>? role,
    Expression<String>? pinHash,
    Expression<bool>? actif,
    Expression<DateTime>? createdAt,
    Expression<DateTime>? updatedAt,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (authId != null) 'auth_id': authId,
      if (boutiqueId != null) 'boutique_id': boutiqueId,
      if (nom != null) 'nom': nom,
      if (telephone != null) 'telephone': telephone,
      if (role != null) 'role': role,
      if (pinHash != null) 'pin_hash': pinHash,
      if (actif != null) 'actif': actif,
      if (createdAt != null) 'created_at': createdAt,
      if (updatedAt != null) 'updated_at': updatedAt,
      if (rowid != null) 'rowid': rowid,
    });
  }

  CreditStockUtilisateursCompanion copyWith(
      {Value<String>? id,
      Value<String?>? authId,
      Value<String>? boutiqueId,
      Value<String>? nom,
      Value<String?>? telephone,
      Value<String>? role,
      Value<String?>? pinHash,
      Value<bool>? actif,
      Value<DateTime>? createdAt,
      Value<DateTime>? updatedAt,
      Value<int>? rowid}) {
    return CreditStockUtilisateursCompanion(
      id: id ?? this.id,
      authId: authId ?? this.authId,
      boutiqueId: boutiqueId ?? this.boutiqueId,
      nom: nom ?? this.nom,
      telephone: telephone ?? this.telephone,
      role: role ?? this.role,
      pinHash: pinHash ?? this.pinHash,
      actif: actif ?? this.actif,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<String>(id.value);
    }
    if (authId.present) {
      map['auth_id'] = Variable<String>(authId.value);
    }
    if (boutiqueId.present) {
      map['boutique_id'] = Variable<String>(boutiqueId.value);
    }
    if (nom.present) {
      map['nom'] = Variable<String>(nom.value);
    }
    if (telephone.present) {
      map['telephone'] = Variable<String>(telephone.value);
    }
    if (role.present) {
      map['role'] = Variable<String>(role.value);
    }
    if (pinHash.present) {
      map['pin_hash'] = Variable<String>(pinHash.value);
    }
    if (actif.present) {
      map['actif'] = Variable<bool>(actif.value);
    }
    if (createdAt.present) {
      map['created_at'] = Variable<DateTime>(createdAt.value);
    }
    if (updatedAt.present) {
      map['updated_at'] = Variable<DateTime>(updatedAt.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('CreditStockUtilisateursCompanion(')
          ..write('id: $id, ')
          ..write('authId: $authId, ')
          ..write('boutiqueId: $boutiqueId, ')
          ..write('nom: $nom, ')
          ..write('telephone: $telephone, ')
          ..write('role: $role, ')
          ..write('pinHash: $pinHash, ')
          ..write('actif: $actif, ')
          ..write('createdAt: $createdAt, ')
          ..write('updatedAt: $updatedAt, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $CreditStockProduitsTable extends CreditStockProduits
    with TableInfo<$CreditStockProduitsTable, CreditStockProduit> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $CreditStockProduitsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<String> id = GeneratedColumn<String>(
      'id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _boutiqueIdMeta =
      const VerificationMeta('boutiqueId');
  @override
  late final GeneratedColumn<String> boutiqueId = GeneratedColumn<String>(
      'boutique_id', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: true,
      defaultConstraints: GeneratedColumn.constraintIsAlways(
          'REFERENCES credistock_boutiques (id)'));
  static const VerificationMeta _nomMeta = const VerificationMeta('nom');
  @override
  late final GeneratedColumn<String> nom = GeneratedColumn<String>(
      'nom', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _descriptionMeta =
      const VerificationMeta('description');
  @override
  late final GeneratedColumn<String> description = GeneratedColumn<String>(
      'description', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _codeBarreMeta =
      const VerificationMeta('codeBarre');
  @override
  late final GeneratedColumn<String> codeBarre = GeneratedColumn<String>(
      'code_barre', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _prixVenteMeta =
      const VerificationMeta('prixVente');
  @override
  late final GeneratedColumn<int> prixVente = GeneratedColumn<int>(
      'prix_vente', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  static const VerificationMeta _prixAchatMeta =
      const VerificationMeta('prixAchat');
  @override
  late final GeneratedColumn<int> prixAchat = GeneratedColumn<int>(
      'prix_achat', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  static const VerificationMeta _quantiteMeta =
      const VerificationMeta('quantite');
  @override
  late final GeneratedColumn<int> quantite = GeneratedColumn<int>(
      'quantite', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  static const VerificationMeta _seuilAlerteMeta =
      const VerificationMeta('seuilAlerte');
  @override
  late final GeneratedColumn<int> seuilAlerte = GeneratedColumn<int>(
      'seuil_alerte', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(5));
  static const VerificationMeta _uniteMeta = const VerificationMeta('unite');
  @override
  late final GeneratedColumn<String> unite = GeneratedColumn<String>(
      'unite', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: false,
      defaultValue: const Constant('unité'));
  static const VerificationMeta _categorieMeta =
      const VerificationMeta('categorie');
  @override
  late final GeneratedColumn<String> categorie = GeneratedColumn<String>(
      'categorie', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _imageUrlMeta =
      const VerificationMeta('imageUrl');
  @override
  late final GeneratedColumn<String> imageUrl = GeneratedColumn<String>(
      'image_url', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _actifMeta = const VerificationMeta('actif');
  @override
  late final GeneratedColumn<bool> actif = GeneratedColumn<bool>(
      'actif', aliasedName, false,
      type: DriftSqlType.bool,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('CHECK ("actif" IN (0, 1))'),
      defaultValue: const Constant(true));
  static const VerificationMeta _syncedMeta = const VerificationMeta('synced');
  @override
  late final GeneratedColumn<bool> synced = GeneratedColumn<bool>(
      'synced', aliasedName, false,
      type: DriftSqlType.bool,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('CHECK ("synced" IN (0, 1))'),
      defaultValue: const Constant(false));
  static const VerificationMeta _createdAtMeta =
      const VerificationMeta('createdAt');
  @override
  late final GeneratedColumn<DateTime> createdAt = GeneratedColumn<DateTime>(
      'created_at', aliasedName, false,
      type: DriftSqlType.dateTime,
      requiredDuringInsert: false,
      defaultValue: currentDateAndTime);
  static const VerificationMeta _updatedAtMeta =
      const VerificationMeta('updatedAt');
  @override
  late final GeneratedColumn<DateTime> updatedAt = GeneratedColumn<DateTime>(
      'updated_at', aliasedName, false,
      type: DriftSqlType.dateTime,
      requiredDuringInsert: false,
      defaultValue: currentDateAndTime);
  @override
  List<GeneratedColumn> get $columns => [
        id,
        boutiqueId,
        nom,
        description,
        codeBarre,
        prixVente,
        prixAchat,
        quantite,
        seuilAlerte,
        unite,
        categorie,
        imageUrl,
        actif,
        synced,
        createdAt,
        updatedAt
      ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'credistock_produits';
  @override
  VerificationContext validateIntegrity(Insertable<CreditStockProduit> instance,
      {bool isInserting = false}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    } else if (isInserting) {
      context.missing(_idMeta);
    }
    if (data.containsKey('boutique_id')) {
      context.handle(
          _boutiqueIdMeta,
          boutiqueId.isAcceptableOrUnknown(
              data['boutique_id']!, _boutiqueIdMeta));
    } else if (isInserting) {
      context.missing(_boutiqueIdMeta);
    }
    if (data.containsKey('nom')) {
      context.handle(
          _nomMeta, nom.isAcceptableOrUnknown(data['nom']!, _nomMeta));
    } else if (isInserting) {
      context.missing(_nomMeta);
    }
    if (data.containsKey('description')) {
      context.handle(
          _descriptionMeta,
          description.isAcceptableOrUnknown(
              data['description']!, _descriptionMeta));
    }
    if (data.containsKey('code_barre')) {
      context.handle(_codeBarreMeta,
          codeBarre.isAcceptableOrUnknown(data['code_barre']!, _codeBarreMeta));
    }
    if (data.containsKey('prix_vente')) {
      context.handle(_prixVenteMeta,
          prixVente.isAcceptableOrUnknown(data['prix_vente']!, _prixVenteMeta));
    }
    if (data.containsKey('prix_achat')) {
      context.handle(_prixAchatMeta,
          prixAchat.isAcceptableOrUnknown(data['prix_achat']!, _prixAchatMeta));
    }
    if (data.containsKey('quantite')) {
      context.handle(_quantiteMeta,
          quantite.isAcceptableOrUnknown(data['quantite']!, _quantiteMeta));
    }
    if (data.containsKey('seuil_alerte')) {
      context.handle(
          _seuilAlerteMeta,
          seuilAlerte.isAcceptableOrUnknown(
              data['seuil_alerte']!, _seuilAlerteMeta));
    }
    if (data.containsKey('unite')) {
      context.handle(
          _uniteMeta, unite.isAcceptableOrUnknown(data['unite']!, _uniteMeta));
    }
    if (data.containsKey('categorie')) {
      context.handle(_categorieMeta,
          categorie.isAcceptableOrUnknown(data['categorie']!, _categorieMeta));
    }
    if (data.containsKey('image_url')) {
      context.handle(_imageUrlMeta,
          imageUrl.isAcceptableOrUnknown(data['image_url']!, _imageUrlMeta));
    }
    if (data.containsKey('actif')) {
      context.handle(
          _actifMeta, actif.isAcceptableOrUnknown(data['actif']!, _actifMeta));
    }
    if (data.containsKey('synced')) {
      context.handle(_syncedMeta,
          synced.isAcceptableOrUnknown(data['synced']!, _syncedMeta));
    }
    if (data.containsKey('created_at')) {
      context.handle(_createdAtMeta,
          createdAt.isAcceptableOrUnknown(data['created_at']!, _createdAtMeta));
    }
    if (data.containsKey('updated_at')) {
      context.handle(_updatedAtMeta,
          updatedAt.isAcceptableOrUnknown(data['updated_at']!, _updatedAtMeta));
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  CreditStockProduit map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return CreditStockProduit(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}id'])!,
      boutiqueId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}boutique_id'])!,
      nom: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}nom'])!,
      description: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}description']),
      codeBarre: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}code_barre']),
      prixVente: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}prix_vente'])!,
      prixAchat: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}prix_achat'])!,
      quantite: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}quantite'])!,
      seuilAlerte: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}seuil_alerte'])!,
      unite: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}unite'])!,
      categorie: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}categorie']),
      imageUrl: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}image_url']),
      actif: attachedDatabase.typeMapping
          .read(DriftSqlType.bool, data['${effectivePrefix}actif'])!,
      synced: attachedDatabase.typeMapping
          .read(DriftSqlType.bool, data['${effectivePrefix}synced'])!,
      createdAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}created_at'])!,
      updatedAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}updated_at'])!,
    );
  }

  @override
  $CreditStockProduitsTable createAlias(String alias) {
    return $CreditStockProduitsTable(attachedDatabase, alias);
  }
}

class CreditStockProduit extends DataClass
    implements Insertable<CreditStockProduit> {
  final String id;
  final String boutiqueId;
  final String nom;
  final String? description;
  final String? codeBarre;
  final int prixVente;
  final int prixAchat;
  final int quantite;
  final int seuilAlerte;
  final String unite;
  final String? categorie;
  final String? imageUrl;
  final bool actif;
  final bool synced;
  final DateTime createdAt;
  final DateTime updatedAt;
  const CreditStockProduit(
      {required this.id,
      required this.boutiqueId,
      required this.nom,
      this.description,
      this.codeBarre,
      required this.prixVente,
      required this.prixAchat,
      required this.quantite,
      required this.seuilAlerte,
      required this.unite,
      this.categorie,
      this.imageUrl,
      required this.actif,
      required this.synced,
      required this.createdAt,
      required this.updatedAt});
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<String>(id);
    map['boutique_id'] = Variable<String>(boutiqueId);
    map['nom'] = Variable<String>(nom);
    if (!nullToAbsent || description != null) {
      map['description'] = Variable<String>(description);
    }
    if (!nullToAbsent || codeBarre != null) {
      map['code_barre'] = Variable<String>(codeBarre);
    }
    map['prix_vente'] = Variable<int>(prixVente);
    map['prix_achat'] = Variable<int>(prixAchat);
    map['quantite'] = Variable<int>(quantite);
    map['seuil_alerte'] = Variable<int>(seuilAlerte);
    map['unite'] = Variable<String>(unite);
    if (!nullToAbsent || categorie != null) {
      map['categorie'] = Variable<String>(categorie);
    }
    if (!nullToAbsent || imageUrl != null) {
      map['image_url'] = Variable<String>(imageUrl);
    }
    map['actif'] = Variable<bool>(actif);
    map['synced'] = Variable<bool>(synced);
    map['created_at'] = Variable<DateTime>(createdAt);
    map['updated_at'] = Variable<DateTime>(updatedAt);
    return map;
  }

  CreditStockProduitsCompanion toCompanion(bool nullToAbsent) {
    return CreditStockProduitsCompanion(
      id: Value(id),
      boutiqueId: Value(boutiqueId),
      nom: Value(nom),
      description: description == null && nullToAbsent
          ? const Value.absent()
          : Value(description),
      codeBarre: codeBarre == null && nullToAbsent
          ? const Value.absent()
          : Value(codeBarre),
      prixVente: Value(prixVente),
      prixAchat: Value(prixAchat),
      quantite: Value(quantite),
      seuilAlerte: Value(seuilAlerte),
      unite: Value(unite),
      categorie: categorie == null && nullToAbsent
          ? const Value.absent()
          : Value(categorie),
      imageUrl: imageUrl == null && nullToAbsent
          ? const Value.absent()
          : Value(imageUrl),
      actif: Value(actif),
      synced: Value(synced),
      createdAt: Value(createdAt),
      updatedAt: Value(updatedAt),
    );
  }

  factory CreditStockProduit.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return CreditStockProduit(
      id: serializer.fromJson<String>(json['id']),
      boutiqueId: serializer.fromJson<String>(json['boutiqueId']),
      nom: serializer.fromJson<String>(json['nom']),
      description: serializer.fromJson<String?>(json['description']),
      codeBarre: serializer.fromJson<String?>(json['codeBarre']),
      prixVente: serializer.fromJson<int>(json['prixVente']),
      prixAchat: serializer.fromJson<int>(json['prixAchat']),
      quantite: serializer.fromJson<int>(json['quantite']),
      seuilAlerte: serializer.fromJson<int>(json['seuilAlerte']),
      unite: serializer.fromJson<String>(json['unite']),
      categorie: serializer.fromJson<String?>(json['categorie']),
      imageUrl: serializer.fromJson<String?>(json['imageUrl']),
      actif: serializer.fromJson<bool>(json['actif']),
      synced: serializer.fromJson<bool>(json['synced']),
      createdAt: serializer.fromJson<DateTime>(json['createdAt']),
      updatedAt: serializer.fromJson<DateTime>(json['updatedAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<String>(id),
      'boutiqueId': serializer.toJson<String>(boutiqueId),
      'nom': serializer.toJson<String>(nom),
      'description': serializer.toJson<String?>(description),
      'codeBarre': serializer.toJson<String?>(codeBarre),
      'prixVente': serializer.toJson<int>(prixVente),
      'prixAchat': serializer.toJson<int>(prixAchat),
      'quantite': serializer.toJson<int>(quantite),
      'seuilAlerte': serializer.toJson<int>(seuilAlerte),
      'unite': serializer.toJson<String>(unite),
      'categorie': serializer.toJson<String?>(categorie),
      'imageUrl': serializer.toJson<String?>(imageUrl),
      'actif': serializer.toJson<bool>(actif),
      'synced': serializer.toJson<bool>(synced),
      'createdAt': serializer.toJson<DateTime>(createdAt),
      'updatedAt': serializer.toJson<DateTime>(updatedAt),
    };
  }

  CreditStockProduit copyWith(
          {String? id,
          String? boutiqueId,
          String? nom,
          Value<String?> description = const Value.absent(),
          Value<String?> codeBarre = const Value.absent(),
          int? prixVente,
          int? prixAchat,
          int? quantite,
          int? seuilAlerte,
          String? unite,
          Value<String?> categorie = const Value.absent(),
          Value<String?> imageUrl = const Value.absent(),
          bool? actif,
          bool? synced,
          DateTime? createdAt,
          DateTime? updatedAt}) =>
      CreditStockProduit(
        id: id ?? this.id,
        boutiqueId: boutiqueId ?? this.boutiqueId,
        nom: nom ?? this.nom,
        description: description.present ? description.value : this.description,
        codeBarre: codeBarre.present ? codeBarre.value : this.codeBarre,
        prixVente: prixVente ?? this.prixVente,
        prixAchat: prixAchat ?? this.prixAchat,
        quantite: quantite ?? this.quantite,
        seuilAlerte: seuilAlerte ?? this.seuilAlerte,
        unite: unite ?? this.unite,
        categorie: categorie.present ? categorie.value : this.categorie,
        imageUrl: imageUrl.present ? imageUrl.value : this.imageUrl,
        actif: actif ?? this.actif,
        synced: synced ?? this.synced,
        createdAt: createdAt ?? this.createdAt,
        updatedAt: updatedAt ?? this.updatedAt,
      );
  CreditStockProduit copyWithCompanion(CreditStockProduitsCompanion data) {
    return CreditStockProduit(
      id: data.id.present ? data.id.value : this.id,
      boutiqueId:
          data.boutiqueId.present ? data.boutiqueId.value : this.boutiqueId,
      nom: data.nom.present ? data.nom.value : this.nom,
      description:
          data.description.present ? data.description.value : this.description,
      codeBarre: data.codeBarre.present ? data.codeBarre.value : this.codeBarre,
      prixVente: data.prixVente.present ? data.prixVente.value : this.prixVente,
      prixAchat: data.prixAchat.present ? data.prixAchat.value : this.prixAchat,
      quantite: data.quantite.present ? data.quantite.value : this.quantite,
      seuilAlerte:
          data.seuilAlerte.present ? data.seuilAlerte.value : this.seuilAlerte,
      unite: data.unite.present ? data.unite.value : this.unite,
      categorie: data.categorie.present ? data.categorie.value : this.categorie,
      imageUrl: data.imageUrl.present ? data.imageUrl.value : this.imageUrl,
      actif: data.actif.present ? data.actif.value : this.actif,
      synced: data.synced.present ? data.synced.value : this.synced,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
      updatedAt: data.updatedAt.present ? data.updatedAt.value : this.updatedAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('CreditStockProduit(')
          ..write('id: $id, ')
          ..write('boutiqueId: $boutiqueId, ')
          ..write('nom: $nom, ')
          ..write('description: $description, ')
          ..write('codeBarre: $codeBarre, ')
          ..write('prixVente: $prixVente, ')
          ..write('prixAchat: $prixAchat, ')
          ..write('quantite: $quantite, ')
          ..write('seuilAlerte: $seuilAlerte, ')
          ..write('unite: $unite, ')
          ..write('categorie: $categorie, ')
          ..write('imageUrl: $imageUrl, ')
          ..write('actif: $actif, ')
          ..write('synced: $synced, ')
          ..write('createdAt: $createdAt, ')
          ..write('updatedAt: $updatedAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
      id,
      boutiqueId,
      nom,
      description,
      codeBarre,
      prixVente,
      prixAchat,
      quantite,
      seuilAlerte,
      unite,
      categorie,
      imageUrl,
      actif,
      synced,
      createdAt,
      updatedAt);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is CreditStockProduit &&
          other.id == this.id &&
          other.boutiqueId == this.boutiqueId &&
          other.nom == this.nom &&
          other.description == this.description &&
          other.codeBarre == this.codeBarre &&
          other.prixVente == this.prixVente &&
          other.prixAchat == this.prixAchat &&
          other.quantite == this.quantite &&
          other.seuilAlerte == this.seuilAlerte &&
          other.unite == this.unite &&
          other.categorie == this.categorie &&
          other.imageUrl == this.imageUrl &&
          other.actif == this.actif &&
          other.synced == this.synced &&
          other.createdAt == this.createdAt &&
          other.updatedAt == this.updatedAt);
}

class CreditStockProduitsCompanion extends UpdateCompanion<CreditStockProduit> {
  final Value<String> id;
  final Value<String> boutiqueId;
  final Value<String> nom;
  final Value<String?> description;
  final Value<String?> codeBarre;
  final Value<int> prixVente;
  final Value<int> prixAchat;
  final Value<int> quantite;
  final Value<int> seuilAlerte;
  final Value<String> unite;
  final Value<String?> categorie;
  final Value<String?> imageUrl;
  final Value<bool> actif;
  final Value<bool> synced;
  final Value<DateTime> createdAt;
  final Value<DateTime> updatedAt;
  final Value<int> rowid;
  const CreditStockProduitsCompanion({
    this.id = const Value.absent(),
    this.boutiqueId = const Value.absent(),
    this.nom = const Value.absent(),
    this.description = const Value.absent(),
    this.codeBarre = const Value.absent(),
    this.prixVente = const Value.absent(),
    this.prixAchat = const Value.absent(),
    this.quantite = const Value.absent(),
    this.seuilAlerte = const Value.absent(),
    this.unite = const Value.absent(),
    this.categorie = const Value.absent(),
    this.imageUrl = const Value.absent(),
    this.actif = const Value.absent(),
    this.synced = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  CreditStockProduitsCompanion.insert({
    required String id,
    required String boutiqueId,
    required String nom,
    this.description = const Value.absent(),
    this.codeBarre = const Value.absent(),
    this.prixVente = const Value.absent(),
    this.prixAchat = const Value.absent(),
    this.quantite = const Value.absent(),
    this.seuilAlerte = const Value.absent(),
    this.unite = const Value.absent(),
    this.categorie = const Value.absent(),
    this.imageUrl = const Value.absent(),
    this.actif = const Value.absent(),
    this.synced = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  })  : id = Value(id),
        boutiqueId = Value(boutiqueId),
        nom = Value(nom);
  static Insertable<CreditStockProduit> custom({
    Expression<String>? id,
    Expression<String>? boutiqueId,
    Expression<String>? nom,
    Expression<String>? description,
    Expression<String>? codeBarre,
    Expression<int>? prixVente,
    Expression<int>? prixAchat,
    Expression<int>? quantite,
    Expression<int>? seuilAlerte,
    Expression<String>? unite,
    Expression<String>? categorie,
    Expression<String>? imageUrl,
    Expression<bool>? actif,
    Expression<bool>? synced,
    Expression<DateTime>? createdAt,
    Expression<DateTime>? updatedAt,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (boutiqueId != null) 'boutique_id': boutiqueId,
      if (nom != null) 'nom': nom,
      if (description != null) 'description': description,
      if (codeBarre != null) 'code_barre': codeBarre,
      if (prixVente != null) 'prix_vente': prixVente,
      if (prixAchat != null) 'prix_achat': prixAchat,
      if (quantite != null) 'quantite': quantite,
      if (seuilAlerte != null) 'seuil_alerte': seuilAlerte,
      if (unite != null) 'unite': unite,
      if (categorie != null) 'categorie': categorie,
      if (imageUrl != null) 'image_url': imageUrl,
      if (actif != null) 'actif': actif,
      if (synced != null) 'synced': synced,
      if (createdAt != null) 'created_at': createdAt,
      if (updatedAt != null) 'updated_at': updatedAt,
      if (rowid != null) 'rowid': rowid,
    });
  }

  CreditStockProduitsCompanion copyWith(
      {Value<String>? id,
      Value<String>? boutiqueId,
      Value<String>? nom,
      Value<String?>? description,
      Value<String?>? codeBarre,
      Value<int>? prixVente,
      Value<int>? prixAchat,
      Value<int>? quantite,
      Value<int>? seuilAlerte,
      Value<String>? unite,
      Value<String?>? categorie,
      Value<String?>? imageUrl,
      Value<bool>? actif,
      Value<bool>? synced,
      Value<DateTime>? createdAt,
      Value<DateTime>? updatedAt,
      Value<int>? rowid}) {
    return CreditStockProduitsCompanion(
      id: id ?? this.id,
      boutiqueId: boutiqueId ?? this.boutiqueId,
      nom: nom ?? this.nom,
      description: description ?? this.description,
      codeBarre: codeBarre ?? this.codeBarre,
      prixVente: prixVente ?? this.prixVente,
      prixAchat: prixAchat ?? this.prixAchat,
      quantite: quantite ?? this.quantite,
      seuilAlerte: seuilAlerte ?? this.seuilAlerte,
      unite: unite ?? this.unite,
      categorie: categorie ?? this.categorie,
      imageUrl: imageUrl ?? this.imageUrl,
      actif: actif ?? this.actif,
      synced: synced ?? this.synced,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<String>(id.value);
    }
    if (boutiqueId.present) {
      map['boutique_id'] = Variable<String>(boutiqueId.value);
    }
    if (nom.present) {
      map['nom'] = Variable<String>(nom.value);
    }
    if (description.present) {
      map['description'] = Variable<String>(description.value);
    }
    if (codeBarre.present) {
      map['code_barre'] = Variable<String>(codeBarre.value);
    }
    if (prixVente.present) {
      map['prix_vente'] = Variable<int>(prixVente.value);
    }
    if (prixAchat.present) {
      map['prix_achat'] = Variable<int>(prixAchat.value);
    }
    if (quantite.present) {
      map['quantite'] = Variable<int>(quantite.value);
    }
    if (seuilAlerte.present) {
      map['seuil_alerte'] = Variable<int>(seuilAlerte.value);
    }
    if (unite.present) {
      map['unite'] = Variable<String>(unite.value);
    }
    if (categorie.present) {
      map['categorie'] = Variable<String>(categorie.value);
    }
    if (imageUrl.present) {
      map['image_url'] = Variable<String>(imageUrl.value);
    }
    if (actif.present) {
      map['actif'] = Variable<bool>(actif.value);
    }
    if (synced.present) {
      map['synced'] = Variable<bool>(synced.value);
    }
    if (createdAt.present) {
      map['created_at'] = Variable<DateTime>(createdAt.value);
    }
    if (updatedAt.present) {
      map['updated_at'] = Variable<DateTime>(updatedAt.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('CreditStockProduitsCompanion(')
          ..write('id: $id, ')
          ..write('boutiqueId: $boutiqueId, ')
          ..write('nom: $nom, ')
          ..write('description: $description, ')
          ..write('codeBarre: $codeBarre, ')
          ..write('prixVente: $prixVente, ')
          ..write('prixAchat: $prixAchat, ')
          ..write('quantite: $quantite, ')
          ..write('seuilAlerte: $seuilAlerte, ')
          ..write('unite: $unite, ')
          ..write('categorie: $categorie, ')
          ..write('imageUrl: $imageUrl, ')
          ..write('actif: $actif, ')
          ..write('synced: $synced, ')
          ..write('createdAt: $createdAt, ')
          ..write('updatedAt: $updatedAt, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $CreditStockClientsTable extends CreditStockClients
    with TableInfo<$CreditStockClientsTable, CreditStockClient> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $CreditStockClientsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<String> id = GeneratedColumn<String>(
      'id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _boutiqueIdMeta =
      const VerificationMeta('boutiqueId');
  @override
  late final GeneratedColumn<String> boutiqueId = GeneratedColumn<String>(
      'boutique_id', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: true,
      defaultConstraints: GeneratedColumn.constraintIsAlways(
          'REFERENCES credistock_boutiques (id)'));
  static const VerificationMeta _nomMeta = const VerificationMeta('nom');
  @override
  late final GeneratedColumn<String> nom = GeneratedColumn<String>(
      'nom', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _telephoneMeta =
      const VerificationMeta('telephone');
  @override
  late final GeneratedColumn<String> telephone = GeneratedColumn<String>(
      'telephone', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _adresseMeta =
      const VerificationMeta('adresse');
  @override
  late final GeneratedColumn<String> adresse = GeneratedColumn<String>(
      'adresse', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _photoUrlMeta =
      const VerificationMeta('photoUrl');
  @override
  late final GeneratedColumn<String> photoUrl = GeneratedColumn<String>(
      'photo_url', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _scoreMeta = const VerificationMeta('score');
  @override
  late final GeneratedColumn<String> score = GeneratedColumn<String>(
      'score', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: false,
      defaultValue: const Constant('moyen'));
  static const VerificationMeta _totalDuMeta =
      const VerificationMeta('totalDu');
  @override
  late final GeneratedColumn<int> totalDu = GeneratedColumn<int>(
      'total_du', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  static const VerificationMeta _nbAchatsMeta =
      const VerificationMeta('nbAchats');
  @override
  late final GeneratedColumn<int> nbAchats = GeneratedColumn<int>(
      'nb_achats', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  static const VerificationMeta _nbRetardsMeta =
      const VerificationMeta('nbRetards');
  @override
  late final GeneratedColumn<int> nbRetards = GeneratedColumn<int>(
      'nb_retards', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  static const VerificationMeta _syncedMeta = const VerificationMeta('synced');
  @override
  late final GeneratedColumn<bool> synced = GeneratedColumn<bool>(
      'synced', aliasedName, false,
      type: DriftSqlType.bool,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('CHECK ("synced" IN (0, 1))'),
      defaultValue: const Constant(false));
  static const VerificationMeta _createdAtMeta =
      const VerificationMeta('createdAt');
  @override
  late final GeneratedColumn<DateTime> createdAt = GeneratedColumn<DateTime>(
      'created_at', aliasedName, false,
      type: DriftSqlType.dateTime,
      requiredDuringInsert: false,
      defaultValue: currentDateAndTime);
  static const VerificationMeta _updatedAtMeta =
      const VerificationMeta('updatedAt');
  @override
  late final GeneratedColumn<DateTime> updatedAt = GeneratedColumn<DateTime>(
      'updated_at', aliasedName, false,
      type: DriftSqlType.dateTime,
      requiredDuringInsert: false,
      defaultValue: currentDateAndTime);
  @override
  List<GeneratedColumn> get $columns => [
        id,
        boutiqueId,
        nom,
        telephone,
        adresse,
        photoUrl,
        score,
        totalDu,
        nbAchats,
        nbRetards,
        synced,
        createdAt,
        updatedAt
      ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'credistock_clients';
  @override
  VerificationContext validateIntegrity(Insertable<CreditStockClient> instance,
      {bool isInserting = false}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    } else if (isInserting) {
      context.missing(_idMeta);
    }
    if (data.containsKey('boutique_id')) {
      context.handle(
          _boutiqueIdMeta,
          boutiqueId.isAcceptableOrUnknown(
              data['boutique_id']!, _boutiqueIdMeta));
    } else if (isInserting) {
      context.missing(_boutiqueIdMeta);
    }
    if (data.containsKey('nom')) {
      context.handle(
          _nomMeta, nom.isAcceptableOrUnknown(data['nom']!, _nomMeta));
    } else if (isInserting) {
      context.missing(_nomMeta);
    }
    if (data.containsKey('telephone')) {
      context.handle(_telephoneMeta,
          telephone.isAcceptableOrUnknown(data['telephone']!, _telephoneMeta));
    }
    if (data.containsKey('adresse')) {
      context.handle(_adresseMeta,
          adresse.isAcceptableOrUnknown(data['adresse']!, _adresseMeta));
    }
    if (data.containsKey('photo_url')) {
      context.handle(_photoUrlMeta,
          photoUrl.isAcceptableOrUnknown(data['photo_url']!, _photoUrlMeta));
    }
    if (data.containsKey('score')) {
      context.handle(
          _scoreMeta, score.isAcceptableOrUnknown(data['score']!, _scoreMeta));
    }
    if (data.containsKey('total_du')) {
      context.handle(_totalDuMeta,
          totalDu.isAcceptableOrUnknown(data['total_du']!, _totalDuMeta));
    }
    if (data.containsKey('nb_achats')) {
      context.handle(_nbAchatsMeta,
          nbAchats.isAcceptableOrUnknown(data['nb_achats']!, _nbAchatsMeta));
    }
    if (data.containsKey('nb_retards')) {
      context.handle(_nbRetardsMeta,
          nbRetards.isAcceptableOrUnknown(data['nb_retards']!, _nbRetardsMeta));
    }
    if (data.containsKey('synced')) {
      context.handle(_syncedMeta,
          synced.isAcceptableOrUnknown(data['synced']!, _syncedMeta));
    }
    if (data.containsKey('created_at')) {
      context.handle(_createdAtMeta,
          createdAt.isAcceptableOrUnknown(data['created_at']!, _createdAtMeta));
    }
    if (data.containsKey('updated_at')) {
      context.handle(_updatedAtMeta,
          updatedAt.isAcceptableOrUnknown(data['updated_at']!, _updatedAtMeta));
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  CreditStockClient map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return CreditStockClient(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}id'])!,
      boutiqueId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}boutique_id'])!,
      nom: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}nom'])!,
      telephone: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}telephone']),
      adresse: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}adresse']),
      photoUrl: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}photo_url']),
      score: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}score'])!,
      totalDu: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}total_du'])!,
      nbAchats: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}nb_achats'])!,
      nbRetards: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}nb_retards'])!,
      synced: attachedDatabase.typeMapping
          .read(DriftSqlType.bool, data['${effectivePrefix}synced'])!,
      createdAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}created_at'])!,
      updatedAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}updated_at'])!,
    );
  }

  @override
  $CreditStockClientsTable createAlias(String alias) {
    return $CreditStockClientsTable(attachedDatabase, alias);
  }
}

class CreditStockClient extends DataClass
    implements Insertable<CreditStockClient> {
  final String id;
  final String boutiqueId;
  final String nom;
  final String? telephone;
  final String? adresse;
  final String? photoUrl;
  final String score;
  final int totalDu;
  final int nbAchats;
  final int nbRetards;
  final bool synced;
  final DateTime createdAt;
  final DateTime updatedAt;
  const CreditStockClient(
      {required this.id,
      required this.boutiqueId,
      required this.nom,
      this.telephone,
      this.adresse,
      this.photoUrl,
      required this.score,
      required this.totalDu,
      required this.nbAchats,
      required this.nbRetards,
      required this.synced,
      required this.createdAt,
      required this.updatedAt});
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<String>(id);
    map['boutique_id'] = Variable<String>(boutiqueId);
    map['nom'] = Variable<String>(nom);
    if (!nullToAbsent || telephone != null) {
      map['telephone'] = Variable<String>(telephone);
    }
    if (!nullToAbsent || adresse != null) {
      map['adresse'] = Variable<String>(adresse);
    }
    if (!nullToAbsent || photoUrl != null) {
      map['photo_url'] = Variable<String>(photoUrl);
    }
    map['score'] = Variable<String>(score);
    map['total_du'] = Variable<int>(totalDu);
    map['nb_achats'] = Variable<int>(nbAchats);
    map['nb_retards'] = Variable<int>(nbRetards);
    map['synced'] = Variable<bool>(synced);
    map['created_at'] = Variable<DateTime>(createdAt);
    map['updated_at'] = Variable<DateTime>(updatedAt);
    return map;
  }

  CreditStockClientsCompanion toCompanion(bool nullToAbsent) {
    return CreditStockClientsCompanion(
      id: Value(id),
      boutiqueId: Value(boutiqueId),
      nom: Value(nom),
      telephone: telephone == null && nullToAbsent
          ? const Value.absent()
          : Value(telephone),
      adresse: adresse == null && nullToAbsent
          ? const Value.absent()
          : Value(adresse),
      photoUrl: photoUrl == null && nullToAbsent
          ? const Value.absent()
          : Value(photoUrl),
      score: Value(score),
      totalDu: Value(totalDu),
      nbAchats: Value(nbAchats),
      nbRetards: Value(nbRetards),
      synced: Value(synced),
      createdAt: Value(createdAt),
      updatedAt: Value(updatedAt),
    );
  }

  factory CreditStockClient.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return CreditStockClient(
      id: serializer.fromJson<String>(json['id']),
      boutiqueId: serializer.fromJson<String>(json['boutiqueId']),
      nom: serializer.fromJson<String>(json['nom']),
      telephone: serializer.fromJson<String?>(json['telephone']),
      adresse: serializer.fromJson<String?>(json['adresse']),
      photoUrl: serializer.fromJson<String?>(json['photoUrl']),
      score: serializer.fromJson<String>(json['score']),
      totalDu: serializer.fromJson<int>(json['totalDu']),
      nbAchats: serializer.fromJson<int>(json['nbAchats']),
      nbRetards: serializer.fromJson<int>(json['nbRetards']),
      synced: serializer.fromJson<bool>(json['synced']),
      createdAt: serializer.fromJson<DateTime>(json['createdAt']),
      updatedAt: serializer.fromJson<DateTime>(json['updatedAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<String>(id),
      'boutiqueId': serializer.toJson<String>(boutiqueId),
      'nom': serializer.toJson<String>(nom),
      'telephone': serializer.toJson<String?>(telephone),
      'adresse': serializer.toJson<String?>(adresse),
      'photoUrl': serializer.toJson<String?>(photoUrl),
      'score': serializer.toJson<String>(score),
      'totalDu': serializer.toJson<int>(totalDu),
      'nbAchats': serializer.toJson<int>(nbAchats),
      'nbRetards': serializer.toJson<int>(nbRetards),
      'synced': serializer.toJson<bool>(synced),
      'createdAt': serializer.toJson<DateTime>(createdAt),
      'updatedAt': serializer.toJson<DateTime>(updatedAt),
    };
  }

  CreditStockClient copyWith(
          {String? id,
          String? boutiqueId,
          String? nom,
          Value<String?> telephone = const Value.absent(),
          Value<String?> adresse = const Value.absent(),
          Value<String?> photoUrl = const Value.absent(),
          String? score,
          int? totalDu,
          int? nbAchats,
          int? nbRetards,
          bool? synced,
          DateTime? createdAt,
          DateTime? updatedAt}) =>
      CreditStockClient(
        id: id ?? this.id,
        boutiqueId: boutiqueId ?? this.boutiqueId,
        nom: nom ?? this.nom,
        telephone: telephone.present ? telephone.value : this.telephone,
        adresse: adresse.present ? adresse.value : this.adresse,
        photoUrl: photoUrl.present ? photoUrl.value : this.photoUrl,
        score: score ?? this.score,
        totalDu: totalDu ?? this.totalDu,
        nbAchats: nbAchats ?? this.nbAchats,
        nbRetards: nbRetards ?? this.nbRetards,
        synced: synced ?? this.synced,
        createdAt: createdAt ?? this.createdAt,
        updatedAt: updatedAt ?? this.updatedAt,
      );
  CreditStockClient copyWithCompanion(CreditStockClientsCompanion data) {
    return CreditStockClient(
      id: data.id.present ? data.id.value : this.id,
      boutiqueId:
          data.boutiqueId.present ? data.boutiqueId.value : this.boutiqueId,
      nom: data.nom.present ? data.nom.value : this.nom,
      telephone: data.telephone.present ? data.telephone.value : this.telephone,
      adresse: data.adresse.present ? data.adresse.value : this.adresse,
      photoUrl: data.photoUrl.present ? data.photoUrl.value : this.photoUrl,
      score: data.score.present ? data.score.value : this.score,
      totalDu: data.totalDu.present ? data.totalDu.value : this.totalDu,
      nbAchats: data.nbAchats.present ? data.nbAchats.value : this.nbAchats,
      nbRetards: data.nbRetards.present ? data.nbRetards.value : this.nbRetards,
      synced: data.synced.present ? data.synced.value : this.synced,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
      updatedAt: data.updatedAt.present ? data.updatedAt.value : this.updatedAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('CreditStockClient(')
          ..write('id: $id, ')
          ..write('boutiqueId: $boutiqueId, ')
          ..write('nom: $nom, ')
          ..write('telephone: $telephone, ')
          ..write('adresse: $adresse, ')
          ..write('photoUrl: $photoUrl, ')
          ..write('score: $score, ')
          ..write('totalDu: $totalDu, ')
          ..write('nbAchats: $nbAchats, ')
          ..write('nbRetards: $nbRetards, ')
          ..write('synced: $synced, ')
          ..write('createdAt: $createdAt, ')
          ..write('updatedAt: $updatedAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
      id,
      boutiqueId,
      nom,
      telephone,
      adresse,
      photoUrl,
      score,
      totalDu,
      nbAchats,
      nbRetards,
      synced,
      createdAt,
      updatedAt);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is CreditStockClient &&
          other.id == this.id &&
          other.boutiqueId == this.boutiqueId &&
          other.nom == this.nom &&
          other.telephone == this.telephone &&
          other.adresse == this.adresse &&
          other.photoUrl == this.photoUrl &&
          other.score == this.score &&
          other.totalDu == this.totalDu &&
          other.nbAchats == this.nbAchats &&
          other.nbRetards == this.nbRetards &&
          other.synced == this.synced &&
          other.createdAt == this.createdAt &&
          other.updatedAt == this.updatedAt);
}

class CreditStockClientsCompanion extends UpdateCompanion<CreditStockClient> {
  final Value<String> id;
  final Value<String> boutiqueId;
  final Value<String> nom;
  final Value<String?> telephone;
  final Value<String?> adresse;
  final Value<String?> photoUrl;
  final Value<String> score;
  final Value<int> totalDu;
  final Value<int> nbAchats;
  final Value<int> nbRetards;
  final Value<bool> synced;
  final Value<DateTime> createdAt;
  final Value<DateTime> updatedAt;
  final Value<int> rowid;
  const CreditStockClientsCompanion({
    this.id = const Value.absent(),
    this.boutiqueId = const Value.absent(),
    this.nom = const Value.absent(),
    this.telephone = const Value.absent(),
    this.adresse = const Value.absent(),
    this.photoUrl = const Value.absent(),
    this.score = const Value.absent(),
    this.totalDu = const Value.absent(),
    this.nbAchats = const Value.absent(),
    this.nbRetards = const Value.absent(),
    this.synced = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  CreditStockClientsCompanion.insert({
    required String id,
    required String boutiqueId,
    required String nom,
    this.telephone = const Value.absent(),
    this.adresse = const Value.absent(),
    this.photoUrl = const Value.absent(),
    this.score = const Value.absent(),
    this.totalDu = const Value.absent(),
    this.nbAchats = const Value.absent(),
    this.nbRetards = const Value.absent(),
    this.synced = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  })  : id = Value(id),
        boutiqueId = Value(boutiqueId),
        nom = Value(nom);
  static Insertable<CreditStockClient> custom({
    Expression<String>? id,
    Expression<String>? boutiqueId,
    Expression<String>? nom,
    Expression<String>? telephone,
    Expression<String>? adresse,
    Expression<String>? photoUrl,
    Expression<String>? score,
    Expression<int>? totalDu,
    Expression<int>? nbAchats,
    Expression<int>? nbRetards,
    Expression<bool>? synced,
    Expression<DateTime>? createdAt,
    Expression<DateTime>? updatedAt,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (boutiqueId != null) 'boutique_id': boutiqueId,
      if (nom != null) 'nom': nom,
      if (telephone != null) 'telephone': telephone,
      if (adresse != null) 'adresse': adresse,
      if (photoUrl != null) 'photo_url': photoUrl,
      if (score != null) 'score': score,
      if (totalDu != null) 'total_du': totalDu,
      if (nbAchats != null) 'nb_achats': nbAchats,
      if (nbRetards != null) 'nb_retards': nbRetards,
      if (synced != null) 'synced': synced,
      if (createdAt != null) 'created_at': createdAt,
      if (updatedAt != null) 'updated_at': updatedAt,
      if (rowid != null) 'rowid': rowid,
    });
  }

  CreditStockClientsCompanion copyWith(
      {Value<String>? id,
      Value<String>? boutiqueId,
      Value<String>? nom,
      Value<String?>? telephone,
      Value<String?>? adresse,
      Value<String?>? photoUrl,
      Value<String>? score,
      Value<int>? totalDu,
      Value<int>? nbAchats,
      Value<int>? nbRetards,
      Value<bool>? synced,
      Value<DateTime>? createdAt,
      Value<DateTime>? updatedAt,
      Value<int>? rowid}) {
    return CreditStockClientsCompanion(
      id: id ?? this.id,
      boutiqueId: boutiqueId ?? this.boutiqueId,
      nom: nom ?? this.nom,
      telephone: telephone ?? this.telephone,
      adresse: adresse ?? this.adresse,
      photoUrl: photoUrl ?? this.photoUrl,
      score: score ?? this.score,
      totalDu: totalDu ?? this.totalDu,
      nbAchats: nbAchats ?? this.nbAchats,
      nbRetards: nbRetards ?? this.nbRetards,
      synced: synced ?? this.synced,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<String>(id.value);
    }
    if (boutiqueId.present) {
      map['boutique_id'] = Variable<String>(boutiqueId.value);
    }
    if (nom.present) {
      map['nom'] = Variable<String>(nom.value);
    }
    if (telephone.present) {
      map['telephone'] = Variable<String>(telephone.value);
    }
    if (adresse.present) {
      map['adresse'] = Variable<String>(adresse.value);
    }
    if (photoUrl.present) {
      map['photo_url'] = Variable<String>(photoUrl.value);
    }
    if (score.present) {
      map['score'] = Variable<String>(score.value);
    }
    if (totalDu.present) {
      map['total_du'] = Variable<int>(totalDu.value);
    }
    if (nbAchats.present) {
      map['nb_achats'] = Variable<int>(nbAchats.value);
    }
    if (nbRetards.present) {
      map['nb_retards'] = Variable<int>(nbRetards.value);
    }
    if (synced.present) {
      map['synced'] = Variable<bool>(synced.value);
    }
    if (createdAt.present) {
      map['created_at'] = Variable<DateTime>(createdAt.value);
    }
    if (updatedAt.present) {
      map['updated_at'] = Variable<DateTime>(updatedAt.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('CreditStockClientsCompanion(')
          ..write('id: $id, ')
          ..write('boutiqueId: $boutiqueId, ')
          ..write('nom: $nom, ')
          ..write('telephone: $telephone, ')
          ..write('adresse: $adresse, ')
          ..write('photoUrl: $photoUrl, ')
          ..write('score: $score, ')
          ..write('totalDu: $totalDu, ')
          ..write('nbAchats: $nbAchats, ')
          ..write('nbRetards: $nbRetards, ')
          ..write('synced: $synced, ')
          ..write('createdAt: $createdAt, ')
          ..write('updatedAt: $updatedAt, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $CreditStockVentesTable extends CreditStockVentes
    with TableInfo<$CreditStockVentesTable, CreditStockVente> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $CreditStockVentesTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<String> id = GeneratedColumn<String>(
      'id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _boutiqueIdMeta =
      const VerificationMeta('boutiqueId');
  @override
  late final GeneratedColumn<String> boutiqueId = GeneratedColumn<String>(
      'boutique_id', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: true,
      defaultConstraints: GeneratedColumn.constraintIsAlways(
          'REFERENCES credistock_boutiques (id)'));
  static const VerificationMeta _utilisateurIdMeta =
      const VerificationMeta('utilisateurId');
  @override
  late final GeneratedColumn<String> utilisateurId = GeneratedColumn<String>(
      'utilisateur_id', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _clientIdMeta =
      const VerificationMeta('clientId');
  @override
  late final GeneratedColumn<String> clientId = GeneratedColumn<String>(
      'client_id', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _typePaiementMeta =
      const VerificationMeta('typePaiement');
  @override
  late final GeneratedColumn<String> typePaiement = GeneratedColumn<String>(
      'type_paiement', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: false,
      defaultValue: const Constant('cash'));
  static const VerificationMeta _montantTotalMeta =
      const VerificationMeta('montantTotal');
  @override
  late final GeneratedColumn<int> montantTotal = GeneratedColumn<int>(
      'montant_total', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  static const VerificationMeta _noteMeta = const VerificationMeta('note');
  @override
  late final GeneratedColumn<String> note = GeneratedColumn<String>(
      'note', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _syncedMeta = const VerificationMeta('synced');
  @override
  late final GeneratedColumn<bool> synced = GeneratedColumn<bool>(
      'synced', aliasedName, false,
      type: DriftSqlType.bool,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('CHECK ("synced" IN (0, 1))'),
      defaultValue: const Constant(false));
  static const VerificationMeta _dateVenteMeta =
      const VerificationMeta('dateVente');
  @override
  late final GeneratedColumn<DateTime> dateVente = GeneratedColumn<DateTime>(
      'date_vente', aliasedName, false,
      type: DriftSqlType.dateTime,
      requiredDuringInsert: false,
      defaultValue: currentDateAndTime);
  static const VerificationMeta _createdAtMeta =
      const VerificationMeta('createdAt');
  @override
  late final GeneratedColumn<DateTime> createdAt = GeneratedColumn<DateTime>(
      'created_at', aliasedName, false,
      type: DriftSqlType.dateTime,
      requiredDuringInsert: false,
      defaultValue: currentDateAndTime);
  @override
  List<GeneratedColumn> get $columns => [
        id,
        boutiqueId,
        utilisateurId,
        clientId,
        typePaiement,
        montantTotal,
        note,
        synced,
        dateVente,
        createdAt
      ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'credistock_ventes';
  @override
  VerificationContext validateIntegrity(Insertable<CreditStockVente> instance,
      {bool isInserting = false}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    } else if (isInserting) {
      context.missing(_idMeta);
    }
    if (data.containsKey('boutique_id')) {
      context.handle(
          _boutiqueIdMeta,
          boutiqueId.isAcceptableOrUnknown(
              data['boutique_id']!, _boutiqueIdMeta));
    } else if (isInserting) {
      context.missing(_boutiqueIdMeta);
    }
    if (data.containsKey('utilisateur_id')) {
      context.handle(
          _utilisateurIdMeta,
          utilisateurId.isAcceptableOrUnknown(
              data['utilisateur_id']!, _utilisateurIdMeta));
    }
    if (data.containsKey('client_id')) {
      context.handle(_clientIdMeta,
          clientId.isAcceptableOrUnknown(data['client_id']!, _clientIdMeta));
    }
    if (data.containsKey('type_paiement')) {
      context.handle(
          _typePaiementMeta,
          typePaiement.isAcceptableOrUnknown(
              data['type_paiement']!, _typePaiementMeta));
    }
    if (data.containsKey('montant_total')) {
      context.handle(
          _montantTotalMeta,
          montantTotal.isAcceptableOrUnknown(
              data['montant_total']!, _montantTotalMeta));
    }
    if (data.containsKey('note')) {
      context.handle(
          _noteMeta, note.isAcceptableOrUnknown(data['note']!, _noteMeta));
    }
    if (data.containsKey('synced')) {
      context.handle(_syncedMeta,
          synced.isAcceptableOrUnknown(data['synced']!, _syncedMeta));
    }
    if (data.containsKey('date_vente')) {
      context.handle(_dateVenteMeta,
          dateVente.isAcceptableOrUnknown(data['date_vente']!, _dateVenteMeta));
    }
    if (data.containsKey('created_at')) {
      context.handle(_createdAtMeta,
          createdAt.isAcceptableOrUnknown(data['created_at']!, _createdAtMeta));
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  CreditStockVente map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return CreditStockVente(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}id'])!,
      boutiqueId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}boutique_id'])!,
      utilisateurId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}utilisateur_id']),
      clientId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}client_id']),
      typePaiement: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}type_paiement'])!,
      montantTotal: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}montant_total'])!,
      note: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}note']),
      synced: attachedDatabase.typeMapping
          .read(DriftSqlType.bool, data['${effectivePrefix}synced'])!,
      dateVente: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}date_vente'])!,
      createdAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}created_at'])!,
    );
  }

  @override
  $CreditStockVentesTable createAlias(String alias) {
    return $CreditStockVentesTable(attachedDatabase, alias);
  }
}

class CreditStockVente extends DataClass
    implements Insertable<CreditStockVente> {
  final String id;
  final String boutiqueId;
  final String? utilisateurId;
  final String? clientId;
  final String typePaiement;
  final int montantTotal;
  final String? note;
  final bool synced;
  final DateTime dateVente;
  final DateTime createdAt;
  const CreditStockVente(
      {required this.id,
      required this.boutiqueId,
      this.utilisateurId,
      this.clientId,
      required this.typePaiement,
      required this.montantTotal,
      this.note,
      required this.synced,
      required this.dateVente,
      required this.createdAt});
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<String>(id);
    map['boutique_id'] = Variable<String>(boutiqueId);
    if (!nullToAbsent || utilisateurId != null) {
      map['utilisateur_id'] = Variable<String>(utilisateurId);
    }
    if (!nullToAbsent || clientId != null) {
      map['client_id'] = Variable<String>(clientId);
    }
    map['type_paiement'] = Variable<String>(typePaiement);
    map['montant_total'] = Variable<int>(montantTotal);
    if (!nullToAbsent || note != null) {
      map['note'] = Variable<String>(note);
    }
    map['synced'] = Variable<bool>(synced);
    map['date_vente'] = Variable<DateTime>(dateVente);
    map['created_at'] = Variable<DateTime>(createdAt);
    return map;
  }

  CreditStockVentesCompanion toCompanion(bool nullToAbsent) {
    return CreditStockVentesCompanion(
      id: Value(id),
      boutiqueId: Value(boutiqueId),
      utilisateurId: utilisateurId == null && nullToAbsent
          ? const Value.absent()
          : Value(utilisateurId),
      clientId: clientId == null && nullToAbsent
          ? const Value.absent()
          : Value(clientId),
      typePaiement: Value(typePaiement),
      montantTotal: Value(montantTotal),
      note: note == null && nullToAbsent ? const Value.absent() : Value(note),
      synced: Value(synced),
      dateVente: Value(dateVente),
      createdAt: Value(createdAt),
    );
  }

  factory CreditStockVente.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return CreditStockVente(
      id: serializer.fromJson<String>(json['id']),
      boutiqueId: serializer.fromJson<String>(json['boutiqueId']),
      utilisateurId: serializer.fromJson<String?>(json['utilisateurId']),
      clientId: serializer.fromJson<String?>(json['clientId']),
      typePaiement: serializer.fromJson<String>(json['typePaiement']),
      montantTotal: serializer.fromJson<int>(json['montantTotal']),
      note: serializer.fromJson<String?>(json['note']),
      synced: serializer.fromJson<bool>(json['synced']),
      dateVente: serializer.fromJson<DateTime>(json['dateVente']),
      createdAt: serializer.fromJson<DateTime>(json['createdAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<String>(id),
      'boutiqueId': serializer.toJson<String>(boutiqueId),
      'utilisateurId': serializer.toJson<String?>(utilisateurId),
      'clientId': serializer.toJson<String?>(clientId),
      'typePaiement': serializer.toJson<String>(typePaiement),
      'montantTotal': serializer.toJson<int>(montantTotal),
      'note': serializer.toJson<String?>(note),
      'synced': serializer.toJson<bool>(synced),
      'dateVente': serializer.toJson<DateTime>(dateVente),
      'createdAt': serializer.toJson<DateTime>(createdAt),
    };
  }

  CreditStockVente copyWith(
          {String? id,
          String? boutiqueId,
          Value<String?> utilisateurId = const Value.absent(),
          Value<String?> clientId = const Value.absent(),
          String? typePaiement,
          int? montantTotal,
          Value<String?> note = const Value.absent(),
          bool? synced,
          DateTime? dateVente,
          DateTime? createdAt}) =>
      CreditStockVente(
        id: id ?? this.id,
        boutiqueId: boutiqueId ?? this.boutiqueId,
        utilisateurId:
            utilisateurId.present ? utilisateurId.value : this.utilisateurId,
        clientId: clientId.present ? clientId.value : this.clientId,
        typePaiement: typePaiement ?? this.typePaiement,
        montantTotal: montantTotal ?? this.montantTotal,
        note: note.present ? note.value : this.note,
        synced: synced ?? this.synced,
        dateVente: dateVente ?? this.dateVente,
        createdAt: createdAt ?? this.createdAt,
      );
  CreditStockVente copyWithCompanion(CreditStockVentesCompanion data) {
    return CreditStockVente(
      id: data.id.present ? data.id.value : this.id,
      boutiqueId:
          data.boutiqueId.present ? data.boutiqueId.value : this.boutiqueId,
      utilisateurId: data.utilisateurId.present
          ? data.utilisateurId.value
          : this.utilisateurId,
      clientId: data.clientId.present ? data.clientId.value : this.clientId,
      typePaiement: data.typePaiement.present
          ? data.typePaiement.value
          : this.typePaiement,
      montantTotal: data.montantTotal.present
          ? data.montantTotal.value
          : this.montantTotal,
      note: data.note.present ? data.note.value : this.note,
      synced: data.synced.present ? data.synced.value : this.synced,
      dateVente: data.dateVente.present ? data.dateVente.value : this.dateVente,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('CreditStockVente(')
          ..write('id: $id, ')
          ..write('boutiqueId: $boutiqueId, ')
          ..write('utilisateurId: $utilisateurId, ')
          ..write('clientId: $clientId, ')
          ..write('typePaiement: $typePaiement, ')
          ..write('montantTotal: $montantTotal, ')
          ..write('note: $note, ')
          ..write('synced: $synced, ')
          ..write('dateVente: $dateVente, ')
          ..write('createdAt: $createdAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(id, boutiqueId, utilisateurId, clientId,
      typePaiement, montantTotal, note, synced, dateVente, createdAt);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is CreditStockVente &&
          other.id == this.id &&
          other.boutiqueId == this.boutiqueId &&
          other.utilisateurId == this.utilisateurId &&
          other.clientId == this.clientId &&
          other.typePaiement == this.typePaiement &&
          other.montantTotal == this.montantTotal &&
          other.note == this.note &&
          other.synced == this.synced &&
          other.dateVente == this.dateVente &&
          other.createdAt == this.createdAt);
}

class CreditStockVentesCompanion extends UpdateCompanion<CreditStockVente> {
  final Value<String> id;
  final Value<String> boutiqueId;
  final Value<String?> utilisateurId;
  final Value<String?> clientId;
  final Value<String> typePaiement;
  final Value<int> montantTotal;
  final Value<String?> note;
  final Value<bool> synced;
  final Value<DateTime> dateVente;
  final Value<DateTime> createdAt;
  final Value<int> rowid;
  const CreditStockVentesCompanion({
    this.id = const Value.absent(),
    this.boutiqueId = const Value.absent(),
    this.utilisateurId = const Value.absent(),
    this.clientId = const Value.absent(),
    this.typePaiement = const Value.absent(),
    this.montantTotal = const Value.absent(),
    this.note = const Value.absent(),
    this.synced = const Value.absent(),
    this.dateVente = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  CreditStockVentesCompanion.insert({
    required String id,
    required String boutiqueId,
    this.utilisateurId = const Value.absent(),
    this.clientId = const Value.absent(),
    this.typePaiement = const Value.absent(),
    this.montantTotal = const Value.absent(),
    this.note = const Value.absent(),
    this.synced = const Value.absent(),
    this.dateVente = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.rowid = const Value.absent(),
  })  : id = Value(id),
        boutiqueId = Value(boutiqueId);
  static Insertable<CreditStockVente> custom({
    Expression<String>? id,
    Expression<String>? boutiqueId,
    Expression<String>? utilisateurId,
    Expression<String>? clientId,
    Expression<String>? typePaiement,
    Expression<int>? montantTotal,
    Expression<String>? note,
    Expression<bool>? synced,
    Expression<DateTime>? dateVente,
    Expression<DateTime>? createdAt,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (boutiqueId != null) 'boutique_id': boutiqueId,
      if (utilisateurId != null) 'utilisateur_id': utilisateurId,
      if (clientId != null) 'client_id': clientId,
      if (typePaiement != null) 'type_paiement': typePaiement,
      if (montantTotal != null) 'montant_total': montantTotal,
      if (note != null) 'note': note,
      if (synced != null) 'synced': synced,
      if (dateVente != null) 'date_vente': dateVente,
      if (createdAt != null) 'created_at': createdAt,
      if (rowid != null) 'rowid': rowid,
    });
  }

  CreditStockVentesCompanion copyWith(
      {Value<String>? id,
      Value<String>? boutiqueId,
      Value<String?>? utilisateurId,
      Value<String?>? clientId,
      Value<String>? typePaiement,
      Value<int>? montantTotal,
      Value<String?>? note,
      Value<bool>? synced,
      Value<DateTime>? dateVente,
      Value<DateTime>? createdAt,
      Value<int>? rowid}) {
    return CreditStockVentesCompanion(
      id: id ?? this.id,
      boutiqueId: boutiqueId ?? this.boutiqueId,
      utilisateurId: utilisateurId ?? this.utilisateurId,
      clientId: clientId ?? this.clientId,
      typePaiement: typePaiement ?? this.typePaiement,
      montantTotal: montantTotal ?? this.montantTotal,
      note: note ?? this.note,
      synced: synced ?? this.synced,
      dateVente: dateVente ?? this.dateVente,
      createdAt: createdAt ?? this.createdAt,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<String>(id.value);
    }
    if (boutiqueId.present) {
      map['boutique_id'] = Variable<String>(boutiqueId.value);
    }
    if (utilisateurId.present) {
      map['utilisateur_id'] = Variable<String>(utilisateurId.value);
    }
    if (clientId.present) {
      map['client_id'] = Variable<String>(clientId.value);
    }
    if (typePaiement.present) {
      map['type_paiement'] = Variable<String>(typePaiement.value);
    }
    if (montantTotal.present) {
      map['montant_total'] = Variable<int>(montantTotal.value);
    }
    if (note.present) {
      map['note'] = Variable<String>(note.value);
    }
    if (synced.present) {
      map['synced'] = Variable<bool>(synced.value);
    }
    if (dateVente.present) {
      map['date_vente'] = Variable<DateTime>(dateVente.value);
    }
    if (createdAt.present) {
      map['created_at'] = Variable<DateTime>(createdAt.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('CreditStockVentesCompanion(')
          ..write('id: $id, ')
          ..write('boutiqueId: $boutiqueId, ')
          ..write('utilisateurId: $utilisateurId, ')
          ..write('clientId: $clientId, ')
          ..write('typePaiement: $typePaiement, ')
          ..write('montantTotal: $montantTotal, ')
          ..write('note: $note, ')
          ..write('synced: $synced, ')
          ..write('dateVente: $dateVente, ')
          ..write('createdAt: $createdAt, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $CreditStockLignesVenteTable extends CreditStockLignesVente
    with TableInfo<$CreditStockLignesVenteTable, CreditStockLignesVenteData> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $CreditStockLignesVenteTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<String> id = GeneratedColumn<String>(
      'id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _venteIdMeta =
      const VerificationMeta('venteId');
  @override
  late final GeneratedColumn<String> venteId = GeneratedColumn<String>(
      'vente_id', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: true,
      defaultConstraints: GeneratedColumn.constraintIsAlways(
          'REFERENCES credistock_ventes (id)'));
  static const VerificationMeta _produitIdMeta =
      const VerificationMeta('produitId');
  @override
  late final GeneratedColumn<String> produitId = GeneratedColumn<String>(
      'produit_id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _boutiqueIdMeta =
      const VerificationMeta('boutiqueId');
  @override
  late final GeneratedColumn<String> boutiqueId = GeneratedColumn<String>(
      'boutique_id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _nomProduitMeta =
      const VerificationMeta('nomProduit');
  @override
  late final GeneratedColumn<String> nomProduit = GeneratedColumn<String>(
      'nom_produit', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _quantiteMeta =
      const VerificationMeta('quantite');
  @override
  late final GeneratedColumn<int> quantite = GeneratedColumn<int>(
      'quantite', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(1));
  static const VerificationMeta _prixUnitaireMeta =
      const VerificationMeta('prixUnitaire');
  @override
  late final GeneratedColumn<int> prixUnitaire = GeneratedColumn<int>(
      'prix_unitaire', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  static const VerificationMeta _sousTotalMeta =
      const VerificationMeta('sousTotal');
  @override
  late final GeneratedColumn<int> sousTotal = GeneratedColumn<int>(
      'sous_total', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  static const VerificationMeta _syncedMeta = const VerificationMeta('synced');
  @override
  late final GeneratedColumn<bool> synced = GeneratedColumn<bool>(
      'synced', aliasedName, false,
      type: DriftSqlType.bool,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('CHECK ("synced" IN (0, 1))'),
      defaultValue: const Constant(false));
  static const VerificationMeta _createdAtMeta =
      const VerificationMeta('createdAt');
  @override
  late final GeneratedColumn<DateTime> createdAt = GeneratedColumn<DateTime>(
      'created_at', aliasedName, false,
      type: DriftSqlType.dateTime,
      requiredDuringInsert: false,
      defaultValue: currentDateAndTime);
  @override
  List<GeneratedColumn> get $columns => [
        id,
        venteId,
        produitId,
        boutiqueId,
        nomProduit,
        quantite,
        prixUnitaire,
        sousTotal,
        synced,
        createdAt
      ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'credistock_lignes_vente';
  @override
  VerificationContext validateIntegrity(
      Insertable<CreditStockLignesVenteData> instance,
      {bool isInserting = false}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    } else if (isInserting) {
      context.missing(_idMeta);
    }
    if (data.containsKey('vente_id')) {
      context.handle(_venteIdMeta,
          venteId.isAcceptableOrUnknown(data['vente_id']!, _venteIdMeta));
    } else if (isInserting) {
      context.missing(_venteIdMeta);
    }
    if (data.containsKey('produit_id')) {
      context.handle(_produitIdMeta,
          produitId.isAcceptableOrUnknown(data['produit_id']!, _produitIdMeta));
    } else if (isInserting) {
      context.missing(_produitIdMeta);
    }
    if (data.containsKey('boutique_id')) {
      context.handle(
          _boutiqueIdMeta,
          boutiqueId.isAcceptableOrUnknown(
              data['boutique_id']!, _boutiqueIdMeta));
    } else if (isInserting) {
      context.missing(_boutiqueIdMeta);
    }
    if (data.containsKey('nom_produit')) {
      context.handle(
          _nomProduitMeta,
          nomProduit.isAcceptableOrUnknown(
              data['nom_produit']!, _nomProduitMeta));
    } else if (isInserting) {
      context.missing(_nomProduitMeta);
    }
    if (data.containsKey('quantite')) {
      context.handle(_quantiteMeta,
          quantite.isAcceptableOrUnknown(data['quantite']!, _quantiteMeta));
    }
    if (data.containsKey('prix_unitaire')) {
      context.handle(
          _prixUnitaireMeta,
          prixUnitaire.isAcceptableOrUnknown(
              data['prix_unitaire']!, _prixUnitaireMeta));
    }
    if (data.containsKey('sous_total')) {
      context.handle(_sousTotalMeta,
          sousTotal.isAcceptableOrUnknown(data['sous_total']!, _sousTotalMeta));
    }
    if (data.containsKey('synced')) {
      context.handle(_syncedMeta,
          synced.isAcceptableOrUnknown(data['synced']!, _syncedMeta));
    }
    if (data.containsKey('created_at')) {
      context.handle(_createdAtMeta,
          createdAt.isAcceptableOrUnknown(data['created_at']!, _createdAtMeta));
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  CreditStockLignesVenteData map(Map<String, dynamic> data,
      {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return CreditStockLignesVenteData(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}id'])!,
      venteId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}vente_id'])!,
      produitId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}produit_id'])!,
      boutiqueId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}boutique_id'])!,
      nomProduit: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}nom_produit'])!,
      quantite: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}quantite'])!,
      prixUnitaire: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}prix_unitaire'])!,
      sousTotal: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}sous_total'])!,
      synced: attachedDatabase.typeMapping
          .read(DriftSqlType.bool, data['${effectivePrefix}synced'])!,
      createdAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}created_at'])!,
    );
  }

  @override
  $CreditStockLignesVenteTable createAlias(String alias) {
    return $CreditStockLignesVenteTable(attachedDatabase, alias);
  }
}

class CreditStockLignesVenteData extends DataClass
    implements Insertable<CreditStockLignesVenteData> {
  final String id;
  final String venteId;
  final String produitId;
  final String boutiqueId;
  final String nomProduit;
  final int quantite;
  final int prixUnitaire;
  final int sousTotal;
  final bool synced;
  final DateTime createdAt;
  const CreditStockLignesVenteData(
      {required this.id,
      required this.venteId,
      required this.produitId,
      required this.boutiqueId,
      required this.nomProduit,
      required this.quantite,
      required this.prixUnitaire,
      required this.sousTotal,
      required this.synced,
      required this.createdAt});
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<String>(id);
    map['vente_id'] = Variable<String>(venteId);
    map['produit_id'] = Variable<String>(produitId);
    map['boutique_id'] = Variable<String>(boutiqueId);
    map['nom_produit'] = Variable<String>(nomProduit);
    map['quantite'] = Variable<int>(quantite);
    map['prix_unitaire'] = Variable<int>(prixUnitaire);
    map['sous_total'] = Variable<int>(sousTotal);
    map['synced'] = Variable<bool>(synced);
    map['created_at'] = Variable<DateTime>(createdAt);
    return map;
  }

  CreditStockLignesVenteCompanion toCompanion(bool nullToAbsent) {
    return CreditStockLignesVenteCompanion(
      id: Value(id),
      venteId: Value(venteId),
      produitId: Value(produitId),
      boutiqueId: Value(boutiqueId),
      nomProduit: Value(nomProduit),
      quantite: Value(quantite),
      prixUnitaire: Value(prixUnitaire),
      sousTotal: Value(sousTotal),
      synced: Value(synced),
      createdAt: Value(createdAt),
    );
  }

  factory CreditStockLignesVenteData.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return CreditStockLignesVenteData(
      id: serializer.fromJson<String>(json['id']),
      venteId: serializer.fromJson<String>(json['venteId']),
      produitId: serializer.fromJson<String>(json['produitId']),
      boutiqueId: serializer.fromJson<String>(json['boutiqueId']),
      nomProduit: serializer.fromJson<String>(json['nomProduit']),
      quantite: serializer.fromJson<int>(json['quantite']),
      prixUnitaire: serializer.fromJson<int>(json['prixUnitaire']),
      sousTotal: serializer.fromJson<int>(json['sousTotal']),
      synced: serializer.fromJson<bool>(json['synced']),
      createdAt: serializer.fromJson<DateTime>(json['createdAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<String>(id),
      'venteId': serializer.toJson<String>(venteId),
      'produitId': serializer.toJson<String>(produitId),
      'boutiqueId': serializer.toJson<String>(boutiqueId),
      'nomProduit': serializer.toJson<String>(nomProduit),
      'quantite': serializer.toJson<int>(quantite),
      'prixUnitaire': serializer.toJson<int>(prixUnitaire),
      'sousTotal': serializer.toJson<int>(sousTotal),
      'synced': serializer.toJson<bool>(synced),
      'createdAt': serializer.toJson<DateTime>(createdAt),
    };
  }

  CreditStockLignesVenteData copyWith(
          {String? id,
          String? venteId,
          String? produitId,
          String? boutiqueId,
          String? nomProduit,
          int? quantite,
          int? prixUnitaire,
          int? sousTotal,
          bool? synced,
          DateTime? createdAt}) =>
      CreditStockLignesVenteData(
        id: id ?? this.id,
        venteId: venteId ?? this.venteId,
        produitId: produitId ?? this.produitId,
        boutiqueId: boutiqueId ?? this.boutiqueId,
        nomProduit: nomProduit ?? this.nomProduit,
        quantite: quantite ?? this.quantite,
        prixUnitaire: prixUnitaire ?? this.prixUnitaire,
        sousTotal: sousTotal ?? this.sousTotal,
        synced: synced ?? this.synced,
        createdAt: createdAt ?? this.createdAt,
      );
  CreditStockLignesVenteData copyWithCompanion(
      CreditStockLignesVenteCompanion data) {
    return CreditStockLignesVenteData(
      id: data.id.present ? data.id.value : this.id,
      venteId: data.venteId.present ? data.venteId.value : this.venteId,
      produitId: data.produitId.present ? data.produitId.value : this.produitId,
      boutiqueId:
          data.boutiqueId.present ? data.boutiqueId.value : this.boutiqueId,
      nomProduit:
          data.nomProduit.present ? data.nomProduit.value : this.nomProduit,
      quantite: data.quantite.present ? data.quantite.value : this.quantite,
      prixUnitaire: data.prixUnitaire.present
          ? data.prixUnitaire.value
          : this.prixUnitaire,
      sousTotal: data.sousTotal.present ? data.sousTotal.value : this.sousTotal,
      synced: data.synced.present ? data.synced.value : this.synced,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('CreditStockLignesVenteData(')
          ..write('id: $id, ')
          ..write('venteId: $venteId, ')
          ..write('produitId: $produitId, ')
          ..write('boutiqueId: $boutiqueId, ')
          ..write('nomProduit: $nomProduit, ')
          ..write('quantite: $quantite, ')
          ..write('prixUnitaire: $prixUnitaire, ')
          ..write('sousTotal: $sousTotal, ')
          ..write('synced: $synced, ')
          ..write('createdAt: $createdAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(id, venteId, produitId, boutiqueId,
      nomProduit, quantite, prixUnitaire, sousTotal, synced, createdAt);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is CreditStockLignesVenteData &&
          other.id == this.id &&
          other.venteId == this.venteId &&
          other.produitId == this.produitId &&
          other.boutiqueId == this.boutiqueId &&
          other.nomProduit == this.nomProduit &&
          other.quantite == this.quantite &&
          other.prixUnitaire == this.prixUnitaire &&
          other.sousTotal == this.sousTotal &&
          other.synced == this.synced &&
          other.createdAt == this.createdAt);
}

class CreditStockLignesVenteCompanion
    extends UpdateCompanion<CreditStockLignesVenteData> {
  final Value<String> id;
  final Value<String> venteId;
  final Value<String> produitId;
  final Value<String> boutiqueId;
  final Value<String> nomProduit;
  final Value<int> quantite;
  final Value<int> prixUnitaire;
  final Value<int> sousTotal;
  final Value<bool> synced;
  final Value<DateTime> createdAt;
  final Value<int> rowid;
  const CreditStockLignesVenteCompanion({
    this.id = const Value.absent(),
    this.venteId = const Value.absent(),
    this.produitId = const Value.absent(),
    this.boutiqueId = const Value.absent(),
    this.nomProduit = const Value.absent(),
    this.quantite = const Value.absent(),
    this.prixUnitaire = const Value.absent(),
    this.sousTotal = const Value.absent(),
    this.synced = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  CreditStockLignesVenteCompanion.insert({
    required String id,
    required String venteId,
    required String produitId,
    required String boutiqueId,
    required String nomProduit,
    this.quantite = const Value.absent(),
    this.prixUnitaire = const Value.absent(),
    this.sousTotal = const Value.absent(),
    this.synced = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.rowid = const Value.absent(),
  })  : id = Value(id),
        venteId = Value(venteId),
        produitId = Value(produitId),
        boutiqueId = Value(boutiqueId),
        nomProduit = Value(nomProduit);
  static Insertable<CreditStockLignesVenteData> custom({
    Expression<String>? id,
    Expression<String>? venteId,
    Expression<String>? produitId,
    Expression<String>? boutiqueId,
    Expression<String>? nomProduit,
    Expression<int>? quantite,
    Expression<int>? prixUnitaire,
    Expression<int>? sousTotal,
    Expression<bool>? synced,
    Expression<DateTime>? createdAt,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (venteId != null) 'vente_id': venteId,
      if (produitId != null) 'produit_id': produitId,
      if (boutiqueId != null) 'boutique_id': boutiqueId,
      if (nomProduit != null) 'nom_produit': nomProduit,
      if (quantite != null) 'quantite': quantite,
      if (prixUnitaire != null) 'prix_unitaire': prixUnitaire,
      if (sousTotal != null) 'sous_total': sousTotal,
      if (synced != null) 'synced': synced,
      if (createdAt != null) 'created_at': createdAt,
      if (rowid != null) 'rowid': rowid,
    });
  }

  CreditStockLignesVenteCompanion copyWith(
      {Value<String>? id,
      Value<String>? venteId,
      Value<String>? produitId,
      Value<String>? boutiqueId,
      Value<String>? nomProduit,
      Value<int>? quantite,
      Value<int>? prixUnitaire,
      Value<int>? sousTotal,
      Value<bool>? synced,
      Value<DateTime>? createdAt,
      Value<int>? rowid}) {
    return CreditStockLignesVenteCompanion(
      id: id ?? this.id,
      venteId: venteId ?? this.venteId,
      produitId: produitId ?? this.produitId,
      boutiqueId: boutiqueId ?? this.boutiqueId,
      nomProduit: nomProduit ?? this.nomProduit,
      quantite: quantite ?? this.quantite,
      prixUnitaire: prixUnitaire ?? this.prixUnitaire,
      sousTotal: sousTotal ?? this.sousTotal,
      synced: synced ?? this.synced,
      createdAt: createdAt ?? this.createdAt,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<String>(id.value);
    }
    if (venteId.present) {
      map['vente_id'] = Variable<String>(venteId.value);
    }
    if (produitId.present) {
      map['produit_id'] = Variable<String>(produitId.value);
    }
    if (boutiqueId.present) {
      map['boutique_id'] = Variable<String>(boutiqueId.value);
    }
    if (nomProduit.present) {
      map['nom_produit'] = Variable<String>(nomProduit.value);
    }
    if (quantite.present) {
      map['quantite'] = Variable<int>(quantite.value);
    }
    if (prixUnitaire.present) {
      map['prix_unitaire'] = Variable<int>(prixUnitaire.value);
    }
    if (sousTotal.present) {
      map['sous_total'] = Variable<int>(sousTotal.value);
    }
    if (synced.present) {
      map['synced'] = Variable<bool>(synced.value);
    }
    if (createdAt.present) {
      map['created_at'] = Variable<DateTime>(createdAt.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('CreditStockLignesVenteCompanion(')
          ..write('id: $id, ')
          ..write('venteId: $venteId, ')
          ..write('produitId: $produitId, ')
          ..write('boutiqueId: $boutiqueId, ')
          ..write('nomProduit: $nomProduit, ')
          ..write('quantite: $quantite, ')
          ..write('prixUnitaire: $prixUnitaire, ')
          ..write('sousTotal: $sousTotal, ')
          ..write('synced: $synced, ')
          ..write('createdAt: $createdAt, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $CreditStockDettesTable extends CreditStockDettes
    with TableInfo<$CreditStockDettesTable, CreditStockDette> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $CreditStockDettesTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<String> id = GeneratedColumn<String>(
      'id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _boutiqueIdMeta =
      const VerificationMeta('boutiqueId');
  @override
  late final GeneratedColumn<String> boutiqueId = GeneratedColumn<String>(
      'boutique_id', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: true,
      defaultConstraints: GeneratedColumn.constraintIsAlways(
          'REFERENCES credistock_boutiques (id)'));
  static const VerificationMeta _clientIdMeta =
      const VerificationMeta('clientId');
  @override
  late final GeneratedColumn<String> clientId = GeneratedColumn<String>(
      'client_id', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: true,
      defaultConstraints: GeneratedColumn.constraintIsAlways(
          'REFERENCES credistock_clients (id)'));
  static const VerificationMeta _venteIdMeta =
      const VerificationMeta('venteId');
  @override
  late final GeneratedColumn<String> venteId = GeneratedColumn<String>(
      'vente_id', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _montantInitialMeta =
      const VerificationMeta('montantInitial');
  @override
  late final GeneratedColumn<int> montantInitial = GeneratedColumn<int>(
      'montant_initial', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  static const VerificationMeta _montantPayeMeta =
      const VerificationMeta('montantPaye');
  @override
  late final GeneratedColumn<int> montantPaye = GeneratedColumn<int>(
      'montant_paye', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  static const VerificationMeta _statutMeta = const VerificationMeta('statut');
  @override
  late final GeneratedColumn<String> statut = GeneratedColumn<String>(
      'statut', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: false,
      defaultValue: const Constant('non_paye'));
  static const VerificationMeta _dateEcheanceMeta =
      const VerificationMeta('dateEcheance');
  @override
  late final GeneratedColumn<DateTime> dateEcheance = GeneratedColumn<DateTime>(
      'date_echeance', aliasedName, true,
      type: DriftSqlType.dateTime, requiredDuringInsert: false);
  static const VerificationMeta _noteMeta = const VerificationMeta('note');
  @override
  late final GeneratedColumn<String> note = GeneratedColumn<String>(
      'note', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _syncedMeta = const VerificationMeta('synced');
  @override
  late final GeneratedColumn<bool> synced = GeneratedColumn<bool>(
      'synced', aliasedName, false,
      type: DriftSqlType.bool,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('CHECK ("synced" IN (0, 1))'),
      defaultValue: const Constant(false));
  static const VerificationMeta _createdAtMeta =
      const VerificationMeta('createdAt');
  @override
  late final GeneratedColumn<DateTime> createdAt = GeneratedColumn<DateTime>(
      'created_at', aliasedName, false,
      type: DriftSqlType.dateTime,
      requiredDuringInsert: false,
      defaultValue: currentDateAndTime);
  static const VerificationMeta _updatedAtMeta =
      const VerificationMeta('updatedAt');
  @override
  late final GeneratedColumn<DateTime> updatedAt = GeneratedColumn<DateTime>(
      'updated_at', aliasedName, false,
      type: DriftSqlType.dateTime,
      requiredDuringInsert: false,
      defaultValue: currentDateAndTime);
  @override
  List<GeneratedColumn> get $columns => [
        id,
        boutiqueId,
        clientId,
        venteId,
        montantInitial,
        montantPaye,
        statut,
        dateEcheance,
        note,
        synced,
        createdAt,
        updatedAt
      ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'credistock_dettes';
  @override
  VerificationContext validateIntegrity(Insertable<CreditStockDette> instance,
      {bool isInserting = false}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    } else if (isInserting) {
      context.missing(_idMeta);
    }
    if (data.containsKey('boutique_id')) {
      context.handle(
          _boutiqueIdMeta,
          boutiqueId.isAcceptableOrUnknown(
              data['boutique_id']!, _boutiqueIdMeta));
    } else if (isInserting) {
      context.missing(_boutiqueIdMeta);
    }
    if (data.containsKey('client_id')) {
      context.handle(_clientIdMeta,
          clientId.isAcceptableOrUnknown(data['client_id']!, _clientIdMeta));
    } else if (isInserting) {
      context.missing(_clientIdMeta);
    }
    if (data.containsKey('vente_id')) {
      context.handle(_venteIdMeta,
          venteId.isAcceptableOrUnknown(data['vente_id']!, _venteIdMeta));
    }
    if (data.containsKey('montant_initial')) {
      context.handle(
          _montantInitialMeta,
          montantInitial.isAcceptableOrUnknown(
              data['montant_initial']!, _montantInitialMeta));
    }
    if (data.containsKey('montant_paye')) {
      context.handle(
          _montantPayeMeta,
          montantPaye.isAcceptableOrUnknown(
              data['montant_paye']!, _montantPayeMeta));
    }
    if (data.containsKey('statut')) {
      context.handle(_statutMeta,
          statut.isAcceptableOrUnknown(data['statut']!, _statutMeta));
    }
    if (data.containsKey('date_echeance')) {
      context.handle(
          _dateEcheanceMeta,
          dateEcheance.isAcceptableOrUnknown(
              data['date_echeance']!, _dateEcheanceMeta));
    }
    if (data.containsKey('note')) {
      context.handle(
          _noteMeta, note.isAcceptableOrUnknown(data['note']!, _noteMeta));
    }
    if (data.containsKey('synced')) {
      context.handle(_syncedMeta,
          synced.isAcceptableOrUnknown(data['synced']!, _syncedMeta));
    }
    if (data.containsKey('created_at')) {
      context.handle(_createdAtMeta,
          createdAt.isAcceptableOrUnknown(data['created_at']!, _createdAtMeta));
    }
    if (data.containsKey('updated_at')) {
      context.handle(_updatedAtMeta,
          updatedAt.isAcceptableOrUnknown(data['updated_at']!, _updatedAtMeta));
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  CreditStockDette map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return CreditStockDette(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}id'])!,
      boutiqueId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}boutique_id'])!,
      clientId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}client_id'])!,
      venteId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}vente_id']),
      montantInitial: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}montant_initial'])!,
      montantPaye: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}montant_paye'])!,
      statut: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}statut'])!,
      dateEcheance: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}date_echeance']),
      note: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}note']),
      synced: attachedDatabase.typeMapping
          .read(DriftSqlType.bool, data['${effectivePrefix}synced'])!,
      createdAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}created_at'])!,
      updatedAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}updated_at'])!,
    );
  }

  @override
  $CreditStockDettesTable createAlias(String alias) {
    return $CreditStockDettesTable(attachedDatabase, alias);
  }
}

class CreditStockDette extends DataClass
    implements Insertable<CreditStockDette> {
  final String id;
  final String boutiqueId;
  final String clientId;
  final String? venteId;
  final int montantInitial;
  final int montantPaye;
  final String statut;
  final DateTime? dateEcheance;
  final String? note;
  final bool synced;
  final DateTime createdAt;
  final DateTime updatedAt;
  const CreditStockDette(
      {required this.id,
      required this.boutiqueId,
      required this.clientId,
      this.venteId,
      required this.montantInitial,
      required this.montantPaye,
      required this.statut,
      this.dateEcheance,
      this.note,
      required this.synced,
      required this.createdAt,
      required this.updatedAt});
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<String>(id);
    map['boutique_id'] = Variable<String>(boutiqueId);
    map['client_id'] = Variable<String>(clientId);
    if (!nullToAbsent || venteId != null) {
      map['vente_id'] = Variable<String>(venteId);
    }
    map['montant_initial'] = Variable<int>(montantInitial);
    map['montant_paye'] = Variable<int>(montantPaye);
    map['statut'] = Variable<String>(statut);
    if (!nullToAbsent || dateEcheance != null) {
      map['date_echeance'] = Variable<DateTime>(dateEcheance);
    }
    if (!nullToAbsent || note != null) {
      map['note'] = Variable<String>(note);
    }
    map['synced'] = Variable<bool>(synced);
    map['created_at'] = Variable<DateTime>(createdAt);
    map['updated_at'] = Variable<DateTime>(updatedAt);
    return map;
  }

  CreditStockDettesCompanion toCompanion(bool nullToAbsent) {
    return CreditStockDettesCompanion(
      id: Value(id),
      boutiqueId: Value(boutiqueId),
      clientId: Value(clientId),
      venteId: venteId == null && nullToAbsent
          ? const Value.absent()
          : Value(venteId),
      montantInitial: Value(montantInitial),
      montantPaye: Value(montantPaye),
      statut: Value(statut),
      dateEcheance: dateEcheance == null && nullToAbsent
          ? const Value.absent()
          : Value(dateEcheance),
      note: note == null && nullToAbsent ? const Value.absent() : Value(note),
      synced: Value(synced),
      createdAt: Value(createdAt),
      updatedAt: Value(updatedAt),
    );
  }

  factory CreditStockDette.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return CreditStockDette(
      id: serializer.fromJson<String>(json['id']),
      boutiqueId: serializer.fromJson<String>(json['boutiqueId']),
      clientId: serializer.fromJson<String>(json['clientId']),
      venteId: serializer.fromJson<String?>(json['venteId']),
      montantInitial: serializer.fromJson<int>(json['montantInitial']),
      montantPaye: serializer.fromJson<int>(json['montantPaye']),
      statut: serializer.fromJson<String>(json['statut']),
      dateEcheance: serializer.fromJson<DateTime?>(json['dateEcheance']),
      note: serializer.fromJson<String?>(json['note']),
      synced: serializer.fromJson<bool>(json['synced']),
      createdAt: serializer.fromJson<DateTime>(json['createdAt']),
      updatedAt: serializer.fromJson<DateTime>(json['updatedAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<String>(id),
      'boutiqueId': serializer.toJson<String>(boutiqueId),
      'clientId': serializer.toJson<String>(clientId),
      'venteId': serializer.toJson<String?>(venteId),
      'montantInitial': serializer.toJson<int>(montantInitial),
      'montantPaye': serializer.toJson<int>(montantPaye),
      'statut': serializer.toJson<String>(statut),
      'dateEcheance': serializer.toJson<DateTime?>(dateEcheance),
      'note': serializer.toJson<String?>(note),
      'synced': serializer.toJson<bool>(synced),
      'createdAt': serializer.toJson<DateTime>(createdAt),
      'updatedAt': serializer.toJson<DateTime>(updatedAt),
    };
  }

  CreditStockDette copyWith(
          {String? id,
          String? boutiqueId,
          String? clientId,
          Value<String?> venteId = const Value.absent(),
          int? montantInitial,
          int? montantPaye,
          String? statut,
          Value<DateTime?> dateEcheance = const Value.absent(),
          Value<String?> note = const Value.absent(),
          bool? synced,
          DateTime? createdAt,
          DateTime? updatedAt}) =>
      CreditStockDette(
        id: id ?? this.id,
        boutiqueId: boutiqueId ?? this.boutiqueId,
        clientId: clientId ?? this.clientId,
        venteId: venteId.present ? venteId.value : this.venteId,
        montantInitial: montantInitial ?? this.montantInitial,
        montantPaye: montantPaye ?? this.montantPaye,
        statut: statut ?? this.statut,
        dateEcheance:
            dateEcheance.present ? dateEcheance.value : this.dateEcheance,
        note: note.present ? note.value : this.note,
        synced: synced ?? this.synced,
        createdAt: createdAt ?? this.createdAt,
        updatedAt: updatedAt ?? this.updatedAt,
      );
  CreditStockDette copyWithCompanion(CreditStockDettesCompanion data) {
    return CreditStockDette(
      id: data.id.present ? data.id.value : this.id,
      boutiqueId:
          data.boutiqueId.present ? data.boutiqueId.value : this.boutiqueId,
      clientId: data.clientId.present ? data.clientId.value : this.clientId,
      venteId: data.venteId.present ? data.venteId.value : this.venteId,
      montantInitial: data.montantInitial.present
          ? data.montantInitial.value
          : this.montantInitial,
      montantPaye:
          data.montantPaye.present ? data.montantPaye.value : this.montantPaye,
      statut: data.statut.present ? data.statut.value : this.statut,
      dateEcheance: data.dateEcheance.present
          ? data.dateEcheance.value
          : this.dateEcheance,
      note: data.note.present ? data.note.value : this.note,
      synced: data.synced.present ? data.synced.value : this.synced,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
      updatedAt: data.updatedAt.present ? data.updatedAt.value : this.updatedAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('CreditStockDette(')
          ..write('id: $id, ')
          ..write('boutiqueId: $boutiqueId, ')
          ..write('clientId: $clientId, ')
          ..write('venteId: $venteId, ')
          ..write('montantInitial: $montantInitial, ')
          ..write('montantPaye: $montantPaye, ')
          ..write('statut: $statut, ')
          ..write('dateEcheance: $dateEcheance, ')
          ..write('note: $note, ')
          ..write('synced: $synced, ')
          ..write('createdAt: $createdAt, ')
          ..write('updatedAt: $updatedAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
      id,
      boutiqueId,
      clientId,
      venteId,
      montantInitial,
      montantPaye,
      statut,
      dateEcheance,
      note,
      synced,
      createdAt,
      updatedAt);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is CreditStockDette &&
          other.id == this.id &&
          other.boutiqueId == this.boutiqueId &&
          other.clientId == this.clientId &&
          other.venteId == this.venteId &&
          other.montantInitial == this.montantInitial &&
          other.montantPaye == this.montantPaye &&
          other.statut == this.statut &&
          other.dateEcheance == this.dateEcheance &&
          other.note == this.note &&
          other.synced == this.synced &&
          other.createdAt == this.createdAt &&
          other.updatedAt == this.updatedAt);
}

class CreditStockDettesCompanion extends UpdateCompanion<CreditStockDette> {
  final Value<String> id;
  final Value<String> boutiqueId;
  final Value<String> clientId;
  final Value<String?> venteId;
  final Value<int> montantInitial;
  final Value<int> montantPaye;
  final Value<String> statut;
  final Value<DateTime?> dateEcheance;
  final Value<String?> note;
  final Value<bool> synced;
  final Value<DateTime> createdAt;
  final Value<DateTime> updatedAt;
  final Value<int> rowid;
  const CreditStockDettesCompanion({
    this.id = const Value.absent(),
    this.boutiqueId = const Value.absent(),
    this.clientId = const Value.absent(),
    this.venteId = const Value.absent(),
    this.montantInitial = const Value.absent(),
    this.montantPaye = const Value.absent(),
    this.statut = const Value.absent(),
    this.dateEcheance = const Value.absent(),
    this.note = const Value.absent(),
    this.synced = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  CreditStockDettesCompanion.insert({
    required String id,
    required String boutiqueId,
    required String clientId,
    this.venteId = const Value.absent(),
    this.montantInitial = const Value.absent(),
    this.montantPaye = const Value.absent(),
    this.statut = const Value.absent(),
    this.dateEcheance = const Value.absent(),
    this.note = const Value.absent(),
    this.synced = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  })  : id = Value(id),
        boutiqueId = Value(boutiqueId),
        clientId = Value(clientId);
  static Insertable<CreditStockDette> custom({
    Expression<String>? id,
    Expression<String>? boutiqueId,
    Expression<String>? clientId,
    Expression<String>? venteId,
    Expression<int>? montantInitial,
    Expression<int>? montantPaye,
    Expression<String>? statut,
    Expression<DateTime>? dateEcheance,
    Expression<String>? note,
    Expression<bool>? synced,
    Expression<DateTime>? createdAt,
    Expression<DateTime>? updatedAt,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (boutiqueId != null) 'boutique_id': boutiqueId,
      if (clientId != null) 'client_id': clientId,
      if (venteId != null) 'vente_id': venteId,
      if (montantInitial != null) 'montant_initial': montantInitial,
      if (montantPaye != null) 'montant_paye': montantPaye,
      if (statut != null) 'statut': statut,
      if (dateEcheance != null) 'date_echeance': dateEcheance,
      if (note != null) 'note': note,
      if (synced != null) 'synced': synced,
      if (createdAt != null) 'created_at': createdAt,
      if (updatedAt != null) 'updated_at': updatedAt,
      if (rowid != null) 'rowid': rowid,
    });
  }

  CreditStockDettesCompanion copyWith(
      {Value<String>? id,
      Value<String>? boutiqueId,
      Value<String>? clientId,
      Value<String?>? venteId,
      Value<int>? montantInitial,
      Value<int>? montantPaye,
      Value<String>? statut,
      Value<DateTime?>? dateEcheance,
      Value<String?>? note,
      Value<bool>? synced,
      Value<DateTime>? createdAt,
      Value<DateTime>? updatedAt,
      Value<int>? rowid}) {
    return CreditStockDettesCompanion(
      id: id ?? this.id,
      boutiqueId: boutiqueId ?? this.boutiqueId,
      clientId: clientId ?? this.clientId,
      venteId: venteId ?? this.venteId,
      montantInitial: montantInitial ?? this.montantInitial,
      montantPaye: montantPaye ?? this.montantPaye,
      statut: statut ?? this.statut,
      dateEcheance: dateEcheance ?? this.dateEcheance,
      note: note ?? this.note,
      synced: synced ?? this.synced,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<String>(id.value);
    }
    if (boutiqueId.present) {
      map['boutique_id'] = Variable<String>(boutiqueId.value);
    }
    if (clientId.present) {
      map['client_id'] = Variable<String>(clientId.value);
    }
    if (venteId.present) {
      map['vente_id'] = Variable<String>(venteId.value);
    }
    if (montantInitial.present) {
      map['montant_initial'] = Variable<int>(montantInitial.value);
    }
    if (montantPaye.present) {
      map['montant_paye'] = Variable<int>(montantPaye.value);
    }
    if (statut.present) {
      map['statut'] = Variable<String>(statut.value);
    }
    if (dateEcheance.present) {
      map['date_echeance'] = Variable<DateTime>(dateEcheance.value);
    }
    if (note.present) {
      map['note'] = Variable<String>(note.value);
    }
    if (synced.present) {
      map['synced'] = Variable<bool>(synced.value);
    }
    if (createdAt.present) {
      map['created_at'] = Variable<DateTime>(createdAt.value);
    }
    if (updatedAt.present) {
      map['updated_at'] = Variable<DateTime>(updatedAt.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('CreditStockDettesCompanion(')
          ..write('id: $id, ')
          ..write('boutiqueId: $boutiqueId, ')
          ..write('clientId: $clientId, ')
          ..write('venteId: $venteId, ')
          ..write('montantInitial: $montantInitial, ')
          ..write('montantPaye: $montantPaye, ')
          ..write('statut: $statut, ')
          ..write('dateEcheance: $dateEcheance, ')
          ..write('note: $note, ')
          ..write('synced: $synced, ')
          ..write('createdAt: $createdAt, ')
          ..write('updatedAt: $updatedAt, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $CreditStockPaiementsTable extends CreditStockPaiements
    with TableInfo<$CreditStockPaiementsTable, CreditStockPaiement> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $CreditStockPaiementsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<String> id = GeneratedColumn<String>(
      'id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _boutiqueIdMeta =
      const VerificationMeta('boutiqueId');
  @override
  late final GeneratedColumn<String> boutiqueId = GeneratedColumn<String>(
      'boutique_id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _detteIdMeta =
      const VerificationMeta('detteId');
  @override
  late final GeneratedColumn<String> detteId = GeneratedColumn<String>(
      'dette_id', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: true,
      defaultConstraints: GeneratedColumn.constraintIsAlways(
          'REFERENCES credistock_dettes (id)'));
  static const VerificationMeta _clientIdMeta =
      const VerificationMeta('clientId');
  @override
  late final GeneratedColumn<String> clientId = GeneratedColumn<String>(
      'client_id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _montantMeta =
      const VerificationMeta('montant');
  @override
  late final GeneratedColumn<int> montant = GeneratedColumn<int>(
      'montant', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  static const VerificationMeta _modePaiementMeta =
      const VerificationMeta('modePaiement');
  @override
  late final GeneratedColumn<String> modePaiement = GeneratedColumn<String>(
      'mode_paiement', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: false,
      defaultValue: const Constant('cash'));
  static const VerificationMeta _noteMeta = const VerificationMeta('note');
  @override
  late final GeneratedColumn<String> note = GeneratedColumn<String>(
      'note', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _syncedMeta = const VerificationMeta('synced');
  @override
  late final GeneratedColumn<bool> synced = GeneratedColumn<bool>(
      'synced', aliasedName, false,
      type: DriftSqlType.bool,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('CHECK ("synced" IN (0, 1))'),
      defaultValue: const Constant(false));
  static const VerificationMeta _createdAtMeta =
      const VerificationMeta('createdAt');
  @override
  late final GeneratedColumn<DateTime> createdAt = GeneratedColumn<DateTime>(
      'created_at', aliasedName, false,
      type: DriftSqlType.dateTime,
      requiredDuringInsert: false,
      defaultValue: currentDateAndTime);
  @override
  List<GeneratedColumn> get $columns => [
        id,
        boutiqueId,
        detteId,
        clientId,
        montant,
        modePaiement,
        note,
        synced,
        createdAt
      ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'credistock_paiements';
  @override
  VerificationContext validateIntegrity(
      Insertable<CreditStockPaiement> instance,
      {bool isInserting = false}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    } else if (isInserting) {
      context.missing(_idMeta);
    }
    if (data.containsKey('boutique_id')) {
      context.handle(
          _boutiqueIdMeta,
          boutiqueId.isAcceptableOrUnknown(
              data['boutique_id']!, _boutiqueIdMeta));
    } else if (isInserting) {
      context.missing(_boutiqueIdMeta);
    }
    if (data.containsKey('dette_id')) {
      context.handle(_detteIdMeta,
          detteId.isAcceptableOrUnknown(data['dette_id']!, _detteIdMeta));
    } else if (isInserting) {
      context.missing(_detteIdMeta);
    }
    if (data.containsKey('client_id')) {
      context.handle(_clientIdMeta,
          clientId.isAcceptableOrUnknown(data['client_id']!, _clientIdMeta));
    } else if (isInserting) {
      context.missing(_clientIdMeta);
    }
    if (data.containsKey('montant')) {
      context.handle(_montantMeta,
          montant.isAcceptableOrUnknown(data['montant']!, _montantMeta));
    }
    if (data.containsKey('mode_paiement')) {
      context.handle(
          _modePaiementMeta,
          modePaiement.isAcceptableOrUnknown(
              data['mode_paiement']!, _modePaiementMeta));
    }
    if (data.containsKey('note')) {
      context.handle(
          _noteMeta, note.isAcceptableOrUnknown(data['note']!, _noteMeta));
    }
    if (data.containsKey('synced')) {
      context.handle(_syncedMeta,
          synced.isAcceptableOrUnknown(data['synced']!, _syncedMeta));
    }
    if (data.containsKey('created_at')) {
      context.handle(_createdAtMeta,
          createdAt.isAcceptableOrUnknown(data['created_at']!, _createdAtMeta));
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  CreditStockPaiement map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return CreditStockPaiement(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}id'])!,
      boutiqueId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}boutique_id'])!,
      detteId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}dette_id'])!,
      clientId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}client_id'])!,
      montant: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}montant'])!,
      modePaiement: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}mode_paiement'])!,
      note: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}note']),
      synced: attachedDatabase.typeMapping
          .read(DriftSqlType.bool, data['${effectivePrefix}synced'])!,
      createdAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}created_at'])!,
    );
  }

  @override
  $CreditStockPaiementsTable createAlias(String alias) {
    return $CreditStockPaiementsTable(attachedDatabase, alias);
  }
}

class CreditStockPaiement extends DataClass
    implements Insertable<CreditStockPaiement> {
  final String id;
  final String boutiqueId;
  final String detteId;
  final String clientId;
  final int montant;
  final String modePaiement;
  final String? note;
  final bool synced;
  final DateTime createdAt;
  const CreditStockPaiement(
      {required this.id,
      required this.boutiqueId,
      required this.detteId,
      required this.clientId,
      required this.montant,
      required this.modePaiement,
      this.note,
      required this.synced,
      required this.createdAt});
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<String>(id);
    map['boutique_id'] = Variable<String>(boutiqueId);
    map['dette_id'] = Variable<String>(detteId);
    map['client_id'] = Variable<String>(clientId);
    map['montant'] = Variable<int>(montant);
    map['mode_paiement'] = Variable<String>(modePaiement);
    if (!nullToAbsent || note != null) {
      map['note'] = Variable<String>(note);
    }
    map['synced'] = Variable<bool>(synced);
    map['created_at'] = Variable<DateTime>(createdAt);
    return map;
  }

  CreditStockPaiementsCompanion toCompanion(bool nullToAbsent) {
    return CreditStockPaiementsCompanion(
      id: Value(id),
      boutiqueId: Value(boutiqueId),
      detteId: Value(detteId),
      clientId: Value(clientId),
      montant: Value(montant),
      modePaiement: Value(modePaiement),
      note: note == null && nullToAbsent ? const Value.absent() : Value(note),
      synced: Value(synced),
      createdAt: Value(createdAt),
    );
  }

  factory CreditStockPaiement.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return CreditStockPaiement(
      id: serializer.fromJson<String>(json['id']),
      boutiqueId: serializer.fromJson<String>(json['boutiqueId']),
      detteId: serializer.fromJson<String>(json['detteId']),
      clientId: serializer.fromJson<String>(json['clientId']),
      montant: serializer.fromJson<int>(json['montant']),
      modePaiement: serializer.fromJson<String>(json['modePaiement']),
      note: serializer.fromJson<String?>(json['note']),
      synced: serializer.fromJson<bool>(json['synced']),
      createdAt: serializer.fromJson<DateTime>(json['createdAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<String>(id),
      'boutiqueId': serializer.toJson<String>(boutiqueId),
      'detteId': serializer.toJson<String>(detteId),
      'clientId': serializer.toJson<String>(clientId),
      'montant': serializer.toJson<int>(montant),
      'modePaiement': serializer.toJson<String>(modePaiement),
      'note': serializer.toJson<String?>(note),
      'synced': serializer.toJson<bool>(synced),
      'createdAt': serializer.toJson<DateTime>(createdAt),
    };
  }

  CreditStockPaiement copyWith(
          {String? id,
          String? boutiqueId,
          String? detteId,
          String? clientId,
          int? montant,
          String? modePaiement,
          Value<String?> note = const Value.absent(),
          bool? synced,
          DateTime? createdAt}) =>
      CreditStockPaiement(
        id: id ?? this.id,
        boutiqueId: boutiqueId ?? this.boutiqueId,
        detteId: detteId ?? this.detteId,
        clientId: clientId ?? this.clientId,
        montant: montant ?? this.montant,
        modePaiement: modePaiement ?? this.modePaiement,
        note: note.present ? note.value : this.note,
        synced: synced ?? this.synced,
        createdAt: createdAt ?? this.createdAt,
      );
  CreditStockPaiement copyWithCompanion(CreditStockPaiementsCompanion data) {
    return CreditStockPaiement(
      id: data.id.present ? data.id.value : this.id,
      boutiqueId:
          data.boutiqueId.present ? data.boutiqueId.value : this.boutiqueId,
      detteId: data.detteId.present ? data.detteId.value : this.detteId,
      clientId: data.clientId.present ? data.clientId.value : this.clientId,
      montant: data.montant.present ? data.montant.value : this.montant,
      modePaiement: data.modePaiement.present
          ? data.modePaiement.value
          : this.modePaiement,
      note: data.note.present ? data.note.value : this.note,
      synced: data.synced.present ? data.synced.value : this.synced,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('CreditStockPaiement(')
          ..write('id: $id, ')
          ..write('boutiqueId: $boutiqueId, ')
          ..write('detteId: $detteId, ')
          ..write('clientId: $clientId, ')
          ..write('montant: $montant, ')
          ..write('modePaiement: $modePaiement, ')
          ..write('note: $note, ')
          ..write('synced: $synced, ')
          ..write('createdAt: $createdAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(id, boutiqueId, detteId, clientId, montant,
      modePaiement, note, synced, createdAt);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is CreditStockPaiement &&
          other.id == this.id &&
          other.boutiqueId == this.boutiqueId &&
          other.detteId == this.detteId &&
          other.clientId == this.clientId &&
          other.montant == this.montant &&
          other.modePaiement == this.modePaiement &&
          other.note == this.note &&
          other.synced == this.synced &&
          other.createdAt == this.createdAt);
}

class CreditStockPaiementsCompanion
    extends UpdateCompanion<CreditStockPaiement> {
  final Value<String> id;
  final Value<String> boutiqueId;
  final Value<String> detteId;
  final Value<String> clientId;
  final Value<int> montant;
  final Value<String> modePaiement;
  final Value<String?> note;
  final Value<bool> synced;
  final Value<DateTime> createdAt;
  final Value<int> rowid;
  const CreditStockPaiementsCompanion({
    this.id = const Value.absent(),
    this.boutiqueId = const Value.absent(),
    this.detteId = const Value.absent(),
    this.clientId = const Value.absent(),
    this.montant = const Value.absent(),
    this.modePaiement = const Value.absent(),
    this.note = const Value.absent(),
    this.synced = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  CreditStockPaiementsCompanion.insert({
    required String id,
    required String boutiqueId,
    required String detteId,
    required String clientId,
    this.montant = const Value.absent(),
    this.modePaiement = const Value.absent(),
    this.note = const Value.absent(),
    this.synced = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.rowid = const Value.absent(),
  })  : id = Value(id),
        boutiqueId = Value(boutiqueId),
        detteId = Value(detteId),
        clientId = Value(clientId);
  static Insertable<CreditStockPaiement> custom({
    Expression<String>? id,
    Expression<String>? boutiqueId,
    Expression<String>? detteId,
    Expression<String>? clientId,
    Expression<int>? montant,
    Expression<String>? modePaiement,
    Expression<String>? note,
    Expression<bool>? synced,
    Expression<DateTime>? createdAt,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (boutiqueId != null) 'boutique_id': boutiqueId,
      if (detteId != null) 'dette_id': detteId,
      if (clientId != null) 'client_id': clientId,
      if (montant != null) 'montant': montant,
      if (modePaiement != null) 'mode_paiement': modePaiement,
      if (note != null) 'note': note,
      if (synced != null) 'synced': synced,
      if (createdAt != null) 'created_at': createdAt,
      if (rowid != null) 'rowid': rowid,
    });
  }

  CreditStockPaiementsCompanion copyWith(
      {Value<String>? id,
      Value<String>? boutiqueId,
      Value<String>? detteId,
      Value<String>? clientId,
      Value<int>? montant,
      Value<String>? modePaiement,
      Value<String?>? note,
      Value<bool>? synced,
      Value<DateTime>? createdAt,
      Value<int>? rowid}) {
    return CreditStockPaiementsCompanion(
      id: id ?? this.id,
      boutiqueId: boutiqueId ?? this.boutiqueId,
      detteId: detteId ?? this.detteId,
      clientId: clientId ?? this.clientId,
      montant: montant ?? this.montant,
      modePaiement: modePaiement ?? this.modePaiement,
      note: note ?? this.note,
      synced: synced ?? this.synced,
      createdAt: createdAt ?? this.createdAt,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<String>(id.value);
    }
    if (boutiqueId.present) {
      map['boutique_id'] = Variable<String>(boutiqueId.value);
    }
    if (detteId.present) {
      map['dette_id'] = Variable<String>(detteId.value);
    }
    if (clientId.present) {
      map['client_id'] = Variable<String>(clientId.value);
    }
    if (montant.present) {
      map['montant'] = Variable<int>(montant.value);
    }
    if (modePaiement.present) {
      map['mode_paiement'] = Variable<String>(modePaiement.value);
    }
    if (note.present) {
      map['note'] = Variable<String>(note.value);
    }
    if (synced.present) {
      map['synced'] = Variable<bool>(synced.value);
    }
    if (createdAt.present) {
      map['created_at'] = Variable<DateTime>(createdAt.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('CreditStockPaiementsCompanion(')
          ..write('id: $id, ')
          ..write('boutiqueId: $boutiqueId, ')
          ..write('detteId: $detteId, ')
          ..write('clientId: $clientId, ')
          ..write('montant: $montant, ')
          ..write('modePaiement: $modePaiement, ')
          ..write('note: $note, ')
          ..write('synced: $synced, ')
          ..write('createdAt: $createdAt, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $CreditStockSyncQueueTable extends CreditStockSyncQueue
    with TableInfo<$CreditStockSyncQueueTable, CreditStockSyncQueueData> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $CreditStockSyncQueueTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<String> id = GeneratedColumn<String>(
      'id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _boutiqueIdMeta =
      const VerificationMeta('boutiqueId');
  @override
  late final GeneratedColumn<String> boutiqueId = GeneratedColumn<String>(
      'boutique_id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _tableName_Meta =
      const VerificationMeta('tableName_');
  @override
  late final GeneratedColumn<String> tableName_ = GeneratedColumn<String>(
      'table_name', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _operationMeta =
      const VerificationMeta('operation');
  @override
  late final GeneratedColumn<String> operation = GeneratedColumn<String>(
      'operation', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _recordIdMeta =
      const VerificationMeta('recordId');
  @override
  late final GeneratedColumn<String> recordId = GeneratedColumn<String>(
      'record_id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _payloadMeta =
      const VerificationMeta('payload');
  @override
  late final GeneratedColumn<String> payload = GeneratedColumn<String>(
      'payload', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _statutMeta = const VerificationMeta('statut');
  @override
  late final GeneratedColumn<String> statut = GeneratedColumn<String>(
      'statut', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: false,
      defaultValue: const Constant('pending'));
  static const VerificationMeta _tentativesMeta =
      const VerificationMeta('tentatives');
  @override
  late final GeneratedColumn<int> tentatives = GeneratedColumn<int>(
      'tentatives', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  static const VerificationMeta _errorMsgMeta =
      const VerificationMeta('errorMsg');
  @override
  late final GeneratedColumn<String> errorMsg = GeneratedColumn<String>(
      'error_msg', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _createdAtMeta =
      const VerificationMeta('createdAt');
  @override
  late final GeneratedColumn<DateTime> createdAt = GeneratedColumn<DateTime>(
      'created_at', aliasedName, false,
      type: DriftSqlType.dateTime,
      requiredDuringInsert: false,
      defaultValue: currentDateAndTime);
  static const VerificationMeta _syncedAtMeta =
      const VerificationMeta('syncedAt');
  @override
  late final GeneratedColumn<DateTime> syncedAt = GeneratedColumn<DateTime>(
      'synced_at', aliasedName, true,
      type: DriftSqlType.dateTime, requiredDuringInsert: false);
  @override
  List<GeneratedColumn> get $columns => [
        id,
        boutiqueId,
        tableName_,
        operation,
        recordId,
        payload,
        statut,
        tentatives,
        errorMsg,
        createdAt,
        syncedAt
      ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'credistock_sync_queue';
  @override
  VerificationContext validateIntegrity(
      Insertable<CreditStockSyncQueueData> instance,
      {bool isInserting = false}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    } else if (isInserting) {
      context.missing(_idMeta);
    }
    if (data.containsKey('boutique_id')) {
      context.handle(
          _boutiqueIdMeta,
          boutiqueId.isAcceptableOrUnknown(
              data['boutique_id']!, _boutiqueIdMeta));
    } else if (isInserting) {
      context.missing(_boutiqueIdMeta);
    }
    if (data.containsKey('table_name')) {
      context.handle(
          _tableName_Meta,
          tableName_.isAcceptableOrUnknown(
              data['table_name']!, _tableName_Meta));
    } else if (isInserting) {
      context.missing(_tableName_Meta);
    }
    if (data.containsKey('operation')) {
      context.handle(_operationMeta,
          operation.isAcceptableOrUnknown(data['operation']!, _operationMeta));
    } else if (isInserting) {
      context.missing(_operationMeta);
    }
    if (data.containsKey('record_id')) {
      context.handle(_recordIdMeta,
          recordId.isAcceptableOrUnknown(data['record_id']!, _recordIdMeta));
    } else if (isInserting) {
      context.missing(_recordIdMeta);
    }
    if (data.containsKey('payload')) {
      context.handle(_payloadMeta,
          payload.isAcceptableOrUnknown(data['payload']!, _payloadMeta));
    } else if (isInserting) {
      context.missing(_payloadMeta);
    }
    if (data.containsKey('statut')) {
      context.handle(_statutMeta,
          statut.isAcceptableOrUnknown(data['statut']!, _statutMeta));
    }
    if (data.containsKey('tentatives')) {
      context.handle(
          _tentativesMeta,
          tentatives.isAcceptableOrUnknown(
              data['tentatives']!, _tentativesMeta));
    }
    if (data.containsKey('error_msg')) {
      context.handle(_errorMsgMeta,
          errorMsg.isAcceptableOrUnknown(data['error_msg']!, _errorMsgMeta));
    }
    if (data.containsKey('created_at')) {
      context.handle(_createdAtMeta,
          createdAt.isAcceptableOrUnknown(data['created_at']!, _createdAtMeta));
    }
    if (data.containsKey('synced_at')) {
      context.handle(_syncedAtMeta,
          syncedAt.isAcceptableOrUnknown(data['synced_at']!, _syncedAtMeta));
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  CreditStockSyncQueueData map(Map<String, dynamic> data,
      {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return CreditStockSyncQueueData(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}id'])!,
      boutiqueId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}boutique_id'])!,
      tableName_: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}table_name'])!,
      operation: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}operation'])!,
      recordId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}record_id'])!,
      payload: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}payload'])!,
      statut: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}statut'])!,
      tentatives: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}tentatives'])!,
      errorMsg: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}error_msg']),
      createdAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}created_at'])!,
      syncedAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}synced_at']),
    );
  }

  @override
  $CreditStockSyncQueueTable createAlias(String alias) {
    return $CreditStockSyncQueueTable(attachedDatabase, alias);
  }
}

class CreditStockSyncQueueData extends DataClass
    implements Insertable<CreditStockSyncQueueData> {
  final String id;
  final String boutiqueId;
  final String tableName_;
  final String operation;
  final String recordId;
  final String payload;
  final String statut;
  final int tentatives;
  final String? errorMsg;
  final DateTime createdAt;
  final DateTime? syncedAt;
  const CreditStockSyncQueueData(
      {required this.id,
      required this.boutiqueId,
      required this.tableName_,
      required this.operation,
      required this.recordId,
      required this.payload,
      required this.statut,
      required this.tentatives,
      this.errorMsg,
      required this.createdAt,
      this.syncedAt});
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<String>(id);
    map['boutique_id'] = Variable<String>(boutiqueId);
    map['table_name'] = Variable<String>(tableName_);
    map['operation'] = Variable<String>(operation);
    map['record_id'] = Variable<String>(recordId);
    map['payload'] = Variable<String>(payload);
    map['statut'] = Variable<String>(statut);
    map['tentatives'] = Variable<int>(tentatives);
    if (!nullToAbsent || errorMsg != null) {
      map['error_msg'] = Variable<String>(errorMsg);
    }
    map['created_at'] = Variable<DateTime>(createdAt);
    if (!nullToAbsent || syncedAt != null) {
      map['synced_at'] = Variable<DateTime>(syncedAt);
    }
    return map;
  }

  CreditStockSyncQueueCompanion toCompanion(bool nullToAbsent) {
    return CreditStockSyncQueueCompanion(
      id: Value(id),
      boutiqueId: Value(boutiqueId),
      tableName_: Value(tableName_),
      operation: Value(operation),
      recordId: Value(recordId),
      payload: Value(payload),
      statut: Value(statut),
      tentatives: Value(tentatives),
      errorMsg: errorMsg == null && nullToAbsent
          ? const Value.absent()
          : Value(errorMsg),
      createdAt: Value(createdAt),
      syncedAt: syncedAt == null && nullToAbsent
          ? const Value.absent()
          : Value(syncedAt),
    );
  }

  factory CreditStockSyncQueueData.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return CreditStockSyncQueueData(
      id: serializer.fromJson<String>(json['id']),
      boutiqueId: serializer.fromJson<String>(json['boutiqueId']),
      tableName_: serializer.fromJson<String>(json['tableName_']),
      operation: serializer.fromJson<String>(json['operation']),
      recordId: serializer.fromJson<String>(json['recordId']),
      payload: serializer.fromJson<String>(json['payload']),
      statut: serializer.fromJson<String>(json['statut']),
      tentatives: serializer.fromJson<int>(json['tentatives']),
      errorMsg: serializer.fromJson<String?>(json['errorMsg']),
      createdAt: serializer.fromJson<DateTime>(json['createdAt']),
      syncedAt: serializer.fromJson<DateTime?>(json['syncedAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<String>(id),
      'boutiqueId': serializer.toJson<String>(boutiqueId),
      'tableName_': serializer.toJson<String>(tableName_),
      'operation': serializer.toJson<String>(operation),
      'recordId': serializer.toJson<String>(recordId),
      'payload': serializer.toJson<String>(payload),
      'statut': serializer.toJson<String>(statut),
      'tentatives': serializer.toJson<int>(tentatives),
      'errorMsg': serializer.toJson<String?>(errorMsg),
      'createdAt': serializer.toJson<DateTime>(createdAt),
      'syncedAt': serializer.toJson<DateTime?>(syncedAt),
    };
  }

  CreditStockSyncQueueData copyWith(
          {String? id,
          String? boutiqueId,
          String? tableName_,
          String? operation,
          String? recordId,
          String? payload,
          String? statut,
          int? tentatives,
          Value<String?> errorMsg = const Value.absent(),
          DateTime? createdAt,
          Value<DateTime?> syncedAt = const Value.absent()}) =>
      CreditStockSyncQueueData(
        id: id ?? this.id,
        boutiqueId: boutiqueId ?? this.boutiqueId,
        tableName_: tableName_ ?? this.tableName_,
        operation: operation ?? this.operation,
        recordId: recordId ?? this.recordId,
        payload: payload ?? this.payload,
        statut: statut ?? this.statut,
        tentatives: tentatives ?? this.tentatives,
        errorMsg: errorMsg.present ? errorMsg.value : this.errorMsg,
        createdAt: createdAt ?? this.createdAt,
        syncedAt: syncedAt.present ? syncedAt.value : this.syncedAt,
      );
  CreditStockSyncQueueData copyWithCompanion(
      CreditStockSyncQueueCompanion data) {
    return CreditStockSyncQueueData(
      id: data.id.present ? data.id.value : this.id,
      boutiqueId:
          data.boutiqueId.present ? data.boutiqueId.value : this.boutiqueId,
      tableName_:
          data.tableName_.present ? data.tableName_.value : this.tableName_,
      operation: data.operation.present ? data.operation.value : this.operation,
      recordId: data.recordId.present ? data.recordId.value : this.recordId,
      payload: data.payload.present ? data.payload.value : this.payload,
      statut: data.statut.present ? data.statut.value : this.statut,
      tentatives:
          data.tentatives.present ? data.tentatives.value : this.tentatives,
      errorMsg: data.errorMsg.present ? data.errorMsg.value : this.errorMsg,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
      syncedAt: data.syncedAt.present ? data.syncedAt.value : this.syncedAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('CreditStockSyncQueueData(')
          ..write('id: $id, ')
          ..write('boutiqueId: $boutiqueId, ')
          ..write('tableName_: $tableName_, ')
          ..write('operation: $operation, ')
          ..write('recordId: $recordId, ')
          ..write('payload: $payload, ')
          ..write('statut: $statut, ')
          ..write('tentatives: $tentatives, ')
          ..write('errorMsg: $errorMsg, ')
          ..write('createdAt: $createdAt, ')
          ..write('syncedAt: $syncedAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(id, boutiqueId, tableName_, operation,
      recordId, payload, statut, tentatives, errorMsg, createdAt, syncedAt);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is CreditStockSyncQueueData &&
          other.id == this.id &&
          other.boutiqueId == this.boutiqueId &&
          other.tableName_ == this.tableName_ &&
          other.operation == this.operation &&
          other.recordId == this.recordId &&
          other.payload == this.payload &&
          other.statut == this.statut &&
          other.tentatives == this.tentatives &&
          other.errorMsg == this.errorMsg &&
          other.createdAt == this.createdAt &&
          other.syncedAt == this.syncedAt);
}

class CreditStockSyncQueueCompanion
    extends UpdateCompanion<CreditStockSyncQueueData> {
  final Value<String> id;
  final Value<String> boutiqueId;
  final Value<String> tableName_;
  final Value<String> operation;
  final Value<String> recordId;
  final Value<String> payload;
  final Value<String> statut;
  final Value<int> tentatives;
  final Value<String?> errorMsg;
  final Value<DateTime> createdAt;
  final Value<DateTime?> syncedAt;
  final Value<int> rowid;
  const CreditStockSyncQueueCompanion({
    this.id = const Value.absent(),
    this.boutiqueId = const Value.absent(),
    this.tableName_ = const Value.absent(),
    this.operation = const Value.absent(),
    this.recordId = const Value.absent(),
    this.payload = const Value.absent(),
    this.statut = const Value.absent(),
    this.tentatives = const Value.absent(),
    this.errorMsg = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.syncedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  CreditStockSyncQueueCompanion.insert({
    required String id,
    required String boutiqueId,
    required String tableName_,
    required String operation,
    required String recordId,
    required String payload,
    this.statut = const Value.absent(),
    this.tentatives = const Value.absent(),
    this.errorMsg = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.syncedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  })  : id = Value(id),
        boutiqueId = Value(boutiqueId),
        tableName_ = Value(tableName_),
        operation = Value(operation),
        recordId = Value(recordId),
        payload = Value(payload);
  static Insertable<CreditStockSyncQueueData> custom({
    Expression<String>? id,
    Expression<String>? boutiqueId,
    Expression<String>? tableName_,
    Expression<String>? operation,
    Expression<String>? recordId,
    Expression<String>? payload,
    Expression<String>? statut,
    Expression<int>? tentatives,
    Expression<String>? errorMsg,
    Expression<DateTime>? createdAt,
    Expression<DateTime>? syncedAt,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (boutiqueId != null) 'boutique_id': boutiqueId,
      if (tableName_ != null) 'table_name': tableName_,
      if (operation != null) 'operation': operation,
      if (recordId != null) 'record_id': recordId,
      if (payload != null) 'payload': payload,
      if (statut != null) 'statut': statut,
      if (tentatives != null) 'tentatives': tentatives,
      if (errorMsg != null) 'error_msg': errorMsg,
      if (createdAt != null) 'created_at': createdAt,
      if (syncedAt != null) 'synced_at': syncedAt,
      if (rowid != null) 'rowid': rowid,
    });
  }

  CreditStockSyncQueueCompanion copyWith(
      {Value<String>? id,
      Value<String>? boutiqueId,
      Value<String>? tableName_,
      Value<String>? operation,
      Value<String>? recordId,
      Value<String>? payload,
      Value<String>? statut,
      Value<int>? tentatives,
      Value<String?>? errorMsg,
      Value<DateTime>? createdAt,
      Value<DateTime?>? syncedAt,
      Value<int>? rowid}) {
    return CreditStockSyncQueueCompanion(
      id: id ?? this.id,
      boutiqueId: boutiqueId ?? this.boutiqueId,
      tableName_: tableName_ ?? this.tableName_,
      operation: operation ?? this.operation,
      recordId: recordId ?? this.recordId,
      payload: payload ?? this.payload,
      statut: statut ?? this.statut,
      tentatives: tentatives ?? this.tentatives,
      errorMsg: errorMsg ?? this.errorMsg,
      createdAt: createdAt ?? this.createdAt,
      syncedAt: syncedAt ?? this.syncedAt,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<String>(id.value);
    }
    if (boutiqueId.present) {
      map['boutique_id'] = Variable<String>(boutiqueId.value);
    }
    if (tableName_.present) {
      map['table_name'] = Variable<String>(tableName_.value);
    }
    if (operation.present) {
      map['operation'] = Variable<String>(operation.value);
    }
    if (recordId.present) {
      map['record_id'] = Variable<String>(recordId.value);
    }
    if (payload.present) {
      map['payload'] = Variable<String>(payload.value);
    }
    if (statut.present) {
      map['statut'] = Variable<String>(statut.value);
    }
    if (tentatives.present) {
      map['tentatives'] = Variable<int>(tentatives.value);
    }
    if (errorMsg.present) {
      map['error_msg'] = Variable<String>(errorMsg.value);
    }
    if (createdAt.present) {
      map['created_at'] = Variable<DateTime>(createdAt.value);
    }
    if (syncedAt.present) {
      map['synced_at'] = Variable<DateTime>(syncedAt.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('CreditStockSyncQueueCompanion(')
          ..write('id: $id, ')
          ..write('boutiqueId: $boutiqueId, ')
          ..write('tableName_: $tableName_, ')
          ..write('operation: $operation, ')
          ..write('recordId: $recordId, ')
          ..write('payload: $payload, ')
          ..write('statut: $statut, ')
          ..write('tentatives: $tentatives, ')
          ..write('errorMsg: $errorMsg, ')
          ..write('createdAt: $createdAt, ')
          ..write('syncedAt: $syncedAt, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $CreditStockAlertesTable extends CreditStockAlertes
    with TableInfo<$CreditStockAlertesTable, CreditStockAlerte> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $CreditStockAlertesTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<String> id = GeneratedColumn<String>(
      'id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _boutiqueIdMeta =
      const VerificationMeta('boutiqueId');
  @override
  late final GeneratedColumn<String> boutiqueId = GeneratedColumn<String>(
      'boutique_id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _typeAlerteMeta =
      const VerificationMeta('typeAlerte');
  @override
  late final GeneratedColumn<String> typeAlerte = GeneratedColumn<String>(
      'type_alerte', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _referenceIdMeta =
      const VerificationMeta('referenceId');
  @override
  late final GeneratedColumn<String> referenceId = GeneratedColumn<String>(
      'reference_id', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _titreMeta = const VerificationMeta('titre');
  @override
  late final GeneratedColumn<String> titre = GeneratedColumn<String>(
      'titre', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _messageMeta =
      const VerificationMeta('message');
  @override
  late final GeneratedColumn<String> message = GeneratedColumn<String>(
      'message', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _luMeta = const VerificationMeta('lu');
  @override
  late final GeneratedColumn<bool> lu = GeneratedColumn<bool>(
      'lu', aliasedName, false,
      type: DriftSqlType.bool,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('CHECK ("lu" IN (0, 1))'),
      defaultValue: const Constant(false));
  static const VerificationMeta _createdAtMeta =
      const VerificationMeta('createdAt');
  @override
  late final GeneratedColumn<DateTime> createdAt = GeneratedColumn<DateTime>(
      'created_at', aliasedName, false,
      type: DriftSqlType.dateTime,
      requiredDuringInsert: false,
      defaultValue: currentDateAndTime);
  @override
  List<GeneratedColumn> get $columns =>
      [id, boutiqueId, typeAlerte, referenceId, titre, message, lu, createdAt];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'credistock_alertes';
  @override
  VerificationContext validateIntegrity(Insertable<CreditStockAlerte> instance,
      {bool isInserting = false}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    } else if (isInserting) {
      context.missing(_idMeta);
    }
    if (data.containsKey('boutique_id')) {
      context.handle(
          _boutiqueIdMeta,
          boutiqueId.isAcceptableOrUnknown(
              data['boutique_id']!, _boutiqueIdMeta));
    } else if (isInserting) {
      context.missing(_boutiqueIdMeta);
    }
    if (data.containsKey('type_alerte')) {
      context.handle(
          _typeAlerteMeta,
          typeAlerte.isAcceptableOrUnknown(
              data['type_alerte']!, _typeAlerteMeta));
    } else if (isInserting) {
      context.missing(_typeAlerteMeta);
    }
    if (data.containsKey('reference_id')) {
      context.handle(
          _referenceIdMeta,
          referenceId.isAcceptableOrUnknown(
              data['reference_id']!, _referenceIdMeta));
    }
    if (data.containsKey('titre')) {
      context.handle(
          _titreMeta, titre.isAcceptableOrUnknown(data['titre']!, _titreMeta));
    } else if (isInserting) {
      context.missing(_titreMeta);
    }
    if (data.containsKey('message')) {
      context.handle(_messageMeta,
          message.isAcceptableOrUnknown(data['message']!, _messageMeta));
    }
    if (data.containsKey('lu')) {
      context.handle(_luMeta, lu.isAcceptableOrUnknown(data['lu']!, _luMeta));
    }
    if (data.containsKey('created_at')) {
      context.handle(_createdAtMeta,
          createdAt.isAcceptableOrUnknown(data['created_at']!, _createdAtMeta));
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  CreditStockAlerte map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return CreditStockAlerte(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}id'])!,
      boutiqueId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}boutique_id'])!,
      typeAlerte: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}type_alerte'])!,
      referenceId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}reference_id']),
      titre: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}titre'])!,
      message: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}message']),
      lu: attachedDatabase.typeMapping
          .read(DriftSqlType.bool, data['${effectivePrefix}lu'])!,
      createdAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}created_at'])!,
    );
  }

  @override
  $CreditStockAlertesTable createAlias(String alias) {
    return $CreditStockAlertesTable(attachedDatabase, alias);
  }
}

class CreditStockAlerte extends DataClass
    implements Insertable<CreditStockAlerte> {
  final String id;
  final String boutiqueId;
  final String typeAlerte;
  final String? referenceId;
  final String titre;
  final String? message;
  final bool lu;
  final DateTime createdAt;
  const CreditStockAlerte(
      {required this.id,
      required this.boutiqueId,
      required this.typeAlerte,
      this.referenceId,
      required this.titre,
      this.message,
      required this.lu,
      required this.createdAt});
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<String>(id);
    map['boutique_id'] = Variable<String>(boutiqueId);
    map['type_alerte'] = Variable<String>(typeAlerte);
    if (!nullToAbsent || referenceId != null) {
      map['reference_id'] = Variable<String>(referenceId);
    }
    map['titre'] = Variable<String>(titre);
    if (!nullToAbsent || message != null) {
      map['message'] = Variable<String>(message);
    }
    map['lu'] = Variable<bool>(lu);
    map['created_at'] = Variable<DateTime>(createdAt);
    return map;
  }

  CreditStockAlertesCompanion toCompanion(bool nullToAbsent) {
    return CreditStockAlertesCompanion(
      id: Value(id),
      boutiqueId: Value(boutiqueId),
      typeAlerte: Value(typeAlerte),
      referenceId: referenceId == null && nullToAbsent
          ? const Value.absent()
          : Value(referenceId),
      titre: Value(titre),
      message: message == null && nullToAbsent
          ? const Value.absent()
          : Value(message),
      lu: Value(lu),
      createdAt: Value(createdAt),
    );
  }

  factory CreditStockAlerte.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return CreditStockAlerte(
      id: serializer.fromJson<String>(json['id']),
      boutiqueId: serializer.fromJson<String>(json['boutiqueId']),
      typeAlerte: serializer.fromJson<String>(json['typeAlerte']),
      referenceId: serializer.fromJson<String?>(json['referenceId']),
      titre: serializer.fromJson<String>(json['titre']),
      message: serializer.fromJson<String?>(json['message']),
      lu: serializer.fromJson<bool>(json['lu']),
      createdAt: serializer.fromJson<DateTime>(json['createdAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<String>(id),
      'boutiqueId': serializer.toJson<String>(boutiqueId),
      'typeAlerte': serializer.toJson<String>(typeAlerte),
      'referenceId': serializer.toJson<String?>(referenceId),
      'titre': serializer.toJson<String>(titre),
      'message': serializer.toJson<String?>(message),
      'lu': serializer.toJson<bool>(lu),
      'createdAt': serializer.toJson<DateTime>(createdAt),
    };
  }

  CreditStockAlerte copyWith(
          {String? id,
          String? boutiqueId,
          String? typeAlerte,
          Value<String?> referenceId = const Value.absent(),
          String? titre,
          Value<String?> message = const Value.absent(),
          bool? lu,
          DateTime? createdAt}) =>
      CreditStockAlerte(
        id: id ?? this.id,
        boutiqueId: boutiqueId ?? this.boutiqueId,
        typeAlerte: typeAlerte ?? this.typeAlerte,
        referenceId: referenceId.present ? referenceId.value : this.referenceId,
        titre: titre ?? this.titre,
        message: message.present ? message.value : this.message,
        lu: lu ?? this.lu,
        createdAt: createdAt ?? this.createdAt,
      );
  CreditStockAlerte copyWithCompanion(CreditStockAlertesCompanion data) {
    return CreditStockAlerte(
      id: data.id.present ? data.id.value : this.id,
      boutiqueId:
          data.boutiqueId.present ? data.boutiqueId.value : this.boutiqueId,
      typeAlerte:
          data.typeAlerte.present ? data.typeAlerte.value : this.typeAlerte,
      referenceId:
          data.referenceId.present ? data.referenceId.value : this.referenceId,
      titre: data.titre.present ? data.titre.value : this.titre,
      message: data.message.present ? data.message.value : this.message,
      lu: data.lu.present ? data.lu.value : this.lu,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('CreditStockAlerte(')
          ..write('id: $id, ')
          ..write('boutiqueId: $boutiqueId, ')
          ..write('typeAlerte: $typeAlerte, ')
          ..write('referenceId: $referenceId, ')
          ..write('titre: $titre, ')
          ..write('message: $message, ')
          ..write('lu: $lu, ')
          ..write('createdAt: $createdAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
      id, boutiqueId, typeAlerte, referenceId, titre, message, lu, createdAt);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is CreditStockAlerte &&
          other.id == this.id &&
          other.boutiqueId == this.boutiqueId &&
          other.typeAlerte == this.typeAlerte &&
          other.referenceId == this.referenceId &&
          other.titre == this.titre &&
          other.message == this.message &&
          other.lu == this.lu &&
          other.createdAt == this.createdAt);
}

class CreditStockAlertesCompanion extends UpdateCompanion<CreditStockAlerte> {
  final Value<String> id;
  final Value<String> boutiqueId;
  final Value<String> typeAlerte;
  final Value<String?> referenceId;
  final Value<String> titre;
  final Value<String?> message;
  final Value<bool> lu;
  final Value<DateTime> createdAt;
  final Value<int> rowid;
  const CreditStockAlertesCompanion({
    this.id = const Value.absent(),
    this.boutiqueId = const Value.absent(),
    this.typeAlerte = const Value.absent(),
    this.referenceId = const Value.absent(),
    this.titre = const Value.absent(),
    this.message = const Value.absent(),
    this.lu = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  CreditStockAlertesCompanion.insert({
    required String id,
    required String boutiqueId,
    required String typeAlerte,
    this.referenceId = const Value.absent(),
    required String titre,
    this.message = const Value.absent(),
    this.lu = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.rowid = const Value.absent(),
  })  : id = Value(id),
        boutiqueId = Value(boutiqueId),
        typeAlerte = Value(typeAlerte),
        titre = Value(titre);
  static Insertable<CreditStockAlerte> custom({
    Expression<String>? id,
    Expression<String>? boutiqueId,
    Expression<String>? typeAlerte,
    Expression<String>? referenceId,
    Expression<String>? titre,
    Expression<String>? message,
    Expression<bool>? lu,
    Expression<DateTime>? createdAt,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (boutiqueId != null) 'boutique_id': boutiqueId,
      if (typeAlerte != null) 'type_alerte': typeAlerte,
      if (referenceId != null) 'reference_id': referenceId,
      if (titre != null) 'titre': titre,
      if (message != null) 'message': message,
      if (lu != null) 'lu': lu,
      if (createdAt != null) 'created_at': createdAt,
      if (rowid != null) 'rowid': rowid,
    });
  }

  CreditStockAlertesCompanion copyWith(
      {Value<String>? id,
      Value<String>? boutiqueId,
      Value<String>? typeAlerte,
      Value<String?>? referenceId,
      Value<String>? titre,
      Value<String?>? message,
      Value<bool>? lu,
      Value<DateTime>? createdAt,
      Value<int>? rowid}) {
    return CreditStockAlertesCompanion(
      id: id ?? this.id,
      boutiqueId: boutiqueId ?? this.boutiqueId,
      typeAlerte: typeAlerte ?? this.typeAlerte,
      referenceId: referenceId ?? this.referenceId,
      titre: titre ?? this.titre,
      message: message ?? this.message,
      lu: lu ?? this.lu,
      createdAt: createdAt ?? this.createdAt,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<String>(id.value);
    }
    if (boutiqueId.present) {
      map['boutique_id'] = Variable<String>(boutiqueId.value);
    }
    if (typeAlerte.present) {
      map['type_alerte'] = Variable<String>(typeAlerte.value);
    }
    if (referenceId.present) {
      map['reference_id'] = Variable<String>(referenceId.value);
    }
    if (titre.present) {
      map['titre'] = Variable<String>(titre.value);
    }
    if (message.present) {
      map['message'] = Variable<String>(message.value);
    }
    if (lu.present) {
      map['lu'] = Variable<bool>(lu.value);
    }
    if (createdAt.present) {
      map['created_at'] = Variable<DateTime>(createdAt.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('CreditStockAlertesCompanion(')
          ..write('id: $id, ')
          ..write('boutiqueId: $boutiqueId, ')
          ..write('typeAlerte: $typeAlerte, ')
          ..write('referenceId: $referenceId, ')
          ..write('titre: $titre, ')
          ..write('message: $message, ')
          ..write('lu: $lu, ')
          ..write('createdAt: $createdAt, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

abstract class _$AppDatabase extends GeneratedDatabase {
  _$AppDatabase(QueryExecutor e) : super(e);
  $AppDatabaseManager get managers => $AppDatabaseManager(this);
  late final $CreditStockBoutiquesTable creditStockBoutiques =
      $CreditStockBoutiquesTable(this);
  late final $CreditStockUtilisateursTable creditStockUtilisateurs =
      $CreditStockUtilisateursTable(this);
  late final $CreditStockProduitsTable creditStockProduits =
      $CreditStockProduitsTable(this);
  late final $CreditStockClientsTable creditStockClients =
      $CreditStockClientsTable(this);
  late final $CreditStockVentesTable creditStockVentes =
      $CreditStockVentesTable(this);
  late final $CreditStockLignesVenteTable creditStockLignesVente =
      $CreditStockLignesVenteTable(this);
  late final $CreditStockDettesTable creditStockDettes =
      $CreditStockDettesTable(this);
  late final $CreditStockPaiementsTable creditStockPaiements =
      $CreditStockPaiementsTable(this);
  late final $CreditStockSyncQueueTable creditStockSyncQueue =
      $CreditStockSyncQueueTable(this);
  late final $CreditStockAlertesTable creditStockAlertes =
      $CreditStockAlertesTable(this);
  @override
  Iterable<TableInfo<Table, Object?>> get allTables =>
      allSchemaEntities.whereType<TableInfo<Table, Object?>>();
  @override
  List<DatabaseSchemaEntity> get allSchemaEntities => [
        creditStockBoutiques,
        creditStockUtilisateurs,
        creditStockProduits,
        creditStockClients,
        creditStockVentes,
        creditStockLignesVente,
        creditStockDettes,
        creditStockPaiements,
        creditStockSyncQueue,
        creditStockAlertes
      ];
}

typedef $$CreditStockBoutiquesTableCreateCompanionBuilder
    = CreditStockBoutiquesCompanion Function({
  required String id,
  required String nom,
  required String telephone,
  Value<String?> adresse,
  Value<String> typeBoutique,
  Value<String?> logoUrl,
  Value<String?> pinHash,
  Value<String> abonnement,
  Value<DateTime?> premiumExpireAt,
  Value<DateTime> createdAt,
  Value<DateTime> updatedAt,
  Value<int> rowid,
});
typedef $$CreditStockBoutiquesTableUpdateCompanionBuilder
    = CreditStockBoutiquesCompanion Function({
  Value<String> id,
  Value<String> nom,
  Value<String> telephone,
  Value<String?> adresse,
  Value<String> typeBoutique,
  Value<String?> logoUrl,
  Value<String?> pinHash,
  Value<String> abonnement,
  Value<DateTime?> premiumExpireAt,
  Value<DateTime> createdAt,
  Value<DateTime> updatedAt,
  Value<int> rowid,
});

final class $$CreditStockBoutiquesTableReferences extends BaseReferences<
    _$AppDatabase, $CreditStockBoutiquesTable, CreditStockBoutique> {
  $$CreditStockBoutiquesTableReferences(
      super.$_db, super.$_table, super.$_typedResult);

  static MultiTypedResultKey<$CreditStockUtilisateursTable,
      List<CreditStockUtilisateur>> _creditStockUtilisateursRefsTable(
          _$AppDatabase db) =>
      MultiTypedResultKey.fromTable(db.creditStockUtilisateurs,
          aliasName: $_aliasNameGenerator(db.creditStockBoutiques.id,
              db.creditStockUtilisateurs.boutiqueId));

  $$CreditStockUtilisateursTableProcessedTableManager
      get creditStockUtilisateursRefs {
    final manager = $$CreditStockUtilisateursTableTableManager(
            $_db, $_db.creditStockUtilisateurs)
        .filter((f) => f.boutiqueId.id.sqlEquals($_itemColumn<String>('id')!));

    final cache =
        $_typedResult.readTableOrNull(_creditStockUtilisateursRefsTable($_db));
    return ProcessedTableManager(
        manager.$state.copyWith(prefetchedData: cache));
  }

  static MultiTypedResultKey<$CreditStockProduitsTable,
      List<CreditStockProduit>> _creditStockProduitsRefsTable(
          _$AppDatabase db) =>
      MultiTypedResultKey.fromTable(db.creditStockProduits,
          aliasName: $_aliasNameGenerator(
              db.creditStockBoutiques.id, db.creditStockProduits.boutiqueId));

  $$CreditStockProduitsTableProcessedTableManager get creditStockProduitsRefs {
    final manager = $$CreditStockProduitsTableTableManager(
            $_db, $_db.creditStockProduits)
        .filter((f) => f.boutiqueId.id.sqlEquals($_itemColumn<String>('id')!));

    final cache =
        $_typedResult.readTableOrNull(_creditStockProduitsRefsTable($_db));
    return ProcessedTableManager(
        manager.$state.copyWith(prefetchedData: cache));
  }

  static MultiTypedResultKey<$CreditStockClientsTable, List<CreditStockClient>>
      _creditStockClientsRefsTable(_$AppDatabase db) =>
          MultiTypedResultKey.fromTable(db.creditStockClients,
              aliasName: $_aliasNameGenerator(db.creditStockBoutiques.id,
                  db.creditStockClients.boutiqueId));

  $$CreditStockClientsTableProcessedTableManager get creditStockClientsRefs {
    final manager = $$CreditStockClientsTableTableManager(
            $_db, $_db.creditStockClients)
        .filter((f) => f.boutiqueId.id.sqlEquals($_itemColumn<String>('id')!));

    final cache =
        $_typedResult.readTableOrNull(_creditStockClientsRefsTable($_db));
    return ProcessedTableManager(
        manager.$state.copyWith(prefetchedData: cache));
  }

  static MultiTypedResultKey<$CreditStockVentesTable, List<CreditStockVente>>
      _creditStockVentesRefsTable(_$AppDatabase db) =>
          MultiTypedResultKey.fromTable(db.creditStockVentes,
              aliasName: $_aliasNameGenerator(
                  db.creditStockBoutiques.id, db.creditStockVentes.boutiqueId));

  $$CreditStockVentesTableProcessedTableManager get creditStockVentesRefs {
    final manager = $$CreditStockVentesTableTableManager(
            $_db, $_db.creditStockVentes)
        .filter((f) => f.boutiqueId.id.sqlEquals($_itemColumn<String>('id')!));

    final cache =
        $_typedResult.readTableOrNull(_creditStockVentesRefsTable($_db));
    return ProcessedTableManager(
        manager.$state.copyWith(prefetchedData: cache));
  }

  static MultiTypedResultKey<$CreditStockDettesTable, List<CreditStockDette>>
      _creditStockDettesRefsTable(_$AppDatabase db) =>
          MultiTypedResultKey.fromTable(db.creditStockDettes,
              aliasName: $_aliasNameGenerator(
                  db.creditStockBoutiques.id, db.creditStockDettes.boutiqueId));

  $$CreditStockDettesTableProcessedTableManager get creditStockDettesRefs {
    final manager = $$CreditStockDettesTableTableManager(
            $_db, $_db.creditStockDettes)
        .filter((f) => f.boutiqueId.id.sqlEquals($_itemColumn<String>('id')!));

    final cache =
        $_typedResult.readTableOrNull(_creditStockDettesRefsTable($_db));
    return ProcessedTableManager(
        manager.$state.copyWith(prefetchedData: cache));
  }
}

class $$CreditStockBoutiquesTableFilterComposer
    extends Composer<_$AppDatabase, $CreditStockBoutiquesTable> {
  $$CreditStockBoutiquesTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get nom => $composableBuilder(
      column: $table.nom, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get telephone => $composableBuilder(
      column: $table.telephone, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get adresse => $composableBuilder(
      column: $table.adresse, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get typeBoutique => $composableBuilder(
      column: $table.typeBoutique, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get logoUrl => $composableBuilder(
      column: $table.logoUrl, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get pinHash => $composableBuilder(
      column: $table.pinHash, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get abonnement => $composableBuilder(
      column: $table.abonnement, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get premiumExpireAt => $composableBuilder(
      column: $table.premiumExpireAt,
      builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get updatedAt => $composableBuilder(
      column: $table.updatedAt, builder: (column) => ColumnFilters(column));

  Expression<bool> creditStockUtilisateursRefs(
      Expression<bool> Function($$CreditStockUtilisateursTableFilterComposer f)
          f) {
    final $$CreditStockUtilisateursTableFilterComposer composer =
        $composerBuilder(
            composer: this,
            getCurrentColumn: (t) => t.id,
            referencedTable: $db.creditStockUtilisateurs,
            getReferencedColumn: (t) => t.boutiqueId,
            builder: (joinBuilder,
                    {$addJoinBuilderToRootComposer,
                    $removeJoinBuilderFromRootComposer}) =>
                $$CreditStockUtilisateursTableFilterComposer(
                  $db: $db,
                  $table: $db.creditStockUtilisateurs,
                  $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
                  joinBuilder: joinBuilder,
                  $removeJoinBuilderFromRootComposer:
                      $removeJoinBuilderFromRootComposer,
                ));
    return f(composer);
  }

  Expression<bool> creditStockProduitsRefs(
      Expression<bool> Function($$CreditStockProduitsTableFilterComposer f) f) {
    final $$CreditStockProduitsTableFilterComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.id,
        referencedTable: $db.creditStockProduits,
        getReferencedColumn: (t) => t.boutiqueId,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$CreditStockProduitsTableFilterComposer(
              $db: $db,
              $table: $db.creditStockProduits,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return f(composer);
  }

  Expression<bool> creditStockClientsRefs(
      Expression<bool> Function($$CreditStockClientsTableFilterComposer f) f) {
    final $$CreditStockClientsTableFilterComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.id,
        referencedTable: $db.creditStockClients,
        getReferencedColumn: (t) => t.boutiqueId,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$CreditStockClientsTableFilterComposer(
              $db: $db,
              $table: $db.creditStockClients,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return f(composer);
  }

  Expression<bool> creditStockVentesRefs(
      Expression<bool> Function($$CreditStockVentesTableFilterComposer f) f) {
    final $$CreditStockVentesTableFilterComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.id,
        referencedTable: $db.creditStockVentes,
        getReferencedColumn: (t) => t.boutiqueId,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$CreditStockVentesTableFilterComposer(
              $db: $db,
              $table: $db.creditStockVentes,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return f(composer);
  }

  Expression<bool> creditStockDettesRefs(
      Expression<bool> Function($$CreditStockDettesTableFilterComposer f) f) {
    final $$CreditStockDettesTableFilterComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.id,
        referencedTable: $db.creditStockDettes,
        getReferencedColumn: (t) => t.boutiqueId,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$CreditStockDettesTableFilterComposer(
              $db: $db,
              $table: $db.creditStockDettes,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return f(composer);
  }
}

class $$CreditStockBoutiquesTableOrderingComposer
    extends Composer<_$AppDatabase, $CreditStockBoutiquesTable> {
  $$CreditStockBoutiquesTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get nom => $composableBuilder(
      column: $table.nom, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get telephone => $composableBuilder(
      column: $table.telephone, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get adresse => $composableBuilder(
      column: $table.adresse, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get typeBoutique => $composableBuilder(
      column: $table.typeBoutique,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get logoUrl => $composableBuilder(
      column: $table.logoUrl, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get pinHash => $composableBuilder(
      column: $table.pinHash, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get abonnement => $composableBuilder(
      column: $table.abonnement, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get premiumExpireAt => $composableBuilder(
      column: $table.premiumExpireAt,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get updatedAt => $composableBuilder(
      column: $table.updatedAt, builder: (column) => ColumnOrderings(column));
}

class $$CreditStockBoutiquesTableAnnotationComposer
    extends Composer<_$AppDatabase, $CreditStockBoutiquesTable> {
  $$CreditStockBoutiquesTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get nom =>
      $composableBuilder(column: $table.nom, builder: (column) => column);

  GeneratedColumn<String> get telephone =>
      $composableBuilder(column: $table.telephone, builder: (column) => column);

  GeneratedColumn<String> get adresse =>
      $composableBuilder(column: $table.adresse, builder: (column) => column);

  GeneratedColumn<String> get typeBoutique => $composableBuilder(
      column: $table.typeBoutique, builder: (column) => column);

  GeneratedColumn<String> get logoUrl =>
      $composableBuilder(column: $table.logoUrl, builder: (column) => column);

  GeneratedColumn<String> get pinHash =>
      $composableBuilder(column: $table.pinHash, builder: (column) => column);

  GeneratedColumn<String> get abonnement => $composableBuilder(
      column: $table.abonnement, builder: (column) => column);

  GeneratedColumn<DateTime> get premiumExpireAt => $composableBuilder(
      column: $table.premiumExpireAt, builder: (column) => column);

  GeneratedColumn<DateTime> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);

  GeneratedColumn<DateTime> get updatedAt =>
      $composableBuilder(column: $table.updatedAt, builder: (column) => column);

  Expression<T> creditStockUtilisateursRefs<T extends Object>(
      Expression<T> Function($$CreditStockUtilisateursTableAnnotationComposer a)
          f) {
    final $$CreditStockUtilisateursTableAnnotationComposer composer =
        $composerBuilder(
            composer: this,
            getCurrentColumn: (t) => t.id,
            referencedTable: $db.creditStockUtilisateurs,
            getReferencedColumn: (t) => t.boutiqueId,
            builder: (joinBuilder,
                    {$addJoinBuilderToRootComposer,
                    $removeJoinBuilderFromRootComposer}) =>
                $$CreditStockUtilisateursTableAnnotationComposer(
                  $db: $db,
                  $table: $db.creditStockUtilisateurs,
                  $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
                  joinBuilder: joinBuilder,
                  $removeJoinBuilderFromRootComposer:
                      $removeJoinBuilderFromRootComposer,
                ));
    return f(composer);
  }

  Expression<T> creditStockProduitsRefs<T extends Object>(
      Expression<T> Function($$CreditStockProduitsTableAnnotationComposer a)
          f) {
    final $$CreditStockProduitsTableAnnotationComposer composer =
        $composerBuilder(
            composer: this,
            getCurrentColumn: (t) => t.id,
            referencedTable: $db.creditStockProduits,
            getReferencedColumn: (t) => t.boutiqueId,
            builder: (joinBuilder,
                    {$addJoinBuilderToRootComposer,
                    $removeJoinBuilderFromRootComposer}) =>
                $$CreditStockProduitsTableAnnotationComposer(
                  $db: $db,
                  $table: $db.creditStockProduits,
                  $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
                  joinBuilder: joinBuilder,
                  $removeJoinBuilderFromRootComposer:
                      $removeJoinBuilderFromRootComposer,
                ));
    return f(composer);
  }

  Expression<T> creditStockClientsRefs<T extends Object>(
      Expression<T> Function($$CreditStockClientsTableAnnotationComposer a) f) {
    final $$CreditStockClientsTableAnnotationComposer composer =
        $composerBuilder(
            composer: this,
            getCurrentColumn: (t) => t.id,
            referencedTable: $db.creditStockClients,
            getReferencedColumn: (t) => t.boutiqueId,
            builder: (joinBuilder,
                    {$addJoinBuilderToRootComposer,
                    $removeJoinBuilderFromRootComposer}) =>
                $$CreditStockClientsTableAnnotationComposer(
                  $db: $db,
                  $table: $db.creditStockClients,
                  $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
                  joinBuilder: joinBuilder,
                  $removeJoinBuilderFromRootComposer:
                      $removeJoinBuilderFromRootComposer,
                ));
    return f(composer);
  }

  Expression<T> creditStockVentesRefs<T extends Object>(
      Expression<T> Function($$CreditStockVentesTableAnnotationComposer a) f) {
    final $$CreditStockVentesTableAnnotationComposer composer =
        $composerBuilder(
            composer: this,
            getCurrentColumn: (t) => t.id,
            referencedTable: $db.creditStockVentes,
            getReferencedColumn: (t) => t.boutiqueId,
            builder: (joinBuilder,
                    {$addJoinBuilderToRootComposer,
                    $removeJoinBuilderFromRootComposer}) =>
                $$CreditStockVentesTableAnnotationComposer(
                  $db: $db,
                  $table: $db.creditStockVentes,
                  $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
                  joinBuilder: joinBuilder,
                  $removeJoinBuilderFromRootComposer:
                      $removeJoinBuilderFromRootComposer,
                ));
    return f(composer);
  }

  Expression<T> creditStockDettesRefs<T extends Object>(
      Expression<T> Function($$CreditStockDettesTableAnnotationComposer a) f) {
    final $$CreditStockDettesTableAnnotationComposer composer =
        $composerBuilder(
            composer: this,
            getCurrentColumn: (t) => t.id,
            referencedTable: $db.creditStockDettes,
            getReferencedColumn: (t) => t.boutiqueId,
            builder: (joinBuilder,
                    {$addJoinBuilderToRootComposer,
                    $removeJoinBuilderFromRootComposer}) =>
                $$CreditStockDettesTableAnnotationComposer(
                  $db: $db,
                  $table: $db.creditStockDettes,
                  $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
                  joinBuilder: joinBuilder,
                  $removeJoinBuilderFromRootComposer:
                      $removeJoinBuilderFromRootComposer,
                ));
    return f(composer);
  }
}

class $$CreditStockBoutiquesTableTableManager extends RootTableManager<
    _$AppDatabase,
    $CreditStockBoutiquesTable,
    CreditStockBoutique,
    $$CreditStockBoutiquesTableFilterComposer,
    $$CreditStockBoutiquesTableOrderingComposer,
    $$CreditStockBoutiquesTableAnnotationComposer,
    $$CreditStockBoutiquesTableCreateCompanionBuilder,
    $$CreditStockBoutiquesTableUpdateCompanionBuilder,
    (CreditStockBoutique, $$CreditStockBoutiquesTableReferences),
    CreditStockBoutique,
    PrefetchHooks Function(
        {bool creditStockUtilisateursRefs,
        bool creditStockProduitsRefs,
        bool creditStockClientsRefs,
        bool creditStockVentesRefs,
        bool creditStockDettesRefs})> {
  $$CreditStockBoutiquesTableTableManager(
      _$AppDatabase db, $CreditStockBoutiquesTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$CreditStockBoutiquesTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$CreditStockBoutiquesTableOrderingComposer(
                  $db: db, $table: table),
          createComputedFieldComposer: () =>
              $$CreditStockBoutiquesTableAnnotationComposer(
                  $db: db, $table: table),
          updateCompanionCallback: ({
            Value<String> id = const Value.absent(),
            Value<String> nom = const Value.absent(),
            Value<String> telephone = const Value.absent(),
            Value<String?> adresse = const Value.absent(),
            Value<String> typeBoutique = const Value.absent(),
            Value<String?> logoUrl = const Value.absent(),
            Value<String?> pinHash = const Value.absent(),
            Value<String> abonnement = const Value.absent(),
            Value<DateTime?> premiumExpireAt = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
            Value<DateTime> updatedAt = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              CreditStockBoutiquesCompanion(
            id: id,
            nom: nom,
            telephone: telephone,
            adresse: adresse,
            typeBoutique: typeBoutique,
            logoUrl: logoUrl,
            pinHash: pinHash,
            abonnement: abonnement,
            premiumExpireAt: premiumExpireAt,
            createdAt: createdAt,
            updatedAt: updatedAt,
            rowid: rowid,
          ),
          createCompanionCallback: ({
            required String id,
            required String nom,
            required String telephone,
            Value<String?> adresse = const Value.absent(),
            Value<String> typeBoutique = const Value.absent(),
            Value<String?> logoUrl = const Value.absent(),
            Value<String?> pinHash = const Value.absent(),
            Value<String> abonnement = const Value.absent(),
            Value<DateTime?> premiumExpireAt = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
            Value<DateTime> updatedAt = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              CreditStockBoutiquesCompanion.insert(
            id: id,
            nom: nom,
            telephone: telephone,
            adresse: adresse,
            typeBoutique: typeBoutique,
            logoUrl: logoUrl,
            pinHash: pinHash,
            abonnement: abonnement,
            premiumExpireAt: premiumExpireAt,
            createdAt: createdAt,
            updatedAt: updatedAt,
            rowid: rowid,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (
                    e.readTable(table),
                    $$CreditStockBoutiquesTableReferences(db, table, e)
                  ))
              .toList(),
          prefetchHooksCallback: (
              {creditStockUtilisateursRefs = false,
              creditStockProduitsRefs = false,
              creditStockClientsRefs = false,
              creditStockVentesRefs = false,
              creditStockDettesRefs = false}) {
            return PrefetchHooks(
              db: db,
              explicitlyWatchedTables: [
                if (creditStockUtilisateursRefs) db.creditStockUtilisateurs,
                if (creditStockProduitsRefs) db.creditStockProduits,
                if (creditStockClientsRefs) db.creditStockClients,
                if (creditStockVentesRefs) db.creditStockVentes,
                if (creditStockDettesRefs) db.creditStockDettes
              ],
              addJoins: null,
              getPrefetchedDataCallback: (items) async {
                return [
                  if (creditStockUtilisateursRefs)
                    await $_getPrefetchedData<CreditStockBoutique,
                            $CreditStockBoutiquesTable, CreditStockUtilisateur>(
                        currentTable: table,
                        referencedTable: $$CreditStockBoutiquesTableReferences
                            ._creditStockUtilisateursRefsTable(db),
                        managerFromTypedResult: (p0) =>
                            $$CreditStockBoutiquesTableReferences(db, table, p0)
                                .creditStockUtilisateursRefs,
                        referencedItemsForCurrentItem:
                            (item, referencedItems) => referencedItems
                                .where((e) => e.boutiqueId == item.id),
                        typedResults: items),
                  if (creditStockProduitsRefs)
                    await $_getPrefetchedData<CreditStockBoutique,
                            $CreditStockBoutiquesTable, CreditStockProduit>(
                        currentTable: table,
                        referencedTable: $$CreditStockBoutiquesTableReferences
                            ._creditStockProduitsRefsTable(db),
                        managerFromTypedResult: (p0) =>
                            $$CreditStockBoutiquesTableReferences(db, table, p0)
                                .creditStockProduitsRefs,
                        referencedItemsForCurrentItem:
                            (item, referencedItems) => referencedItems
                                .where((e) => e.boutiqueId == item.id),
                        typedResults: items),
                  if (creditStockClientsRefs)
                    await $_getPrefetchedData<CreditStockBoutique,
                            $CreditStockBoutiquesTable, CreditStockClient>(
                        currentTable: table,
                        referencedTable: $$CreditStockBoutiquesTableReferences
                            ._creditStockClientsRefsTable(db),
                        managerFromTypedResult: (p0) =>
                            $$CreditStockBoutiquesTableReferences(db, table, p0)
                                .creditStockClientsRefs,
                        referencedItemsForCurrentItem:
                            (item, referencedItems) => referencedItems
                                .where((e) => e.boutiqueId == item.id),
                        typedResults: items),
                  if (creditStockVentesRefs)
                    await $_getPrefetchedData<CreditStockBoutique,
                            $CreditStockBoutiquesTable, CreditStockVente>(
                        currentTable: table,
                        referencedTable: $$CreditStockBoutiquesTableReferences
                            ._creditStockVentesRefsTable(db),
                        managerFromTypedResult: (p0) =>
                            $$CreditStockBoutiquesTableReferences(db, table, p0)
                                .creditStockVentesRefs,
                        referencedItemsForCurrentItem:
                            (item, referencedItems) => referencedItems
                                .where((e) => e.boutiqueId == item.id),
                        typedResults: items),
                  if (creditStockDettesRefs)
                    await $_getPrefetchedData<CreditStockBoutique,
                            $CreditStockBoutiquesTable, CreditStockDette>(
                        currentTable: table,
                        referencedTable: $$CreditStockBoutiquesTableReferences
                            ._creditStockDettesRefsTable(db),
                        managerFromTypedResult: (p0) =>
                            $$CreditStockBoutiquesTableReferences(db, table, p0)
                                .creditStockDettesRefs,
                        referencedItemsForCurrentItem:
                            (item, referencedItems) => referencedItems
                                .where((e) => e.boutiqueId == item.id),
                        typedResults: items)
                ];
              },
            );
          },
        ));
}

typedef $$CreditStockBoutiquesTableProcessedTableManager
    = ProcessedTableManager<
        _$AppDatabase,
        $CreditStockBoutiquesTable,
        CreditStockBoutique,
        $$CreditStockBoutiquesTableFilterComposer,
        $$CreditStockBoutiquesTableOrderingComposer,
        $$CreditStockBoutiquesTableAnnotationComposer,
        $$CreditStockBoutiquesTableCreateCompanionBuilder,
        $$CreditStockBoutiquesTableUpdateCompanionBuilder,
        (CreditStockBoutique, $$CreditStockBoutiquesTableReferences),
        CreditStockBoutique,
        PrefetchHooks Function(
            {bool creditStockUtilisateursRefs,
            bool creditStockProduitsRefs,
            bool creditStockClientsRefs,
            bool creditStockVentesRefs,
            bool creditStockDettesRefs})>;
typedef $$CreditStockUtilisateursTableCreateCompanionBuilder
    = CreditStockUtilisateursCompanion Function({
  required String id,
  Value<String?> authId,
  required String boutiqueId,
  required String nom,
  Value<String?> telephone,
  Value<String> role,
  Value<String?> pinHash,
  Value<bool> actif,
  Value<DateTime> createdAt,
  Value<DateTime> updatedAt,
  Value<int> rowid,
});
typedef $$CreditStockUtilisateursTableUpdateCompanionBuilder
    = CreditStockUtilisateursCompanion Function({
  Value<String> id,
  Value<String?> authId,
  Value<String> boutiqueId,
  Value<String> nom,
  Value<String?> telephone,
  Value<String> role,
  Value<String?> pinHash,
  Value<bool> actif,
  Value<DateTime> createdAt,
  Value<DateTime> updatedAt,
  Value<int> rowid,
});

final class $$CreditStockUtilisateursTableReferences extends BaseReferences<
    _$AppDatabase, $CreditStockUtilisateursTable, CreditStockUtilisateur> {
  $$CreditStockUtilisateursTableReferences(
      super.$_db, super.$_table, super.$_typedResult);

  static $CreditStockBoutiquesTable _boutiqueIdTable(_$AppDatabase db) =>
      db.creditStockBoutiques.createAlias($_aliasNameGenerator(
          db.creditStockUtilisateurs.boutiqueId, db.creditStockBoutiques.id));

  $$CreditStockBoutiquesTableProcessedTableManager get boutiqueId {
    final $_column = $_itemColumn<String>('boutique_id')!;

    final manager =
        $$CreditStockBoutiquesTableTableManager($_db, $_db.creditStockBoutiques)
            .filter((f) => f.id.sqlEquals($_column));
    final item = $_typedResult.readTableOrNull(_boutiqueIdTable($_db));
    if (item == null) return manager;
    return ProcessedTableManager(
        manager.$state.copyWith(prefetchedData: [item]));
  }
}

class $$CreditStockUtilisateursTableFilterComposer
    extends Composer<_$AppDatabase, $CreditStockUtilisateursTable> {
  $$CreditStockUtilisateursTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get authId => $composableBuilder(
      column: $table.authId, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get nom => $composableBuilder(
      column: $table.nom, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get telephone => $composableBuilder(
      column: $table.telephone, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get role => $composableBuilder(
      column: $table.role, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get pinHash => $composableBuilder(
      column: $table.pinHash, builder: (column) => ColumnFilters(column));

  ColumnFilters<bool> get actif => $composableBuilder(
      column: $table.actif, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get updatedAt => $composableBuilder(
      column: $table.updatedAt, builder: (column) => ColumnFilters(column));

  $$CreditStockBoutiquesTableFilterComposer get boutiqueId {
    final $$CreditStockBoutiquesTableFilterComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.boutiqueId,
        referencedTable: $db.creditStockBoutiques,
        getReferencedColumn: (t) => t.id,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$CreditStockBoutiquesTableFilterComposer(
              $db: $db,
              $table: $db.creditStockBoutiques,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return composer;
  }
}

class $$CreditStockUtilisateursTableOrderingComposer
    extends Composer<_$AppDatabase, $CreditStockUtilisateursTable> {
  $$CreditStockUtilisateursTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get authId => $composableBuilder(
      column: $table.authId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get nom => $composableBuilder(
      column: $table.nom, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get telephone => $composableBuilder(
      column: $table.telephone, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get role => $composableBuilder(
      column: $table.role, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get pinHash => $composableBuilder(
      column: $table.pinHash, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<bool> get actif => $composableBuilder(
      column: $table.actif, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get updatedAt => $composableBuilder(
      column: $table.updatedAt, builder: (column) => ColumnOrderings(column));

  $$CreditStockBoutiquesTableOrderingComposer get boutiqueId {
    final $$CreditStockBoutiquesTableOrderingComposer composer =
        $composerBuilder(
            composer: this,
            getCurrentColumn: (t) => t.boutiqueId,
            referencedTable: $db.creditStockBoutiques,
            getReferencedColumn: (t) => t.id,
            builder: (joinBuilder,
                    {$addJoinBuilderToRootComposer,
                    $removeJoinBuilderFromRootComposer}) =>
                $$CreditStockBoutiquesTableOrderingComposer(
                  $db: $db,
                  $table: $db.creditStockBoutiques,
                  $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
                  joinBuilder: joinBuilder,
                  $removeJoinBuilderFromRootComposer:
                      $removeJoinBuilderFromRootComposer,
                ));
    return composer;
  }
}

class $$CreditStockUtilisateursTableAnnotationComposer
    extends Composer<_$AppDatabase, $CreditStockUtilisateursTable> {
  $$CreditStockUtilisateursTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get authId =>
      $composableBuilder(column: $table.authId, builder: (column) => column);

  GeneratedColumn<String> get nom =>
      $composableBuilder(column: $table.nom, builder: (column) => column);

  GeneratedColumn<String> get telephone =>
      $composableBuilder(column: $table.telephone, builder: (column) => column);

  GeneratedColumn<String> get role =>
      $composableBuilder(column: $table.role, builder: (column) => column);

  GeneratedColumn<String> get pinHash =>
      $composableBuilder(column: $table.pinHash, builder: (column) => column);

  GeneratedColumn<bool> get actif =>
      $composableBuilder(column: $table.actif, builder: (column) => column);

  GeneratedColumn<DateTime> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);

  GeneratedColumn<DateTime> get updatedAt =>
      $composableBuilder(column: $table.updatedAt, builder: (column) => column);

  $$CreditStockBoutiquesTableAnnotationComposer get boutiqueId {
    final $$CreditStockBoutiquesTableAnnotationComposer composer =
        $composerBuilder(
            composer: this,
            getCurrentColumn: (t) => t.boutiqueId,
            referencedTable: $db.creditStockBoutiques,
            getReferencedColumn: (t) => t.id,
            builder: (joinBuilder,
                    {$addJoinBuilderToRootComposer,
                    $removeJoinBuilderFromRootComposer}) =>
                $$CreditStockBoutiquesTableAnnotationComposer(
                  $db: $db,
                  $table: $db.creditStockBoutiques,
                  $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
                  joinBuilder: joinBuilder,
                  $removeJoinBuilderFromRootComposer:
                      $removeJoinBuilderFromRootComposer,
                ));
    return composer;
  }
}

class $$CreditStockUtilisateursTableTableManager extends RootTableManager<
    _$AppDatabase,
    $CreditStockUtilisateursTable,
    CreditStockUtilisateur,
    $$CreditStockUtilisateursTableFilterComposer,
    $$CreditStockUtilisateursTableOrderingComposer,
    $$CreditStockUtilisateursTableAnnotationComposer,
    $$CreditStockUtilisateursTableCreateCompanionBuilder,
    $$CreditStockUtilisateursTableUpdateCompanionBuilder,
    (CreditStockUtilisateur, $$CreditStockUtilisateursTableReferences),
    CreditStockUtilisateur,
    PrefetchHooks Function({bool boutiqueId})> {
  $$CreditStockUtilisateursTableTableManager(
      _$AppDatabase db, $CreditStockUtilisateursTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$CreditStockUtilisateursTableFilterComposer(
                  $db: db, $table: table),
          createOrderingComposer: () =>
              $$CreditStockUtilisateursTableOrderingComposer(
                  $db: db, $table: table),
          createComputedFieldComposer: () =>
              $$CreditStockUtilisateursTableAnnotationComposer(
                  $db: db, $table: table),
          updateCompanionCallback: ({
            Value<String> id = const Value.absent(),
            Value<String?> authId = const Value.absent(),
            Value<String> boutiqueId = const Value.absent(),
            Value<String> nom = const Value.absent(),
            Value<String?> telephone = const Value.absent(),
            Value<String> role = const Value.absent(),
            Value<String?> pinHash = const Value.absent(),
            Value<bool> actif = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
            Value<DateTime> updatedAt = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              CreditStockUtilisateursCompanion(
            id: id,
            authId: authId,
            boutiqueId: boutiqueId,
            nom: nom,
            telephone: telephone,
            role: role,
            pinHash: pinHash,
            actif: actif,
            createdAt: createdAt,
            updatedAt: updatedAt,
            rowid: rowid,
          ),
          createCompanionCallback: ({
            required String id,
            Value<String?> authId = const Value.absent(),
            required String boutiqueId,
            required String nom,
            Value<String?> telephone = const Value.absent(),
            Value<String> role = const Value.absent(),
            Value<String?> pinHash = const Value.absent(),
            Value<bool> actif = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
            Value<DateTime> updatedAt = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              CreditStockUtilisateursCompanion.insert(
            id: id,
            authId: authId,
            boutiqueId: boutiqueId,
            nom: nom,
            telephone: telephone,
            role: role,
            pinHash: pinHash,
            actif: actif,
            createdAt: createdAt,
            updatedAt: updatedAt,
            rowid: rowid,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (
                    e.readTable(table),
                    $$CreditStockUtilisateursTableReferences(db, table, e)
                  ))
              .toList(),
          prefetchHooksCallback: ({boutiqueId = false}) {
            return PrefetchHooks(
              db: db,
              explicitlyWatchedTables: [],
              addJoins: <
                  T extends TableManagerState<
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic>>(state) {
                if (boutiqueId) {
                  state = state.withJoin(
                    currentTable: table,
                    currentColumn: table.boutiqueId,
                    referencedTable: $$CreditStockUtilisateursTableReferences
                        ._boutiqueIdTable(db),
                    referencedColumn: $$CreditStockUtilisateursTableReferences
                        ._boutiqueIdTable(db)
                        .id,
                  ) as T;
                }

                return state;
              },
              getPrefetchedDataCallback: (items) async {
                return [];
              },
            );
          },
        ));
}

typedef $$CreditStockUtilisateursTableProcessedTableManager
    = ProcessedTableManager<
        _$AppDatabase,
        $CreditStockUtilisateursTable,
        CreditStockUtilisateur,
        $$CreditStockUtilisateursTableFilterComposer,
        $$CreditStockUtilisateursTableOrderingComposer,
        $$CreditStockUtilisateursTableAnnotationComposer,
        $$CreditStockUtilisateursTableCreateCompanionBuilder,
        $$CreditStockUtilisateursTableUpdateCompanionBuilder,
        (CreditStockUtilisateur, $$CreditStockUtilisateursTableReferences),
        CreditStockUtilisateur,
        PrefetchHooks Function({bool boutiqueId})>;
typedef $$CreditStockProduitsTableCreateCompanionBuilder
    = CreditStockProduitsCompanion Function({
  required String id,
  required String boutiqueId,
  required String nom,
  Value<String?> description,
  Value<String?> codeBarre,
  Value<int> prixVente,
  Value<int> prixAchat,
  Value<int> quantite,
  Value<int> seuilAlerte,
  Value<String> unite,
  Value<String?> categorie,
  Value<String?> imageUrl,
  Value<bool> actif,
  Value<bool> synced,
  Value<DateTime> createdAt,
  Value<DateTime> updatedAt,
  Value<int> rowid,
});
typedef $$CreditStockProduitsTableUpdateCompanionBuilder
    = CreditStockProduitsCompanion Function({
  Value<String> id,
  Value<String> boutiqueId,
  Value<String> nom,
  Value<String?> description,
  Value<String?> codeBarre,
  Value<int> prixVente,
  Value<int> prixAchat,
  Value<int> quantite,
  Value<int> seuilAlerte,
  Value<String> unite,
  Value<String?> categorie,
  Value<String?> imageUrl,
  Value<bool> actif,
  Value<bool> synced,
  Value<DateTime> createdAt,
  Value<DateTime> updatedAt,
  Value<int> rowid,
});

final class $$CreditStockProduitsTableReferences extends BaseReferences<
    _$AppDatabase, $CreditStockProduitsTable, CreditStockProduit> {
  $$CreditStockProduitsTableReferences(
      super.$_db, super.$_table, super.$_typedResult);

  static $CreditStockBoutiquesTable _boutiqueIdTable(_$AppDatabase db) =>
      db.creditStockBoutiques.createAlias($_aliasNameGenerator(
          db.creditStockProduits.boutiqueId, db.creditStockBoutiques.id));

  $$CreditStockBoutiquesTableProcessedTableManager get boutiqueId {
    final $_column = $_itemColumn<String>('boutique_id')!;

    final manager =
        $$CreditStockBoutiquesTableTableManager($_db, $_db.creditStockBoutiques)
            .filter((f) => f.id.sqlEquals($_column));
    final item = $_typedResult.readTableOrNull(_boutiqueIdTable($_db));
    if (item == null) return manager;
    return ProcessedTableManager(
        manager.$state.copyWith(prefetchedData: [item]));
  }
}

class $$CreditStockProduitsTableFilterComposer
    extends Composer<_$AppDatabase, $CreditStockProduitsTable> {
  $$CreditStockProduitsTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get nom => $composableBuilder(
      column: $table.nom, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get description => $composableBuilder(
      column: $table.description, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get codeBarre => $composableBuilder(
      column: $table.codeBarre, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get prixVente => $composableBuilder(
      column: $table.prixVente, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get prixAchat => $composableBuilder(
      column: $table.prixAchat, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get quantite => $composableBuilder(
      column: $table.quantite, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get seuilAlerte => $composableBuilder(
      column: $table.seuilAlerte, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get unite => $composableBuilder(
      column: $table.unite, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get categorie => $composableBuilder(
      column: $table.categorie, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get imageUrl => $composableBuilder(
      column: $table.imageUrl, builder: (column) => ColumnFilters(column));

  ColumnFilters<bool> get actif => $composableBuilder(
      column: $table.actif, builder: (column) => ColumnFilters(column));

  ColumnFilters<bool> get synced => $composableBuilder(
      column: $table.synced, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get updatedAt => $composableBuilder(
      column: $table.updatedAt, builder: (column) => ColumnFilters(column));

  $$CreditStockBoutiquesTableFilterComposer get boutiqueId {
    final $$CreditStockBoutiquesTableFilterComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.boutiqueId,
        referencedTable: $db.creditStockBoutiques,
        getReferencedColumn: (t) => t.id,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$CreditStockBoutiquesTableFilterComposer(
              $db: $db,
              $table: $db.creditStockBoutiques,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return composer;
  }
}

class $$CreditStockProduitsTableOrderingComposer
    extends Composer<_$AppDatabase, $CreditStockProduitsTable> {
  $$CreditStockProduitsTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get nom => $composableBuilder(
      column: $table.nom, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get description => $composableBuilder(
      column: $table.description, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get codeBarre => $composableBuilder(
      column: $table.codeBarre, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get prixVente => $composableBuilder(
      column: $table.prixVente, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get prixAchat => $composableBuilder(
      column: $table.prixAchat, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get quantite => $composableBuilder(
      column: $table.quantite, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get seuilAlerte => $composableBuilder(
      column: $table.seuilAlerte, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get unite => $composableBuilder(
      column: $table.unite, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get categorie => $composableBuilder(
      column: $table.categorie, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get imageUrl => $composableBuilder(
      column: $table.imageUrl, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<bool> get actif => $composableBuilder(
      column: $table.actif, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<bool> get synced => $composableBuilder(
      column: $table.synced, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get updatedAt => $composableBuilder(
      column: $table.updatedAt, builder: (column) => ColumnOrderings(column));

  $$CreditStockBoutiquesTableOrderingComposer get boutiqueId {
    final $$CreditStockBoutiquesTableOrderingComposer composer =
        $composerBuilder(
            composer: this,
            getCurrentColumn: (t) => t.boutiqueId,
            referencedTable: $db.creditStockBoutiques,
            getReferencedColumn: (t) => t.id,
            builder: (joinBuilder,
                    {$addJoinBuilderToRootComposer,
                    $removeJoinBuilderFromRootComposer}) =>
                $$CreditStockBoutiquesTableOrderingComposer(
                  $db: $db,
                  $table: $db.creditStockBoutiques,
                  $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
                  joinBuilder: joinBuilder,
                  $removeJoinBuilderFromRootComposer:
                      $removeJoinBuilderFromRootComposer,
                ));
    return composer;
  }
}

class $$CreditStockProduitsTableAnnotationComposer
    extends Composer<_$AppDatabase, $CreditStockProduitsTable> {
  $$CreditStockProduitsTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get nom =>
      $composableBuilder(column: $table.nom, builder: (column) => column);

  GeneratedColumn<String> get description => $composableBuilder(
      column: $table.description, builder: (column) => column);

  GeneratedColumn<String> get codeBarre =>
      $composableBuilder(column: $table.codeBarre, builder: (column) => column);

  GeneratedColumn<int> get prixVente =>
      $composableBuilder(column: $table.prixVente, builder: (column) => column);

  GeneratedColumn<int> get prixAchat =>
      $composableBuilder(column: $table.prixAchat, builder: (column) => column);

  GeneratedColumn<int> get quantite =>
      $composableBuilder(column: $table.quantite, builder: (column) => column);

  GeneratedColumn<int> get seuilAlerte => $composableBuilder(
      column: $table.seuilAlerte, builder: (column) => column);

  GeneratedColumn<String> get unite =>
      $composableBuilder(column: $table.unite, builder: (column) => column);

  GeneratedColumn<String> get categorie =>
      $composableBuilder(column: $table.categorie, builder: (column) => column);

  GeneratedColumn<String> get imageUrl =>
      $composableBuilder(column: $table.imageUrl, builder: (column) => column);

  GeneratedColumn<bool> get actif =>
      $composableBuilder(column: $table.actif, builder: (column) => column);

  GeneratedColumn<bool> get synced =>
      $composableBuilder(column: $table.synced, builder: (column) => column);

  GeneratedColumn<DateTime> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);

  GeneratedColumn<DateTime> get updatedAt =>
      $composableBuilder(column: $table.updatedAt, builder: (column) => column);

  $$CreditStockBoutiquesTableAnnotationComposer get boutiqueId {
    final $$CreditStockBoutiquesTableAnnotationComposer composer =
        $composerBuilder(
            composer: this,
            getCurrentColumn: (t) => t.boutiqueId,
            referencedTable: $db.creditStockBoutiques,
            getReferencedColumn: (t) => t.id,
            builder: (joinBuilder,
                    {$addJoinBuilderToRootComposer,
                    $removeJoinBuilderFromRootComposer}) =>
                $$CreditStockBoutiquesTableAnnotationComposer(
                  $db: $db,
                  $table: $db.creditStockBoutiques,
                  $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
                  joinBuilder: joinBuilder,
                  $removeJoinBuilderFromRootComposer:
                      $removeJoinBuilderFromRootComposer,
                ));
    return composer;
  }
}

class $$CreditStockProduitsTableTableManager extends RootTableManager<
    _$AppDatabase,
    $CreditStockProduitsTable,
    CreditStockProduit,
    $$CreditStockProduitsTableFilterComposer,
    $$CreditStockProduitsTableOrderingComposer,
    $$CreditStockProduitsTableAnnotationComposer,
    $$CreditStockProduitsTableCreateCompanionBuilder,
    $$CreditStockProduitsTableUpdateCompanionBuilder,
    (CreditStockProduit, $$CreditStockProduitsTableReferences),
    CreditStockProduit,
    PrefetchHooks Function({bool boutiqueId})> {
  $$CreditStockProduitsTableTableManager(
      _$AppDatabase db, $CreditStockProduitsTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$CreditStockProduitsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$CreditStockProduitsTableOrderingComposer(
                  $db: db, $table: table),
          createComputedFieldComposer: () =>
              $$CreditStockProduitsTableAnnotationComposer(
                  $db: db, $table: table),
          updateCompanionCallback: ({
            Value<String> id = const Value.absent(),
            Value<String> boutiqueId = const Value.absent(),
            Value<String> nom = const Value.absent(),
            Value<String?> description = const Value.absent(),
            Value<String?> codeBarre = const Value.absent(),
            Value<int> prixVente = const Value.absent(),
            Value<int> prixAchat = const Value.absent(),
            Value<int> quantite = const Value.absent(),
            Value<int> seuilAlerte = const Value.absent(),
            Value<String> unite = const Value.absent(),
            Value<String?> categorie = const Value.absent(),
            Value<String?> imageUrl = const Value.absent(),
            Value<bool> actif = const Value.absent(),
            Value<bool> synced = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
            Value<DateTime> updatedAt = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              CreditStockProduitsCompanion(
            id: id,
            boutiqueId: boutiqueId,
            nom: nom,
            description: description,
            codeBarre: codeBarre,
            prixVente: prixVente,
            prixAchat: prixAchat,
            quantite: quantite,
            seuilAlerte: seuilAlerte,
            unite: unite,
            categorie: categorie,
            imageUrl: imageUrl,
            actif: actif,
            synced: synced,
            createdAt: createdAt,
            updatedAt: updatedAt,
            rowid: rowid,
          ),
          createCompanionCallback: ({
            required String id,
            required String boutiqueId,
            required String nom,
            Value<String?> description = const Value.absent(),
            Value<String?> codeBarre = const Value.absent(),
            Value<int> prixVente = const Value.absent(),
            Value<int> prixAchat = const Value.absent(),
            Value<int> quantite = const Value.absent(),
            Value<int> seuilAlerte = const Value.absent(),
            Value<String> unite = const Value.absent(),
            Value<String?> categorie = const Value.absent(),
            Value<String?> imageUrl = const Value.absent(),
            Value<bool> actif = const Value.absent(),
            Value<bool> synced = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
            Value<DateTime> updatedAt = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              CreditStockProduitsCompanion.insert(
            id: id,
            boutiqueId: boutiqueId,
            nom: nom,
            description: description,
            codeBarre: codeBarre,
            prixVente: prixVente,
            prixAchat: prixAchat,
            quantite: quantite,
            seuilAlerte: seuilAlerte,
            unite: unite,
            categorie: categorie,
            imageUrl: imageUrl,
            actif: actif,
            synced: synced,
            createdAt: createdAt,
            updatedAt: updatedAt,
            rowid: rowid,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (
                    e.readTable(table),
                    $$CreditStockProduitsTableReferences(db, table, e)
                  ))
              .toList(),
          prefetchHooksCallback: ({boutiqueId = false}) {
            return PrefetchHooks(
              db: db,
              explicitlyWatchedTables: [],
              addJoins: <
                  T extends TableManagerState<
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic>>(state) {
                if (boutiqueId) {
                  state = state.withJoin(
                    currentTable: table,
                    currentColumn: table.boutiqueId,
                    referencedTable: $$CreditStockProduitsTableReferences
                        ._boutiqueIdTable(db),
                    referencedColumn: $$CreditStockProduitsTableReferences
                        ._boutiqueIdTable(db)
                        .id,
                  ) as T;
                }

                return state;
              },
              getPrefetchedDataCallback: (items) async {
                return [];
              },
            );
          },
        ));
}

typedef $$CreditStockProduitsTableProcessedTableManager = ProcessedTableManager<
    _$AppDatabase,
    $CreditStockProduitsTable,
    CreditStockProduit,
    $$CreditStockProduitsTableFilterComposer,
    $$CreditStockProduitsTableOrderingComposer,
    $$CreditStockProduitsTableAnnotationComposer,
    $$CreditStockProduitsTableCreateCompanionBuilder,
    $$CreditStockProduitsTableUpdateCompanionBuilder,
    (CreditStockProduit, $$CreditStockProduitsTableReferences),
    CreditStockProduit,
    PrefetchHooks Function({bool boutiqueId})>;
typedef $$CreditStockClientsTableCreateCompanionBuilder
    = CreditStockClientsCompanion Function({
  required String id,
  required String boutiqueId,
  required String nom,
  Value<String?> telephone,
  Value<String?> adresse,
  Value<String?> photoUrl,
  Value<String> score,
  Value<int> totalDu,
  Value<int> nbAchats,
  Value<int> nbRetards,
  Value<bool> synced,
  Value<DateTime> createdAt,
  Value<DateTime> updatedAt,
  Value<int> rowid,
});
typedef $$CreditStockClientsTableUpdateCompanionBuilder
    = CreditStockClientsCompanion Function({
  Value<String> id,
  Value<String> boutiqueId,
  Value<String> nom,
  Value<String?> telephone,
  Value<String?> adresse,
  Value<String?> photoUrl,
  Value<String> score,
  Value<int> totalDu,
  Value<int> nbAchats,
  Value<int> nbRetards,
  Value<bool> synced,
  Value<DateTime> createdAt,
  Value<DateTime> updatedAt,
  Value<int> rowid,
});

final class $$CreditStockClientsTableReferences extends BaseReferences<
    _$AppDatabase, $CreditStockClientsTable, CreditStockClient> {
  $$CreditStockClientsTableReferences(
      super.$_db, super.$_table, super.$_typedResult);

  static $CreditStockBoutiquesTable _boutiqueIdTable(_$AppDatabase db) =>
      db.creditStockBoutiques.createAlias($_aliasNameGenerator(
          db.creditStockClients.boutiqueId, db.creditStockBoutiques.id));

  $$CreditStockBoutiquesTableProcessedTableManager get boutiqueId {
    final $_column = $_itemColumn<String>('boutique_id')!;

    final manager =
        $$CreditStockBoutiquesTableTableManager($_db, $_db.creditStockBoutiques)
            .filter((f) => f.id.sqlEquals($_column));
    final item = $_typedResult.readTableOrNull(_boutiqueIdTable($_db));
    if (item == null) return manager;
    return ProcessedTableManager(
        manager.$state.copyWith(prefetchedData: [item]));
  }

  static MultiTypedResultKey<$CreditStockDettesTable, List<CreditStockDette>>
      _creditStockDettesRefsTable(_$AppDatabase db) =>
          MultiTypedResultKey.fromTable(db.creditStockDettes,
              aliasName: $_aliasNameGenerator(
                  db.creditStockClients.id, db.creditStockDettes.clientId));

  $$CreditStockDettesTableProcessedTableManager get creditStockDettesRefs {
    final manager = $$CreditStockDettesTableTableManager(
            $_db, $_db.creditStockDettes)
        .filter((f) => f.clientId.id.sqlEquals($_itemColumn<String>('id')!));

    final cache =
        $_typedResult.readTableOrNull(_creditStockDettesRefsTable($_db));
    return ProcessedTableManager(
        manager.$state.copyWith(prefetchedData: cache));
  }
}

class $$CreditStockClientsTableFilterComposer
    extends Composer<_$AppDatabase, $CreditStockClientsTable> {
  $$CreditStockClientsTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get nom => $composableBuilder(
      column: $table.nom, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get telephone => $composableBuilder(
      column: $table.telephone, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get adresse => $composableBuilder(
      column: $table.adresse, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get photoUrl => $composableBuilder(
      column: $table.photoUrl, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get score => $composableBuilder(
      column: $table.score, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get totalDu => $composableBuilder(
      column: $table.totalDu, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get nbAchats => $composableBuilder(
      column: $table.nbAchats, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get nbRetards => $composableBuilder(
      column: $table.nbRetards, builder: (column) => ColumnFilters(column));

  ColumnFilters<bool> get synced => $composableBuilder(
      column: $table.synced, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get updatedAt => $composableBuilder(
      column: $table.updatedAt, builder: (column) => ColumnFilters(column));

  $$CreditStockBoutiquesTableFilterComposer get boutiqueId {
    final $$CreditStockBoutiquesTableFilterComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.boutiqueId,
        referencedTable: $db.creditStockBoutiques,
        getReferencedColumn: (t) => t.id,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$CreditStockBoutiquesTableFilterComposer(
              $db: $db,
              $table: $db.creditStockBoutiques,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return composer;
  }

  Expression<bool> creditStockDettesRefs(
      Expression<bool> Function($$CreditStockDettesTableFilterComposer f) f) {
    final $$CreditStockDettesTableFilterComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.id,
        referencedTable: $db.creditStockDettes,
        getReferencedColumn: (t) => t.clientId,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$CreditStockDettesTableFilterComposer(
              $db: $db,
              $table: $db.creditStockDettes,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return f(composer);
  }
}

class $$CreditStockClientsTableOrderingComposer
    extends Composer<_$AppDatabase, $CreditStockClientsTable> {
  $$CreditStockClientsTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get nom => $composableBuilder(
      column: $table.nom, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get telephone => $composableBuilder(
      column: $table.telephone, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get adresse => $composableBuilder(
      column: $table.adresse, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get photoUrl => $composableBuilder(
      column: $table.photoUrl, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get score => $composableBuilder(
      column: $table.score, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get totalDu => $composableBuilder(
      column: $table.totalDu, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get nbAchats => $composableBuilder(
      column: $table.nbAchats, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get nbRetards => $composableBuilder(
      column: $table.nbRetards, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<bool> get synced => $composableBuilder(
      column: $table.synced, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get updatedAt => $composableBuilder(
      column: $table.updatedAt, builder: (column) => ColumnOrderings(column));

  $$CreditStockBoutiquesTableOrderingComposer get boutiqueId {
    final $$CreditStockBoutiquesTableOrderingComposer composer =
        $composerBuilder(
            composer: this,
            getCurrentColumn: (t) => t.boutiqueId,
            referencedTable: $db.creditStockBoutiques,
            getReferencedColumn: (t) => t.id,
            builder: (joinBuilder,
                    {$addJoinBuilderToRootComposer,
                    $removeJoinBuilderFromRootComposer}) =>
                $$CreditStockBoutiquesTableOrderingComposer(
                  $db: $db,
                  $table: $db.creditStockBoutiques,
                  $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
                  joinBuilder: joinBuilder,
                  $removeJoinBuilderFromRootComposer:
                      $removeJoinBuilderFromRootComposer,
                ));
    return composer;
  }
}

class $$CreditStockClientsTableAnnotationComposer
    extends Composer<_$AppDatabase, $CreditStockClientsTable> {
  $$CreditStockClientsTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get nom =>
      $composableBuilder(column: $table.nom, builder: (column) => column);

  GeneratedColumn<String> get telephone =>
      $composableBuilder(column: $table.telephone, builder: (column) => column);

  GeneratedColumn<String> get adresse =>
      $composableBuilder(column: $table.adresse, builder: (column) => column);

  GeneratedColumn<String> get photoUrl =>
      $composableBuilder(column: $table.photoUrl, builder: (column) => column);

  GeneratedColumn<String> get score =>
      $composableBuilder(column: $table.score, builder: (column) => column);

  GeneratedColumn<int> get totalDu =>
      $composableBuilder(column: $table.totalDu, builder: (column) => column);

  GeneratedColumn<int> get nbAchats =>
      $composableBuilder(column: $table.nbAchats, builder: (column) => column);

  GeneratedColumn<int> get nbRetards =>
      $composableBuilder(column: $table.nbRetards, builder: (column) => column);

  GeneratedColumn<bool> get synced =>
      $composableBuilder(column: $table.synced, builder: (column) => column);

  GeneratedColumn<DateTime> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);

  GeneratedColumn<DateTime> get updatedAt =>
      $composableBuilder(column: $table.updatedAt, builder: (column) => column);

  $$CreditStockBoutiquesTableAnnotationComposer get boutiqueId {
    final $$CreditStockBoutiquesTableAnnotationComposer composer =
        $composerBuilder(
            composer: this,
            getCurrentColumn: (t) => t.boutiqueId,
            referencedTable: $db.creditStockBoutiques,
            getReferencedColumn: (t) => t.id,
            builder: (joinBuilder,
                    {$addJoinBuilderToRootComposer,
                    $removeJoinBuilderFromRootComposer}) =>
                $$CreditStockBoutiquesTableAnnotationComposer(
                  $db: $db,
                  $table: $db.creditStockBoutiques,
                  $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
                  joinBuilder: joinBuilder,
                  $removeJoinBuilderFromRootComposer:
                      $removeJoinBuilderFromRootComposer,
                ));
    return composer;
  }

  Expression<T> creditStockDettesRefs<T extends Object>(
      Expression<T> Function($$CreditStockDettesTableAnnotationComposer a) f) {
    final $$CreditStockDettesTableAnnotationComposer composer =
        $composerBuilder(
            composer: this,
            getCurrentColumn: (t) => t.id,
            referencedTable: $db.creditStockDettes,
            getReferencedColumn: (t) => t.clientId,
            builder: (joinBuilder,
                    {$addJoinBuilderToRootComposer,
                    $removeJoinBuilderFromRootComposer}) =>
                $$CreditStockDettesTableAnnotationComposer(
                  $db: $db,
                  $table: $db.creditStockDettes,
                  $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
                  joinBuilder: joinBuilder,
                  $removeJoinBuilderFromRootComposer:
                      $removeJoinBuilderFromRootComposer,
                ));
    return f(composer);
  }
}

class $$CreditStockClientsTableTableManager extends RootTableManager<
    _$AppDatabase,
    $CreditStockClientsTable,
    CreditStockClient,
    $$CreditStockClientsTableFilterComposer,
    $$CreditStockClientsTableOrderingComposer,
    $$CreditStockClientsTableAnnotationComposer,
    $$CreditStockClientsTableCreateCompanionBuilder,
    $$CreditStockClientsTableUpdateCompanionBuilder,
    (CreditStockClient, $$CreditStockClientsTableReferences),
    CreditStockClient,
    PrefetchHooks Function({bool boutiqueId, bool creditStockDettesRefs})> {
  $$CreditStockClientsTableTableManager(
      _$AppDatabase db, $CreditStockClientsTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$CreditStockClientsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$CreditStockClientsTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$CreditStockClientsTableAnnotationComposer(
                  $db: db, $table: table),
          updateCompanionCallback: ({
            Value<String> id = const Value.absent(),
            Value<String> boutiqueId = const Value.absent(),
            Value<String> nom = const Value.absent(),
            Value<String?> telephone = const Value.absent(),
            Value<String?> adresse = const Value.absent(),
            Value<String?> photoUrl = const Value.absent(),
            Value<String> score = const Value.absent(),
            Value<int> totalDu = const Value.absent(),
            Value<int> nbAchats = const Value.absent(),
            Value<int> nbRetards = const Value.absent(),
            Value<bool> synced = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
            Value<DateTime> updatedAt = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              CreditStockClientsCompanion(
            id: id,
            boutiqueId: boutiqueId,
            nom: nom,
            telephone: telephone,
            adresse: adresse,
            photoUrl: photoUrl,
            score: score,
            totalDu: totalDu,
            nbAchats: nbAchats,
            nbRetards: nbRetards,
            synced: synced,
            createdAt: createdAt,
            updatedAt: updatedAt,
            rowid: rowid,
          ),
          createCompanionCallback: ({
            required String id,
            required String boutiqueId,
            required String nom,
            Value<String?> telephone = const Value.absent(),
            Value<String?> adresse = const Value.absent(),
            Value<String?> photoUrl = const Value.absent(),
            Value<String> score = const Value.absent(),
            Value<int> totalDu = const Value.absent(),
            Value<int> nbAchats = const Value.absent(),
            Value<int> nbRetards = const Value.absent(),
            Value<bool> synced = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
            Value<DateTime> updatedAt = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              CreditStockClientsCompanion.insert(
            id: id,
            boutiqueId: boutiqueId,
            nom: nom,
            telephone: telephone,
            adresse: adresse,
            photoUrl: photoUrl,
            score: score,
            totalDu: totalDu,
            nbAchats: nbAchats,
            nbRetards: nbRetards,
            synced: synced,
            createdAt: createdAt,
            updatedAt: updatedAt,
            rowid: rowid,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (
                    e.readTable(table),
                    $$CreditStockClientsTableReferences(db, table, e)
                  ))
              .toList(),
          prefetchHooksCallback: (
              {boutiqueId = false, creditStockDettesRefs = false}) {
            return PrefetchHooks(
              db: db,
              explicitlyWatchedTables: [
                if (creditStockDettesRefs) db.creditStockDettes
              ],
              addJoins: <
                  T extends TableManagerState<
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic>>(state) {
                if (boutiqueId) {
                  state = state.withJoin(
                    currentTable: table,
                    currentColumn: table.boutiqueId,
                    referencedTable: $$CreditStockClientsTableReferences
                        ._boutiqueIdTable(db),
                    referencedColumn: $$CreditStockClientsTableReferences
                        ._boutiqueIdTable(db)
                        .id,
                  ) as T;
                }

                return state;
              },
              getPrefetchedDataCallback: (items) async {
                return [
                  if (creditStockDettesRefs)
                    await $_getPrefetchedData<CreditStockClient,
                            $CreditStockClientsTable, CreditStockDette>(
                        currentTable: table,
                        referencedTable: $$CreditStockClientsTableReferences
                            ._creditStockDettesRefsTable(db),
                        managerFromTypedResult: (p0) =>
                            $$CreditStockClientsTableReferences(db, table, p0)
                                .creditStockDettesRefs,
                        referencedItemsForCurrentItem: (item,
                                referencedItems) =>
                            referencedItems.where((e) => e.clientId == item.id),
                        typedResults: items)
                ];
              },
            );
          },
        ));
}

typedef $$CreditStockClientsTableProcessedTableManager = ProcessedTableManager<
    _$AppDatabase,
    $CreditStockClientsTable,
    CreditStockClient,
    $$CreditStockClientsTableFilterComposer,
    $$CreditStockClientsTableOrderingComposer,
    $$CreditStockClientsTableAnnotationComposer,
    $$CreditStockClientsTableCreateCompanionBuilder,
    $$CreditStockClientsTableUpdateCompanionBuilder,
    (CreditStockClient, $$CreditStockClientsTableReferences),
    CreditStockClient,
    PrefetchHooks Function({bool boutiqueId, bool creditStockDettesRefs})>;
typedef $$CreditStockVentesTableCreateCompanionBuilder
    = CreditStockVentesCompanion Function({
  required String id,
  required String boutiqueId,
  Value<String?> utilisateurId,
  Value<String?> clientId,
  Value<String> typePaiement,
  Value<int> montantTotal,
  Value<String?> note,
  Value<bool> synced,
  Value<DateTime> dateVente,
  Value<DateTime> createdAt,
  Value<int> rowid,
});
typedef $$CreditStockVentesTableUpdateCompanionBuilder
    = CreditStockVentesCompanion Function({
  Value<String> id,
  Value<String> boutiqueId,
  Value<String?> utilisateurId,
  Value<String?> clientId,
  Value<String> typePaiement,
  Value<int> montantTotal,
  Value<String?> note,
  Value<bool> synced,
  Value<DateTime> dateVente,
  Value<DateTime> createdAt,
  Value<int> rowid,
});

final class $$CreditStockVentesTableReferences extends BaseReferences<
    _$AppDatabase, $CreditStockVentesTable, CreditStockVente> {
  $$CreditStockVentesTableReferences(
      super.$_db, super.$_table, super.$_typedResult);

  static $CreditStockBoutiquesTable _boutiqueIdTable(_$AppDatabase db) =>
      db.creditStockBoutiques.createAlias($_aliasNameGenerator(
          db.creditStockVentes.boutiqueId, db.creditStockBoutiques.id));

  $$CreditStockBoutiquesTableProcessedTableManager get boutiqueId {
    final $_column = $_itemColumn<String>('boutique_id')!;

    final manager =
        $$CreditStockBoutiquesTableTableManager($_db, $_db.creditStockBoutiques)
            .filter((f) => f.id.sqlEquals($_column));
    final item = $_typedResult.readTableOrNull(_boutiqueIdTable($_db));
    if (item == null) return manager;
    return ProcessedTableManager(
        manager.$state.copyWith(prefetchedData: [item]));
  }

  static MultiTypedResultKey<$CreditStockLignesVenteTable,
      List<CreditStockLignesVenteData>> _creditStockLignesVenteRefsTable(
          _$AppDatabase db) =>
      MultiTypedResultKey.fromTable(db.creditStockLignesVente,
          aliasName: $_aliasNameGenerator(
              db.creditStockVentes.id, db.creditStockLignesVente.venteId));

  $$CreditStockLignesVenteTableProcessedTableManager
      get creditStockLignesVenteRefs {
    final manager = $$CreditStockLignesVenteTableTableManager(
            $_db, $_db.creditStockLignesVente)
        .filter((f) => f.venteId.id.sqlEquals($_itemColumn<String>('id')!));

    final cache =
        $_typedResult.readTableOrNull(_creditStockLignesVenteRefsTable($_db));
    return ProcessedTableManager(
        manager.$state.copyWith(prefetchedData: cache));
  }
}

class $$CreditStockVentesTableFilterComposer
    extends Composer<_$AppDatabase, $CreditStockVentesTable> {
  $$CreditStockVentesTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get utilisateurId => $composableBuilder(
      column: $table.utilisateurId, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get clientId => $composableBuilder(
      column: $table.clientId, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get typePaiement => $composableBuilder(
      column: $table.typePaiement, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get montantTotal => $composableBuilder(
      column: $table.montantTotal, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get note => $composableBuilder(
      column: $table.note, builder: (column) => ColumnFilters(column));

  ColumnFilters<bool> get synced => $composableBuilder(
      column: $table.synced, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get dateVente => $composableBuilder(
      column: $table.dateVente, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnFilters(column));

  $$CreditStockBoutiquesTableFilterComposer get boutiqueId {
    final $$CreditStockBoutiquesTableFilterComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.boutiqueId,
        referencedTable: $db.creditStockBoutiques,
        getReferencedColumn: (t) => t.id,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$CreditStockBoutiquesTableFilterComposer(
              $db: $db,
              $table: $db.creditStockBoutiques,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return composer;
  }

  Expression<bool> creditStockLignesVenteRefs(
      Expression<bool> Function($$CreditStockLignesVenteTableFilterComposer f)
          f) {
    final $$CreditStockLignesVenteTableFilterComposer composer =
        $composerBuilder(
            composer: this,
            getCurrentColumn: (t) => t.id,
            referencedTable: $db.creditStockLignesVente,
            getReferencedColumn: (t) => t.venteId,
            builder: (joinBuilder,
                    {$addJoinBuilderToRootComposer,
                    $removeJoinBuilderFromRootComposer}) =>
                $$CreditStockLignesVenteTableFilterComposer(
                  $db: $db,
                  $table: $db.creditStockLignesVente,
                  $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
                  joinBuilder: joinBuilder,
                  $removeJoinBuilderFromRootComposer:
                      $removeJoinBuilderFromRootComposer,
                ));
    return f(composer);
  }
}

class $$CreditStockVentesTableOrderingComposer
    extends Composer<_$AppDatabase, $CreditStockVentesTable> {
  $$CreditStockVentesTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get utilisateurId => $composableBuilder(
      column: $table.utilisateurId,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get clientId => $composableBuilder(
      column: $table.clientId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get typePaiement => $composableBuilder(
      column: $table.typePaiement,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get montantTotal => $composableBuilder(
      column: $table.montantTotal,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get note => $composableBuilder(
      column: $table.note, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<bool> get synced => $composableBuilder(
      column: $table.synced, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get dateVente => $composableBuilder(
      column: $table.dateVente, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnOrderings(column));

  $$CreditStockBoutiquesTableOrderingComposer get boutiqueId {
    final $$CreditStockBoutiquesTableOrderingComposer composer =
        $composerBuilder(
            composer: this,
            getCurrentColumn: (t) => t.boutiqueId,
            referencedTable: $db.creditStockBoutiques,
            getReferencedColumn: (t) => t.id,
            builder: (joinBuilder,
                    {$addJoinBuilderToRootComposer,
                    $removeJoinBuilderFromRootComposer}) =>
                $$CreditStockBoutiquesTableOrderingComposer(
                  $db: $db,
                  $table: $db.creditStockBoutiques,
                  $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
                  joinBuilder: joinBuilder,
                  $removeJoinBuilderFromRootComposer:
                      $removeJoinBuilderFromRootComposer,
                ));
    return composer;
  }
}

class $$CreditStockVentesTableAnnotationComposer
    extends Composer<_$AppDatabase, $CreditStockVentesTable> {
  $$CreditStockVentesTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get utilisateurId => $composableBuilder(
      column: $table.utilisateurId, builder: (column) => column);

  GeneratedColumn<String> get clientId =>
      $composableBuilder(column: $table.clientId, builder: (column) => column);

  GeneratedColumn<String> get typePaiement => $composableBuilder(
      column: $table.typePaiement, builder: (column) => column);

  GeneratedColumn<int> get montantTotal => $composableBuilder(
      column: $table.montantTotal, builder: (column) => column);

  GeneratedColumn<String> get note =>
      $composableBuilder(column: $table.note, builder: (column) => column);

  GeneratedColumn<bool> get synced =>
      $composableBuilder(column: $table.synced, builder: (column) => column);

  GeneratedColumn<DateTime> get dateVente =>
      $composableBuilder(column: $table.dateVente, builder: (column) => column);

  GeneratedColumn<DateTime> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);

  $$CreditStockBoutiquesTableAnnotationComposer get boutiqueId {
    final $$CreditStockBoutiquesTableAnnotationComposer composer =
        $composerBuilder(
            composer: this,
            getCurrentColumn: (t) => t.boutiqueId,
            referencedTable: $db.creditStockBoutiques,
            getReferencedColumn: (t) => t.id,
            builder: (joinBuilder,
                    {$addJoinBuilderToRootComposer,
                    $removeJoinBuilderFromRootComposer}) =>
                $$CreditStockBoutiquesTableAnnotationComposer(
                  $db: $db,
                  $table: $db.creditStockBoutiques,
                  $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
                  joinBuilder: joinBuilder,
                  $removeJoinBuilderFromRootComposer:
                      $removeJoinBuilderFromRootComposer,
                ));
    return composer;
  }

  Expression<T> creditStockLignesVenteRefs<T extends Object>(
      Expression<T> Function($$CreditStockLignesVenteTableAnnotationComposer a)
          f) {
    final $$CreditStockLignesVenteTableAnnotationComposer composer =
        $composerBuilder(
            composer: this,
            getCurrentColumn: (t) => t.id,
            referencedTable: $db.creditStockLignesVente,
            getReferencedColumn: (t) => t.venteId,
            builder: (joinBuilder,
                    {$addJoinBuilderToRootComposer,
                    $removeJoinBuilderFromRootComposer}) =>
                $$CreditStockLignesVenteTableAnnotationComposer(
                  $db: $db,
                  $table: $db.creditStockLignesVente,
                  $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
                  joinBuilder: joinBuilder,
                  $removeJoinBuilderFromRootComposer:
                      $removeJoinBuilderFromRootComposer,
                ));
    return f(composer);
  }
}

class $$CreditStockVentesTableTableManager extends RootTableManager<
    _$AppDatabase,
    $CreditStockVentesTable,
    CreditStockVente,
    $$CreditStockVentesTableFilterComposer,
    $$CreditStockVentesTableOrderingComposer,
    $$CreditStockVentesTableAnnotationComposer,
    $$CreditStockVentesTableCreateCompanionBuilder,
    $$CreditStockVentesTableUpdateCompanionBuilder,
    (CreditStockVente, $$CreditStockVentesTableReferences),
    CreditStockVente,
    PrefetchHooks Function(
        {bool boutiqueId, bool creditStockLignesVenteRefs})> {
  $$CreditStockVentesTableTableManager(
      _$AppDatabase db, $CreditStockVentesTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$CreditStockVentesTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$CreditStockVentesTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$CreditStockVentesTableAnnotationComposer(
                  $db: db, $table: table),
          updateCompanionCallback: ({
            Value<String> id = const Value.absent(),
            Value<String> boutiqueId = const Value.absent(),
            Value<String?> utilisateurId = const Value.absent(),
            Value<String?> clientId = const Value.absent(),
            Value<String> typePaiement = const Value.absent(),
            Value<int> montantTotal = const Value.absent(),
            Value<String?> note = const Value.absent(),
            Value<bool> synced = const Value.absent(),
            Value<DateTime> dateVente = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              CreditStockVentesCompanion(
            id: id,
            boutiqueId: boutiqueId,
            utilisateurId: utilisateurId,
            clientId: clientId,
            typePaiement: typePaiement,
            montantTotal: montantTotal,
            note: note,
            synced: synced,
            dateVente: dateVente,
            createdAt: createdAt,
            rowid: rowid,
          ),
          createCompanionCallback: ({
            required String id,
            required String boutiqueId,
            Value<String?> utilisateurId = const Value.absent(),
            Value<String?> clientId = const Value.absent(),
            Value<String> typePaiement = const Value.absent(),
            Value<int> montantTotal = const Value.absent(),
            Value<String?> note = const Value.absent(),
            Value<bool> synced = const Value.absent(),
            Value<DateTime> dateVente = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              CreditStockVentesCompanion.insert(
            id: id,
            boutiqueId: boutiqueId,
            utilisateurId: utilisateurId,
            clientId: clientId,
            typePaiement: typePaiement,
            montantTotal: montantTotal,
            note: note,
            synced: synced,
            dateVente: dateVente,
            createdAt: createdAt,
            rowid: rowid,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (
                    e.readTable(table),
                    $$CreditStockVentesTableReferences(db, table, e)
                  ))
              .toList(),
          prefetchHooksCallback: (
              {boutiqueId = false, creditStockLignesVenteRefs = false}) {
            return PrefetchHooks(
              db: db,
              explicitlyWatchedTables: [
                if (creditStockLignesVenteRefs) db.creditStockLignesVente
              ],
              addJoins: <
                  T extends TableManagerState<
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic>>(state) {
                if (boutiqueId) {
                  state = state.withJoin(
                    currentTable: table,
                    currentColumn: table.boutiqueId,
                    referencedTable:
                        $$CreditStockVentesTableReferences._boutiqueIdTable(db),
                    referencedColumn: $$CreditStockVentesTableReferences
                        ._boutiqueIdTable(db)
                        .id,
                  ) as T;
                }

                return state;
              },
              getPrefetchedDataCallback: (items) async {
                return [
                  if (creditStockLignesVenteRefs)
                    await $_getPrefetchedData<
                            CreditStockVente,
                            $CreditStockVentesTable,
                            CreditStockLignesVenteData>(
                        currentTable: table,
                        referencedTable: $$CreditStockVentesTableReferences
                            ._creditStockLignesVenteRefsTable(db),
                        managerFromTypedResult: (p0) =>
                            $$CreditStockVentesTableReferences(db, table, p0)
                                .creditStockLignesVenteRefs,
                        referencedItemsForCurrentItem: (item,
                                referencedItems) =>
                            referencedItems.where((e) => e.venteId == item.id),
                        typedResults: items)
                ];
              },
            );
          },
        ));
}

typedef $$CreditStockVentesTableProcessedTableManager = ProcessedTableManager<
    _$AppDatabase,
    $CreditStockVentesTable,
    CreditStockVente,
    $$CreditStockVentesTableFilterComposer,
    $$CreditStockVentesTableOrderingComposer,
    $$CreditStockVentesTableAnnotationComposer,
    $$CreditStockVentesTableCreateCompanionBuilder,
    $$CreditStockVentesTableUpdateCompanionBuilder,
    (CreditStockVente, $$CreditStockVentesTableReferences),
    CreditStockVente,
    PrefetchHooks Function({bool boutiqueId, bool creditStockLignesVenteRefs})>;
typedef $$CreditStockLignesVenteTableCreateCompanionBuilder
    = CreditStockLignesVenteCompanion Function({
  required String id,
  required String venteId,
  required String produitId,
  required String boutiqueId,
  required String nomProduit,
  Value<int> quantite,
  Value<int> prixUnitaire,
  Value<int> sousTotal,
  Value<bool> synced,
  Value<DateTime> createdAt,
  Value<int> rowid,
});
typedef $$CreditStockLignesVenteTableUpdateCompanionBuilder
    = CreditStockLignesVenteCompanion Function({
  Value<String> id,
  Value<String> venteId,
  Value<String> produitId,
  Value<String> boutiqueId,
  Value<String> nomProduit,
  Value<int> quantite,
  Value<int> prixUnitaire,
  Value<int> sousTotal,
  Value<bool> synced,
  Value<DateTime> createdAt,
  Value<int> rowid,
});

final class $$CreditStockLignesVenteTableReferences extends BaseReferences<
    _$AppDatabase, $CreditStockLignesVenteTable, CreditStockLignesVenteData> {
  $$CreditStockLignesVenteTableReferences(
      super.$_db, super.$_table, super.$_typedResult);

  static $CreditStockVentesTable _venteIdTable(_$AppDatabase db) =>
      db.creditStockVentes.createAlias($_aliasNameGenerator(
          db.creditStockLignesVente.venteId, db.creditStockVentes.id));

  $$CreditStockVentesTableProcessedTableManager get venteId {
    final $_column = $_itemColumn<String>('vente_id')!;

    final manager =
        $$CreditStockVentesTableTableManager($_db, $_db.creditStockVentes)
            .filter((f) => f.id.sqlEquals($_column));
    final item = $_typedResult.readTableOrNull(_venteIdTable($_db));
    if (item == null) return manager;
    return ProcessedTableManager(
        manager.$state.copyWith(prefetchedData: [item]));
  }
}

class $$CreditStockLignesVenteTableFilterComposer
    extends Composer<_$AppDatabase, $CreditStockLignesVenteTable> {
  $$CreditStockLignesVenteTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get produitId => $composableBuilder(
      column: $table.produitId, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get boutiqueId => $composableBuilder(
      column: $table.boutiqueId, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get nomProduit => $composableBuilder(
      column: $table.nomProduit, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get quantite => $composableBuilder(
      column: $table.quantite, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get prixUnitaire => $composableBuilder(
      column: $table.prixUnitaire, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get sousTotal => $composableBuilder(
      column: $table.sousTotal, builder: (column) => ColumnFilters(column));

  ColumnFilters<bool> get synced => $composableBuilder(
      column: $table.synced, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnFilters(column));

  $$CreditStockVentesTableFilterComposer get venteId {
    final $$CreditStockVentesTableFilterComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.venteId,
        referencedTable: $db.creditStockVentes,
        getReferencedColumn: (t) => t.id,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$CreditStockVentesTableFilterComposer(
              $db: $db,
              $table: $db.creditStockVentes,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return composer;
  }
}

class $$CreditStockLignesVenteTableOrderingComposer
    extends Composer<_$AppDatabase, $CreditStockLignesVenteTable> {
  $$CreditStockLignesVenteTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get produitId => $composableBuilder(
      column: $table.produitId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get boutiqueId => $composableBuilder(
      column: $table.boutiqueId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get nomProduit => $composableBuilder(
      column: $table.nomProduit, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get quantite => $composableBuilder(
      column: $table.quantite, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get prixUnitaire => $composableBuilder(
      column: $table.prixUnitaire,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get sousTotal => $composableBuilder(
      column: $table.sousTotal, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<bool> get synced => $composableBuilder(
      column: $table.synced, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnOrderings(column));

  $$CreditStockVentesTableOrderingComposer get venteId {
    final $$CreditStockVentesTableOrderingComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.venteId,
        referencedTable: $db.creditStockVentes,
        getReferencedColumn: (t) => t.id,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$CreditStockVentesTableOrderingComposer(
              $db: $db,
              $table: $db.creditStockVentes,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return composer;
  }
}

class $$CreditStockLignesVenteTableAnnotationComposer
    extends Composer<_$AppDatabase, $CreditStockLignesVenteTable> {
  $$CreditStockLignesVenteTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get produitId =>
      $composableBuilder(column: $table.produitId, builder: (column) => column);

  GeneratedColumn<String> get boutiqueId => $composableBuilder(
      column: $table.boutiqueId, builder: (column) => column);

  GeneratedColumn<String> get nomProduit => $composableBuilder(
      column: $table.nomProduit, builder: (column) => column);

  GeneratedColumn<int> get quantite =>
      $composableBuilder(column: $table.quantite, builder: (column) => column);

  GeneratedColumn<int> get prixUnitaire => $composableBuilder(
      column: $table.prixUnitaire, builder: (column) => column);

  GeneratedColumn<int> get sousTotal =>
      $composableBuilder(column: $table.sousTotal, builder: (column) => column);

  GeneratedColumn<bool> get synced =>
      $composableBuilder(column: $table.synced, builder: (column) => column);

  GeneratedColumn<DateTime> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);

  $$CreditStockVentesTableAnnotationComposer get venteId {
    final $$CreditStockVentesTableAnnotationComposer composer =
        $composerBuilder(
            composer: this,
            getCurrentColumn: (t) => t.venteId,
            referencedTable: $db.creditStockVentes,
            getReferencedColumn: (t) => t.id,
            builder: (joinBuilder,
                    {$addJoinBuilderToRootComposer,
                    $removeJoinBuilderFromRootComposer}) =>
                $$CreditStockVentesTableAnnotationComposer(
                  $db: $db,
                  $table: $db.creditStockVentes,
                  $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
                  joinBuilder: joinBuilder,
                  $removeJoinBuilderFromRootComposer:
                      $removeJoinBuilderFromRootComposer,
                ));
    return composer;
  }
}

class $$CreditStockLignesVenteTableTableManager extends RootTableManager<
    _$AppDatabase,
    $CreditStockLignesVenteTable,
    CreditStockLignesVenteData,
    $$CreditStockLignesVenteTableFilterComposer,
    $$CreditStockLignesVenteTableOrderingComposer,
    $$CreditStockLignesVenteTableAnnotationComposer,
    $$CreditStockLignesVenteTableCreateCompanionBuilder,
    $$CreditStockLignesVenteTableUpdateCompanionBuilder,
    (CreditStockLignesVenteData, $$CreditStockLignesVenteTableReferences),
    CreditStockLignesVenteData,
    PrefetchHooks Function({bool venteId})> {
  $$CreditStockLignesVenteTableTableManager(
      _$AppDatabase db, $CreditStockLignesVenteTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$CreditStockLignesVenteTableFilterComposer(
                  $db: db, $table: table),
          createOrderingComposer: () =>
              $$CreditStockLignesVenteTableOrderingComposer(
                  $db: db, $table: table),
          createComputedFieldComposer: () =>
              $$CreditStockLignesVenteTableAnnotationComposer(
                  $db: db, $table: table),
          updateCompanionCallback: ({
            Value<String> id = const Value.absent(),
            Value<String> venteId = const Value.absent(),
            Value<String> produitId = const Value.absent(),
            Value<String> boutiqueId = const Value.absent(),
            Value<String> nomProduit = const Value.absent(),
            Value<int> quantite = const Value.absent(),
            Value<int> prixUnitaire = const Value.absent(),
            Value<int> sousTotal = const Value.absent(),
            Value<bool> synced = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              CreditStockLignesVenteCompanion(
            id: id,
            venteId: venteId,
            produitId: produitId,
            boutiqueId: boutiqueId,
            nomProduit: nomProduit,
            quantite: quantite,
            prixUnitaire: prixUnitaire,
            sousTotal: sousTotal,
            synced: synced,
            createdAt: createdAt,
            rowid: rowid,
          ),
          createCompanionCallback: ({
            required String id,
            required String venteId,
            required String produitId,
            required String boutiqueId,
            required String nomProduit,
            Value<int> quantite = const Value.absent(),
            Value<int> prixUnitaire = const Value.absent(),
            Value<int> sousTotal = const Value.absent(),
            Value<bool> synced = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              CreditStockLignesVenteCompanion.insert(
            id: id,
            venteId: venteId,
            produitId: produitId,
            boutiqueId: boutiqueId,
            nomProduit: nomProduit,
            quantite: quantite,
            prixUnitaire: prixUnitaire,
            sousTotal: sousTotal,
            synced: synced,
            createdAt: createdAt,
            rowid: rowid,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (
                    e.readTable(table),
                    $$CreditStockLignesVenteTableReferences(db, table, e)
                  ))
              .toList(),
          prefetchHooksCallback: ({venteId = false}) {
            return PrefetchHooks(
              db: db,
              explicitlyWatchedTables: [],
              addJoins: <
                  T extends TableManagerState<
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic>>(state) {
                if (venteId) {
                  state = state.withJoin(
                    currentTable: table,
                    currentColumn: table.venteId,
                    referencedTable: $$CreditStockLignesVenteTableReferences
                        ._venteIdTable(db),
                    referencedColumn: $$CreditStockLignesVenteTableReferences
                        ._venteIdTable(db)
                        .id,
                  ) as T;
                }

                return state;
              },
              getPrefetchedDataCallback: (items) async {
                return [];
              },
            );
          },
        ));
}

typedef $$CreditStockLignesVenteTableProcessedTableManager
    = ProcessedTableManager<
        _$AppDatabase,
        $CreditStockLignesVenteTable,
        CreditStockLignesVenteData,
        $$CreditStockLignesVenteTableFilterComposer,
        $$CreditStockLignesVenteTableOrderingComposer,
        $$CreditStockLignesVenteTableAnnotationComposer,
        $$CreditStockLignesVenteTableCreateCompanionBuilder,
        $$CreditStockLignesVenteTableUpdateCompanionBuilder,
        (CreditStockLignesVenteData, $$CreditStockLignesVenteTableReferences),
        CreditStockLignesVenteData,
        PrefetchHooks Function({bool venteId})>;
typedef $$CreditStockDettesTableCreateCompanionBuilder
    = CreditStockDettesCompanion Function({
  required String id,
  required String boutiqueId,
  required String clientId,
  Value<String?> venteId,
  Value<int> montantInitial,
  Value<int> montantPaye,
  Value<String> statut,
  Value<DateTime?> dateEcheance,
  Value<String?> note,
  Value<bool> synced,
  Value<DateTime> createdAt,
  Value<DateTime> updatedAt,
  Value<int> rowid,
});
typedef $$CreditStockDettesTableUpdateCompanionBuilder
    = CreditStockDettesCompanion Function({
  Value<String> id,
  Value<String> boutiqueId,
  Value<String> clientId,
  Value<String?> venteId,
  Value<int> montantInitial,
  Value<int> montantPaye,
  Value<String> statut,
  Value<DateTime?> dateEcheance,
  Value<String?> note,
  Value<bool> synced,
  Value<DateTime> createdAt,
  Value<DateTime> updatedAt,
  Value<int> rowid,
});

final class $$CreditStockDettesTableReferences extends BaseReferences<
    _$AppDatabase, $CreditStockDettesTable, CreditStockDette> {
  $$CreditStockDettesTableReferences(
      super.$_db, super.$_table, super.$_typedResult);

  static $CreditStockBoutiquesTable _boutiqueIdTable(_$AppDatabase db) =>
      db.creditStockBoutiques.createAlias($_aliasNameGenerator(
          db.creditStockDettes.boutiqueId, db.creditStockBoutiques.id));

  $$CreditStockBoutiquesTableProcessedTableManager get boutiqueId {
    final $_column = $_itemColumn<String>('boutique_id')!;

    final manager =
        $$CreditStockBoutiquesTableTableManager($_db, $_db.creditStockBoutiques)
            .filter((f) => f.id.sqlEquals($_column));
    final item = $_typedResult.readTableOrNull(_boutiqueIdTable($_db));
    if (item == null) return manager;
    return ProcessedTableManager(
        manager.$state.copyWith(prefetchedData: [item]));
  }

  static $CreditStockClientsTable _clientIdTable(_$AppDatabase db) =>
      db.creditStockClients.createAlias($_aliasNameGenerator(
          db.creditStockDettes.clientId, db.creditStockClients.id));

  $$CreditStockClientsTableProcessedTableManager get clientId {
    final $_column = $_itemColumn<String>('client_id')!;

    final manager =
        $$CreditStockClientsTableTableManager($_db, $_db.creditStockClients)
            .filter((f) => f.id.sqlEquals($_column));
    final item = $_typedResult.readTableOrNull(_clientIdTable($_db));
    if (item == null) return manager;
    return ProcessedTableManager(
        manager.$state.copyWith(prefetchedData: [item]));
  }

  static MultiTypedResultKey<$CreditStockPaiementsTable,
      List<CreditStockPaiement>> _creditStockPaiementsRefsTable(
          _$AppDatabase db) =>
      MultiTypedResultKey.fromTable(db.creditStockPaiements,
          aliasName: $_aliasNameGenerator(
              db.creditStockDettes.id, db.creditStockPaiements.detteId));

  $$CreditStockPaiementsTableProcessedTableManager
      get creditStockPaiementsRefs {
    final manager =
        $$CreditStockPaiementsTableTableManager($_db, $_db.creditStockPaiements)
            .filter((f) => f.detteId.id.sqlEquals($_itemColumn<String>('id')!));

    final cache =
        $_typedResult.readTableOrNull(_creditStockPaiementsRefsTable($_db));
    return ProcessedTableManager(
        manager.$state.copyWith(prefetchedData: cache));
  }
}

class $$CreditStockDettesTableFilterComposer
    extends Composer<_$AppDatabase, $CreditStockDettesTable> {
  $$CreditStockDettesTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get venteId => $composableBuilder(
      column: $table.venteId, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get montantInitial => $composableBuilder(
      column: $table.montantInitial,
      builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get montantPaye => $composableBuilder(
      column: $table.montantPaye, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get statut => $composableBuilder(
      column: $table.statut, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get dateEcheance => $composableBuilder(
      column: $table.dateEcheance, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get note => $composableBuilder(
      column: $table.note, builder: (column) => ColumnFilters(column));

  ColumnFilters<bool> get synced => $composableBuilder(
      column: $table.synced, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get updatedAt => $composableBuilder(
      column: $table.updatedAt, builder: (column) => ColumnFilters(column));

  $$CreditStockBoutiquesTableFilterComposer get boutiqueId {
    final $$CreditStockBoutiquesTableFilterComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.boutiqueId,
        referencedTable: $db.creditStockBoutiques,
        getReferencedColumn: (t) => t.id,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$CreditStockBoutiquesTableFilterComposer(
              $db: $db,
              $table: $db.creditStockBoutiques,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return composer;
  }

  $$CreditStockClientsTableFilterComposer get clientId {
    final $$CreditStockClientsTableFilterComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.clientId,
        referencedTable: $db.creditStockClients,
        getReferencedColumn: (t) => t.id,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$CreditStockClientsTableFilterComposer(
              $db: $db,
              $table: $db.creditStockClients,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return composer;
  }

  Expression<bool> creditStockPaiementsRefs(
      Expression<bool> Function($$CreditStockPaiementsTableFilterComposer f)
          f) {
    final $$CreditStockPaiementsTableFilterComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.id,
        referencedTable: $db.creditStockPaiements,
        getReferencedColumn: (t) => t.detteId,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$CreditStockPaiementsTableFilterComposer(
              $db: $db,
              $table: $db.creditStockPaiements,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return f(composer);
  }
}

class $$CreditStockDettesTableOrderingComposer
    extends Composer<_$AppDatabase, $CreditStockDettesTable> {
  $$CreditStockDettesTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get venteId => $composableBuilder(
      column: $table.venteId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get montantInitial => $composableBuilder(
      column: $table.montantInitial,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get montantPaye => $composableBuilder(
      column: $table.montantPaye, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get statut => $composableBuilder(
      column: $table.statut, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get dateEcheance => $composableBuilder(
      column: $table.dateEcheance,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get note => $composableBuilder(
      column: $table.note, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<bool> get synced => $composableBuilder(
      column: $table.synced, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get updatedAt => $composableBuilder(
      column: $table.updatedAt, builder: (column) => ColumnOrderings(column));

  $$CreditStockBoutiquesTableOrderingComposer get boutiqueId {
    final $$CreditStockBoutiquesTableOrderingComposer composer =
        $composerBuilder(
            composer: this,
            getCurrentColumn: (t) => t.boutiqueId,
            referencedTable: $db.creditStockBoutiques,
            getReferencedColumn: (t) => t.id,
            builder: (joinBuilder,
                    {$addJoinBuilderToRootComposer,
                    $removeJoinBuilderFromRootComposer}) =>
                $$CreditStockBoutiquesTableOrderingComposer(
                  $db: $db,
                  $table: $db.creditStockBoutiques,
                  $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
                  joinBuilder: joinBuilder,
                  $removeJoinBuilderFromRootComposer:
                      $removeJoinBuilderFromRootComposer,
                ));
    return composer;
  }

  $$CreditStockClientsTableOrderingComposer get clientId {
    final $$CreditStockClientsTableOrderingComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.clientId,
        referencedTable: $db.creditStockClients,
        getReferencedColumn: (t) => t.id,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$CreditStockClientsTableOrderingComposer(
              $db: $db,
              $table: $db.creditStockClients,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return composer;
  }
}

class $$CreditStockDettesTableAnnotationComposer
    extends Composer<_$AppDatabase, $CreditStockDettesTable> {
  $$CreditStockDettesTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get venteId =>
      $composableBuilder(column: $table.venteId, builder: (column) => column);

  GeneratedColumn<int> get montantInitial => $composableBuilder(
      column: $table.montantInitial, builder: (column) => column);

  GeneratedColumn<int> get montantPaye => $composableBuilder(
      column: $table.montantPaye, builder: (column) => column);

  GeneratedColumn<String> get statut =>
      $composableBuilder(column: $table.statut, builder: (column) => column);

  GeneratedColumn<DateTime> get dateEcheance => $composableBuilder(
      column: $table.dateEcheance, builder: (column) => column);

  GeneratedColumn<String> get note =>
      $composableBuilder(column: $table.note, builder: (column) => column);

  GeneratedColumn<bool> get synced =>
      $composableBuilder(column: $table.synced, builder: (column) => column);

  GeneratedColumn<DateTime> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);

  GeneratedColumn<DateTime> get updatedAt =>
      $composableBuilder(column: $table.updatedAt, builder: (column) => column);

  $$CreditStockBoutiquesTableAnnotationComposer get boutiqueId {
    final $$CreditStockBoutiquesTableAnnotationComposer composer =
        $composerBuilder(
            composer: this,
            getCurrentColumn: (t) => t.boutiqueId,
            referencedTable: $db.creditStockBoutiques,
            getReferencedColumn: (t) => t.id,
            builder: (joinBuilder,
                    {$addJoinBuilderToRootComposer,
                    $removeJoinBuilderFromRootComposer}) =>
                $$CreditStockBoutiquesTableAnnotationComposer(
                  $db: $db,
                  $table: $db.creditStockBoutiques,
                  $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
                  joinBuilder: joinBuilder,
                  $removeJoinBuilderFromRootComposer:
                      $removeJoinBuilderFromRootComposer,
                ));
    return composer;
  }

  $$CreditStockClientsTableAnnotationComposer get clientId {
    final $$CreditStockClientsTableAnnotationComposer composer =
        $composerBuilder(
            composer: this,
            getCurrentColumn: (t) => t.clientId,
            referencedTable: $db.creditStockClients,
            getReferencedColumn: (t) => t.id,
            builder: (joinBuilder,
                    {$addJoinBuilderToRootComposer,
                    $removeJoinBuilderFromRootComposer}) =>
                $$CreditStockClientsTableAnnotationComposer(
                  $db: $db,
                  $table: $db.creditStockClients,
                  $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
                  joinBuilder: joinBuilder,
                  $removeJoinBuilderFromRootComposer:
                      $removeJoinBuilderFromRootComposer,
                ));
    return composer;
  }

  Expression<T> creditStockPaiementsRefs<T extends Object>(
      Expression<T> Function($$CreditStockPaiementsTableAnnotationComposer a)
          f) {
    final $$CreditStockPaiementsTableAnnotationComposer composer =
        $composerBuilder(
            composer: this,
            getCurrentColumn: (t) => t.id,
            referencedTable: $db.creditStockPaiements,
            getReferencedColumn: (t) => t.detteId,
            builder: (joinBuilder,
                    {$addJoinBuilderToRootComposer,
                    $removeJoinBuilderFromRootComposer}) =>
                $$CreditStockPaiementsTableAnnotationComposer(
                  $db: $db,
                  $table: $db.creditStockPaiements,
                  $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
                  joinBuilder: joinBuilder,
                  $removeJoinBuilderFromRootComposer:
                      $removeJoinBuilderFromRootComposer,
                ));
    return f(composer);
  }
}

class $$CreditStockDettesTableTableManager extends RootTableManager<
    _$AppDatabase,
    $CreditStockDettesTable,
    CreditStockDette,
    $$CreditStockDettesTableFilterComposer,
    $$CreditStockDettesTableOrderingComposer,
    $$CreditStockDettesTableAnnotationComposer,
    $$CreditStockDettesTableCreateCompanionBuilder,
    $$CreditStockDettesTableUpdateCompanionBuilder,
    (CreditStockDette, $$CreditStockDettesTableReferences),
    CreditStockDette,
    PrefetchHooks Function(
        {bool boutiqueId, bool clientId, bool creditStockPaiementsRefs})> {
  $$CreditStockDettesTableTableManager(
      _$AppDatabase db, $CreditStockDettesTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$CreditStockDettesTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$CreditStockDettesTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$CreditStockDettesTableAnnotationComposer(
                  $db: db, $table: table),
          updateCompanionCallback: ({
            Value<String> id = const Value.absent(),
            Value<String> boutiqueId = const Value.absent(),
            Value<String> clientId = const Value.absent(),
            Value<String?> venteId = const Value.absent(),
            Value<int> montantInitial = const Value.absent(),
            Value<int> montantPaye = const Value.absent(),
            Value<String> statut = const Value.absent(),
            Value<DateTime?> dateEcheance = const Value.absent(),
            Value<String?> note = const Value.absent(),
            Value<bool> synced = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
            Value<DateTime> updatedAt = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              CreditStockDettesCompanion(
            id: id,
            boutiqueId: boutiqueId,
            clientId: clientId,
            venteId: venteId,
            montantInitial: montantInitial,
            montantPaye: montantPaye,
            statut: statut,
            dateEcheance: dateEcheance,
            note: note,
            synced: synced,
            createdAt: createdAt,
            updatedAt: updatedAt,
            rowid: rowid,
          ),
          createCompanionCallback: ({
            required String id,
            required String boutiqueId,
            required String clientId,
            Value<String?> venteId = const Value.absent(),
            Value<int> montantInitial = const Value.absent(),
            Value<int> montantPaye = const Value.absent(),
            Value<String> statut = const Value.absent(),
            Value<DateTime?> dateEcheance = const Value.absent(),
            Value<String?> note = const Value.absent(),
            Value<bool> synced = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
            Value<DateTime> updatedAt = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              CreditStockDettesCompanion.insert(
            id: id,
            boutiqueId: boutiqueId,
            clientId: clientId,
            venteId: venteId,
            montantInitial: montantInitial,
            montantPaye: montantPaye,
            statut: statut,
            dateEcheance: dateEcheance,
            note: note,
            synced: synced,
            createdAt: createdAt,
            updatedAt: updatedAt,
            rowid: rowid,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (
                    e.readTable(table),
                    $$CreditStockDettesTableReferences(db, table, e)
                  ))
              .toList(),
          prefetchHooksCallback: (
              {boutiqueId = false,
              clientId = false,
              creditStockPaiementsRefs = false}) {
            return PrefetchHooks(
              db: db,
              explicitlyWatchedTables: [
                if (creditStockPaiementsRefs) db.creditStockPaiements
              ],
              addJoins: <
                  T extends TableManagerState<
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic>>(state) {
                if (boutiqueId) {
                  state = state.withJoin(
                    currentTable: table,
                    currentColumn: table.boutiqueId,
                    referencedTable:
                        $$CreditStockDettesTableReferences._boutiqueIdTable(db),
                    referencedColumn: $$CreditStockDettesTableReferences
                        ._boutiqueIdTable(db)
                        .id,
                  ) as T;
                }
                if (clientId) {
                  state = state.withJoin(
                    currentTable: table,
                    currentColumn: table.clientId,
                    referencedTable:
                        $$CreditStockDettesTableReferences._clientIdTable(db),
                    referencedColumn: $$CreditStockDettesTableReferences
                        ._clientIdTable(db)
                        .id,
                  ) as T;
                }

                return state;
              },
              getPrefetchedDataCallback: (items) async {
                return [
                  if (creditStockPaiementsRefs)
                    await $_getPrefetchedData<CreditStockDette,
                            $CreditStockDettesTable, CreditStockPaiement>(
                        currentTable: table,
                        referencedTable: $$CreditStockDettesTableReferences
                            ._creditStockPaiementsRefsTable(db),
                        managerFromTypedResult: (p0) =>
                            $$CreditStockDettesTableReferences(db, table, p0)
                                .creditStockPaiementsRefs,
                        referencedItemsForCurrentItem: (item,
                                referencedItems) =>
                            referencedItems.where((e) => e.detteId == item.id),
                        typedResults: items)
                ];
              },
            );
          },
        ));
}

typedef $$CreditStockDettesTableProcessedTableManager = ProcessedTableManager<
    _$AppDatabase,
    $CreditStockDettesTable,
    CreditStockDette,
    $$CreditStockDettesTableFilterComposer,
    $$CreditStockDettesTableOrderingComposer,
    $$CreditStockDettesTableAnnotationComposer,
    $$CreditStockDettesTableCreateCompanionBuilder,
    $$CreditStockDettesTableUpdateCompanionBuilder,
    (CreditStockDette, $$CreditStockDettesTableReferences),
    CreditStockDette,
    PrefetchHooks Function(
        {bool boutiqueId, bool clientId, bool creditStockPaiementsRefs})>;
typedef $$CreditStockPaiementsTableCreateCompanionBuilder
    = CreditStockPaiementsCompanion Function({
  required String id,
  required String boutiqueId,
  required String detteId,
  required String clientId,
  Value<int> montant,
  Value<String> modePaiement,
  Value<String?> note,
  Value<bool> synced,
  Value<DateTime> createdAt,
  Value<int> rowid,
});
typedef $$CreditStockPaiementsTableUpdateCompanionBuilder
    = CreditStockPaiementsCompanion Function({
  Value<String> id,
  Value<String> boutiqueId,
  Value<String> detteId,
  Value<String> clientId,
  Value<int> montant,
  Value<String> modePaiement,
  Value<String?> note,
  Value<bool> synced,
  Value<DateTime> createdAt,
  Value<int> rowid,
});

final class $$CreditStockPaiementsTableReferences extends BaseReferences<
    _$AppDatabase, $CreditStockPaiementsTable, CreditStockPaiement> {
  $$CreditStockPaiementsTableReferences(
      super.$_db, super.$_table, super.$_typedResult);

  static $CreditStockDettesTable _detteIdTable(_$AppDatabase db) =>
      db.creditStockDettes.createAlias($_aliasNameGenerator(
          db.creditStockPaiements.detteId, db.creditStockDettes.id));

  $$CreditStockDettesTableProcessedTableManager get detteId {
    final $_column = $_itemColumn<String>('dette_id')!;

    final manager =
        $$CreditStockDettesTableTableManager($_db, $_db.creditStockDettes)
            .filter((f) => f.id.sqlEquals($_column));
    final item = $_typedResult.readTableOrNull(_detteIdTable($_db));
    if (item == null) return manager;
    return ProcessedTableManager(
        manager.$state.copyWith(prefetchedData: [item]));
  }
}

class $$CreditStockPaiementsTableFilterComposer
    extends Composer<_$AppDatabase, $CreditStockPaiementsTable> {
  $$CreditStockPaiementsTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get boutiqueId => $composableBuilder(
      column: $table.boutiqueId, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get clientId => $composableBuilder(
      column: $table.clientId, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get montant => $composableBuilder(
      column: $table.montant, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get modePaiement => $composableBuilder(
      column: $table.modePaiement, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get note => $composableBuilder(
      column: $table.note, builder: (column) => ColumnFilters(column));

  ColumnFilters<bool> get synced => $composableBuilder(
      column: $table.synced, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnFilters(column));

  $$CreditStockDettesTableFilterComposer get detteId {
    final $$CreditStockDettesTableFilterComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.detteId,
        referencedTable: $db.creditStockDettes,
        getReferencedColumn: (t) => t.id,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$CreditStockDettesTableFilterComposer(
              $db: $db,
              $table: $db.creditStockDettes,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return composer;
  }
}

class $$CreditStockPaiementsTableOrderingComposer
    extends Composer<_$AppDatabase, $CreditStockPaiementsTable> {
  $$CreditStockPaiementsTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get boutiqueId => $composableBuilder(
      column: $table.boutiqueId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get clientId => $composableBuilder(
      column: $table.clientId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get montant => $composableBuilder(
      column: $table.montant, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get modePaiement => $composableBuilder(
      column: $table.modePaiement,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get note => $composableBuilder(
      column: $table.note, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<bool> get synced => $composableBuilder(
      column: $table.synced, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnOrderings(column));

  $$CreditStockDettesTableOrderingComposer get detteId {
    final $$CreditStockDettesTableOrderingComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.detteId,
        referencedTable: $db.creditStockDettes,
        getReferencedColumn: (t) => t.id,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$CreditStockDettesTableOrderingComposer(
              $db: $db,
              $table: $db.creditStockDettes,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return composer;
  }
}

class $$CreditStockPaiementsTableAnnotationComposer
    extends Composer<_$AppDatabase, $CreditStockPaiementsTable> {
  $$CreditStockPaiementsTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get boutiqueId => $composableBuilder(
      column: $table.boutiqueId, builder: (column) => column);

  GeneratedColumn<String> get clientId =>
      $composableBuilder(column: $table.clientId, builder: (column) => column);

  GeneratedColumn<int> get montant =>
      $composableBuilder(column: $table.montant, builder: (column) => column);

  GeneratedColumn<String> get modePaiement => $composableBuilder(
      column: $table.modePaiement, builder: (column) => column);

  GeneratedColumn<String> get note =>
      $composableBuilder(column: $table.note, builder: (column) => column);

  GeneratedColumn<bool> get synced =>
      $composableBuilder(column: $table.synced, builder: (column) => column);

  GeneratedColumn<DateTime> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);

  $$CreditStockDettesTableAnnotationComposer get detteId {
    final $$CreditStockDettesTableAnnotationComposer composer =
        $composerBuilder(
            composer: this,
            getCurrentColumn: (t) => t.detteId,
            referencedTable: $db.creditStockDettes,
            getReferencedColumn: (t) => t.id,
            builder: (joinBuilder,
                    {$addJoinBuilderToRootComposer,
                    $removeJoinBuilderFromRootComposer}) =>
                $$CreditStockDettesTableAnnotationComposer(
                  $db: $db,
                  $table: $db.creditStockDettes,
                  $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
                  joinBuilder: joinBuilder,
                  $removeJoinBuilderFromRootComposer:
                      $removeJoinBuilderFromRootComposer,
                ));
    return composer;
  }
}

class $$CreditStockPaiementsTableTableManager extends RootTableManager<
    _$AppDatabase,
    $CreditStockPaiementsTable,
    CreditStockPaiement,
    $$CreditStockPaiementsTableFilterComposer,
    $$CreditStockPaiementsTableOrderingComposer,
    $$CreditStockPaiementsTableAnnotationComposer,
    $$CreditStockPaiementsTableCreateCompanionBuilder,
    $$CreditStockPaiementsTableUpdateCompanionBuilder,
    (CreditStockPaiement, $$CreditStockPaiementsTableReferences),
    CreditStockPaiement,
    PrefetchHooks Function({bool detteId})> {
  $$CreditStockPaiementsTableTableManager(
      _$AppDatabase db, $CreditStockPaiementsTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$CreditStockPaiementsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$CreditStockPaiementsTableOrderingComposer(
                  $db: db, $table: table),
          createComputedFieldComposer: () =>
              $$CreditStockPaiementsTableAnnotationComposer(
                  $db: db, $table: table),
          updateCompanionCallback: ({
            Value<String> id = const Value.absent(),
            Value<String> boutiqueId = const Value.absent(),
            Value<String> detteId = const Value.absent(),
            Value<String> clientId = const Value.absent(),
            Value<int> montant = const Value.absent(),
            Value<String> modePaiement = const Value.absent(),
            Value<String?> note = const Value.absent(),
            Value<bool> synced = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              CreditStockPaiementsCompanion(
            id: id,
            boutiqueId: boutiqueId,
            detteId: detteId,
            clientId: clientId,
            montant: montant,
            modePaiement: modePaiement,
            note: note,
            synced: synced,
            createdAt: createdAt,
            rowid: rowid,
          ),
          createCompanionCallback: ({
            required String id,
            required String boutiqueId,
            required String detteId,
            required String clientId,
            Value<int> montant = const Value.absent(),
            Value<String> modePaiement = const Value.absent(),
            Value<String?> note = const Value.absent(),
            Value<bool> synced = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              CreditStockPaiementsCompanion.insert(
            id: id,
            boutiqueId: boutiqueId,
            detteId: detteId,
            clientId: clientId,
            montant: montant,
            modePaiement: modePaiement,
            note: note,
            synced: synced,
            createdAt: createdAt,
            rowid: rowid,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (
                    e.readTable(table),
                    $$CreditStockPaiementsTableReferences(db, table, e)
                  ))
              .toList(),
          prefetchHooksCallback: ({detteId = false}) {
            return PrefetchHooks(
              db: db,
              explicitlyWatchedTables: [],
              addJoins: <
                  T extends TableManagerState<
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic,
                      dynamic>>(state) {
                if (detteId) {
                  state = state.withJoin(
                    currentTable: table,
                    currentColumn: table.detteId,
                    referencedTable:
                        $$CreditStockPaiementsTableReferences._detteIdTable(db),
                    referencedColumn: $$CreditStockPaiementsTableReferences
                        ._detteIdTable(db)
                        .id,
                  ) as T;
                }

                return state;
              },
              getPrefetchedDataCallback: (items) async {
                return [];
              },
            );
          },
        ));
}

typedef $$CreditStockPaiementsTableProcessedTableManager
    = ProcessedTableManager<
        _$AppDatabase,
        $CreditStockPaiementsTable,
        CreditStockPaiement,
        $$CreditStockPaiementsTableFilterComposer,
        $$CreditStockPaiementsTableOrderingComposer,
        $$CreditStockPaiementsTableAnnotationComposer,
        $$CreditStockPaiementsTableCreateCompanionBuilder,
        $$CreditStockPaiementsTableUpdateCompanionBuilder,
        (CreditStockPaiement, $$CreditStockPaiementsTableReferences),
        CreditStockPaiement,
        PrefetchHooks Function({bool detteId})>;
typedef $$CreditStockSyncQueueTableCreateCompanionBuilder
    = CreditStockSyncQueueCompanion Function({
  required String id,
  required String boutiqueId,
  required String tableName_,
  required String operation,
  required String recordId,
  required String payload,
  Value<String> statut,
  Value<int> tentatives,
  Value<String?> errorMsg,
  Value<DateTime> createdAt,
  Value<DateTime?> syncedAt,
  Value<int> rowid,
});
typedef $$CreditStockSyncQueueTableUpdateCompanionBuilder
    = CreditStockSyncQueueCompanion Function({
  Value<String> id,
  Value<String> boutiqueId,
  Value<String> tableName_,
  Value<String> operation,
  Value<String> recordId,
  Value<String> payload,
  Value<String> statut,
  Value<int> tentatives,
  Value<String?> errorMsg,
  Value<DateTime> createdAt,
  Value<DateTime?> syncedAt,
  Value<int> rowid,
});

class $$CreditStockSyncQueueTableFilterComposer
    extends Composer<_$AppDatabase, $CreditStockSyncQueueTable> {
  $$CreditStockSyncQueueTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get boutiqueId => $composableBuilder(
      column: $table.boutiqueId, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get tableName_ => $composableBuilder(
      column: $table.tableName_, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get operation => $composableBuilder(
      column: $table.operation, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get recordId => $composableBuilder(
      column: $table.recordId, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get payload => $composableBuilder(
      column: $table.payload, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get statut => $composableBuilder(
      column: $table.statut, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get tentatives => $composableBuilder(
      column: $table.tentatives, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get errorMsg => $composableBuilder(
      column: $table.errorMsg, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get syncedAt => $composableBuilder(
      column: $table.syncedAt, builder: (column) => ColumnFilters(column));
}

class $$CreditStockSyncQueueTableOrderingComposer
    extends Composer<_$AppDatabase, $CreditStockSyncQueueTable> {
  $$CreditStockSyncQueueTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get boutiqueId => $composableBuilder(
      column: $table.boutiqueId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get tableName_ => $composableBuilder(
      column: $table.tableName_, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get operation => $composableBuilder(
      column: $table.operation, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get recordId => $composableBuilder(
      column: $table.recordId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get payload => $composableBuilder(
      column: $table.payload, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get statut => $composableBuilder(
      column: $table.statut, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get tentatives => $composableBuilder(
      column: $table.tentatives, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get errorMsg => $composableBuilder(
      column: $table.errorMsg, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get syncedAt => $composableBuilder(
      column: $table.syncedAt, builder: (column) => ColumnOrderings(column));
}

class $$CreditStockSyncQueueTableAnnotationComposer
    extends Composer<_$AppDatabase, $CreditStockSyncQueueTable> {
  $$CreditStockSyncQueueTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get boutiqueId => $composableBuilder(
      column: $table.boutiqueId, builder: (column) => column);

  GeneratedColumn<String> get tableName_ => $composableBuilder(
      column: $table.tableName_, builder: (column) => column);

  GeneratedColumn<String> get operation =>
      $composableBuilder(column: $table.operation, builder: (column) => column);

  GeneratedColumn<String> get recordId =>
      $composableBuilder(column: $table.recordId, builder: (column) => column);

  GeneratedColumn<String> get payload =>
      $composableBuilder(column: $table.payload, builder: (column) => column);

  GeneratedColumn<String> get statut =>
      $composableBuilder(column: $table.statut, builder: (column) => column);

  GeneratedColumn<int> get tentatives => $composableBuilder(
      column: $table.tentatives, builder: (column) => column);

  GeneratedColumn<String> get errorMsg =>
      $composableBuilder(column: $table.errorMsg, builder: (column) => column);

  GeneratedColumn<DateTime> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);

  GeneratedColumn<DateTime> get syncedAt =>
      $composableBuilder(column: $table.syncedAt, builder: (column) => column);
}

class $$CreditStockSyncQueueTableTableManager extends RootTableManager<
    _$AppDatabase,
    $CreditStockSyncQueueTable,
    CreditStockSyncQueueData,
    $$CreditStockSyncQueueTableFilterComposer,
    $$CreditStockSyncQueueTableOrderingComposer,
    $$CreditStockSyncQueueTableAnnotationComposer,
    $$CreditStockSyncQueueTableCreateCompanionBuilder,
    $$CreditStockSyncQueueTableUpdateCompanionBuilder,
    (
      CreditStockSyncQueueData,
      BaseReferences<_$AppDatabase, $CreditStockSyncQueueTable,
          CreditStockSyncQueueData>
    ),
    CreditStockSyncQueueData,
    PrefetchHooks Function()> {
  $$CreditStockSyncQueueTableTableManager(
      _$AppDatabase db, $CreditStockSyncQueueTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$CreditStockSyncQueueTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$CreditStockSyncQueueTableOrderingComposer(
                  $db: db, $table: table),
          createComputedFieldComposer: () =>
              $$CreditStockSyncQueueTableAnnotationComposer(
                  $db: db, $table: table),
          updateCompanionCallback: ({
            Value<String> id = const Value.absent(),
            Value<String> boutiqueId = const Value.absent(),
            Value<String> tableName_ = const Value.absent(),
            Value<String> operation = const Value.absent(),
            Value<String> recordId = const Value.absent(),
            Value<String> payload = const Value.absent(),
            Value<String> statut = const Value.absent(),
            Value<int> tentatives = const Value.absent(),
            Value<String?> errorMsg = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
            Value<DateTime?> syncedAt = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              CreditStockSyncQueueCompanion(
            id: id,
            boutiqueId: boutiqueId,
            tableName_: tableName_,
            operation: operation,
            recordId: recordId,
            payload: payload,
            statut: statut,
            tentatives: tentatives,
            errorMsg: errorMsg,
            createdAt: createdAt,
            syncedAt: syncedAt,
            rowid: rowid,
          ),
          createCompanionCallback: ({
            required String id,
            required String boutiqueId,
            required String tableName_,
            required String operation,
            required String recordId,
            required String payload,
            Value<String> statut = const Value.absent(),
            Value<int> tentatives = const Value.absent(),
            Value<String?> errorMsg = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
            Value<DateTime?> syncedAt = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              CreditStockSyncQueueCompanion.insert(
            id: id,
            boutiqueId: boutiqueId,
            tableName_: tableName_,
            operation: operation,
            recordId: recordId,
            payload: payload,
            statut: statut,
            tentatives: tentatives,
            errorMsg: errorMsg,
            createdAt: createdAt,
            syncedAt: syncedAt,
            rowid: rowid,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ));
}

typedef $$CreditStockSyncQueueTableProcessedTableManager
    = ProcessedTableManager<
        _$AppDatabase,
        $CreditStockSyncQueueTable,
        CreditStockSyncQueueData,
        $$CreditStockSyncQueueTableFilterComposer,
        $$CreditStockSyncQueueTableOrderingComposer,
        $$CreditStockSyncQueueTableAnnotationComposer,
        $$CreditStockSyncQueueTableCreateCompanionBuilder,
        $$CreditStockSyncQueueTableUpdateCompanionBuilder,
        (
          CreditStockSyncQueueData,
          BaseReferences<_$AppDatabase, $CreditStockSyncQueueTable,
              CreditStockSyncQueueData>
        ),
        CreditStockSyncQueueData,
        PrefetchHooks Function()>;
typedef $$CreditStockAlertesTableCreateCompanionBuilder
    = CreditStockAlertesCompanion Function({
  required String id,
  required String boutiqueId,
  required String typeAlerte,
  Value<String?> referenceId,
  required String titre,
  Value<String?> message,
  Value<bool> lu,
  Value<DateTime> createdAt,
  Value<int> rowid,
});
typedef $$CreditStockAlertesTableUpdateCompanionBuilder
    = CreditStockAlertesCompanion Function({
  Value<String> id,
  Value<String> boutiqueId,
  Value<String> typeAlerte,
  Value<String?> referenceId,
  Value<String> titre,
  Value<String?> message,
  Value<bool> lu,
  Value<DateTime> createdAt,
  Value<int> rowid,
});

class $$CreditStockAlertesTableFilterComposer
    extends Composer<_$AppDatabase, $CreditStockAlertesTable> {
  $$CreditStockAlertesTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get boutiqueId => $composableBuilder(
      column: $table.boutiqueId, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get typeAlerte => $composableBuilder(
      column: $table.typeAlerte, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get referenceId => $composableBuilder(
      column: $table.referenceId, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get titre => $composableBuilder(
      column: $table.titre, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get message => $composableBuilder(
      column: $table.message, builder: (column) => ColumnFilters(column));

  ColumnFilters<bool> get lu => $composableBuilder(
      column: $table.lu, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnFilters(column));
}

class $$CreditStockAlertesTableOrderingComposer
    extends Composer<_$AppDatabase, $CreditStockAlertesTable> {
  $$CreditStockAlertesTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get boutiqueId => $composableBuilder(
      column: $table.boutiqueId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get typeAlerte => $composableBuilder(
      column: $table.typeAlerte, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get referenceId => $composableBuilder(
      column: $table.referenceId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get titre => $composableBuilder(
      column: $table.titre, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get message => $composableBuilder(
      column: $table.message, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<bool> get lu => $composableBuilder(
      column: $table.lu, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnOrderings(column));
}

class $$CreditStockAlertesTableAnnotationComposer
    extends Composer<_$AppDatabase, $CreditStockAlertesTable> {
  $$CreditStockAlertesTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get boutiqueId => $composableBuilder(
      column: $table.boutiqueId, builder: (column) => column);

  GeneratedColumn<String> get typeAlerte => $composableBuilder(
      column: $table.typeAlerte, builder: (column) => column);

  GeneratedColumn<String> get referenceId => $composableBuilder(
      column: $table.referenceId, builder: (column) => column);

  GeneratedColumn<String> get titre =>
      $composableBuilder(column: $table.titre, builder: (column) => column);

  GeneratedColumn<String> get message =>
      $composableBuilder(column: $table.message, builder: (column) => column);

  GeneratedColumn<bool> get lu =>
      $composableBuilder(column: $table.lu, builder: (column) => column);

  GeneratedColumn<DateTime> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);
}

class $$CreditStockAlertesTableTableManager extends RootTableManager<
    _$AppDatabase,
    $CreditStockAlertesTable,
    CreditStockAlerte,
    $$CreditStockAlertesTableFilterComposer,
    $$CreditStockAlertesTableOrderingComposer,
    $$CreditStockAlertesTableAnnotationComposer,
    $$CreditStockAlertesTableCreateCompanionBuilder,
    $$CreditStockAlertesTableUpdateCompanionBuilder,
    (
      CreditStockAlerte,
      BaseReferences<_$AppDatabase, $CreditStockAlertesTable, CreditStockAlerte>
    ),
    CreditStockAlerte,
    PrefetchHooks Function()> {
  $$CreditStockAlertesTableTableManager(
      _$AppDatabase db, $CreditStockAlertesTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$CreditStockAlertesTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$CreditStockAlertesTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$CreditStockAlertesTableAnnotationComposer(
                  $db: db, $table: table),
          updateCompanionCallback: ({
            Value<String> id = const Value.absent(),
            Value<String> boutiqueId = const Value.absent(),
            Value<String> typeAlerte = const Value.absent(),
            Value<String?> referenceId = const Value.absent(),
            Value<String> titre = const Value.absent(),
            Value<String?> message = const Value.absent(),
            Value<bool> lu = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              CreditStockAlertesCompanion(
            id: id,
            boutiqueId: boutiqueId,
            typeAlerte: typeAlerte,
            referenceId: referenceId,
            titre: titre,
            message: message,
            lu: lu,
            createdAt: createdAt,
            rowid: rowid,
          ),
          createCompanionCallback: ({
            required String id,
            required String boutiqueId,
            required String typeAlerte,
            Value<String?> referenceId = const Value.absent(),
            required String titre,
            Value<String?> message = const Value.absent(),
            Value<bool> lu = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              CreditStockAlertesCompanion.insert(
            id: id,
            boutiqueId: boutiqueId,
            typeAlerte: typeAlerte,
            referenceId: referenceId,
            titre: titre,
            message: message,
            lu: lu,
            createdAt: createdAt,
            rowid: rowid,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ));
}

typedef $$CreditStockAlertesTableProcessedTableManager = ProcessedTableManager<
    _$AppDatabase,
    $CreditStockAlertesTable,
    CreditStockAlerte,
    $$CreditStockAlertesTableFilterComposer,
    $$CreditStockAlertesTableOrderingComposer,
    $$CreditStockAlertesTableAnnotationComposer,
    $$CreditStockAlertesTableCreateCompanionBuilder,
    $$CreditStockAlertesTableUpdateCompanionBuilder,
    (
      CreditStockAlerte,
      BaseReferences<_$AppDatabase, $CreditStockAlertesTable, CreditStockAlerte>
    ),
    CreditStockAlerte,
    PrefetchHooks Function()>;

class $AppDatabaseManager {
  final _$AppDatabase _db;
  $AppDatabaseManager(this._db);
  $$CreditStockBoutiquesTableTableManager get creditStockBoutiques =>
      $$CreditStockBoutiquesTableTableManager(_db, _db.creditStockBoutiques);
  $$CreditStockUtilisateursTableTableManager get creditStockUtilisateurs =>
      $$CreditStockUtilisateursTableTableManager(
          _db, _db.creditStockUtilisateurs);
  $$CreditStockProduitsTableTableManager get creditStockProduits =>
      $$CreditStockProduitsTableTableManager(_db, _db.creditStockProduits);
  $$CreditStockClientsTableTableManager get creditStockClients =>
      $$CreditStockClientsTableTableManager(_db, _db.creditStockClients);
  $$CreditStockVentesTableTableManager get creditStockVentes =>
      $$CreditStockVentesTableTableManager(_db, _db.creditStockVentes);
  $$CreditStockLignesVenteTableTableManager get creditStockLignesVente =>
      $$CreditStockLignesVenteTableTableManager(
          _db, _db.creditStockLignesVente);
  $$CreditStockDettesTableTableManager get creditStockDettes =>
      $$CreditStockDettesTableTableManager(_db, _db.creditStockDettes);
  $$CreditStockPaiementsTableTableManager get creditStockPaiements =>
      $$CreditStockPaiementsTableTableManager(_db, _db.creditStockPaiements);
  $$CreditStockSyncQueueTableTableManager get creditStockSyncQueue =>
      $$CreditStockSyncQueueTableTableManager(_db, _db.creditStockSyncQueue);
  $$CreditStockAlertesTableTableManager get creditStockAlertes =>
      $$CreditStockAlertesTableTableManager(_db, _db.creditStockAlertes);
}
