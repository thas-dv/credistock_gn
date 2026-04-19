// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'app_database.dart';

// ignore_for_file: type=lint
class $BoutiquesTable extends Boutiques
    with TableInfo<$BoutiquesTable, Boutique> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $BoutiquesTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<String> id = GeneratedColumn<String>(
      'id', aliasedName, false,
      additionalChecks:
          GeneratedColumn.checkTextLength(minTextLength: 36, maxTextLength: 36),
      type: DriftSqlType.string,
      requiredDuringInsert: true);
  static const VerificationMeta _nomMeta = const VerificationMeta('nom');
  @override
  late final GeneratedColumn<String> nom = GeneratedColumn<String>(
      'nom', aliasedName, false,
      additionalChecks: GeneratedColumn.checkTextLength(maxTextLength: 100),
      type: DriftSqlType.string,
      requiredDuringInsert: true);
  static const VerificationMeta _adresseMeta =
      const VerificationMeta('adresse');
  @override
  late final GeneratedColumn<String> adresse = GeneratedColumn<String>(
      'adresse', aliasedName, true,
      additionalChecks: GeneratedColumn.checkTextLength(maxTextLength: 200),
      type: DriftSqlType.string,
      requiredDuringInsert: false);
  static const VerificationMeta _telephoneMeta =
      const VerificationMeta('telephone');
  @override
  late final GeneratedColumn<String> telephone = GeneratedColumn<String>(
      'telephone', aliasedName, false,
      additionalChecks: GeneratedColumn.checkTextLength(maxTextLength: 20),
      type: DriftSqlType.string,
      requiredDuringInsert: true);
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
      [id, nom, adresse, telephone, createdAt];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'boutiques';
  @override
  VerificationContext validateIntegrity(Insertable<Boutique> instance,
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
    if (data.containsKey('adresse')) {
      context.handle(_adresseMeta,
          adresse.isAcceptableOrUnknown(data['adresse']!, _adresseMeta));
    }
    if (data.containsKey('telephone')) {
      context.handle(_telephoneMeta,
          telephone.isAcceptableOrUnknown(data['telephone']!, _telephoneMeta));
    } else if (isInserting) {
      context.missing(_telephoneMeta);
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
  Boutique map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return Boutique(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}id'])!,
      nom: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}nom'])!,
      adresse: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}adresse']),
      telephone: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}telephone'])!,
      createdAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}created_at'])!,
    );
  }

  @override
  $BoutiquesTable createAlias(String alias) {
    return $BoutiquesTable(attachedDatabase, alias);
  }
}

class Boutique extends DataClass implements Insertable<Boutique> {
  final String id;
  final String nom;
  final String? adresse;
  final String telephone;
  final DateTime createdAt;
  const Boutique(
      {required this.id,
      required this.nom,
      this.adresse,
      required this.telephone,
      required this.createdAt});
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<String>(id);
    map['nom'] = Variable<String>(nom);
    if (!nullToAbsent || adresse != null) {
      map['adresse'] = Variable<String>(adresse);
    }
    map['telephone'] = Variable<String>(telephone);
    map['created_at'] = Variable<DateTime>(createdAt);
    return map;
  }

  BoutiquesCompanion toCompanion(bool nullToAbsent) {
    return BoutiquesCompanion(
      id: Value(id),
      nom: Value(nom),
      adresse: adresse == null && nullToAbsent
          ? const Value.absent()
          : Value(adresse),
      telephone: Value(telephone),
      createdAt: Value(createdAt),
    );
  }

  factory Boutique.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return Boutique(
      id: serializer.fromJson<String>(json['id']),
      nom: serializer.fromJson<String>(json['nom']),
      adresse: serializer.fromJson<String?>(json['adresse']),
      telephone: serializer.fromJson<String>(json['telephone']),
      createdAt: serializer.fromJson<DateTime>(json['createdAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<String>(id),
      'nom': serializer.toJson<String>(nom),
      'adresse': serializer.toJson<String?>(adresse),
      'telephone': serializer.toJson<String>(telephone),
      'createdAt': serializer.toJson<DateTime>(createdAt),
    };
  }

  Boutique copyWith(
          {String? id,
          String? nom,
          Value<String?> adresse = const Value.absent(),
          String? telephone,
          DateTime? createdAt}) =>
      Boutique(
        id: id ?? this.id,
        nom: nom ?? this.nom,
        adresse: adresse.present ? adresse.value : this.adresse,
        telephone: telephone ?? this.telephone,
        createdAt: createdAt ?? this.createdAt,
      );
  Boutique copyWithCompanion(BoutiquesCompanion data) {
    return Boutique(
      id: data.id.present ? data.id.value : this.id,
      nom: data.nom.present ? data.nom.value : this.nom,
      adresse: data.adresse.present ? data.adresse.value : this.adresse,
      telephone: data.telephone.present ? data.telephone.value : this.telephone,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('outique(')
          ..write('id: $id, ')
          ..write('nom: $nom, ')
          ..write('adresse: $adresse, ')
          ..write('telephone: $telephone, ')
          ..write('createdAt: $createdAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(id, nom, adresse, telephone, createdAt);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is Boutique &&
          other.id == this.id &&
          other.nom == this.nom &&
          other.adresse == this.adresse &&
          other.telephone == this.telephone &&
          other.createdAt == this.createdAt);
}

class BoutiquesCompanion extends UpdateCompanion<Boutique> {
  final Value<String> id;
  final Value<String> nom;
  final Value<String?> adresse;
  final Value<String> telephone;
  final Value<DateTime> createdAt;
  final Value<int> rowid;
  const BoutiquesCompanion({
    this.id = const Value.absent(),
    this.nom = const Value.absent(),
    this.adresse = const Value.absent(),
    this.telephone = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  BoutiquesCompanion.insert({
    required String id,
    required String nom,
    this.adresse = const Value.absent(),
    required String telephone,
    this.createdAt = const Value.absent(),
    this.rowid = const Value.absent(),
  })  : id = Value(id),
        nom = Value(nom),
        telephone = Value(telephone);
  static Insertable<Boutique> custom({
    Expression<String>? id,
    Expression<String>? nom,
    Expression<String>? adresse,
    Expression<String>? telephone,
    Expression<DateTime>? createdAt,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (nom != null) 'nom': nom,
      if (adresse != null) 'adresse': adresse,
      if (telephone != null) 'telephone': telephone,
      if (createdAt != null) 'created_at': createdAt,
      if (rowid != null) 'rowid': rowid,
    });
  }

  BoutiquesCompanion copyWith(
      {Value<String>? id,
      Value<String>? nom,
      Value<String?>? adresse,
      Value<String>? telephone,
      Value<DateTime>? createdAt,
      Value<int>? rowid}) {
    return BoutiquesCompanion(
      id: id ?? this.id,
      nom: nom ?? this.nom,
      adresse: adresse ?? this.adresse,
      telephone: telephone ?? this.telephone,
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
    if (nom.present) {
      map['nom'] = Variable<String>(nom.value);
    }
    if (adresse.present) {
      map['adresse'] = Variable<String>(adresse.value);
    }
    if (telephone.present) {
      map['telephone'] = Variable<String>(telephone.value);
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
    return (StringBuffer('BoutiquesCompanion(')
          ..write('id: $id, ')
          ..write('nom: $nom, ')
          ..write('adresse: $adresse, ')
          ..write('telephone: $telephone, ')
          ..write('createdAt: $createdAt, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $UtilisateursTable extends Utilisateurs
    with TableInfo<$UtilisateursTable, Utilisateur> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $UtilisateursTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<String> id = GeneratedColumn<String>(
      'id', aliasedName, false,
      additionalChecks:
          GeneratedColumn.checkTextLength(minTextLength: 36, maxTextLength: 36),
      type: DriftSqlType.string,
      requiredDuringInsert: true);
  static const VerificationMeta _boutiqueIdMeta =
      const VerificationMeta('boutiqueId');
  @override
  late final GeneratedColumn<String> boutiqueId = GeneratedColumn<String>(
      'boutique_id', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: true,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('REFERENCES boutiques (id)'));
  static const VerificationMeta _nomMeta = const VerificationMeta('nom');
  @override
  late final GeneratedColumn<String> nom = GeneratedColumn<String>(
      'nom', aliasedName, false,
      additionalChecks: GeneratedColumn.checkTextLength(maxTextLength: 100),
      type: DriftSqlType.string,
      requiredDuringInsert: true);
  static const VerificationMeta _roleMeta = const VerificationMeta('role');
  @override
  late final GeneratedColumn<String> role = GeneratedColumn<String>(
      'role', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: false,
      defaultValue: const Constant('employe'));
  static const VerificationMeta _motDePasseMeta =
      const VerificationMeta('motDePasse');
  @override
  late final GeneratedColumn<String> motDePasse = GeneratedColumn<String>(
      'mot_de_passe', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _pinHashMeta =
      const VerificationMeta('pinHash');
  @override
  late final GeneratedColumn<String> pinHash = GeneratedColumn<String>(
      'pin_hash', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
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
      [id, boutiqueId, nom, role, motDePasse, pinHash, createdAt];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'utilisateurs';
  @override
  VerificationContext validateIntegrity(Insertable<Utilisateur> instance,
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
    if (data.containsKey('role')) {
      context.handle(
          _roleMeta, role.isAcceptableOrUnknown(data['role']!, _roleMeta));
    }
    if (data.containsKey('mot_de_passe')) {
      context.handle(
          _motDePasseMeta,
          motDePasse.isAcceptableOrUnknown(
              data['mot_de_passe']!, _motDePasseMeta));
    } else if (isInserting) {
      context.missing(_motDePasseMeta);
    }
    if (data.containsKey('pin_hash')) {
      context.handle(_pinHashMeta,
          pinHash.isAcceptableOrUnknown(data['pin_hash']!, _pinHashMeta));
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
  Utilisateur map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return Utilisateur(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}id'])!,
      boutiqueId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}boutique_id'])!,
      nom: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}nom'])!,
      role: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}role'])!,
      motDePasse: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}mot_de_passe'])!,
      pinHash: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}pin_hash']),
      createdAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}created_at'])!,
    );
  }

  @override
  $UtilisateursTable createAlias(String alias) {
    return $UtilisateursTable(attachedDatabase, alias);
  }
}

class Utilisateur extends DataClass implements Insertable<Utilisateur> {
  final String id;
  final String boutiqueId;
  final String nom;
  final String role;
  final String motDePasse;
  final String? pinHash;
  final DateTime createdAt;
  const Utilisateur(
      {required this.id,
      required this.boutiqueId,
      required this.nom,
      required this.role,
      required this.motDePasse,
      this.pinHash,
      required this.createdAt});
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<String>(id);
    map['boutique_id'] = Variable<String>(boutiqueId);
    map['nom'] = Variable<String>(nom);
    map['role'] = Variable<String>(role);
    map['mot_de_passe'] = Variable<String>(motDePasse);
    if (!nullToAbsent || pinHash != null) {
      map['pin_hash'] = Variable<String>(pinHash);
    }
    map['created_at'] = Variable<DateTime>(createdAt);
    return map;
  }

  UtilisateursCompanion toCompanion(bool nullToAbsent) {
    return UtilisateursCompanion(
      id: Value(id),
      boutiqueId: Value(boutiqueId),
      nom: Value(nom),
      role: Value(role),
      motDePasse: Value(motDePasse),
      pinHash: pinHash == null && nullToAbsent
          ? const Value.absent()
          : Value(pinHash),
      createdAt: Value(createdAt),
    );
  }

  factory Utilisateur.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return Utilisateur(
      id: serializer.fromJson<String>(json['id']),
      boutiqueId: serializer.fromJson<String>(json['boutiqueId']),
      nom: serializer.fromJson<String>(json['nom']),
      role: serializer.fromJson<String>(json['role']),
      motDePasse: serializer.fromJson<String>(json['motDePasse']),
      pinHash: serializer.fromJson<String?>(json['pinHash']),
      createdAt: serializer.fromJson<DateTime>(json['createdAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<String>(id),
      'boutiqueId': serializer.toJson<String>(boutiqueId),
      'nom': serializer.toJson<String>(nom),
      'role': serializer.toJson<String>(role),
      'motDePasse': serializer.toJson<String>(motDePasse),
      'pinHash': serializer.toJson<String?>(pinHash),
      'createdAt': serializer.toJson<DateTime>(createdAt),
    };
  }

  Utilisateur copyWith(
          {String? id,
          String? boutiqueId,
          String? nom,
          String? role,
          String? motDePasse,
          Value<String?> pinHash = const Value.absent(),
          DateTime? createdAt}) =>
      Utilisateur(
        id: id ?? this.id,
        boutiqueId: boutiqueId ?? this.boutiqueId,
        nom: nom ?? this.nom,
        role: role ?? this.role,
        motDePasse: motDePasse ?? this.motDePasse,
        pinHash: pinHash.present ? pinHash.value : this.pinHash,
        createdAt: createdAt ?? this.createdAt,
      );
  Utilisateur copyWithCompanion(UtilisateursCompanion data) {
    return Utilisateur(
      id: data.id.present ? data.id.value : this.id,
      boutiqueId:
          data.boutiqueId.present ? data.boutiqueId.value : this.boutiqueId,
      nom: data.nom.present ? data.nom.value : this.nom,
      role: data.role.present ? data.role.value : this.role,
      motDePasse:
          data.motDePasse.present ? data.motDePasse.value : this.motDePasse,
      pinHash: data.pinHash.present ? data.pinHash.value : this.pinHash,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('Utilisateur(')
          ..write('id: $id, ')
          ..write('boutiqueId: $boutiqueId, ')
          ..write('nom: $nom, ')
          ..write('role: $role, ')
          ..write('motDePasse: $motDePasse, ')
          ..write('pinHash: $pinHash, ')
          ..write('createdAt: $createdAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode =>
      Object.hash(id, boutiqueId, nom, role, motDePasse, pinHash, createdAt);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is Utilisateur &&
          other.id == this.id &&
          other.boutiqueId == this.boutiqueId &&
          other.nom == this.nom &&
          other.role == this.role &&
          other.motDePasse == this.motDePasse &&
          other.pinHash == this.pinHash &&
          other.createdAt == this.createdAt);
}

class UtilisateursCompanion extends UpdateCompanion<Utilisateur> {
  final Value<String> id;
  final Value<String> boutiqueId;
  final Value<String> nom;
  final Value<String> role;
  final Value<String> motDePasse;
  final Value<String?> pinHash;
  final Value<DateTime> createdAt;
  final Value<int> rowid;
  const UtilisateursCompanion({
    this.id = const Value.absent(),
    this.boutiqueId = const Value.absent(),
    this.nom = const Value.absent(),
    this.role = const Value.absent(),
    this.motDePasse = const Value.absent(),
    this.pinHash = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  UtilisateursCompanion.insert({
    required String id,
    required String boutiqueId,
    required String nom,
    this.role = const Value.absent(),
    required String motDePasse,
    this.pinHash = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.rowid = const Value.absent(),
  })  : id = Value(id),
        boutiqueId = Value(boutiqueId),
        nom = Value(nom),
        motDePasse = Value(motDePasse);
  static Insertable<Utilisateur> custom({
    Expression<String>? id,
    Expression<String>? boutiqueId,
    Expression<String>? nom,
    Expression<String>? role,
    Expression<String>? motDePasse,
    Expression<String>? pinHash,
    Expression<DateTime>? createdAt,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (boutiqueId != null) 'boutique_id': boutiqueId,
      if (nom != null) 'nom': nom,
      if (role != null) 'role': role,
      if (motDePasse != null) 'mot_de_passe': motDePasse,
      if (pinHash != null) 'pin_hash': pinHash,
      if (createdAt != null) 'created_at': createdAt,
      if (rowid != null) 'rowid': rowid,
    });
  }

  UtilisateursCompanion copyWith(
      {Value<String>? id,
      Value<String>? boutiqueId,
      Value<String>? nom,
      Value<String>? role,
      Value<String>? motDePasse,
      Value<String?>? pinHash,
      Value<DateTime>? createdAt,
      Value<int>? rowid}) {
    return UtilisateursCompanion(
      id: id ?? this.id,
      boutiqueId: boutiqueId ?? this.boutiqueId,
      nom: nom ?? this.nom,
      role: role ?? this.role,
      motDePasse: motDePasse ?? this.motDePasse,
      pinHash: pinHash ?? this.pinHash,
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
    if (nom.present) {
      map['nom'] = Variable<String>(nom.value);
    }
    if (role.present) {
      map['role'] = Variable<String>(role.value);
    }
    if (motDePasse.present) {
      map['mot_de_passe'] = Variable<String>(motDePasse.value);
    }
    if (pinHash.present) {
      map['pin_hash'] = Variable<String>(pinHash.value);
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
    return (StringBuffer('UtilisateursCompanion(')
          ..write('id: $id, ')
          ..write('boutiqueId: $boutiqueId, ')
          ..write('nom: $nom, ')
          ..write('role: $role, ')
          ..write('motDePasse: $motDePasse, ')
          ..write('pinHash: $pinHash, ')
          ..write('createdAt: $createdAt, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $ProduitsTable extends Produits with TableInfo<$ProduitsTable, Produit> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $ProduitsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<String> id = GeneratedColumn<String>(
      'id', aliasedName, false,
      additionalChecks:
          GeneratedColumn.checkTextLength(minTextLength: 36, maxTextLength: 36),
      type: DriftSqlType.string,
      requiredDuringInsert: true);
  static const VerificationMeta _boutiqueIdMeta =
      const VerificationMeta('boutiqueId');
  @override
  late final GeneratedColumn<String> boutiqueId = GeneratedColumn<String>(
      'boutique_id', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: true,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('REFERENCES boutiques (id)'));
  static const VerificationMeta _nomMeta = const VerificationMeta('nom');
  @override
  late final GeneratedColumn<String> nom = GeneratedColumn<String>(
      'nom', aliasedName, false,
      additionalChecks: GeneratedColumn.checkTextLength(maxTextLength: 100),
      type: DriftSqlType.string,
      requiredDuringInsert: true);
  static const VerificationMeta _categorieMeta =
      const VerificationMeta('categorie');
  @override
  late final GeneratedColumn<String> categorie = GeneratedColumn<String>(
      'categorie', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: false,
      defaultValue: const Constant('general'));
  static const VerificationMeta _prixVenteMeta =
      const VerificationMeta('prixVente');
  @override
  late final GeneratedColumn<int> prixVente = GeneratedColumn<int>(
      'prix_vente', aliasedName, false,
      type: DriftSqlType.int, requiredDuringInsert: true);
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
  static const VerificationMeta _syncedMeta = const VerificationMeta('synced');
  @override
  late final GeneratedColumn<bool> synced = GeneratedColumn<bool>(
      'synced', aliasedName, false,
      type: DriftSqlType.bool,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('CHECK ("synced" IN (0, 1))'),
      defaultValue: const Constant(true));
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
        categorie,
        prixVente,
        prixAchat,
        quantite,
        seuilAlerte,
        synced,
        updatedAt
      ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'produits';
  @override
  VerificationContext validateIntegrity(Insertable<Produit> instance,
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
    if (data.containsKey('categorie')) {
      context.handle(_categorieMeta,
          categorie.isAcceptableOrUnknown(data['categorie']!, _categorieMeta));
    }
    if (data.containsKey('prix_vente')) {
      context.handle(_prixVenteMeta,
          prixVente.isAcceptableOrUnknown(data['prix_vente']!, _prixVenteMeta));
    } else if (isInserting) {
      context.missing(_prixVenteMeta);
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
    if (data.containsKey('synced')) {
      context.handle(_syncedMeta,
          synced.isAcceptableOrUnknown(data['synced']!, _syncedMeta));
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
  Produit map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return Produit(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}id'])!,
      boutiqueId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}boutique_id'])!,
      nom: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}nom'])!,
      categorie: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}categorie'])!,
      prixVente: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}prix_vente'])!,
      prixAchat: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}prix_achat'])!,
      quantite: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}quantite'])!,
      seuilAlerte: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}seuil_alerte'])!,
      synced: attachedDatabase.typeMapping
          .read(DriftSqlType.bool, data['${effectivePrefix}synced'])!,
      updatedAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}updated_at'])!,
    );
  }

  @override
  $ProduitsTable createAlias(String alias) {
    return $ProduitsTable(attachedDatabase, alias);
  }
}

class Produit extends DataClass implements Insertable<Produit> {
  final String id;
  final String boutiqueId;
  final String nom;
  final String categorie;
  final int prixVente;
  final int prixAchat;
  final int quantite;
  final int seuilAlerte;
  final bool synced;
  final DateTime updatedAt;
  const Produit(
      {required this.id,
      required this.boutiqueId,
      required this.nom,
      required this.categorie,
      required this.prixVente,
      required this.prixAchat,
      required this.quantite,
      required this.seuilAlerte,
      required this.synced,
      required this.updatedAt});
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<String>(id);
    map['boutique_id'] = Variable<String>(boutiqueId);
    map['nom'] = Variable<String>(nom);
    map['categorie'] = Variable<String>(categorie);
    map['prix_vente'] = Variable<int>(prixVente);
    map['prix_achat'] = Variable<int>(prixAchat);
    map['quantite'] = Variable<int>(quantite);
    map['seuil_alerte'] = Variable<int>(seuilAlerte);
    map['synced'] = Variable<bool>(synced);
    map['updated_at'] = Variable<DateTime>(updatedAt);
    return map;
  }

  ProduitsCompanion toCompanion(bool nullToAbsent) {
    return ProduitsCompanion(
      id: Value(id),
      boutiqueId: Value(boutiqueId),
      nom: Value(nom),
      categorie: Value(categorie),
      prixVente: Value(prixVente),
      prixAchat: Value(prixAchat),
      quantite: Value(quantite),
      seuilAlerte: Value(seuilAlerte),
      synced: Value(synced),
      updatedAt: Value(updatedAt),
    );
  }

  factory Produit.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return Produit(
      id: serializer.fromJson<String>(json['id']),
      boutiqueId: serializer.fromJson<String>(json['boutiqueId']),
      nom: serializer.fromJson<String>(json['nom']),
      categorie: serializer.fromJson<String>(json['categorie']),
      prixVente: serializer.fromJson<int>(json['prixVente']),
      prixAchat: serializer.fromJson<int>(json['prixAchat']),
      quantite: serializer.fromJson<int>(json['quantite']),
      seuilAlerte: serializer.fromJson<int>(json['seuilAlerte']),
      synced: serializer.fromJson<bool>(json['synced']),
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
      'categorie': serializer.toJson<String>(categorie),
      'prixVente': serializer.toJson<int>(prixVente),
      'prixAchat': serializer.toJson<int>(prixAchat),
      'quantite': serializer.toJson<int>(quantite),
      'seuilAlerte': serializer.toJson<int>(seuilAlerte),
      'synced': serializer.toJson<bool>(synced),
      'updatedAt': serializer.toJson<DateTime>(updatedAt),
    };
  }

  Produit copyWith(
          {String? id,
          String? boutiqueId,
          String? nom,
          String? categorie,
          int? prixVente,
          int? prixAchat,
          int? quantite,
          int? seuilAlerte,
          bool? synced,
          DateTime? updatedAt}) =>
      Produit(
        id: id ?? this.id,
        boutiqueId: boutiqueId ?? this.boutiqueId,
        nom: nom ?? this.nom,
        categorie: categorie ?? this.categorie,
        prixVente: prixVente ?? this.prixVente,
        prixAchat: prixAchat ?? this.prixAchat,
        quantite: quantite ?? this.quantite,
        seuilAlerte: seuilAlerte ?? this.seuilAlerte,
        synced: synced ?? this.synced,
        updatedAt: updatedAt ?? this.updatedAt,
      );
  Produit copyWithCompanion(ProduitsCompanion data) {
    return Produit(
      id: data.id.present ? data.id.value : this.id,
      boutiqueId:
          data.boutiqueId.present ? data.boutiqueId.value : this.boutiqueId,
      nom: data.nom.present ? data.nom.value : this.nom,
      categorie: data.categorie.present ? data.categorie.value : this.categorie,
      prixVente: data.prixVente.present ? data.prixVente.value : this.prixVente,
      prixAchat: data.prixAchat.present ? data.prixAchat.value : this.prixAchat,
      quantite: data.quantite.present ? data.quantite.value : this.quantite,
      seuilAlerte:
          data.seuilAlerte.present ? data.seuilAlerte.value : this.seuilAlerte,
      synced: data.synced.present ? data.synced.value : this.synced,
      updatedAt: data.updatedAt.present ? data.updatedAt.value : this.updatedAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('Produit(')
          ..write('id: $id, ')
          ..write('boutiqueId: $boutiqueId, ')
          ..write('nom: $nom, ')
          ..write('categorie: $categorie, ')
          ..write('prixVente: $prixVente, ')
          ..write('prixAchat: $prixAchat, ')
          ..write('quantite: $quantite, ')
          ..write('seuilAlerte: $seuilAlerte, ')
          ..write('synced: $synced, ')
          ..write('updatedAt: $updatedAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(id, boutiqueId, nom, categorie, prixVente,
      prixAchat, quantite, seuilAlerte, synced, updatedAt);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is Produit &&
          other.id == this.id &&
          other.boutiqueId == this.boutiqueId &&
          other.nom == this.nom &&
          other.categorie == this.categorie &&
          other.prixVente == this.prixVente &&
          other.prixAchat == this.prixAchat &&
          other.quantite == this.quantite &&
          other.seuilAlerte == this.seuilAlerte &&
          other.synced == this.synced &&
          other.updatedAt == this.updatedAt);
}

class ProduitsCompanion extends UpdateCompanion<Produit> {
  final Value<String> id;
  final Value<String> boutiqueId;
  final Value<String> nom;
  final Value<String> categorie;
  final Value<int> prixVente;
  final Value<int> prixAchat;
  final Value<int> quantite;
  final Value<int> seuilAlerte;
  final Value<bool> synced;
  final Value<DateTime> updatedAt;
  final Value<int> rowid;
  const ProduitsCompanion({
    this.id = const Value.absent(),
    this.boutiqueId = const Value.absent(),
    this.nom = const Value.absent(),
    this.categorie = const Value.absent(),
    this.prixVente = const Value.absent(),
    this.prixAchat = const Value.absent(),
    this.quantite = const Value.absent(),
    this.seuilAlerte = const Value.absent(),
    this.synced = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  ProduitsCompanion.insert({
    required String id,
    required String boutiqueId,
    required String nom,
    this.categorie = const Value.absent(),
    required int prixVente,
    this.prixAchat = const Value.absent(),
    this.quantite = const Value.absent(),
    this.seuilAlerte = const Value.absent(),
    this.synced = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  })  : id = Value(id),
        boutiqueId = Value(boutiqueId),
        nom = Value(nom),
        prixVente = Value(prixVente);
  static Insertable<Produit> custom({
    Expression<String>? id,
    Expression<String>? boutiqueId,
    Expression<String>? nom,
    Expression<String>? categorie,
    Expression<int>? prixVente,
    Expression<int>? prixAchat,
    Expression<int>? quantite,
    Expression<int>? seuilAlerte,
    Expression<bool>? synced,
    Expression<DateTime>? updatedAt,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (boutiqueId != null) 'boutique_id': boutiqueId,
      if (nom != null) 'nom': nom,
      if (categorie != null) 'categorie': categorie,
      if (prixVente != null) 'prix_vente': prixVente,
      if (prixAchat != null) 'prix_achat': prixAchat,
      if (quantite != null) 'quantite': quantite,
      if (seuilAlerte != null) 'seuil_alerte': seuilAlerte,
      if (synced != null) 'synced': synced,
      if (updatedAt != null) 'updated_at': updatedAt,
      if (rowid != null) 'rowid': rowid,
    });
  }

  ProduitsCompanion copyWith(
      {Value<String>? id,
      Value<String>? boutiqueId,
      Value<String>? nom,
      Value<String>? categorie,
      Value<int>? prixVente,
      Value<int>? prixAchat,
      Value<int>? quantite,
      Value<int>? seuilAlerte,
      Value<bool>? synced,
      Value<DateTime>? updatedAt,
      Value<int>? rowid}) {
    return ProduitsCompanion(
      id: id ?? this.id,
      boutiqueId: boutiqueId ?? this.boutiqueId,
      nom: nom ?? this.nom,
      categorie: categorie ?? this.categorie,
      prixVente: prixVente ?? this.prixVente,
      prixAchat: prixAchat ?? this.prixAchat,
      quantite: quantite ?? this.quantite,
      seuilAlerte: seuilAlerte ?? this.seuilAlerte,
      synced: synced ?? this.synced,
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
    if (categorie.present) {
      map['categorie'] = Variable<String>(categorie.value);
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
    if (synced.present) {
      map['synced'] = Variable<bool>(synced.value);
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
    return (StringBuffer('ProduitsCompanion(')
          ..write('id: $id, ')
          ..write('boutiqueId: $boutiqueId, ')
          ..write('nom: $nom, ')
          ..write('categorie: $categorie, ')
          ..write('prixVente: $prixVente, ')
          ..write('prixAchat: $prixAchat, ')
          ..write('quantite: $quantite, ')
          ..write('seuilAlerte: $seuilAlerte, ')
          ..write('synced: $synced, ')
          ..write('updatedAt: $updatedAt, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $ClientsTable extends Clients with TableInfo<$ClientsTable, Client> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $ClientsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<String> id = GeneratedColumn<String>(
      'id', aliasedName, false,
      additionalChecks:
          GeneratedColumn.checkTextLength(minTextLength: 36, maxTextLength: 36),
      type: DriftSqlType.string,
      requiredDuringInsert: true);
  static const VerificationMeta _boutiqueIdMeta =
      const VerificationMeta('boutiqueId');
  @override
  late final GeneratedColumn<String> boutiqueId = GeneratedColumn<String>(
      'boutique_id', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: true,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('REFERENCES boutiques (id)'));
  static const VerificationMeta _nomMeta = const VerificationMeta('nom');
  @override
  late final GeneratedColumn<String> nom = GeneratedColumn<String>(
      'nom', aliasedName, false,
      additionalChecks: GeneratedColumn.checkTextLength(maxTextLength: 100),
      type: DriftSqlType.string,
      requiredDuringInsert: true);
  static const VerificationMeta _telephoneMeta =
      const VerificationMeta('telephone');
  @override
  late final GeneratedColumn<String> telephone = GeneratedColumn<String>(
      'telephone', aliasedName, true,
      additionalChecks: GeneratedColumn.checkTextLength(maxTextLength: 20),
      type: DriftSqlType.string,
      requiredDuringInsert: false);
  static const VerificationMeta _scoreMeta = const VerificationMeta('score');
  @override
  late final GeneratedColumn<String> score = GeneratedColumn<String>(
      'score', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: false,
      defaultValue: const Constant('bon'));
  static const VerificationMeta _totalDuMeta =
      const VerificationMeta('totalDu');
  @override
  late final GeneratedColumn<int> totalDu = GeneratedColumn<int>(
      'total_du', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  static const VerificationMeta _nombreDettesMeta =
      const VerificationMeta('nombreDettes');
  @override
  late final GeneratedColumn<int> nombreDettes = GeneratedColumn<int>(
      'nombre_dettes', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  static const VerificationMeta _nombresRemboursementsMeta =
      const VerificationMeta('nombresRemboursements');
  @override
  late final GeneratedColumn<int> nombresRemboursements = GeneratedColumn<int>(
      'nombres_remboursements', aliasedName, false,
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
      defaultValue: const Constant(true));
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
        nom,
        telephone,
        score,
        totalDu,
        nombreDettes,
        nombresRemboursements,
        synced,
        createdAt
      ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'clients';
  @override
  VerificationContext validateIntegrity(Insertable<Client> instance,
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
    if (data.containsKey('score')) {
      context.handle(
          _scoreMeta, score.isAcceptableOrUnknown(data['score']!, _scoreMeta));
    }
    if (data.containsKey('total_du')) {
      context.handle(_totalDuMeta,
          totalDu.isAcceptableOrUnknown(data['total_du']!, _totalDuMeta));
    }
    if (data.containsKey('nombre_dettes')) {
      context.handle(
          _nombreDettesMeta,
          nombreDettes.isAcceptableOrUnknown(
              data['nombre_dettes']!, _nombreDettesMeta));
    }
    if (data.containsKey('nombres_remboursements')) {
      context.handle(
          _nombresRemboursementsMeta,
          nombresRemboursements.isAcceptableOrUnknown(
              data['nombres_remboursements']!, _nombresRemboursementsMeta));
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
  Client map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return Client(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}id'])!,
      boutiqueId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}boutique_id'])!,
      nom: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}nom'])!,
      telephone: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}telephone']),
      score: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}score'])!,
      totalDu: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}total_du'])!,
      nombreDettes: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}nombre_dettes'])!,
      nombresRemboursements: attachedDatabase.typeMapping.read(
          DriftSqlType.int, data['${effectivePrefix}nombres_remboursements'])!,
      synced: attachedDatabase.typeMapping
          .read(DriftSqlType.bool, data['${effectivePrefix}synced'])!,
      createdAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}created_at'])!,
    );
  }

  @override
  $ClientsTable createAlias(String alias) {
    return $ClientsTable(attachedDatabase, alias);
  }
}

class Client extends DataClass implements Insertable<Client> {
  final String id;
  final String boutiqueId;
  final String nom;
  final String? telephone;
  final String score;
  final int totalDu;
  final int nombreDettes;
  final int nombresRemboursements;
  final bool synced;
  final DateTime createdAt;
  const Client(
      {required this.id,
      required this.boutiqueId,
      required this.nom,
      this.telephone,
      required this.score,
      required this.totalDu,
      required this.nombreDettes,
      required this.nombresRemboursements,
      required this.synced,
      required this.createdAt});
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<String>(id);
    map['boutique_id'] = Variable<String>(boutiqueId);
    map['nom'] = Variable<String>(nom);
    if (!nullToAbsent || telephone != null) {
      map['telephone'] = Variable<String>(telephone);
    }
    map['score'] = Variable<String>(score);
    map['total_du'] = Variable<int>(totalDu);
    map['nombre_dettes'] = Variable<int>(nombreDettes);
    map['nombres_remboursements'] = Variable<int>(nombresRemboursements);
    map['synced'] = Variable<bool>(synced);
    map['created_at'] = Variable<DateTime>(createdAt);
    return map;
  }

  ClientsCompanion toCompanion(bool nullToAbsent) {
    return ClientsCompanion(
      id: Value(id),
      boutiqueId: Value(boutiqueId),
      nom: Value(nom),
      telephone: telephone == null && nullToAbsent
          ? const Value.absent()
          : Value(telephone),
      score: Value(score),
      totalDu: Value(totalDu),
      nombreDettes: Value(nombreDettes),
      nombresRemboursements: Value(nombresRemboursements),
      synced: Value(synced),
      createdAt: Value(createdAt),
    );
  }

  factory Client.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return Client(
      id: serializer.fromJson<String>(json['id']),
      boutiqueId: serializer.fromJson<String>(json['boutiqueId']),
      nom: serializer.fromJson<String>(json['nom']),
      telephone: serializer.fromJson<String?>(json['telephone']),
      score: serializer.fromJson<String>(json['score']),
      totalDu: serializer.fromJson<int>(json['totalDu']),
      nombreDettes: serializer.fromJson<int>(json['nombreDettes']),
      nombresRemboursements:
          serializer.fromJson<int>(json['nombresRemboursements']),
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
      'nom': serializer.toJson<String>(nom),
      'telephone': serializer.toJson<String?>(telephone),
      'score': serializer.toJson<String>(score),
      'totalDu': serializer.toJson<int>(totalDu),
      'nombreDettes': serializer.toJson<int>(nombreDettes),
      'nombresRemboursements': serializer.toJson<int>(nombresRemboursements),
      'synced': serializer.toJson<bool>(synced),
      'createdAt': serializer.toJson<DateTime>(createdAt),
    };
  }

  Client copyWith(
          {String? id,
          String? boutiqueId,
          String? nom,
          Value<String?> telephone = const Value.absent(),
          String? score,
          int? totalDu,
          int? nombreDettes,
          int? nombresRemboursements,
          bool? synced,
          DateTime? createdAt}) =>
      Client(
        id: id ?? this.id,
        boutiqueId: boutiqueId ?? this.boutiqueId,
        nom: nom ?? this.nom,
        telephone: telephone.present ? telephone.value : this.telephone,
        score: score ?? this.score,
        totalDu: totalDu ?? this.totalDu,
        nombreDettes: nombreDettes ?? this.nombreDettes,
        nombresRemboursements:
            nombresRemboursements ?? this.nombresRemboursements,
        synced: synced ?? this.synced,
        createdAt: createdAt ?? this.createdAt,
      );
  Client copyWithCompanion(ClientsCompanion data) {
    return Client(
      id: data.id.present ? data.id.value : this.id,
      boutiqueId:
          data.boutiqueId.present ? data.boutiqueId.value : this.boutiqueId,
      nom: data.nom.present ? data.nom.value : this.nom,
      telephone: data.telephone.present ? data.telephone.value : this.telephone,
      score: data.score.present ? data.score.value : this.score,
      totalDu: data.totalDu.present ? data.totalDu.value : this.totalDu,
      nombreDettes: data.nombreDettes.present
          ? data.nombreDettes.value
          : this.nombreDettes,
      nombresRemboursements: data.nombresRemboursements.present
          ? data.nombresRemboursements.value
          : this.nombresRemboursements,
      synced: data.synced.present ? data.synced.value : this.synced,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('Client(')
          ..write('id: $id, ')
          ..write('boutiqueId: $boutiqueId, ')
          ..write('nom: $nom, ')
          ..write('telephone: $telephone, ')
          ..write('score: $score, ')
          ..write('totalDu: $totalDu, ')
          ..write('nombreDettes: $nombreDettes, ')
          ..write('nombresRemboursements: $nombresRemboursements, ')
          ..write('synced: $synced, ')
          ..write('createdAt: $createdAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(id, boutiqueId, nom, telephone, score,
      totalDu, nombreDettes, nombresRemboursements, synced, createdAt);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is Client &&
          other.id == this.id &&
          other.boutiqueId == this.boutiqueId &&
          other.nom == this.nom &&
          other.telephone == this.telephone &&
          other.score == this.score &&
          other.totalDu == this.totalDu &&
          other.nombreDettes == this.nombreDettes &&
          other.nombresRemboursements == this.nombresRemboursements &&
          other.synced == this.synced &&
          other.createdAt == this.createdAt);
}

class ClientsCompanion extends UpdateCompanion<Client> {
  final Value<String> id;
  final Value<String> boutiqueId;
  final Value<String> nom;
  final Value<String?> telephone;
  final Value<String> score;
  final Value<int> totalDu;
  final Value<int> nombreDettes;
  final Value<int> nombresRemboursements;
  final Value<bool> synced;
  final Value<DateTime> createdAt;
  final Value<int> rowid;
  const ClientsCompanion({
    this.id = const Value.absent(),
    this.boutiqueId = const Value.absent(),
    this.nom = const Value.absent(),
    this.telephone = const Value.absent(),
    this.score = const Value.absent(),
    this.totalDu = const Value.absent(),
    this.nombreDettes = const Value.absent(),
    this.nombresRemboursements = const Value.absent(),
    this.synced = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  ClientsCompanion.insert({
    required String id,
    required String boutiqueId,
    required String nom,
    this.telephone = const Value.absent(),
    this.score = const Value.absent(),
    this.totalDu = const Value.absent(),
    this.nombreDettes = const Value.absent(),
    this.nombresRemboursements = const Value.absent(),
    this.synced = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.rowid = const Value.absent(),
  })  : id = Value(id),
        boutiqueId = Value(boutiqueId),
        nom = Value(nom);
  static Insertable<Client> custom({
    Expression<String>? id,
    Expression<String>? boutiqueId,
    Expression<String>? nom,
    Expression<String>? telephone,
    Expression<String>? score,
    Expression<int>? totalDu,
    Expression<int>? nombreDettes,
    Expression<int>? nombresRemboursements,
    Expression<bool>? synced,
    Expression<DateTime>? createdAt,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (boutiqueId != null) 'boutique_id': boutiqueId,
      if (nom != null) 'nom': nom,
      if (telephone != null) 'telephone': telephone,
      if (score != null) 'score': score,
      if (totalDu != null) 'total_du': totalDu,
      if (nombreDettes != null) 'nombre_dettes': nombreDettes,
      if (nombresRemboursements != null)
        'nombres_remboursements': nombresRemboursements,
      if (synced != null) 'synced': synced,
      if (createdAt != null) 'created_at': createdAt,
      if (rowid != null) 'rowid': rowid,
    });
  }

  ClientsCompanion copyWith(
      {Value<String>? id,
      Value<String>? boutiqueId,
      Value<String>? nom,
      Value<String?>? telephone,
      Value<String>? score,
      Value<int>? totalDu,
      Value<int>? nombreDettes,
      Value<int>? nombresRemboursements,
      Value<bool>? synced,
      Value<DateTime>? createdAt,
      Value<int>? rowid}) {
    return ClientsCompanion(
      id: id ?? this.id,
      boutiqueId: boutiqueId ?? this.boutiqueId,
      nom: nom ?? this.nom,
      telephone: telephone ?? this.telephone,
      score: score ?? this.score,
      totalDu: totalDu ?? this.totalDu,
      nombreDettes: nombreDettes ?? this.nombreDettes,
      nombresRemboursements:
          nombresRemboursements ?? this.nombresRemboursements,
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
    if (nom.present) {
      map['nom'] = Variable<String>(nom.value);
    }
    if (telephone.present) {
      map['telephone'] = Variable<String>(telephone.value);
    }
    if (score.present) {
      map['score'] = Variable<String>(score.value);
    }
    if (totalDu.present) {
      map['total_du'] = Variable<int>(totalDu.value);
    }
    if (nombreDettes.present) {
      map['nombre_dettes'] = Variable<int>(nombreDettes.value);
    }
    if (nombresRemboursements.present) {
      map['nombres_remboursements'] =
          Variable<int>(nombresRemboursements.value);
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
    return (StringBuffer('ClientsCompanion(')
          ..write('id: $id, ')
          ..write('boutiqueId: $boutiqueId, ')
          ..write('nom: $nom, ')
          ..write('telephone: $telephone, ')
          ..write('score: $score, ')
          ..write('totalDu: $totalDu, ')
          ..write('nombreDettes: $nombreDettes, ')
          ..write('nombresRemboursements: $nombresRemboursements, ')
          ..write('synced: $synced, ')
          ..write('createdAt: $createdAt, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $VentesTable extends Ventes with TableInfo<$VentesTable, Vente> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $VentesTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<String> id = GeneratedColumn<String>(
      'id', aliasedName, false,
      additionalChecks:
          GeneratedColumn.checkTextLength(minTextLength: 36, maxTextLength: 36),
      type: DriftSqlType.string,
      requiredDuringInsert: true);
  static const VerificationMeta _boutiqueIdMeta =
      const VerificationMeta('boutiqueId');
  @override
  late final GeneratedColumn<String> boutiqueId = GeneratedColumn<String>(
      'boutique_id', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: true,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('REFERENCES boutiques (id)'));
  static const VerificationMeta _produitIdMeta =
      const VerificationMeta('produitId');
  @override
  late final GeneratedColumn<String> produitId = GeneratedColumn<String>(
      'produit_id', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: true,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('REFERENCES produits (id)'));
  static const VerificationMeta _clientIdMeta =
      const VerificationMeta('clientId');
  @override
  late final GeneratedColumn<String> clientId = GeneratedColumn<String>(
      'client_id', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _utilisateurIdMeta =
      const VerificationMeta('utilisateurId');
  @override
  late final GeneratedColumn<String> utilisateurId = GeneratedColumn<String>(
      'utilisateur_id', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: true,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('REFERENCES utilisateurs (id)'));
  static const VerificationMeta _quantiteMeta =
      const VerificationMeta('quantite');
  @override
  late final GeneratedColumn<int> quantite = GeneratedColumn<int>(
      'quantite', aliasedName, false,
      type: DriftSqlType.int, requiredDuringInsert: true);
  static const VerificationMeta _prixUnitaireMeta =
      const VerificationMeta('prixUnitaire');
  @override
  late final GeneratedColumn<int> prixUnitaire = GeneratedColumn<int>(
      'prix_unitaire', aliasedName, false,
      type: DriftSqlType.int, requiredDuringInsert: true);
  static const VerificationMeta _montantTotalMeta =
      const VerificationMeta('montantTotal');
  @override
  late final GeneratedColumn<int> montantTotal = GeneratedColumn<int>(
      'montant_total', aliasedName, false,
      type: DriftSqlType.int, requiredDuringInsert: true);
  static const VerificationMeta _typePaiementMeta =
      const VerificationMeta('typePaiement');
  @override
  late final GeneratedColumn<String> typePaiement = GeneratedColumn<String>(
      'type_paiement', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _sourceMeta = const VerificationMeta('source');
  @override
  late final GeneratedColumn<String> source = GeneratedColumn<String>(
      'source', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: false,
      defaultValue: const Constant('manuel'));
  static const VerificationMeta _syncedMeta = const VerificationMeta('synced');
  @override
  late final GeneratedColumn<bool> synced = GeneratedColumn<bool>(
      'synced', aliasedName, false,
      type: DriftSqlType.bool,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('CHECK ("synced" IN (0, 1))'),
      defaultValue: const Constant(false));
  static const VerificationMeta _dateMeta = const VerificationMeta('date');
  @override
  late final GeneratedColumn<DateTime> date = GeneratedColumn<DateTime>(
      'date', aliasedName, false,
      type: DriftSqlType.dateTime,
      requiredDuringInsert: false,
      defaultValue: currentDateAndTime);
  @override
  List<GeneratedColumn> get $columns => [
        id,
        boutiqueId,
        produitId,
        clientId,
        utilisateurId,
        quantite,
        prixUnitaire,
        montantTotal,
        typePaiement,
        source,
        synced,
        date
      ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'ventes';
  @override
  VerificationContext validateIntegrity(Insertable<Vente> instance,
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
    if (data.containsKey('produit_id')) {
      context.handle(_produitIdMeta,
          produitId.isAcceptableOrUnknown(data['produit_id']!, _produitIdMeta));
    } else if (isInserting) {
      context.missing(_produitIdMeta);
    }
    if (data.containsKey('client_id')) {
      context.handle(_clientIdMeta,
          clientId.isAcceptableOrUnknown(data['client_id']!, _clientIdMeta));
    }
    if (data.containsKey('utilisateur_id')) {
      context.handle(
          _utilisateurIdMeta,
          utilisateurId.isAcceptableOrUnknown(
              data['utilisateur_id']!, _utilisateurIdMeta));
    } else if (isInserting) {
      context.missing(_utilisateurIdMeta);
    }
    if (data.containsKey('quantite')) {
      context.handle(_quantiteMeta,
          quantite.isAcceptableOrUnknown(data['quantite']!, _quantiteMeta));
    } else if (isInserting) {
      context.missing(_quantiteMeta);
    }
    if (data.containsKey('prix_unitaire')) {
      context.handle(
          _prixUnitaireMeta,
          prixUnitaire.isAcceptableOrUnknown(
              data['prix_unitaire']!, _prixUnitaireMeta));
    } else if (isInserting) {
      context.missing(_prixUnitaireMeta);
    }
    if (data.containsKey('montant_total')) {
      context.handle(
          _montantTotalMeta,
          montantTotal.isAcceptableOrUnknown(
              data['montant_total']!, _montantTotalMeta));
    } else if (isInserting) {
      context.missing(_montantTotalMeta);
    }
    if (data.containsKey('type_paiement')) {
      context.handle(
          _typePaiementMeta,
          typePaiement.isAcceptableOrUnknown(
              data['type_paiement']!, _typePaiementMeta));
    } else if (isInserting) {
      context.missing(_typePaiementMeta);
    }
    if (data.containsKey('source')) {
      context.handle(_sourceMeta,
          source.isAcceptableOrUnknown(data['source']!, _sourceMeta));
    }
    if (data.containsKey('synced')) {
      context.handle(_syncedMeta,
          synced.isAcceptableOrUnknown(data['synced']!, _syncedMeta));
    }
    if (data.containsKey('date')) {
      context.handle(
          _dateMeta, date.isAcceptableOrUnknown(data['date']!, _dateMeta));
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  Vente map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return Vente(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}id'])!,
      boutiqueId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}boutique_id'])!,
      produitId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}produit_id'])!,
      clientId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}client_id']),
      utilisateurId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}utilisateur_id'])!,
      quantite: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}quantite'])!,
      prixUnitaire: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}prix_unitaire'])!,
      montantTotal: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}montant_total'])!,
      typePaiement: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}type_paiement'])!,
      source: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}source'])!,
      synced: attachedDatabase.typeMapping
          .read(DriftSqlType.bool, data['${effectivePrefix}synced'])!,
      date: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}date'])!,
    );
  }

  @override
  $VentesTable createAlias(String alias) {
    return $VentesTable(attachedDatabase, alias);
  }
}

class Vente extends DataClass implements Insertable<Vente> {
  final String id;
  final String boutiqueId;
  final String produitId;
  final String? clientId;
  final String utilisateurId;
  final int quantite;
  final int prixUnitaire;
  final int montantTotal;
  final String typePaiement;
  final String source;
  final bool synced;
  final DateTime date;
  const Vente(
      {required this.id,
      required this.boutiqueId,
      required this.produitId,
      this.clientId,
      required this.utilisateurId,
      required this.quantite,
      required this.prixUnitaire,
      required this.montantTotal,
      required this.typePaiement,
      required this.source,
      required this.synced,
      required this.date});
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<String>(id);
    map['boutique_id'] = Variable<String>(boutiqueId);
    map['produit_id'] = Variable<String>(produitId);
    if (!nullToAbsent || clientId != null) {
      map['client_id'] = Variable<String>(clientId);
    }
    map['utilisateur_id'] = Variable<String>(utilisateurId);
    map['quantite'] = Variable<int>(quantite);
    map['prix_unitaire'] = Variable<int>(prixUnitaire);
    map['montant_total'] = Variable<int>(montantTotal);
    map['type_paiement'] = Variable<String>(typePaiement);
    map['source'] = Variable<String>(source);
    map['synced'] = Variable<bool>(synced);
    map['date'] = Variable<DateTime>(date);
    return map;
  }

  VentesCompanion toCompanion(bool nullToAbsent) {
    return VentesCompanion(
      id: Value(id),
      boutiqueId: Value(boutiqueId),
      produitId: Value(produitId),
      clientId: clientId == null && nullToAbsent
          ? const Value.absent()
          : Value(clientId),
      utilisateurId: Value(utilisateurId),
      quantite: Value(quantite),
      prixUnitaire: Value(prixUnitaire),
      montantTotal: Value(montantTotal),
      typePaiement: Value(typePaiement),
      source: Value(source),
      synced: Value(synced),
      date: Value(date),
    );
  }

  factory Vente.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return Vente(
      id: serializer.fromJson<String>(json['id']),
      boutiqueId: serializer.fromJson<String>(json['boutiqueId']),
      produitId: serializer.fromJson<String>(json['produitId']),
      clientId: serializer.fromJson<String?>(json['clientId']),
      utilisateurId: serializer.fromJson<String>(json['utilisateurId']),
      quantite: serializer.fromJson<int>(json['quantite']),
      prixUnitaire: serializer.fromJson<int>(json['prixUnitaire']),
      montantTotal: serializer.fromJson<int>(json['montantTotal']),
      typePaiement: serializer.fromJson<String>(json['typePaiement']),
      source: serializer.fromJson<String>(json['source']),
      synced: serializer.fromJson<bool>(json['synced']),
      date: serializer.fromJson<DateTime>(json['date']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<String>(id),
      'boutiqueId': serializer.toJson<String>(boutiqueId),
      'produitId': serializer.toJson<String>(produitId),
      'clientId': serializer.toJson<String?>(clientId),
      'utilisateurId': serializer.toJson<String>(utilisateurId),
      'quantite': serializer.toJson<int>(quantite),
      'prixUnitaire': serializer.toJson<int>(prixUnitaire),
      'montantTotal': serializer.toJson<int>(montantTotal),
      'typePaiement': serializer.toJson<String>(typePaiement),
      'source': serializer.toJson<String>(source),
      'synced': serializer.toJson<bool>(synced),
      'date': serializer.toJson<DateTime>(date),
    };
  }

  Vente copyWith(
          {String? id,
          String? boutiqueId,
          String? produitId,
          Value<String?> clientId = const Value.absent(),
          String? utilisateurId,
          int? quantite,
          int? prixUnitaire,
          int? montantTotal,
          String? typePaiement,
          String? source,
          bool? synced,
          DateTime? date}) =>
      Vente(
        id: id ?? this.id,
        boutiqueId: boutiqueId ?? this.boutiqueId,
        produitId: produitId ?? this.produitId,
        clientId: clientId.present ? clientId.value : this.clientId,
        utilisateurId: utilisateurId ?? this.utilisateurId,
        quantite: quantite ?? this.quantite,
        prixUnitaire: prixUnitaire ?? this.prixUnitaire,
        montantTotal: montantTotal ?? this.montantTotal,
        typePaiement: typePaiement ?? this.typePaiement,
        source: source ?? this.source,
        synced: synced ?? this.synced,
        date: date ?? this.date,
      );
  Vente copyWithCompanion(VentesCompanion data) {
    return Vente(
      id: data.id.present ? data.id.value : this.id,
      boutiqueId:
          data.boutiqueId.present ? data.boutiqueId.value : this.boutiqueId,
      produitId: data.produitId.present ? data.produitId.value : this.produitId,
      clientId: data.clientId.present ? data.clientId.value : this.clientId,
      utilisateurId: data.utilisateurId.present
          ? data.utilisateurId.value
          : this.utilisateurId,
      quantite: data.quantite.present ? data.quantite.value : this.quantite,
      prixUnitaire: data.prixUnitaire.present
          ? data.prixUnitaire.value
          : this.prixUnitaire,
      montantTotal: data.montantTotal.present
          ? data.montantTotal.value
          : this.montantTotal,
      typePaiement: data.typePaiement.present
          ? data.typePaiement.value
          : this.typePaiement,
      source: data.source.present ? data.source.value : this.source,
      synced: data.synced.present ? data.synced.value : this.synced,
      date: data.date.present ? data.date.value : this.date,
    );
  }

  @override
  String toString() {
    return (StringBuffer('Vente(')
          ..write('id: $id, ')
          ..write('boutiqueId: $boutiqueId, ')
          ..write('produitId: $produitId, ')
          ..write('clientId: $clientId, ')
          ..write('utilisateurId: $utilisateurId, ')
          ..write('quantite: $quantite, ')
          ..write('prixUnitaire: $prixUnitaire, ')
          ..write('montantTotal: $montantTotal, ')
          ..write('typePaiement: $typePaiement, ')
          ..write('source: $source, ')
          ..write('synced: $synced, ')
          ..write('date: $date')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
      id,
      boutiqueId,
      produitId,
      clientId,
      utilisateurId,
      quantite,
      prixUnitaire,
      montantTotal,
      typePaiement,
      source,
      synced,
      date);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is Vente &&
          other.id == this.id &&
          other.boutiqueId == this.boutiqueId &&
          other.produitId == this.produitId &&
          other.clientId == this.clientId &&
          other.utilisateurId == this.utilisateurId &&
          other.quantite == this.quantite &&
          other.prixUnitaire == this.prixUnitaire &&
          other.montantTotal == this.montantTotal &&
          other.typePaiement == this.typePaiement &&
          other.source == this.source &&
          other.synced == this.synced &&
          other.date == this.date);
}

class VentesCompanion extends UpdateCompanion<Vente> {
  final Value<String> id;
  final Value<String> boutiqueId;
  final Value<String> produitId;
  final Value<String?> clientId;
  final Value<String> utilisateurId;
  final Value<int> quantite;
  final Value<int> prixUnitaire;
  final Value<int> montantTotal;
  final Value<String> typePaiement;
  final Value<String> source;
  final Value<bool> synced;
  final Value<DateTime> date;
  final Value<int> rowid;
  const VentesCompanion({
    this.id = const Value.absent(),
    this.boutiqueId = const Value.absent(),
    this.produitId = const Value.absent(),
    this.clientId = const Value.absent(),
    this.utilisateurId = const Value.absent(),
    this.quantite = const Value.absent(),
    this.prixUnitaire = const Value.absent(),
    this.montantTotal = const Value.absent(),
    this.typePaiement = const Value.absent(),
    this.source = const Value.absent(),
    this.synced = const Value.absent(),
    this.date = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  VentesCompanion.insert({
    required String id,
    required String boutiqueId,
    required String produitId,
    this.clientId = const Value.absent(),
    required String utilisateurId,
    required int quantite,
    required int prixUnitaire,
    required int montantTotal,
    required String typePaiement,
    this.source = const Value.absent(),
    this.synced = const Value.absent(),
    this.date = const Value.absent(),
    this.rowid = const Value.absent(),
  })  : id = Value(id),
        boutiqueId = Value(boutiqueId),
        produitId = Value(produitId),
        utilisateurId = Value(utilisateurId),
        quantite = Value(quantite),
        prixUnitaire = Value(prixUnitaire),
        montantTotal = Value(montantTotal),
        typePaiement = Value(typePaiement);
  static Insertable<Vente> custom({
    Expression<String>? id,
    Expression<String>? boutiqueId,
    Expression<String>? produitId,
    Expression<String>? clientId,
    Expression<String>? utilisateurId,
    Expression<int>? quantite,
    Expression<int>? prixUnitaire,
    Expression<int>? montantTotal,
    Expression<String>? typePaiement,
    Expression<String>? source,
    Expression<bool>? synced,
    Expression<DateTime>? date,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (boutiqueId != null) 'boutique_id': boutiqueId,
      if (produitId != null) 'produit_id': produitId,
      if (clientId != null) 'client_id': clientId,
      if (utilisateurId != null) 'utilisateur_id': utilisateurId,
      if (quantite != null) 'quantite': quantite,
      if (prixUnitaire != null) 'prix_unitaire': prixUnitaire,
      if (montantTotal != null) 'montant_total': montantTotal,
      if (typePaiement != null) 'type_paiement': typePaiement,
      if (source != null) 'source': source,
      if (synced != null) 'synced': synced,
      if (date != null) 'date': date,
      if (rowid != null) 'rowid': rowid,
    });
  }

  VentesCompanion copyWith(
      {Value<String>? id,
      Value<String>? boutiqueId,
      Value<String>? produitId,
      Value<String?>? clientId,
      Value<String>? utilisateurId,
      Value<int>? quantite,
      Value<int>? prixUnitaire,
      Value<int>? montantTotal,
      Value<String>? typePaiement,
      Value<String>? source,
      Value<bool>? synced,
      Value<DateTime>? date,
      Value<int>? rowid}) {
    return VentesCompanion(
      id: id ?? this.id,
      boutiqueId: boutiqueId ?? this.boutiqueId,
      produitId: produitId ?? this.produitId,
      clientId: clientId ?? this.clientId,
      utilisateurId: utilisateurId ?? this.utilisateurId,
      quantite: quantite ?? this.quantite,
      prixUnitaire: prixUnitaire ?? this.prixUnitaire,
      montantTotal: montantTotal ?? this.montantTotal,
      typePaiement: typePaiement ?? this.typePaiement,
      source: source ?? this.source,
      synced: synced ?? this.synced,
      date: date ?? this.date,
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
    if (produitId.present) {
      map['produit_id'] = Variable<String>(produitId.value);
    }
    if (clientId.present) {
      map['client_id'] = Variable<String>(clientId.value);
    }
    if (utilisateurId.present) {
      map['utilisateur_id'] = Variable<String>(utilisateurId.value);
    }
    if (quantite.present) {
      map['quantite'] = Variable<int>(quantite.value);
    }
    if (prixUnitaire.present) {
      map['prix_unitaire'] = Variable<int>(prixUnitaire.value);
    }
    if (montantTotal.present) {
      map['montant_total'] = Variable<int>(montantTotal.value);
    }
    if (typePaiement.present) {
      map['type_paiement'] = Variable<String>(typePaiement.value);
    }
    if (source.present) {
      map['source'] = Variable<String>(source.value);
    }
    if (synced.present) {
      map['synced'] = Variable<bool>(synced.value);
    }
    if (date.present) {
      map['date'] = Variable<DateTime>(date.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('VentesCompanion(')
          ..write('id: $id, ')
          ..write('boutiqueId: $boutiqueId, ')
          ..write('produitId: $produitId, ')
          ..write('clientId: $clientId, ')
          ..write('utilisateurId: $utilisateurId, ')
          ..write('quantite: $quantite, ')
          ..write('prixUnitaire: $prixUnitaire, ')
          ..write('montantTotal: $montantTotal, ')
          ..write('typePaiement: $typePaiement, ')
          ..write('source: $source, ')
          ..write('synced: $synced, ')
          ..write('date: $date, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $DettesTable extends Dettes with TableInfo<$DettesTable, Dette> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $DettesTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<String> id = GeneratedColumn<String>(
      'id', aliasedName, false,
      additionalChecks:
          GeneratedColumn.checkTextLength(minTextLength: 36, maxTextLength: 36),
      type: DriftSqlType.string,
      requiredDuringInsert: true);
  static const VerificationMeta _clientIdMeta =
      const VerificationMeta('clientId');
  @override
  late final GeneratedColumn<String> clientId = GeneratedColumn<String>(
      'client_id', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: true,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('REFERENCES clients (id)'));
  static const VerificationMeta _venteIdMeta =
      const VerificationMeta('venteId');
  @override
  late final GeneratedColumn<String> venteId = GeneratedColumn<String>(
      'vente_id', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: true,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('REFERENCES ventes (id)'));
  static const VerificationMeta _boutiqueIdMeta =
      const VerificationMeta('boutiqueId');
  @override
  late final GeneratedColumn<String> boutiqueId = GeneratedColumn<String>(
      'boutique_id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _montantMeta =
      const VerificationMeta('montant');
  @override
  late final GeneratedColumn<int> montant = GeneratedColumn<int>(
      'montant', aliasedName, false,
      type: DriftSqlType.int, requiredDuringInsert: true);
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
  static const VerificationMeta _rappel1JourEnvoyeMeta =
      const VerificationMeta('rappel1JourEnvoye');
  @override
  late final GeneratedColumn<bool> rappel1JourEnvoye = GeneratedColumn<bool>(
      'rappel1_jour_envoye', aliasedName, false,
      type: DriftSqlType.bool,
      requiredDuringInsert: false,
      defaultConstraints: GeneratedColumn.constraintIsAlways(
          'CHECK ("rappel1_jour_envoye" IN (0, 1))'),
      defaultValue: const Constant(false));
  static const VerificationMeta _rappel3JoursEnvoyeMeta =
      const VerificationMeta('rappel3JoursEnvoye');
  @override
  late final GeneratedColumn<bool> rappel3JoursEnvoye = GeneratedColumn<bool>(
      'rappel3_jours_envoye', aliasedName, false,
      type: DriftSqlType.bool,
      requiredDuringInsert: false,
      defaultConstraints: GeneratedColumn.constraintIsAlways(
          'CHECK ("rappel3_jours_envoye" IN (0, 1))'),
      defaultValue: const Constant(false));
  static const VerificationMeta _rappel7JoursEnvoyeMeta =
      const VerificationMeta('rappel7JoursEnvoye');
  @override
  late final GeneratedColumn<bool> rappel7JoursEnvoye = GeneratedColumn<bool>(
      'rappel7_jours_envoye', aliasedName, false,
      type: DriftSqlType.bool,
      requiredDuringInsert: false,
      defaultConstraints: GeneratedColumn.constraintIsAlways(
          'CHECK ("rappel7_jours_envoye" IN (0, 1))'),
      defaultValue: const Constant(false));
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
        clientId,
        venteId,
        boutiqueId,
        montant,
        montantPaye,
        statut,
        dateEcheance,
        rappel1JourEnvoye,
        rappel3JoursEnvoye,
        rappel7JoursEnvoye,
        synced,
        createdAt,
        updatedAt
      ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'dettes';
  @override
  VerificationContext validateIntegrity(Insertable<Dette> instance,
      {bool isInserting = false}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    } else if (isInserting) {
      context.missing(_idMeta);
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
    } else if (isInserting) {
      context.missing(_venteIdMeta);
    }
    if (data.containsKey('boutique_id')) {
      context.handle(
          _boutiqueIdMeta,
          boutiqueId.isAcceptableOrUnknown(
              data['boutique_id']!, _boutiqueIdMeta));
    } else if (isInserting) {
      context.missing(_boutiqueIdMeta);
    }
    if (data.containsKey('montant')) {
      context.handle(_montantMeta,
          montant.isAcceptableOrUnknown(data['montant']!, _montantMeta));
    } else if (isInserting) {
      context.missing(_montantMeta);
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
    if (data.containsKey('rappel1_jour_envoye')) {
      context.handle(
          _rappel1JourEnvoyeMeta,
          rappel1JourEnvoye.isAcceptableOrUnknown(
              data['rappel1_jour_envoye']!, _rappel1JourEnvoyeMeta));
    }
    if (data.containsKey('rappel3_jours_envoye')) {
      context.handle(
          _rappel3JoursEnvoyeMeta,
          rappel3JoursEnvoye.isAcceptableOrUnknown(
              data['rappel3_jours_envoye']!, _rappel3JoursEnvoyeMeta));
    }
    if (data.containsKey('rappel7_jours_envoye')) {
      context.handle(
          _rappel7JoursEnvoyeMeta,
          rappel7JoursEnvoye.isAcceptableOrUnknown(
              data['rappel7_jours_envoye']!, _rappel7JoursEnvoyeMeta));
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
  Dette map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return Dette(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}id'])!,
      clientId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}client_id'])!,
      venteId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}vente_id'])!,
      boutiqueId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}boutique_id'])!,
      montant: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}montant'])!,
      montantPaye: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}montant_paye'])!,
      statut: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}statut'])!,
      dateEcheance: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}date_echeance']),
      rappel1JourEnvoye: attachedDatabase.typeMapping.read(
          DriftSqlType.bool, data['${effectivePrefix}rappel1_jour_envoye'])!,
      rappel3JoursEnvoye: attachedDatabase.typeMapping.read(
          DriftSqlType.bool, data['${effectivePrefix}rappel3_jours_envoye'])!,
      rappel7JoursEnvoye: attachedDatabase.typeMapping.read(
          DriftSqlType.bool, data['${effectivePrefix}rappel7_jours_envoye'])!,
      synced: attachedDatabase.typeMapping
          .read(DriftSqlType.bool, data['${effectivePrefix}synced'])!,
      createdAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}created_at'])!,
      updatedAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}updated_at'])!,
    );
  }

  @override
  $DettesTable createAlias(String alias) {
    return $DettesTable(attachedDatabase, alias);
  }
}

class Dette extends DataClass implements Insertable<Dette> {
  final String id;
  final String clientId;
  final String venteId;
  final String boutiqueId;
  final int montant;
  final int montantPaye;
  final String statut;
  final DateTime? dateEcheance;
  final bool rappel1JourEnvoye;
  final bool rappel3JoursEnvoye;
  final bool rappel7JoursEnvoye;
  final bool synced;
  final DateTime createdAt;
  final DateTime updatedAt;
  const Dette(
      {required this.id,
      required this.clientId,
      required this.venteId,
      required this.boutiqueId,
      required this.montant,
      required this.montantPaye,
      required this.statut,
      this.dateEcheance,
      required this.rappel1JourEnvoye,
      required this.rappel3JoursEnvoye,
      required this.rappel7JoursEnvoye,
      required this.synced,
      required this.createdAt,
      required this.updatedAt});
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<String>(id);
    map['client_id'] = Variable<String>(clientId);
    map['vente_id'] = Variable<String>(venteId);
    map['boutique_id'] = Variable<String>(boutiqueId);
    map['montant'] = Variable<int>(montant);
    map['montant_paye'] = Variable<int>(montantPaye);
    map['statut'] = Variable<String>(statut);
    if (!nullToAbsent || dateEcheance != null) {
      map['date_echeance'] = Variable<DateTime>(dateEcheance);
    }
    map['rappel1_jour_envoye'] = Variable<bool>(rappel1JourEnvoye);
    map['rappel3_jours_envoye'] = Variable<bool>(rappel3JoursEnvoye);
    map['rappel7_jours_envoye'] = Variable<bool>(rappel7JoursEnvoye);
    map['synced'] = Variable<bool>(synced);
    map['created_at'] = Variable<DateTime>(createdAt);
    map['updated_at'] = Variable<DateTime>(updatedAt);
    return map;
  }

  DettesCompanion toCompanion(bool nullToAbsent) {
    return DettesCompanion(
      id: Value(id),
      clientId: Value(clientId),
      venteId: Value(venteId),
      boutiqueId: Value(boutiqueId),
      montant: Value(montant),
      montantPaye: Value(montantPaye),
      statut: Value(statut),
      dateEcheance: dateEcheance == null && nullToAbsent
          ? const Value.absent()
          : Value(dateEcheance),
      rappel1JourEnvoye: Value(rappel1JourEnvoye),
      rappel3JoursEnvoye: Value(rappel3JoursEnvoye),
      rappel7JoursEnvoye: Value(rappel7JoursEnvoye),
      synced: Value(synced),
      createdAt: Value(createdAt),
      updatedAt: Value(updatedAt),
    );
  }

  factory Dette.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return Dette(
      id: serializer.fromJson<String>(json['id']),
      clientId: serializer.fromJson<String>(json['clientId']),
      venteId: serializer.fromJson<String>(json['venteId']),
      boutiqueId: serializer.fromJson<String>(json['boutiqueId']),
      montant: serializer.fromJson<int>(json['montant']),
      montantPaye: serializer.fromJson<int>(json['montantPaye']),
      statut: serializer.fromJson<String>(json['statut']),
      dateEcheance: serializer.fromJson<DateTime?>(json['dateEcheance']),
      rappel1JourEnvoye: serializer.fromJson<bool>(json['rappel1JourEnvoye']),
      rappel3JoursEnvoye: serializer.fromJson<bool>(json['rappel3JoursEnvoye']),
      rappel7JoursEnvoye: serializer.fromJson<bool>(json['rappel7JoursEnvoye']),
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
      'clientId': serializer.toJson<String>(clientId),
      'venteId': serializer.toJson<String>(venteId),
      'boutiqueId': serializer.toJson<String>(boutiqueId),
      'montant': serializer.toJson<int>(montant),
      'montantPaye': serializer.toJson<int>(montantPaye),
      'statut': serializer.toJson<String>(statut),
      'dateEcheance': serializer.toJson<DateTime?>(dateEcheance),
      'rappel1JourEnvoye': serializer.toJson<bool>(rappel1JourEnvoye),
      'rappel3JoursEnvoye': serializer.toJson<bool>(rappel3JoursEnvoye),
      'rappel7JoursEnvoye': serializer.toJson<bool>(rappel7JoursEnvoye),
      'synced': serializer.toJson<bool>(synced),
      'createdAt': serializer.toJson<DateTime>(createdAt),
      'updatedAt': serializer.toJson<DateTime>(updatedAt),
    };
  }

  Dette copyWith(
          {String? id,
          String? clientId,
          String? venteId,
          String? boutiqueId,
          int? montant,
          int? montantPaye,
          String? statut,
          Value<DateTime?> dateEcheance = const Value.absent(),
          bool? rappel1JourEnvoye,
          bool? rappel3JoursEnvoye,
          bool? rappel7JoursEnvoye,
          bool? synced,
          DateTime? createdAt,
          DateTime? updatedAt}) =>
      Dette(
        id: id ?? this.id,
        clientId: clientId ?? this.clientId,
        venteId: venteId ?? this.venteId,
        boutiqueId: boutiqueId ?? this.boutiqueId,
        montant: montant ?? this.montant,
        montantPaye: montantPaye ?? this.montantPaye,
        statut: statut ?? this.statut,
        dateEcheance:
            dateEcheance.present ? dateEcheance.value : this.dateEcheance,
        rappel1JourEnvoye: rappel1JourEnvoye ?? this.rappel1JourEnvoye,
        rappel3JoursEnvoye: rappel3JoursEnvoye ?? this.rappel3JoursEnvoye,
        rappel7JoursEnvoye: rappel7JoursEnvoye ?? this.rappel7JoursEnvoye,
        synced: synced ?? this.synced,
        createdAt: createdAt ?? this.createdAt,
        updatedAt: updatedAt ?? this.updatedAt,
      );
  Dette copyWithCompanion(DettesCompanion data) {
    return Dette(
      id: data.id.present ? data.id.value : this.id,
      clientId: data.clientId.present ? data.clientId.value : this.clientId,
      venteId: data.venteId.present ? data.venteId.value : this.venteId,
      boutiqueId:
          data.boutiqueId.present ? data.boutiqueId.value : this.boutiqueId,
      montant: data.montant.present ? data.montant.value : this.montant,
      montantPaye:
          data.montantPaye.present ? data.montantPaye.value : this.montantPaye,
      statut: data.statut.present ? data.statut.value : this.statut,
      dateEcheance: data.dateEcheance.present
          ? data.dateEcheance.value
          : this.dateEcheance,
      rappel1JourEnvoye: data.rappel1JourEnvoye.present
          ? data.rappel1JourEnvoye.value
          : this.rappel1JourEnvoye,
      rappel3JoursEnvoye: data.rappel3JoursEnvoye.present
          ? data.rappel3JoursEnvoye.value
          : this.rappel3JoursEnvoye,
      rappel7JoursEnvoye: data.rappel7JoursEnvoye.present
          ? data.rappel7JoursEnvoye.value
          : this.rappel7JoursEnvoye,
      synced: data.synced.present ? data.synced.value : this.synced,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
      updatedAt: data.updatedAt.present ? data.updatedAt.value : this.updatedAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('Dette(')
          ..write('id: $id, ')
          ..write('clientId: $clientId, ')
          ..write('venteId: $venteId, ')
          ..write('boutiqueId: $boutiqueId, ')
          ..write('montant: $montant, ')
          ..write('montantPaye: $montantPaye, ')
          ..write('statut: $statut, ')
          ..write('dateEcheance: $dateEcheance, ')
          ..write('rappel1JourEnvoye: $rappel1JourEnvoye, ')
          ..write('rappel3JoursEnvoye: $rappel3JoursEnvoye, ')
          ..write('rappel7JoursEnvoye: $rappel7JoursEnvoye, ')
          ..write('synced: $synced, ')
          ..write('createdAt: $createdAt, ')
          ..write('updatedAt: $updatedAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
      id,
      clientId,
      venteId,
      boutiqueId,
      montant,
      montantPaye,
      statut,
      dateEcheance,
      rappel1JourEnvoye,
      rappel3JoursEnvoye,
      rappel7JoursEnvoye,
      synced,
      createdAt,
      updatedAt);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is Dette &&
          other.id == this.id &&
          other.clientId == this.clientId &&
          other.venteId == this.venteId &&
          other.boutiqueId == this.boutiqueId &&
          other.montant == this.montant &&
          other.montantPaye == this.montantPaye &&
          other.statut == this.statut &&
          other.dateEcheance == this.dateEcheance &&
          other.rappel1JourEnvoye == this.rappel1JourEnvoye &&
          other.rappel3JoursEnvoye == this.rappel3JoursEnvoye &&
          other.rappel7JoursEnvoye == this.rappel7JoursEnvoye &&
          other.synced == this.synced &&
          other.createdAt == this.createdAt &&
          other.updatedAt == this.updatedAt);
}

class DettesCompanion extends UpdateCompanion<Dette> {
  final Value<String> id;
  final Value<String> clientId;
  final Value<String> venteId;
  final Value<String> boutiqueId;
  final Value<int> montant;
  final Value<int> montantPaye;
  final Value<String> statut;
  final Value<DateTime?> dateEcheance;
  final Value<bool> rappel1JourEnvoye;
  final Value<bool> rappel3JoursEnvoye;
  final Value<bool> rappel7JoursEnvoye;
  final Value<bool> synced;
  final Value<DateTime> createdAt;
  final Value<DateTime> updatedAt;
  final Value<int> rowid;
  const DettesCompanion({
    this.id = const Value.absent(),
    this.clientId = const Value.absent(),
    this.venteId = const Value.absent(),
    this.boutiqueId = const Value.absent(),
    this.montant = const Value.absent(),
    this.montantPaye = const Value.absent(),
    this.statut = const Value.absent(),
    this.dateEcheance = const Value.absent(),
    this.rappel1JourEnvoye = const Value.absent(),
    this.rappel3JoursEnvoye = const Value.absent(),
    this.rappel7JoursEnvoye = const Value.absent(),
    this.synced = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  DettesCompanion.insert({
    required String id,
    required String clientId,
    required String venteId,
    required String boutiqueId,
    required int montant,
    this.montantPaye = const Value.absent(),
    this.statut = const Value.absent(),
    this.dateEcheance = const Value.absent(),
    this.rappel1JourEnvoye = const Value.absent(),
    this.rappel3JoursEnvoye = const Value.absent(),
    this.rappel7JoursEnvoye = const Value.absent(),
    this.synced = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.updatedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  })  : id = Value(id),
        clientId = Value(clientId),
        venteId = Value(venteId),
        boutiqueId = Value(boutiqueId),
        montant = Value(montant);
  static Insertable<Dette> custom({
    Expression<String>? id,
    Expression<String>? clientId,
    Expression<String>? venteId,
    Expression<String>? boutiqueId,
    Expression<int>? montant,
    Expression<int>? montantPaye,
    Expression<String>? statut,
    Expression<DateTime>? dateEcheance,
    Expression<bool>? rappel1JourEnvoye,
    Expression<bool>? rappel3JoursEnvoye,
    Expression<bool>? rappel7JoursEnvoye,
    Expression<bool>? synced,
    Expression<DateTime>? createdAt,
    Expression<DateTime>? updatedAt,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (clientId != null) 'client_id': clientId,
      if (venteId != null) 'vente_id': venteId,
      if (boutiqueId != null) 'boutique_id': boutiqueId,
      if (montant != null) 'montant': montant,
      if (montantPaye != null) 'montant_paye': montantPaye,
      if (statut != null) 'statut': statut,
      if (dateEcheance != null) 'date_echeance': dateEcheance,
      if (rappel1JourEnvoye != null) 'rappel1_jour_envoye': rappel1JourEnvoye,
      if (rappel3JoursEnvoye != null)
        'rappel3_jours_envoye': rappel3JoursEnvoye,
      if (rappel7JoursEnvoye != null)
        'rappel7_jours_envoye': rappel7JoursEnvoye,
      if (synced != null) 'synced': synced,
      if (createdAt != null) 'created_at': createdAt,
      if (updatedAt != null) 'updated_at': updatedAt,
      if (rowid != null) 'rowid': rowid,
    });
  }

  DettesCompanion copyWith(
      {Value<String>? id,
      Value<String>? clientId,
      Value<String>? venteId,
      Value<String>? boutiqueId,
      Value<int>? montant,
      Value<int>? montantPaye,
      Value<String>? statut,
      Value<DateTime?>? dateEcheance,
      Value<bool>? rappel1JourEnvoye,
      Value<bool>? rappel3JoursEnvoye,
      Value<bool>? rappel7JoursEnvoye,
      Value<bool>? synced,
      Value<DateTime>? createdAt,
      Value<DateTime>? updatedAt,
      Value<int>? rowid}) {
    return DettesCompanion(
      id: id ?? this.id,
      clientId: clientId ?? this.clientId,
      venteId: venteId ?? this.venteId,
      boutiqueId: boutiqueId ?? this.boutiqueId,
      montant: montant ?? this.montant,
      montantPaye: montantPaye ?? this.montantPaye,
      statut: statut ?? this.statut,
      dateEcheance: dateEcheance ?? this.dateEcheance,
      rappel1JourEnvoye: rappel1JourEnvoye ?? this.rappel1JourEnvoye,
      rappel3JoursEnvoye: rappel3JoursEnvoye ?? this.rappel3JoursEnvoye,
      rappel7JoursEnvoye: rappel7JoursEnvoye ?? this.rappel7JoursEnvoye,
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
    if (clientId.present) {
      map['client_id'] = Variable<String>(clientId.value);
    }
    if (venteId.present) {
      map['vente_id'] = Variable<String>(venteId.value);
    }
    if (boutiqueId.present) {
      map['boutique_id'] = Variable<String>(boutiqueId.value);
    }
    if (montant.present) {
      map['montant'] = Variable<int>(montant.value);
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
    if (rappel1JourEnvoye.present) {
      map['rappel1_jour_envoye'] = Variable<bool>(rappel1JourEnvoye.value);
    }
    if (rappel3JoursEnvoye.present) {
      map['rappel3_jours_envoye'] = Variable<bool>(rappel3JoursEnvoye.value);
    }
    if (rappel7JoursEnvoye.present) {
      map['rappel7_jours_envoye'] = Variable<bool>(rappel7JoursEnvoye.value);
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
    return (StringBuffer('DettesCompanion(')
          ..write('id: $id, ')
          ..write('clientId: $clientId, ')
          ..write('venteId: $venteId, ')
          ..write('boutiqueId: $boutiqueId, ')
          ..write('montant: $montant, ')
          ..write('montantPaye: $montantPaye, ')
          ..write('statut: $statut, ')
          ..write('dateEcheance: $dateEcheance, ')
          ..write('rappel1JourEnvoye: $rappel1JourEnvoye, ')
          ..write('rappel3JoursEnvoye: $rappel3JoursEnvoye, ')
          ..write('rappel7JoursEnvoye: $rappel7JoursEnvoye, ')
          ..write('synced: $synced, ')
          ..write('createdAt: $createdAt, ')
          ..write('updatedAt: $updatedAt, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $PaiementsTable extends Paiements
    with TableInfo<$PaiementsTable, Paiement> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $PaiementsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<String> id = GeneratedColumn<String>(
      'id', aliasedName, false,
      additionalChecks:
          GeneratedColumn.checkTextLength(minTextLength: 36, maxTextLength: 36),
      type: DriftSqlType.string,
      requiredDuringInsert: true);
  static const VerificationMeta _detteIdMeta =
      const VerificationMeta('detteId');
  @override
  late final GeneratedColumn<String> detteId = GeneratedColumn<String>(
      'dette_id', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: true,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('REFERENCES dettes (id)'));
  static const VerificationMeta _boutiqueIdMeta =
      const VerificationMeta('boutiqueId');
  @override
  late final GeneratedColumn<String> boutiqueId = GeneratedColumn<String>(
      'boutique_id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _montantMeta =
      const VerificationMeta('montant');
  @override
  late final GeneratedColumn<int> montant = GeneratedColumn<int>(
      'montant', aliasedName, false,
      type: DriftSqlType.int, requiredDuringInsert: true);
  static const VerificationMeta _modePaiementMeta =
      const VerificationMeta('modePaiement');
  @override
  late final GeneratedColumn<String> modePaiement = GeneratedColumn<String>(
      'mode_paiement', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: false,
      defaultValue: const Constant('especes'));
  static const VerificationMeta _syncedMeta = const VerificationMeta('synced');
  @override
  late final GeneratedColumn<bool> synced = GeneratedColumn<bool>(
      'synced', aliasedName, false,
      type: DriftSqlType.bool,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('CHECK ("synced" IN (0, 1))'),
      defaultValue: const Constant(false));
  static const VerificationMeta _dateMeta = const VerificationMeta('date');
  @override
  late final GeneratedColumn<DateTime> date = GeneratedColumn<DateTime>(
      'date', aliasedName, false,
      type: DriftSqlType.dateTime,
      requiredDuringInsert: false,
      defaultValue: currentDateAndTime);
  @override
  List<GeneratedColumn> get $columns =>
      [id, detteId, boutiqueId, montant, modePaiement, synced, date];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'paiements';
  @override
  VerificationContext validateIntegrity(Insertable<Paiement> instance,
      {bool isInserting = false}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    } else if (isInserting) {
      context.missing(_idMeta);
    }
    if (data.containsKey('dette_id')) {
      context.handle(_detteIdMeta,
          detteId.isAcceptableOrUnknown(data['dette_id']!, _detteIdMeta));
    } else if (isInserting) {
      context.missing(_detteIdMeta);
    }
    if (data.containsKey('boutique_id')) {
      context.handle(
          _boutiqueIdMeta,
          boutiqueId.isAcceptableOrUnknown(
              data['boutique_id']!, _boutiqueIdMeta));
    } else if (isInserting) {
      context.missing(_boutiqueIdMeta);
    }
    if (data.containsKey('montant')) {
      context.handle(_montantMeta,
          montant.isAcceptableOrUnknown(data['montant']!, _montantMeta));
    } else if (isInserting) {
      context.missing(_montantMeta);
    }
    if (data.containsKey('mode_paiement')) {
      context.handle(
          _modePaiementMeta,
          modePaiement.isAcceptableOrUnknown(
              data['mode_paiement']!, _modePaiementMeta));
    }
    if (data.containsKey('synced')) {
      context.handle(_syncedMeta,
          synced.isAcceptableOrUnknown(data['synced']!, _syncedMeta));
    }
    if (data.containsKey('date')) {
      context.handle(
          _dateMeta, date.isAcceptableOrUnknown(data['date']!, _dateMeta));
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  Paiement map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return Paiement(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}id'])!,
      detteId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}dette_id'])!,
      boutiqueId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}boutique_id'])!,
      montant: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}montant'])!,
      modePaiement: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}mode_paiement'])!,
      synced: attachedDatabase.typeMapping
          .read(DriftSqlType.bool, data['${effectivePrefix}synced'])!,
      date: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}date'])!,
    );
  }

  @override
  $PaiementsTable createAlias(String alias) {
    return $PaiementsTable(attachedDatabase, alias);
  }
}

class Paiement extends DataClass implements Insertable<Paiement> {
  final String id;
  final String detteId;
  final String boutiqueId;
  final int montant;
  final String modePaiement;
  final bool synced;
  final DateTime date;
  const Paiement(
      {required this.id,
      required this.detteId,
      required this.boutiqueId,
      required this.montant,
      required this.modePaiement,
      required this.synced,
      required this.date});
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<String>(id);
    map['dette_id'] = Variable<String>(detteId);
    map['boutique_id'] = Variable<String>(boutiqueId);
    map['montant'] = Variable<int>(montant);
    map['mode_paiement'] = Variable<String>(modePaiement);
    map['synced'] = Variable<bool>(synced);
    map['date'] = Variable<DateTime>(date);
    return map;
  }

  PaiementsCompanion toCompanion(bool nullToAbsent) {
    return PaiementsCompanion(
      id: Value(id),
      detteId: Value(detteId),
      boutiqueId: Value(boutiqueId),
      montant: Value(montant),
      modePaiement: Value(modePaiement),
      synced: Value(synced),
      date: Value(date),
    );
  }

  factory Paiement.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return Paiement(
      id: serializer.fromJson<String>(json['id']),
      detteId: serializer.fromJson<String>(json['detteId']),
      boutiqueId: serializer.fromJson<String>(json['boutiqueId']),
      montant: serializer.fromJson<int>(json['montant']),
      modePaiement: serializer.fromJson<String>(json['modePaiement']),
      synced: serializer.fromJson<bool>(json['synced']),
      date: serializer.fromJson<DateTime>(json['date']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<String>(id),
      'detteId': serializer.toJson<String>(detteId),
      'boutiqueId': serializer.toJson<String>(boutiqueId),
      'montant': serializer.toJson<int>(montant),
      'modePaiement': serializer.toJson<String>(modePaiement),
      'synced': serializer.toJson<bool>(synced),
      'date': serializer.toJson<DateTime>(date),
    };
  }

  Paiement copyWith(
          {String? id,
          String? detteId,
          String? boutiqueId,
          int? montant,
          String? modePaiement,
          bool? synced,
          DateTime? date}) =>
      Paiement(
        id: id ?? this.id,
        detteId: detteId ?? this.detteId,
        boutiqueId: boutiqueId ?? this.boutiqueId,
        montant: montant ?? this.montant,
        modePaiement: modePaiement ?? this.modePaiement,
        synced: synced ?? this.synced,
        date: date ?? this.date,
      );
  Paiement copyWithCompanion(PaiementsCompanion data) {
    return Paiement(
      id: data.id.present ? data.id.value : this.id,
      detteId: data.detteId.present ? data.detteId.value : this.detteId,
      boutiqueId:
          data.boutiqueId.present ? data.boutiqueId.value : this.boutiqueId,
      montant: data.montant.present ? data.montant.value : this.montant,
      modePaiement: data.modePaiement.present
          ? data.modePaiement.value
          : this.modePaiement,
      synced: data.synced.present ? data.synced.value : this.synced,
      date: data.date.present ? data.date.value : this.date,
    );
  }

  @override
  String toString() {
    return (StringBuffer('Paiement(')
          ..write('id: $id, ')
          ..write('detteId: $detteId, ')
          ..write('boutiqueId: $boutiqueId, ')
          ..write('montant: $montant, ')
          ..write('modePaiement: $modePaiement, ')
          ..write('synced: $synced, ')
          ..write('date: $date')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode =>
      Object.hash(id, detteId, boutiqueId, montant, modePaiement, synced, date);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is Paiement &&
          other.id == this.id &&
          other.detteId == this.detteId &&
          other.boutiqueId == this.boutiqueId &&
          other.montant == this.montant &&
          other.modePaiement == this.modePaiement &&
          other.synced == this.synced &&
          other.date == this.date);
}

class PaiementsCompanion extends UpdateCompanion<Paiement> {
  final Value<String> id;
  final Value<String> detteId;
  final Value<String> boutiqueId;
  final Value<int> montant;
  final Value<String> modePaiement;
  final Value<bool> synced;
  final Value<DateTime> date;
  final Value<int> rowid;
  const PaiementsCompanion({
    this.id = const Value.absent(),
    this.detteId = const Value.absent(),
    this.boutiqueId = const Value.absent(),
    this.montant = const Value.absent(),
    this.modePaiement = const Value.absent(),
    this.synced = const Value.absent(),
    this.date = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  PaiementsCompanion.insert({
    required String id,
    required String detteId,
    required String boutiqueId,
    required int montant,
    this.modePaiement = const Value.absent(),
    this.synced = const Value.absent(),
    this.date = const Value.absent(),
    this.rowid = const Value.absent(),
  })  : id = Value(id),
        detteId = Value(detteId),
        boutiqueId = Value(boutiqueId),
        montant = Value(montant);
  static Insertable<Paiement> custom({
    Expression<String>? id,
    Expression<String>? detteId,
    Expression<String>? boutiqueId,
    Expression<int>? montant,
    Expression<String>? modePaiement,
    Expression<bool>? synced,
    Expression<DateTime>? date,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (detteId != null) 'dette_id': detteId,
      if (boutiqueId != null) 'boutique_id': boutiqueId,
      if (montant != null) 'montant': montant,
      if (modePaiement != null) 'mode_paiement': modePaiement,
      if (synced != null) 'synced': synced,
      if (date != null) 'date': date,
      if (rowid != null) 'rowid': rowid,
    });
  }

  PaiementsCompanion copyWith(
      {Value<String>? id,
      Value<String>? detteId,
      Value<String>? boutiqueId,
      Value<int>? montant,
      Value<String>? modePaiement,
      Value<bool>? synced,
      Value<DateTime>? date,
      Value<int>? rowid}) {
    return PaiementsCompanion(
      id: id ?? this.id,
      detteId: detteId ?? this.detteId,
      boutiqueId: boutiqueId ?? this.boutiqueId,
      montant: montant ?? this.montant,
      modePaiement: modePaiement ?? this.modePaiement,
      synced: synced ?? this.synced,
      date: date ?? this.date,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<String>(id.value);
    }
    if (detteId.present) {
      map['dette_id'] = Variable<String>(detteId.value);
    }
    if (boutiqueId.present) {
      map['boutique_id'] = Variable<String>(boutiqueId.value);
    }
    if (montant.present) {
      map['montant'] = Variable<int>(montant.value);
    }
    if (modePaiement.present) {
      map['mode_paiement'] = Variable<String>(modePaiement.value);
    }
    if (synced.present) {
      map['synced'] = Variable<bool>(synced.value);
    }
    if (date.present) {
      map['date'] = Variable<DateTime>(date.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('PaiementsCompanion(')
          ..write('id: $id, ')
          ..write('detteId: $detteId, ')
          ..write('boutiqueId: $boutiqueId, ')
          ..write('montant: $montant, ')
          ..write('modePaiement: $modePaiement, ')
          ..write('synced: $synced, ')
          ..write('date: $date, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $SyncQueueTable extends SyncQueue
    with TableInfo<$SyncQueueTable, SyncQueueData> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $SyncQueueTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<String> id = GeneratedColumn<String>(
      'id', aliasedName, false,
      additionalChecks:
          GeneratedColumn.checkTextLength(minTextLength: 36, maxTextLength: 36),
      type: DriftSqlType.string,
      requiredDuringInsert: true);
  static const VerificationMeta _targetTableMeta =
      const VerificationMeta('targetTable');
  @override
  late final GeneratedColumn<String> targetTable = GeneratedColumn<String>(
      'table_name', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _recordIdMeta =
      const VerificationMeta('recordId');
  @override
  late final GeneratedColumn<String> recordId = GeneratedColumn<String>(
      'record_id', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _operationMeta =
      const VerificationMeta('operation');
  @override
  late final GeneratedColumn<String> operation = GeneratedColumn<String>(
      'operation', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _payloadMeta =
      const VerificationMeta('payload');
  @override
  late final GeneratedColumn<String> payload = GeneratedColumn<String>(
      'payload', aliasedName, false,
      type: DriftSqlType.string, requiredDuringInsert: true);
  static const VerificationMeta _retryCountMeta =
      const VerificationMeta('retryCount');
  @override
  late final GeneratedColumn<int> retryCount = GeneratedColumn<int>(
      'retry_count', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
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
      [id, targetTable, recordId, operation, payload, retryCount, createdAt];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'sync_queue';
  @override
  VerificationContext validateIntegrity(Insertable<SyncQueueData> instance,
      {bool isInserting = false}) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    } else if (isInserting) {
      context.missing(_idMeta);
    }
    if (data.containsKey('table_name')) {
      context.handle(
          _targetTableMeta,
          targetTable.isAcceptableOrUnknown(
              data['table_name']!, _targetTableMeta));
    } else if (isInserting) {
      context.missing(_targetTableMeta);
    }
    if (data.containsKey('record_id')) {
      context.handle(_recordIdMeta,
          recordId.isAcceptableOrUnknown(data['record_id']!, _recordIdMeta));
    } else if (isInserting) {
      context.missing(_recordIdMeta);
    }
    if (data.containsKey('operation')) {
      context.handle(_operationMeta,
          operation.isAcceptableOrUnknown(data['operation']!, _operationMeta));
    } else if (isInserting) {
      context.missing(_operationMeta);
    }
    if (data.containsKey('payload')) {
      context.handle(_payloadMeta,
          payload.isAcceptableOrUnknown(data['payload']!, _payloadMeta));
    } else if (isInserting) {
      context.missing(_payloadMeta);
    }
    if (data.containsKey('retry_count')) {
      context.handle(
          _retryCountMeta,
          retryCount.isAcceptableOrUnknown(
              data['retry_count']!, _retryCountMeta));
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
  SyncQueueData map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return SyncQueueData(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}id'])!,
      targetTable: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}table_name'])!,
      recordId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}record_id'])!,
      operation: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}operation'])!,
      payload: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}payload'])!,
      retryCount: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}retry_count'])!,
      createdAt: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}created_at'])!,
    );
  }

  @override
  $SyncQueueTable createAlias(String alias) {
    return $SyncQueueTable(attachedDatabase, alias);
  }
}

class SyncQueueData extends DataClass implements Insertable<SyncQueueData> {
  final String id;
  final String targetTable;
  final String recordId;
  final String operation;
  final String payload;
  final int retryCount;
  final DateTime createdAt;
  const SyncQueueData(
      {required this.id,
      required this.targetTable,
      required this.recordId,
      required this.operation,
      required this.payload,
      required this.retryCount,
      required this.createdAt});
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<String>(id);
    map['table_name'] = Variable<String>(targetTable);
    map['record_id'] = Variable<String>(recordId);
    map['operation'] = Variable<String>(operation);
    map['payload'] = Variable<String>(payload);
    map['retry_count'] = Variable<int>(retryCount);
    map['created_at'] = Variable<DateTime>(createdAt);
    return map;
  }

  SyncQueueCompanion toCompanion(bool nullToAbsent) {
    return SyncQueueCompanion(
      id: Value(id),
      targetTable: Value(targetTable),
      recordId: Value(recordId),
      operation: Value(operation),
      payload: Value(payload),
      retryCount: Value(retryCount),
      createdAt: Value(createdAt),
    );
  }

  factory SyncQueueData.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return SyncQueueData(
      id: serializer.fromJson<String>(json['id']),
      targetTable: serializer.fromJson<String>(json['targetTable']),
      recordId: serializer.fromJson<String>(json['recordId']),
      operation: serializer.fromJson<String>(json['operation']),
      payload: serializer.fromJson<String>(json['payload']),
      retryCount: serializer.fromJson<int>(json['retryCount']),
      createdAt: serializer.fromJson<DateTime>(json['createdAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<String>(id),
      'targetTable': serializer.toJson<String>(targetTable),
      'recordId': serializer.toJson<String>(recordId),
      'operation': serializer.toJson<String>(operation),
      'payload': serializer.toJson<String>(payload),
      'retryCount': serializer.toJson<int>(retryCount),
      'createdAt': serializer.toJson<DateTime>(createdAt),
    };
  }

  SyncQueueData copyWith(
          {String? id,
          String? targetTable,
          String? recordId,
          String? operation,
          String? payload,
          int? retryCount,
          DateTime? createdAt}) =>
      SyncQueueData(
        id: id ?? this.id,
        targetTable: targetTable ?? this.targetTable,
        recordId: recordId ?? this.recordId,
        operation: operation ?? this.operation,
        payload: payload ?? this.payload,
        retryCount: retryCount ?? this.retryCount,
        createdAt: createdAt ?? this.createdAt,
      );
  SyncQueueData copyWithCompanion(SyncQueueCompanion data) {
    return SyncQueueData(
      id: data.id.present ? data.id.value : this.id,
      targetTable:
          data.targetTable.present ? data.targetTable.value : this.targetTable,
      recordId: data.recordId.present ? data.recordId.value : this.recordId,
      operation: data.operation.present ? data.operation.value : this.operation,
      payload: data.payload.present ? data.payload.value : this.payload,
      retryCount:
          data.retryCount.present ? data.retryCount.value : this.retryCount,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('SyncQueueData(')
          ..write('id: $id, ')
          ..write('targetTable: $targetTable, ')
          ..write('recordId: $recordId, ')
          ..write('operation: $operation, ')
          ..write('payload: $payload, ')
          ..write('retryCount: $retryCount, ')
          ..write('createdAt: $createdAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
      id, targetTable, recordId, operation, payload, retryCount, createdAt);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is SyncQueueData &&
          other.id == this.id &&
          other.targetTable == this.targetTable &&
          other.recordId == this.recordId &&
          other.operation == this.operation &&
          other.payload == this.payload &&
          other.retryCount == this.retryCount &&
          other.createdAt == this.createdAt);
}

class SyncQueueCompanion extends UpdateCompanion<SyncQueueData> {
  final Value<String> id;
  final Value<String> targetTable;
  final Value<String> recordId;
  final Value<String> operation;
  final Value<String> payload;
  final Value<int> retryCount;
  final Value<DateTime> createdAt;
  final Value<int> rowid;
  const SyncQueueCompanion({
    this.id = const Value.absent(),
    this.targetTable = const Value.absent(),
    this.recordId = const Value.absent(),
    this.operation = const Value.absent(),
    this.payload = const Value.absent(),
    this.retryCount = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  SyncQueueCompanion.insert({
    required String id,
    required String targetTable,
    required String recordId,
    required String operation,
    required String payload,
    this.retryCount = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.rowid = const Value.absent(),
  })  : id = Value(id),
        targetTable = Value(targetTable),
        recordId = Value(recordId),
        operation = Value(operation),
        payload = Value(payload);
  static Insertable<SyncQueueData> custom({
    Expression<String>? id,
    Expression<String>? targetTable,
    Expression<String>? recordId,
    Expression<String>? operation,
    Expression<String>? payload,
    Expression<int>? retryCount,
    Expression<DateTime>? createdAt,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (targetTable != null) 'table_name': targetTable,
      if (recordId != null) 'record_id': recordId,
      if (operation != null) 'operation': operation,
      if (payload != null) 'payload': payload,
      if (retryCount != null) 'retry_count': retryCount,
      if (createdAt != null) 'created_at': createdAt,
      if (rowid != null) 'rowid': rowid,
    });
  }

  SyncQueueCompanion copyWith(
      {Value<String>? id,
      Value<String>? targetTable,
      Value<String>? recordId,
      Value<String>? operation,
      Value<String>? payload,
      Value<int>? retryCount,
      Value<DateTime>? createdAt,
      Value<int>? rowid}) {
    return SyncQueueCompanion(
      id: id ?? this.id,
      targetTable: targetTable ?? this.targetTable,
      recordId: recordId ?? this.recordId,
      operation: operation ?? this.operation,
      payload: payload ?? this.payload,
      retryCount: retryCount ?? this.retryCount,
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
    if (targetTable.present) {
      map['table_name'] = Variable<String>(targetTable.value);
    }
    if (recordId.present) {
      map['record_id'] = Variable<String>(recordId.value);
    }
    if (operation.present) {
      map['operation'] = Variable<String>(operation.value);
    }
    if (payload.present) {
      map['payload'] = Variable<String>(payload.value);
    }
    if (retryCount.present) {
      map['retry_count'] = Variable<int>(retryCount.value);
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
    return (StringBuffer('SyncQueueCompanion(')
          ..write('id: $id, ')
          ..write('targetTable: $targetTable, ')
          ..write('recordId: $recordId, ')
          ..write('operation: $operation, ')
          ..write('payload: $payload, ')
          ..write('retryCount: $retryCount, ')
          ..write('createdAt: $createdAt, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $AbonnementsTable extends Abonnements
    with TableInfo<$AbonnementsTable, Abonnement> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $AbonnementsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<String> id = GeneratedColumn<String>(
      'id', aliasedName, false,
      additionalChecks:
          GeneratedColumn.checkTextLength(minTextLength: 36, maxTextLength: 36),
      type: DriftSqlType.string,
      requiredDuringInsert: true);
  static const VerificationMeta _boutiqueIdMeta =
      const VerificationMeta('boutiqueId');
  @override
  late final GeneratedColumn<String> boutiqueId = GeneratedColumn<String>(
      'boutique_id', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: true,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('REFERENCES boutiques (id)'));
  static const VerificationMeta _planMeta = const VerificationMeta('plan');
  @override
  late final GeneratedColumn<String> plan = GeneratedColumn<String>(
      'plan', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: false,
      defaultValue: const Constant('gratuit'));
  static const VerificationMeta _statutMeta = const VerificationMeta('statut');
  @override
  late final GeneratedColumn<String> statut = GeneratedColumn<String>(
      'statut', aliasedName, false,
      type: DriftSqlType.string,
      requiredDuringInsert: false,
      defaultValue: const Constant('actif'));
  static const VerificationMeta _modePaiementMeta =
      const VerificationMeta('modePaiement');
  @override
  late final GeneratedColumn<String> modePaiement = GeneratedColumn<String>(
      'mode_paiement', aliasedName, true,
      type: DriftSqlType.string, requiredDuringInsert: false);
  static const VerificationMeta _montantMeta =
      const VerificationMeta('montant');
  @override
  late final GeneratedColumn<int> montant = GeneratedColumn<int>(
      'montant', aliasedName, false,
      type: DriftSqlType.int,
      requiredDuringInsert: false,
      defaultValue: const Constant(0));
  static const VerificationMeta _dateDebutMeta =
      const VerificationMeta('dateDebut');
  @override
  late final GeneratedColumn<DateTime> dateDebut = GeneratedColumn<DateTime>(
      'date_debut', aliasedName, false,
      type: DriftSqlType.dateTime,
      requiredDuringInsert: false,
      defaultValue: currentDateAndTime);
  static const VerificationMeta _dateFinMeta =
      const VerificationMeta('dateFin');
  @override
  late final GeneratedColumn<DateTime> dateFin = GeneratedColumn<DateTime>(
      'date_fin', aliasedName, true,
      type: DriftSqlType.dateTime, requiredDuringInsert: false);
  static const VerificationMeta _syncedMeta = const VerificationMeta('synced');
  @override
  late final GeneratedColumn<bool> synced = GeneratedColumn<bool>(
      'synced', aliasedName, false,
      type: DriftSqlType.bool,
      requiredDuringInsert: false,
      defaultConstraints:
          GeneratedColumn.constraintIsAlways('CHECK ("synced" IN (0, 1))'),
      defaultValue: const Constant(false));
  @override
  List<GeneratedColumn> get $columns => [
        id,
        boutiqueId,
        plan,
        statut,
        modePaiement,
        montant,
        dateDebut,
        dateFin,
        synced
      ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'abonnements';
  @override
  VerificationContext validateIntegrity(Insertable<Abonnement> instance,
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
    if (data.containsKey('plan')) {
      context.handle(
          _planMeta, plan.isAcceptableOrUnknown(data['plan']!, _planMeta));
    }
    if (data.containsKey('statut')) {
      context.handle(_statutMeta,
          statut.isAcceptableOrUnknown(data['statut']!, _statutMeta));
    }
    if (data.containsKey('mode_paiement')) {
      context.handle(
          _modePaiementMeta,
          modePaiement.isAcceptableOrUnknown(
              data['mode_paiement']!, _modePaiementMeta));
    }
    if (data.containsKey('montant')) {
      context.handle(_montantMeta,
          montant.isAcceptableOrUnknown(data['montant']!, _montantMeta));
    }
    if (data.containsKey('date_debut')) {
      context.handle(_dateDebutMeta,
          dateDebut.isAcceptableOrUnknown(data['date_debut']!, _dateDebutMeta));
    }
    if (data.containsKey('date_fin')) {
      context.handle(_dateFinMeta,
          dateFin.isAcceptableOrUnknown(data['date_fin']!, _dateFinMeta));
    }
    if (data.containsKey('synced')) {
      context.handle(_syncedMeta,
          synced.isAcceptableOrUnknown(data['synced']!, _syncedMeta));
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  Abonnement map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return Abonnement(
      id: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}id'])!,
      boutiqueId: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}boutique_id'])!,
      plan: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}plan'])!,
      statut: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}statut'])!,
      modePaiement: attachedDatabase.typeMapping
          .read(DriftSqlType.string, data['${effectivePrefix}mode_paiement']),
      montant: attachedDatabase.typeMapping
          .read(DriftSqlType.int, data['${effectivePrefix}montant'])!,
      dateDebut: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}date_debut'])!,
      dateFin: attachedDatabase.typeMapping
          .read(DriftSqlType.dateTime, data['${effectivePrefix}date_fin']),
      synced: attachedDatabase.typeMapping
          .read(DriftSqlType.bool, data['${effectivePrefix}synced'])!,
    );
  }

  @override
  $AbonnementsTable createAlias(String alias) {
    return $AbonnementsTable(attachedDatabase, alias);
  }
}

class Abonnement extends DataClass implements Insertable<Abonnement> {
  final String id;
  final String boutiqueId;
  final String plan;
  final String statut;
  final String? modePaiement;
  final int montant;
  final DateTime dateDebut;
  final DateTime? dateFin;
  final bool synced;
  const Abonnement(
      {required this.id,
      required this.boutiqueId,
      required this.plan,
      required this.statut,
      this.modePaiement,
      required this.montant,
      required this.dateDebut,
      this.dateFin,
      required this.synced});
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<String>(id);
    map['boutique_id'] = Variable<String>(boutiqueId);
    map['plan'] = Variable<String>(plan);
    map['statut'] = Variable<String>(statut);
    if (!nullToAbsent || modePaiement != null) {
      map['mode_paiement'] = Variable<String>(modePaiement);
    }
    map['montant'] = Variable<int>(montant);
    map['date_debut'] = Variable<DateTime>(dateDebut);
    if (!nullToAbsent || dateFin != null) {
      map['date_fin'] = Variable<DateTime>(dateFin);
    }
    map['synced'] = Variable<bool>(synced);
    return map;
  }

  AbonnementsCompanion toCompanion(bool nullToAbsent) {
    return AbonnementsCompanion(
      id: Value(id),
      boutiqueId: Value(boutiqueId),
      plan: Value(plan),
      statut: Value(statut),
      modePaiement: modePaiement == null && nullToAbsent
          ? const Value.absent()
          : Value(modePaiement),
      montant: Value(montant),
      dateDebut: Value(dateDebut),
      dateFin: dateFin == null && nullToAbsent
          ? const Value.absent()
          : Value(dateFin),
      synced: Value(synced),
    );
  }

  factory Abonnement.fromJson(Map<String, dynamic> json,
      {ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return Abonnement(
      id: serializer.fromJson<String>(json['id']),
      boutiqueId: serializer.fromJson<String>(json['boutiqueId']),
      plan: serializer.fromJson<String>(json['plan']),
      statut: serializer.fromJson<String>(json['statut']),
      modePaiement: serializer.fromJson<String?>(json['modePaiement']),
      montant: serializer.fromJson<int>(json['montant']),
      dateDebut: serializer.fromJson<DateTime>(json['dateDebut']),
      dateFin: serializer.fromJson<DateTime?>(json['dateFin']),
      synced: serializer.fromJson<bool>(json['synced']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<String>(id),
      'boutiqueId': serializer.toJson<String>(boutiqueId),
      'plan': serializer.toJson<String>(plan),
      'statut': serializer.toJson<String>(statut),
      'modePaiement': serializer.toJson<String?>(modePaiement),
      'montant': serializer.toJson<int>(montant),
      'dateDebut': serializer.toJson<DateTime>(dateDebut),
      'dateFin': serializer.toJson<DateTime?>(dateFin),
      'synced': serializer.toJson<bool>(synced),
    };
  }

  Abonnement copyWith(
          {String? id,
          String? boutiqueId,
          String? plan,
          String? statut,
          Value<String?> modePaiement = const Value.absent(),
          int? montant,
          DateTime? dateDebut,
          Value<DateTime?> dateFin = const Value.absent(),
          bool? synced}) =>
      Abonnement(
        id: id ?? this.id,
        boutiqueId: boutiqueId ?? this.boutiqueId,
        plan: plan ?? this.plan,
        statut: statut ?? this.statut,
        modePaiement:
            modePaiement.present ? modePaiement.value : this.modePaiement,
        montant: montant ?? this.montant,
        dateDebut: dateDebut ?? this.dateDebut,
        dateFin: dateFin.present ? dateFin.value : this.dateFin,
        synced: synced ?? this.synced,
      );
  Abonnement copyWithCompanion(AbonnementsCompanion data) {
    return Abonnement(
      id: data.id.present ? data.id.value : this.id,
      boutiqueId:
          data.boutiqueId.present ? data.boutiqueId.value : this.boutiqueId,
      plan: data.plan.present ? data.plan.value : this.plan,
      statut: data.statut.present ? data.statut.value : this.statut,
      modePaiement: data.modePaiement.present
          ? data.modePaiement.value
          : this.modePaiement,
      montant: data.montant.present ? data.montant.value : this.montant,
      dateDebut: data.dateDebut.present ? data.dateDebut.value : this.dateDebut,
      dateFin: data.dateFin.present ? data.dateFin.value : this.dateFin,
      synced: data.synced.present ? data.synced.value : this.synced,
    );
  }

  @override
  String toString() {
    return (StringBuffer('Abonnement(')
          ..write('id: $id, ')
          ..write('boutiqueId: $boutiqueId, ')
          ..write('plan: $plan, ')
          ..write('statut: $statut, ')
          ..write('modePaiement: $modePaiement, ')
          ..write('montant: $montant, ')
          ..write('dateDebut: $dateDebut, ')
          ..write('dateFin: $dateFin, ')
          ..write('synced: $synced')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(id, boutiqueId, plan, statut, modePaiement,
      montant, dateDebut, dateFin, synced);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is Abonnement &&
          other.id == this.id &&
          other.boutiqueId == this.boutiqueId &&
          other.plan == this.plan &&
          other.statut == this.statut &&
          other.modePaiement == this.modePaiement &&
          other.montant == this.montant &&
          other.dateDebut == this.dateDebut &&
          other.dateFin == this.dateFin &&
          other.synced == this.synced);
}

class AbonnementsCompanion extends UpdateCompanion<Abonnement> {
  final Value<String> id;
  final Value<String> boutiqueId;
  final Value<String> plan;
  final Value<String> statut;
  final Value<String?> modePaiement;
  final Value<int> montant;
  final Value<DateTime> dateDebut;
  final Value<DateTime?> dateFin;
  final Value<bool> synced;
  final Value<int> rowid;
  const AbonnementsCompanion({
    this.id = const Value.absent(),
    this.boutiqueId = const Value.absent(),
    this.plan = const Value.absent(),
    this.statut = const Value.absent(),
    this.modePaiement = const Value.absent(),
    this.montant = const Value.absent(),
    this.dateDebut = const Value.absent(),
    this.dateFin = const Value.absent(),
    this.synced = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  AbonnementsCompanion.insert({
    required String id,
    required String boutiqueId,
    this.plan = const Value.absent(),
    this.statut = const Value.absent(),
    this.modePaiement = const Value.absent(),
    this.montant = const Value.absent(),
    this.dateDebut = const Value.absent(),
    this.dateFin = const Value.absent(),
    this.synced = const Value.absent(),
    this.rowid = const Value.absent(),
  })  : id = Value(id),
        boutiqueId = Value(boutiqueId);
  static Insertable<Abonnement> custom({
    Expression<String>? id,
    Expression<String>? boutiqueId,
    Expression<String>? plan,
    Expression<String>? statut,
    Expression<String>? modePaiement,
    Expression<int>? montant,
    Expression<DateTime>? dateDebut,
    Expression<DateTime>? dateFin,
    Expression<bool>? synced,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (boutiqueId != null) 'boutique_id': boutiqueId,
      if (plan != null) 'plan': plan,
      if (statut != null) 'statut': statut,
      if (modePaiement != null) 'mode_paiement': modePaiement,
      if (montant != null) 'montant': montant,
      if (dateDebut != null) 'date_debut': dateDebut,
      if (dateFin != null) 'date_fin': dateFin,
      if (synced != null) 'synced': synced,
      if (rowid != null) 'rowid': rowid,
    });
  }

  AbonnementsCompanion copyWith(
      {Value<String>? id,
      Value<String>? boutiqueId,
      Value<String>? plan,
      Value<String>? statut,
      Value<String?>? modePaiement,
      Value<int>? montant,
      Value<DateTime>? dateDebut,
      Value<DateTime?>? dateFin,
      Value<bool>? synced,
      Value<int>? rowid}) {
    return AbonnementsCompanion(
      id: id ?? this.id,
      boutiqueId: boutiqueId ?? this.boutiqueId,
      plan: plan ?? this.plan,
      statut: statut ?? this.statut,
      modePaiement: modePaiement ?? this.modePaiement,
      montant: montant ?? this.montant,
      dateDebut: dateDebut ?? this.dateDebut,
      dateFin: dateFin ?? this.dateFin,
      synced: synced ?? this.synced,
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
    if (plan.present) {
      map['plan'] = Variable<String>(plan.value);
    }
    if (statut.present) {
      map['statut'] = Variable<String>(statut.value);
    }
    if (modePaiement.present) {
      map['mode_paiement'] = Variable<String>(modePaiement.value);
    }
    if (montant.present) {
      map['montant'] = Variable<int>(montant.value);
    }
    if (dateDebut.present) {
      map['date_debut'] = Variable<DateTime>(dateDebut.value);
    }
    if (dateFin.present) {
      map['date_fin'] = Variable<DateTime>(dateFin.value);
    }
    if (synced.present) {
      map['synced'] = Variable<bool>(synced.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('AbonnementsCompanion(')
          ..write('id: $id, ')
          ..write('boutiqueId: $boutiqueId, ')
          ..write('plan: $plan, ')
          ..write('statut: $statut, ')
          ..write('modePaiement: $modePaiement, ')
          ..write('montant: $montant, ')
          ..write('dateDebut: $dateDebut, ')
          ..write('dateFin: $dateFin, ')
          ..write('synced: $synced, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

abstract class _$AppDatabase extends GeneratedDatabase {
  _$AppDatabase(QueryExecutor e) : super(e);
  $AppDatabaseManager get managers => $AppDatabaseManager(this);
  late final $BoutiquesTable boutiques = $BoutiquesTable(this);
  late final $UtilisateursTable utilisateurs = $UtilisateursTable(this);
  late final $ProduitsTable produits = $ProduitsTable(this);
  late final $ClientsTable clients = $ClientsTable(this);
  late final $VentesTable ventes = $VentesTable(this);
  late final $DettesTable dettes = $DettesTable(this);
  late final $PaiementsTable paiements = $PaiementsTable(this);
  late final $SyncQueueTable syncQueue = $SyncQueueTable(this);
  late final $AbonnementsTable abonnements = $AbonnementsTable(this);
  @override
  Iterable<TableInfo<Table, Object?>> get allTables =>
      allSchemaEntities.whereType<TableInfo<Table, Object?>>();
  @override
  List<DatabaseSchemaEntity> get allSchemaEntities => [
        boutiques,
        utilisateurs,
        produits,
        clients,
        ventes,
        dettes,
        paiements,
        syncQueue,
        abonnements
      ];
}

typedef $$BoutiquesTableCreateCompanionBuilder = BoutiquesCompanion Function({
  required String id,
  required String nom,
  Value<String?> adresse,
  required String telephone,
  Value<DateTime> createdAt,
  Value<int> rowid,
});
typedef $$BoutiquesTableUpdateCompanionBuilder = BoutiquesCompanion Function({
  Value<String> id,
  Value<String> nom,
  Value<String?> adresse,
  Value<String> telephone,
  Value<DateTime> createdAt,
  Value<int> rowid,
});

final class $$BoutiquesTableReferences
    extends BaseReferences<_$AppDatabase, $BoutiquesTable, Boutique> {
  $$BoutiquesTableReferences(super.$_db, super.$_table, super.$_typedResult);

  static MultiTypedResultKey<$UtilisateursTable, List<Utilisateur>>
      _utilisateursRefsTable(_$AppDatabase db) =>
          MultiTypedResultKey.fromTable(db.utilisateurs,
              aliasName: $_aliasNameGenerator(
                  db.boutiques.id, db.utilisateurs.boutiqueId));

  $$UtilisateursTableProcessedTableManager get utilisateursRefs {
    final manager = $$UtilisateursTableTableManager($_db, $_db.utilisateurs)
        .filter((f) => f.boutiqueId.id.sqlEquals($_itemColumn<String>('id')!));

    final cache = $_typedResult.readTableOrNull(_utilisateursRefsTable($_db));
    return ProcessedTableManager(
        manager.$state.copyWith(prefetchedData: cache));
  }

  static MultiTypedResultKey<$ProduitsTable, List<Produit>> _produitsRefsTable(
          _$AppDatabase db) =>
      MultiTypedResultKey.fromTable(db.produits,
          aliasName:
              $_aliasNameGenerator(db.boutiques.id, db.produits.boutiqueId));

  $$ProduitsTableProcessedTableManager get produitsRefs {
    final manager = $$ProduitsTableTableManager($_db, $_db.produits)
        .filter((f) => f.boutiqueId.id.sqlEquals($_itemColumn<String>('id')!));

    final cache = $_typedResult.readTableOrNull(_produitsRefsTable($_db));
    return ProcessedTableManager(
        manager.$state.copyWith(prefetchedData: cache));
  }

  static MultiTypedResultKey<$ClientsTable, List<Client>> _clientsRefsTable(
          _$AppDatabase db) =>
      MultiTypedResultKey.fromTable(db.clients,
          aliasName:
              $_aliasNameGenerator(db.boutiques.id, db.clients.boutiqueId));

  $$ClientsTableProcessedTableManager get clientsRefs {
    final manager = $$ClientsTableTableManager($_db, $_db.clients)
        .filter((f) => f.boutiqueId.id.sqlEquals($_itemColumn<String>('id')!));

    final cache = $_typedResult.readTableOrNull(_clientsRefsTable($_db));
    return ProcessedTableManager(
        manager.$state.copyWith(prefetchedData: cache));
  }

  static MultiTypedResultKey<$VentesTable, List<Vente>> _ventesRefsTable(
          _$AppDatabase db) =>
      MultiTypedResultKey.fromTable(db.ventes,
          aliasName:
              $_aliasNameGenerator(db.boutiques.id, db.ventes.boutiqueId));

  $$VentesTableProcessedTableManager get ventesRefs {
    final manager = $$VentesTableTableManager($_db, $_db.ventes)
        .filter((f) => f.boutiqueId.id.sqlEquals($_itemColumn<String>('id')!));

    final cache = $_typedResult.readTableOrNull(_ventesRefsTable($_db));
    return ProcessedTableManager(
        manager.$state.copyWith(prefetchedData: cache));
  }

  static MultiTypedResultKey<$AbonnementsTable, List<Abonnement>>
      _abonnementsRefsTable(_$AppDatabase db) => MultiTypedResultKey.fromTable(
          db.abonnements,
          aliasName:
              $_aliasNameGenerator(db.boutiques.id, db.abonnements.boutiqueId));

  $$AbonnementsTableProcessedTableManager get abonnementsRefs {
    final manager = $$AbonnementsTableTableManager($_db, $_db.abonnements)
        .filter((f) => f.boutiqueId.id.sqlEquals($_itemColumn<String>('id')!));

    final cache = $_typedResult.readTableOrNull(_abonnementsRefsTable($_db));
    return ProcessedTableManager(
        manager.$state.copyWith(prefetchedData: cache));
  }
}

class $$BoutiquesTableFilterComposer
    extends Composer<_$AppDatabase, $BoutiquesTable> {
  $$BoutiquesTableFilterComposer({
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

  ColumnFilters<String> get adresse => $composableBuilder(
      column: $table.adresse, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get telephone => $composableBuilder(
      column: $table.telephone, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnFilters(column));

  Expression<bool> utilisateursRefs(
      Expression<bool> Function($$UtilisateursTableFilterComposer f) f) {
    final $$UtilisateursTableFilterComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.id,
        referencedTable: $db.utilisateurs,
        getReferencedColumn: (t) => t.boutiqueId,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$UtilisateursTableFilterComposer(
              $db: $db,
              $table: $db.utilisateurs,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return f(composer);
  }

  Expression<bool> produitsRefs(
      Expression<bool> Function($$ProduitsTableFilterComposer f) f) {
    final $$ProduitsTableFilterComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.id,
        referencedTable: $db.produits,
        getReferencedColumn: (t) => t.boutiqueId,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$ProduitsTableFilterComposer(
              $db: $db,
              $table: $db.produits,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return f(composer);
  }

  Expression<bool> clientsRefs(
      Expression<bool> Function($$ClientsTableFilterComposer f) f) {
    final $$ClientsTableFilterComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.id,
        referencedTable: $db.clients,
        getReferencedColumn: (t) => t.boutiqueId,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$ClientsTableFilterComposer(
              $db: $db,
              $table: $db.clients,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return f(composer);
  }

  Expression<bool> ventesRefs(
      Expression<bool> Function($$VentesTableFilterComposer f) f) {
    final $$VentesTableFilterComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.id,
        referencedTable: $db.ventes,
        getReferencedColumn: (t) => t.boutiqueId,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$VentesTableFilterComposer(
              $db: $db,
              $table: $db.ventes,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return f(composer);
  }

  Expression<bool> abonnementsRefs(
      Expression<bool> Function($$AbonnementsTableFilterComposer f) f) {
    final $$AbonnementsTableFilterComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.id,
        referencedTable: $db.abonnements,
        getReferencedColumn: (t) => t.boutiqueId,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$AbonnementsTableFilterComposer(
              $db: $db,
              $table: $db.abonnements,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return f(composer);
  }
}

class $$BoutiquesTableOrderingComposer
    extends Composer<_$AppDatabase, $BoutiquesTable> {
  $$BoutiquesTableOrderingComposer({
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

  ColumnOrderings<String> get adresse => $composableBuilder(
      column: $table.adresse, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get telephone => $composableBuilder(
      column: $table.telephone, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnOrderings(column));
}

class $$BoutiquesTableAnnotationComposer
    extends Composer<_$AppDatabase, $BoutiquesTable> {
  $$BoutiquesTableAnnotationComposer({
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

  GeneratedColumn<String> get adresse =>
      $composableBuilder(column: $table.adresse, builder: (column) => column);

  GeneratedColumn<String> get telephone =>
      $composableBuilder(column: $table.telephone, builder: (column) => column);

  GeneratedColumn<DateTime> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);

  Expression<T> utilisateursRefs<T extends Object>(
      Expression<T> Function($$UtilisateursTableAnnotationComposer a) f) {
    final $$UtilisateursTableAnnotationComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.id,
        referencedTable: $db.utilisateurs,
        getReferencedColumn: (t) => t.boutiqueId,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$UtilisateursTableAnnotationComposer(
              $db: $db,
              $table: $db.utilisateurs,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return f(composer);
  }

  Expression<T> produitsRefs<T extends Object>(
      Expression<T> Function($$ProduitsTableAnnotationComposer a) f) {
    final $$ProduitsTableAnnotationComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.id,
        referencedTable: $db.produits,
        getReferencedColumn: (t) => t.boutiqueId,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$ProduitsTableAnnotationComposer(
              $db: $db,
              $table: $db.produits,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return f(composer);
  }

  Expression<T> clientsRefs<T extends Object>(
      Expression<T> Function($$ClientsTableAnnotationComposer a) f) {
    final $$ClientsTableAnnotationComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.id,
        referencedTable: $db.clients,
        getReferencedColumn: (t) => t.boutiqueId,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$ClientsTableAnnotationComposer(
              $db: $db,
              $table: $db.clients,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return f(composer);
  }

  Expression<T> ventesRefs<T extends Object>(
      Expression<T> Function($$VentesTableAnnotationComposer a) f) {
    final $$VentesTableAnnotationComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.id,
        referencedTable: $db.ventes,
        getReferencedColumn: (t) => t.boutiqueId,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$VentesTableAnnotationComposer(
              $db: $db,
              $table: $db.ventes,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return f(composer);
  }

  Expression<T> abonnementsRefs<T extends Object>(
      Expression<T> Function($$AbonnementsTableAnnotationComposer a) f) {
    final $$AbonnementsTableAnnotationComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.id,
        referencedTable: $db.abonnements,
        getReferencedColumn: (t) => t.boutiqueId,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$AbonnementsTableAnnotationComposer(
              $db: $db,
              $table: $db.abonnements,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return f(composer);
  }
}

class $$BoutiquesTableTableManager extends RootTableManager<
    _$AppDatabase,
    $BoutiquesTable,
    Boutique,
    $$BoutiquesTableFilterComposer,
    $$BoutiquesTableOrderingComposer,
    $$BoutiquesTableAnnotationComposer,
    $$BoutiquesTableCreateCompanionBuilder,
    $$BoutiquesTableUpdateCompanionBuilder,
    (Boutique, $$BoutiquesTableReferences),
    Boutique,
    PrefetchHooks Function(
        {bool utilisateursRefs,
        bool produitsRefs,
        bool clientsRefs,
        bool ventesRefs,
        bool abonnementsRefs})> {
  $$BoutiquesTableTableManager(_$AppDatabase db, $BoutiquesTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$BoutiquesTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$BoutiquesTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$BoutiquesTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback: ({
            Value<String> id = const Value.absent(),
            Value<String> nom = const Value.absent(),
            Value<String?> adresse = const Value.absent(),
            Value<String> telephone = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              BoutiquesCompanion(
            id: id,
            nom: nom,
            adresse: adresse,
            telephone: telephone,
            createdAt: createdAt,
            rowid: rowid,
          ),
          createCompanionCallback: ({
            required String id,
            required String nom,
            Value<String?> adresse = const Value.absent(),
            required String telephone,
            Value<DateTime> createdAt = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              BoutiquesCompanion.insert(
            id: id,
            nom: nom,
            adresse: adresse,
            telephone: telephone,
            createdAt: createdAt,
            rowid: rowid,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (
                    e.readTable(table),
                    $$BoutiquesTableReferences(db, table, e)
                  ))
              .toList(),
          prefetchHooksCallback: (
              {utilisateursRefs = false,
              produitsRefs = false,
              clientsRefs = false,
              ventesRefs = false,
              abonnementsRefs = false}) {
            return PrefetchHooks(
              db: db,
              explicitlyWatchedTables: [
                if (utilisateursRefs) db.utilisateurs,
                if (produitsRefs) db.produits,
                if (clientsRefs) db.clients,
                if (ventesRefs) db.ventes,
                if (abonnementsRefs) db.abonnements
              ],
              addJoins: null,
              getPrefetchedDataCallback: (items) async {
                return [
                  if (utilisateursRefs)
                    await $_getPrefetchedData<Boutique, $BoutiquesTable,
                            Utilisateur>(
                        currentTable: table,
                        referencedTable: $$BoutiquesTableReferences
                            ._utilisateursRefsTable(db),
                        managerFromTypedResult: (p0) =>
                            $$BoutiquesTableReferences(db, table, p0)
                                .utilisateursRefs,
                        referencedItemsForCurrentItem:
                            (item, referencedItems) => referencedItems
                                .where((e) => e.boutiqueId == item.id),
                        typedResults: items),
                  if (produitsRefs)
                    await $_getPrefetchedData<Boutique, $BoutiquesTable,
                            Produit>(
                        currentTable: table,
                        referencedTable:
                            $$BoutiquesTableReferences._produitsRefsTable(db),
                        managerFromTypedResult: (p0) =>
                            $$BoutiquesTableReferences(db, table, p0)
                                .produitsRefs,
                        referencedItemsForCurrentItem:
                            (item, referencedItems) => referencedItems
                                .where((e) => e.boutiqueId == item.id),
                        typedResults: items),
                  if (clientsRefs)
                    await $_getPrefetchedData<Boutique, $BoutiquesTable,
                            Client>(
                        currentTable: table,
                        referencedTable:
                            $$BoutiquesTableReferences._clientsRefsTable(db),
                        managerFromTypedResult: (p0) =>
                            $$BoutiquesTableReferences(db, table, p0)
                                .clientsRefs,
                        referencedItemsForCurrentItem:
                            (item, referencedItems) => referencedItems
                                .where((e) => e.boutiqueId == item.id),
                        typedResults: items),
                  if (ventesRefs)
                    await $_getPrefetchedData<Boutique, $BoutiquesTable, Vente>(
                        currentTable: table,
                        referencedTable:
                            $$BoutiquesTableReferences._ventesRefsTable(db),
                        managerFromTypedResult: (p0) =>
                            $$BoutiquesTableReferences(db, table, p0)
                                .ventesRefs,
                        referencedItemsForCurrentItem:
                            (item, referencedItems) => referencedItems
                                .where((e) => e.boutiqueId == item.id),
                        typedResults: items),
                  if (abonnementsRefs)
                    await $_getPrefetchedData<Boutique, $BoutiquesTable,
                            Abonnement>(
                        currentTable: table,
                        referencedTable: $$BoutiquesTableReferences
                            ._abonnementsRefsTable(db),
                        managerFromTypedResult: (p0) =>
                            $$BoutiquesTableReferences(db, table, p0)
                                .abonnementsRefs,
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

typedef $$BoutiquesTableProcessedTableManager = ProcessedTableManager<
    _$AppDatabase,
    $BoutiquesTable,
    Boutique,
    $$BoutiquesTableFilterComposer,
    $$BoutiquesTableOrderingComposer,
    $$BoutiquesTableAnnotationComposer,
    $$BoutiquesTableCreateCompanionBuilder,
    $$BoutiquesTableUpdateCompanionBuilder,
    (Boutique, $$BoutiquesTableReferences),
    Boutique,
    PrefetchHooks Function(
        {bool utilisateursRefs,
        bool produitsRefs,
        bool clientsRefs,
        bool ventesRefs,
        bool abonnementsRefs})>;
typedef $$UtilisateursTableCreateCompanionBuilder = UtilisateursCompanion
    Function({
  required String id,
  required String boutiqueId,
  required String nom,
  Value<String> role,
  required String motDePasse,
  Value<String?> pinHash,
  Value<DateTime> createdAt,
  Value<int> rowid,
});
typedef $$UtilisateursTableUpdateCompanionBuilder = UtilisateursCompanion
    Function({
  Value<String> id,
  Value<String> boutiqueId,
  Value<String> nom,
  Value<String> role,
  Value<String> motDePasse,
  Value<String?> pinHash,
  Value<DateTime> createdAt,
  Value<int> rowid,
});

final class $$UtilisateursTableReferences
    extends BaseReferences<_$AppDatabase, $UtilisateursTable, Utilisateur> {
  $$UtilisateursTableReferences(super.$_db, super.$_table, super.$_typedResult);

  static $BoutiquesTable _boutiqueIdTable(_$AppDatabase db) =>
      db.boutiques.createAlias(
          $_aliasNameGenerator(db.utilisateurs.boutiqueId, db.boutiques.id));

  $$BoutiquesTableProcessedTableManager get boutiqueId {
    final $_column = $_itemColumn<String>('boutique_id')!;

    final manager = $$BoutiquesTableTableManager($_db, $_db.boutiques)
        .filter((f) => f.id.sqlEquals($_column));
    final item = $_typedResult.readTableOrNull(_boutiqueIdTable($_db));
    if (item == null) return manager;
    return ProcessedTableManager(
        manager.$state.copyWith(prefetchedData: [item]));
  }

  static MultiTypedResultKey<$VentesTable, List<Vente>> _ventesRefsTable(
          _$AppDatabase db) =>
      MultiTypedResultKey.fromTable(db.ventes,
          aliasName: $_aliasNameGenerator(
              db.utilisateurs.id, db.ventes.utilisateurId));

  $$VentesTableProcessedTableManager get ventesRefs {
    final manager = $$VentesTableTableManager($_db, $_db.ventes).filter(
        (f) => f.utilisateurId.id.sqlEquals($_itemColumn<String>('id')!));

    final cache = $_typedResult.readTableOrNull(_ventesRefsTable($_db));
    return ProcessedTableManager(
        manager.$state.copyWith(prefetchedData: cache));
  }
}

class $$UtilisateursTableFilterComposer
    extends Composer<_$AppDatabase, $UtilisateursTable> {
  $$UtilisateursTableFilterComposer({
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

  ColumnFilters<String> get role => $composableBuilder(
      column: $table.role, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get motDePasse => $composableBuilder(
      column: $table.motDePasse, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get pinHash => $composableBuilder(
      column: $table.pinHash, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnFilters(column));

  $$BoutiquesTableFilterComposer get boutiqueId {
    final $$BoutiquesTableFilterComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.boutiqueId,
        referencedTable: $db.boutiques,
        getReferencedColumn: (t) => t.id,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$BoutiquesTableFilterComposer(
              $db: $db,
              $table: $db.boutiques,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return composer;
  }

  Expression<bool> ventesRefs(
      Expression<bool> Function($$VentesTableFilterComposer f) f) {
    final $$VentesTableFilterComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.id,
        referencedTable: $db.ventes,
        getReferencedColumn: (t) => t.utilisateurId,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$VentesTableFilterComposer(
              $db: $db,
              $table: $db.ventes,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return f(composer);
  }
}

class $$UtilisateursTableOrderingComposer
    extends Composer<_$AppDatabase, $UtilisateursTable> {
  $$UtilisateursTableOrderingComposer({
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

  ColumnOrderings<String> get role => $composableBuilder(
      column: $table.role, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get motDePasse => $composableBuilder(
      column: $table.motDePasse, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get pinHash => $composableBuilder(
      column: $table.pinHash, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnOrderings(column));

  $$BoutiquesTableOrderingComposer get boutiqueId {
    final $$BoutiquesTableOrderingComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.boutiqueId,
        referencedTable: $db.boutiques,
        getReferencedColumn: (t) => t.id,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$BoutiquesTableOrderingComposer(
              $db: $db,
              $table: $db.boutiques,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return composer;
  }
}

class $$UtilisateursTableAnnotationComposer
    extends Composer<_$AppDatabase, $UtilisateursTable> {
  $$UtilisateursTableAnnotationComposer({
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

  GeneratedColumn<String> get role =>
      $composableBuilder(column: $table.role, builder: (column) => column);

  GeneratedColumn<String> get motDePasse => $composableBuilder(
      column: $table.motDePasse, builder: (column) => column);

  GeneratedColumn<String> get pinHash =>
      $composableBuilder(column: $table.pinHash, builder: (column) => column);

  GeneratedColumn<DateTime> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);

  $$BoutiquesTableAnnotationComposer get boutiqueId {
    final $$BoutiquesTableAnnotationComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.boutiqueId,
        referencedTable: $db.boutiques,
        getReferencedColumn: (t) => t.id,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$BoutiquesTableAnnotationComposer(
              $db: $db,
              $table: $db.boutiques,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return composer;
  }

  Expression<T> ventesRefs<T extends Object>(
      Expression<T> Function($$VentesTableAnnotationComposer a) f) {
    final $$VentesTableAnnotationComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.id,
        referencedTable: $db.ventes,
        getReferencedColumn: (t) => t.utilisateurId,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$VentesTableAnnotationComposer(
              $db: $db,
              $table: $db.ventes,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return f(composer);
  }
}

class $$UtilisateursTableTableManager extends RootTableManager<
    _$AppDatabase,
    $UtilisateursTable,
    Utilisateur,
    $$UtilisateursTableFilterComposer,
    $$UtilisateursTableOrderingComposer,
    $$UtilisateursTableAnnotationComposer,
    $$UtilisateursTableCreateCompanionBuilder,
    $$UtilisateursTableUpdateCompanionBuilder,
    (Utilisateur, $$UtilisateursTableReferences),
    Utilisateur,
    PrefetchHooks Function({bool boutiqueId, bool ventesRefs})> {
  $$UtilisateursTableTableManager(_$AppDatabase db, $UtilisateursTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$UtilisateursTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$UtilisateursTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$UtilisateursTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback: ({
            Value<String> id = const Value.absent(),
            Value<String> boutiqueId = const Value.absent(),
            Value<String> nom = const Value.absent(),
            Value<String> role = const Value.absent(),
            Value<String> motDePasse = const Value.absent(),
            Value<String?> pinHash = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              UtilisateursCompanion(
            id: id,
            boutiqueId: boutiqueId,
            nom: nom,
            role: role,
            motDePasse: motDePasse,
            pinHash: pinHash,
            createdAt: createdAt,
            rowid: rowid,
          ),
          createCompanionCallback: ({
            required String id,
            required String boutiqueId,
            required String nom,
            Value<String> role = const Value.absent(),
            required String motDePasse,
            Value<String?> pinHash = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              UtilisateursCompanion.insert(
            id: id,
            boutiqueId: boutiqueId,
            nom: nom,
            role: role,
            motDePasse: motDePasse,
            pinHash: pinHash,
            createdAt: createdAt,
            rowid: rowid,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (
                    e.readTable(table),
                    $$UtilisateursTableReferences(db, table, e)
                  ))
              .toList(),
          prefetchHooksCallback: ({boutiqueId = false, ventesRefs = false}) {
            return PrefetchHooks(
              db: db,
              explicitlyWatchedTables: [if (ventesRefs) db.ventes],
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
                        $$UtilisateursTableReferences._boutiqueIdTable(db),
                    referencedColumn:
                        $$UtilisateursTableReferences._boutiqueIdTable(db).id,
                  ) as T;
                }

                return state;
              },
              getPrefetchedDataCallback: (items) async {
                return [
                  if (ventesRefs)
                    await $_getPrefetchedData<Utilisateur, $UtilisateursTable,
                            Vente>(
                        currentTable: table,
                        referencedTable:
                            $$UtilisateursTableReferences._ventesRefsTable(db),
                        managerFromTypedResult: (p0) =>
                            $$UtilisateursTableReferences(db, table, p0)
                                .ventesRefs,
                        referencedItemsForCurrentItem:
                            (item, referencedItems) => referencedItems
                                .where((e) => e.utilisateurId == item.id),
                        typedResults: items)
                ];
              },
            );
          },
        ));
}

typedef $$UtilisateursTableProcessedTableManager = ProcessedTableManager<
    _$AppDatabase,
    $UtilisateursTable,
    Utilisateur,
    $$UtilisateursTableFilterComposer,
    $$UtilisateursTableOrderingComposer,
    $$UtilisateursTableAnnotationComposer,
    $$UtilisateursTableCreateCompanionBuilder,
    $$UtilisateursTableUpdateCompanionBuilder,
    (Utilisateur, $$UtilisateursTableReferences),
    Utilisateur,
    PrefetchHooks Function({bool boutiqueId, bool ventesRefs})>;
typedef $$ProduitsTableCreateCompanionBuilder = ProduitsCompanion Function({
  required String id,
  required String boutiqueId,
  required String nom,
  Value<String> categorie,
  required int prixVente,
  Value<int> prixAchat,
  Value<int> quantite,
  Value<int> seuilAlerte,
  Value<bool> synced,
  Value<DateTime> updatedAt,
  Value<int> rowid,
});
typedef $$ProduitsTableUpdateCompanionBuilder = ProduitsCompanion Function({
  Value<String> id,
  Value<String> boutiqueId,
  Value<String> nom,
  Value<String> categorie,
  Value<int> prixVente,
  Value<int> prixAchat,
  Value<int> quantite,
  Value<int> seuilAlerte,
  Value<bool> synced,
  Value<DateTime> updatedAt,
  Value<int> rowid,
});

final class $$ProduitsTableReferences
    extends BaseReferences<_$AppDatabase, $ProduitsTable, Produit> {
  $$ProduitsTableReferences(super.$_db, super.$_table, super.$_typedResult);

  static $BoutiquesTable _boutiqueIdTable(_$AppDatabase db) =>
      db.boutiques.createAlias(
          $_aliasNameGenerator(db.produits.boutiqueId, db.boutiques.id));

  $$BoutiquesTableProcessedTableManager get boutiqueId {
    final $_column = $_itemColumn<String>('boutique_id')!;

    final manager = $$BoutiquesTableTableManager($_db, $_db.boutiques)
        .filter((f) => f.id.sqlEquals($_column));
    final item = $_typedResult.readTableOrNull(_boutiqueIdTable($_db));
    if (item == null) return manager;
    return ProcessedTableManager(
        manager.$state.copyWith(prefetchedData: [item]));
  }

  static MultiTypedResultKey<$VentesTable, List<Vente>> _ventesRefsTable(
          _$AppDatabase db) =>
      MultiTypedResultKey.fromTable(db.ventes,
          aliasName: $_aliasNameGenerator(db.produits.id, db.ventes.produitId));

  $$VentesTableProcessedTableManager get ventesRefs {
    final manager = $$VentesTableTableManager($_db, $_db.ventes)
        .filter((f) => f.produitId.id.sqlEquals($_itemColumn<String>('id')!));

    final cache = $_typedResult.readTableOrNull(_ventesRefsTable($_db));
    return ProcessedTableManager(
        manager.$state.copyWith(prefetchedData: cache));
  }
}

class $$ProduitsTableFilterComposer
    extends Composer<_$AppDatabase, $ProduitsTable> {
  $$ProduitsTableFilterComposer({
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

  ColumnFilters<String> get categorie => $composableBuilder(
      column: $table.categorie, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get prixVente => $composableBuilder(
      column: $table.prixVente, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get prixAchat => $composableBuilder(
      column: $table.prixAchat, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get quantite => $composableBuilder(
      column: $table.quantite, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get seuilAlerte => $composableBuilder(
      column: $table.seuilAlerte, builder: (column) => ColumnFilters(column));

  ColumnFilters<bool> get synced => $composableBuilder(
      column: $table.synced, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get updatedAt => $composableBuilder(
      column: $table.updatedAt, builder: (column) => ColumnFilters(column));

  $$BoutiquesTableFilterComposer get boutiqueId {
    final $$BoutiquesTableFilterComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.boutiqueId,
        referencedTable: $db.boutiques,
        getReferencedColumn: (t) => t.id,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$BoutiquesTableFilterComposer(
              $db: $db,
              $table: $db.boutiques,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return composer;
  }

  Expression<bool> ventesRefs(
      Expression<bool> Function($$VentesTableFilterComposer f) f) {
    final $$VentesTableFilterComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.id,
        referencedTable: $db.ventes,
        getReferencedColumn: (t) => t.produitId,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$VentesTableFilterComposer(
              $db: $db,
              $table: $db.ventes,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return f(composer);
  }
}

class $$ProduitsTableOrderingComposer
    extends Composer<_$AppDatabase, $ProduitsTable> {
  $$ProduitsTableOrderingComposer({
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

  ColumnOrderings<String> get categorie => $composableBuilder(
      column: $table.categorie, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get prixVente => $composableBuilder(
      column: $table.prixVente, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get prixAchat => $composableBuilder(
      column: $table.prixAchat, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get quantite => $composableBuilder(
      column: $table.quantite, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get seuilAlerte => $composableBuilder(
      column: $table.seuilAlerte, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<bool> get synced => $composableBuilder(
      column: $table.synced, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get updatedAt => $composableBuilder(
      column: $table.updatedAt, builder: (column) => ColumnOrderings(column));

  $$BoutiquesTableOrderingComposer get boutiqueId {
    final $$BoutiquesTableOrderingComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.boutiqueId,
        referencedTable: $db.boutiques,
        getReferencedColumn: (t) => t.id,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$BoutiquesTableOrderingComposer(
              $db: $db,
              $table: $db.boutiques,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return composer;
  }
}

class $$ProduitsTableAnnotationComposer
    extends Composer<_$AppDatabase, $ProduitsTable> {
  $$ProduitsTableAnnotationComposer({
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

  GeneratedColumn<String> get categorie =>
      $composableBuilder(column: $table.categorie, builder: (column) => column);

  GeneratedColumn<int> get prixVente =>
      $composableBuilder(column: $table.prixVente, builder: (column) => column);

  GeneratedColumn<int> get prixAchat =>
      $composableBuilder(column: $table.prixAchat, builder: (column) => column);

  GeneratedColumn<int> get quantite =>
      $composableBuilder(column: $table.quantite, builder: (column) => column);

  GeneratedColumn<int> get seuilAlerte => $composableBuilder(
      column: $table.seuilAlerte, builder: (column) => column);

  GeneratedColumn<bool> get synced =>
      $composableBuilder(column: $table.synced, builder: (column) => column);

  GeneratedColumn<DateTime> get updatedAt =>
      $composableBuilder(column: $table.updatedAt, builder: (column) => column);

  $$BoutiquesTableAnnotationComposer get boutiqueId {
    final $$BoutiquesTableAnnotationComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.boutiqueId,
        referencedTable: $db.boutiques,
        getReferencedColumn: (t) => t.id,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$BoutiquesTableAnnotationComposer(
              $db: $db,
              $table: $db.boutiques,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return composer;
  }

  Expression<T> ventesRefs<T extends Object>(
      Expression<T> Function($$VentesTableAnnotationComposer a) f) {
    final $$VentesTableAnnotationComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.id,
        referencedTable: $db.ventes,
        getReferencedColumn: (t) => t.produitId,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$VentesTableAnnotationComposer(
              $db: $db,
              $table: $db.ventes,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return f(composer);
  }
}

class $$ProduitsTableTableManager extends RootTableManager<
    _$AppDatabase,
    $ProduitsTable,
    Produit,
    $$ProduitsTableFilterComposer,
    $$ProduitsTableOrderingComposer,
    $$ProduitsTableAnnotationComposer,
    $$ProduitsTableCreateCompanionBuilder,
    $$ProduitsTableUpdateCompanionBuilder,
    (Produit, $$ProduitsTableReferences),
    Produit,
    PrefetchHooks Function({bool boutiqueId, bool ventesRefs})> {
  $$ProduitsTableTableManager(_$AppDatabase db, $ProduitsTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$ProduitsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$ProduitsTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$ProduitsTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback: ({
            Value<String> id = const Value.absent(),
            Value<String> boutiqueId = const Value.absent(),
            Value<String> nom = const Value.absent(),
            Value<String> categorie = const Value.absent(),
            Value<int> prixVente = const Value.absent(),
            Value<int> prixAchat = const Value.absent(),
            Value<int> quantite = const Value.absent(),
            Value<int> seuilAlerte = const Value.absent(),
            Value<bool> synced = const Value.absent(),
            Value<DateTime> updatedAt = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              ProduitsCompanion(
            id: id,
            boutiqueId: boutiqueId,
            nom: nom,
            categorie: categorie,
            prixVente: prixVente,
            prixAchat: prixAchat,
            quantite: quantite,
            seuilAlerte: seuilAlerte,
            synced: synced,
            updatedAt: updatedAt,
            rowid: rowid,
          ),
          createCompanionCallback: ({
            required String id,
            required String boutiqueId,
            required String nom,
            Value<String> categorie = const Value.absent(),
            required int prixVente,
            Value<int> prixAchat = const Value.absent(),
            Value<int> quantite = const Value.absent(),
            Value<int> seuilAlerte = const Value.absent(),
            Value<bool> synced = const Value.absent(),
            Value<DateTime> updatedAt = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              ProduitsCompanion.insert(
            id: id,
            boutiqueId: boutiqueId,
            nom: nom,
            categorie: categorie,
            prixVente: prixVente,
            prixAchat: prixAchat,
            quantite: quantite,
            seuilAlerte: seuilAlerte,
            synced: synced,
            updatedAt: updatedAt,
            rowid: rowid,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) =>
                  (e.readTable(table), $$ProduitsTableReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: ({boutiqueId = false, ventesRefs = false}) {
            return PrefetchHooks(
              db: db,
              explicitlyWatchedTables: [if (ventesRefs) db.ventes],
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
                        $$ProduitsTableReferences._boutiqueIdTable(db),
                    referencedColumn:
                        $$ProduitsTableReferences._boutiqueIdTable(db).id,
                  ) as T;
                }

                return state;
              },
              getPrefetchedDataCallback: (items) async {
                return [
                  if (ventesRefs)
                    await $_getPrefetchedData<Produit, $ProduitsTable, Vente>(
                        currentTable: table,
                        referencedTable:
                            $$ProduitsTableReferences._ventesRefsTable(db),
                        managerFromTypedResult: (p0) =>
                            $$ProduitsTableReferences(db, table, p0).ventesRefs,
                        referencedItemsForCurrentItem:
                            (item, referencedItems) => referencedItems
                                .where((e) => e.produitId == item.id),
                        typedResults: items)
                ];
              },
            );
          },
        ));
}

typedef $$ProduitsTableProcessedTableManager = ProcessedTableManager<
    _$AppDatabase,
    $ProduitsTable,
    Produit,
    $$ProduitsTableFilterComposer,
    $$ProduitsTableOrderingComposer,
    $$ProduitsTableAnnotationComposer,
    $$ProduitsTableCreateCompanionBuilder,
    $$ProduitsTableUpdateCompanionBuilder,
    (Produit, $$ProduitsTableReferences),
    Produit,
    PrefetchHooks Function({bool boutiqueId, bool ventesRefs})>;
typedef $$ClientsTableCreateCompanionBuilder = ClientsCompanion Function({
  required String id,
  required String boutiqueId,
  required String nom,
  Value<String?> telephone,
  Value<String> score,
  Value<int> totalDu,
  Value<int> nombreDettes,
  Value<int> nombresRemboursements,
  Value<bool> synced,
  Value<DateTime> createdAt,
  Value<int> rowid,
});
typedef $$ClientsTableUpdateCompanionBuilder = ClientsCompanion Function({
  Value<String> id,
  Value<String> boutiqueId,
  Value<String> nom,
  Value<String?> telephone,
  Value<String> score,
  Value<int> totalDu,
  Value<int> nombreDettes,
  Value<int> nombresRemboursements,
  Value<bool> synced,
  Value<DateTime> createdAt,
  Value<int> rowid,
});

final class $$ClientsTableReferences
    extends BaseReferences<_$AppDatabase, $ClientsTable, Client> {
  $$ClientsTableReferences(super.$_db, super.$_table, super.$_typedResult);

  static $BoutiquesTable _boutiqueIdTable(_$AppDatabase db) =>
      db.boutiques.createAlias(
          $_aliasNameGenerator(db.clients.boutiqueId, db.boutiques.id));

  $$BoutiquesTableProcessedTableManager get boutiqueId {
    final $_column = $_itemColumn<String>('boutique_id')!;

    final manager = $$BoutiquesTableTableManager($_db, $_db.boutiques)
        .filter((f) => f.id.sqlEquals($_column));
    final item = $_typedResult.readTableOrNull(_boutiqueIdTable($_db));
    if (item == null) return manager;
    return ProcessedTableManager(
        manager.$state.copyWith(prefetchedData: [item]));
  }

  static MultiTypedResultKey<$DettesTable, List<Dette>> _dettesRefsTable(
          _$AppDatabase db) =>
      MultiTypedResultKey.fromTable(db.dettes,
          aliasName: $_aliasNameGenerator(db.clients.id, db.dettes.clientId));

  $$DettesTableProcessedTableManager get dettesRefs {
    final manager = $$DettesTableTableManager($_db, $_db.dettes)
        .filter((f) => f.clientId.id.sqlEquals($_itemColumn<String>('id')!));

    final cache = $_typedResult.readTableOrNull(_dettesRefsTable($_db));
    return ProcessedTableManager(
        manager.$state.copyWith(prefetchedData: cache));
  }
}

class $$ClientsTableFilterComposer
    extends Composer<_$AppDatabase, $ClientsTable> {
  $$ClientsTableFilterComposer({
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

  ColumnFilters<String> get score => $composableBuilder(
      column: $table.score, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get totalDu => $composableBuilder(
      column: $table.totalDu, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get nombreDettes => $composableBuilder(
      column: $table.nombreDettes, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get nombresRemboursements => $composableBuilder(
      column: $table.nombresRemboursements,
      builder: (column) => ColumnFilters(column));

  ColumnFilters<bool> get synced => $composableBuilder(
      column: $table.synced, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnFilters(column));

  $$BoutiquesTableFilterComposer get boutiqueId {
    final $$BoutiquesTableFilterComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.boutiqueId,
        referencedTable: $db.boutiques,
        getReferencedColumn: (t) => t.id,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$BoutiquesTableFilterComposer(
              $db: $db,
              $table: $db.boutiques,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return composer;
  }

  Expression<bool> dettesRefs(
      Expression<bool> Function($$DettesTableFilterComposer f) f) {
    final $$DettesTableFilterComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.id,
        referencedTable: $db.dettes,
        getReferencedColumn: (t) => t.clientId,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$DettesTableFilterComposer(
              $db: $db,
              $table: $db.dettes,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return f(composer);
  }
}

class $$ClientsTableOrderingComposer
    extends Composer<_$AppDatabase, $ClientsTable> {
  $$ClientsTableOrderingComposer({
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

  ColumnOrderings<String> get score => $composableBuilder(
      column: $table.score, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get totalDu => $composableBuilder(
      column: $table.totalDu, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get nombreDettes => $composableBuilder(
      column: $table.nombreDettes,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get nombresRemboursements => $composableBuilder(
      column: $table.nombresRemboursements,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<bool> get synced => $composableBuilder(
      column: $table.synced, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnOrderings(column));

  $$BoutiquesTableOrderingComposer get boutiqueId {
    final $$BoutiquesTableOrderingComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.boutiqueId,
        referencedTable: $db.boutiques,
        getReferencedColumn: (t) => t.id,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$BoutiquesTableOrderingComposer(
              $db: $db,
              $table: $db.boutiques,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return composer;
  }
}

class $$ClientsTableAnnotationComposer
    extends Composer<_$AppDatabase, $ClientsTable> {
  $$ClientsTableAnnotationComposer({
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

  GeneratedColumn<String> get score =>
      $composableBuilder(column: $table.score, builder: (column) => column);

  GeneratedColumn<int> get totalDu =>
      $composableBuilder(column: $table.totalDu, builder: (column) => column);

  GeneratedColumn<int> get nombreDettes => $composableBuilder(
      column: $table.nombreDettes, builder: (column) => column);

  GeneratedColumn<int> get nombresRemboursements => $composableBuilder(
      column: $table.nombresRemboursements, builder: (column) => column);

  GeneratedColumn<bool> get synced =>
      $composableBuilder(column: $table.synced, builder: (column) => column);

  GeneratedColumn<DateTime> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);

  $$BoutiquesTableAnnotationComposer get boutiqueId {
    final $$BoutiquesTableAnnotationComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.boutiqueId,
        referencedTable: $db.boutiques,
        getReferencedColumn: (t) => t.id,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$BoutiquesTableAnnotationComposer(
              $db: $db,
              $table: $db.boutiques,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return composer;
  }

  Expression<T> dettesRefs<T extends Object>(
      Expression<T> Function($$DettesTableAnnotationComposer a) f) {
    final $$DettesTableAnnotationComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.id,
        referencedTable: $db.dettes,
        getReferencedColumn: (t) => t.clientId,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$DettesTableAnnotationComposer(
              $db: $db,
              $table: $db.dettes,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return f(composer);
  }
}

class $$ClientsTableTableManager extends RootTableManager<
    _$AppDatabase,
    $ClientsTable,
    Client,
    $$ClientsTableFilterComposer,
    $$ClientsTableOrderingComposer,
    $$ClientsTableAnnotationComposer,
    $$ClientsTableCreateCompanionBuilder,
    $$ClientsTableUpdateCompanionBuilder,
    (Client, $$ClientsTableReferences),
    Client,
    PrefetchHooks Function({bool boutiqueId, bool dettesRefs})> {
  $$ClientsTableTableManager(_$AppDatabase db, $ClientsTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$ClientsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$ClientsTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$ClientsTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback: ({
            Value<String> id = const Value.absent(),
            Value<String> boutiqueId = const Value.absent(),
            Value<String> nom = const Value.absent(),
            Value<String?> telephone = const Value.absent(),
            Value<String> score = const Value.absent(),
            Value<int> totalDu = const Value.absent(),
            Value<int> nombreDettes = const Value.absent(),
            Value<int> nombresRemboursements = const Value.absent(),
            Value<bool> synced = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              ClientsCompanion(
            id: id,
            boutiqueId: boutiqueId,
            nom: nom,
            telephone: telephone,
            score: score,
            totalDu: totalDu,
            nombreDettes: nombreDettes,
            nombresRemboursements: nombresRemboursements,
            synced: synced,
            createdAt: createdAt,
            rowid: rowid,
          ),
          createCompanionCallback: ({
            required String id,
            required String boutiqueId,
            required String nom,
            Value<String?> telephone = const Value.absent(),
            Value<String> score = const Value.absent(),
            Value<int> totalDu = const Value.absent(),
            Value<int> nombreDettes = const Value.absent(),
            Value<int> nombresRemboursements = const Value.absent(),
            Value<bool> synced = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              ClientsCompanion.insert(
            id: id,
            boutiqueId: boutiqueId,
            nom: nom,
            telephone: telephone,
            score: score,
            totalDu: totalDu,
            nombreDettes: nombreDettes,
            nombresRemboursements: nombresRemboursements,
            synced: synced,
            createdAt: createdAt,
            rowid: rowid,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) =>
                  (e.readTable(table), $$ClientsTableReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: ({boutiqueId = false, dettesRefs = false}) {
            return PrefetchHooks(
              db: db,
              explicitlyWatchedTables: [if (dettesRefs) db.dettes],
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
                        $$ClientsTableReferences._boutiqueIdTable(db),
                    referencedColumn:
                        $$ClientsTableReferences._boutiqueIdTable(db).id,
                  ) as T;
                }

                return state;
              },
              getPrefetchedDataCallback: (items) async {
                return [
                  if (dettesRefs)
                    await $_getPrefetchedData<Client, $ClientsTable, Dette>(
                        currentTable: table,
                        referencedTable:
                            $$ClientsTableReferences._dettesRefsTable(db),
                        managerFromTypedResult: (p0) =>
                            $$ClientsTableReferences(db, table, p0).dettesRefs,
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

typedef $$ClientsTableProcessedTableManager = ProcessedTableManager<
    _$AppDatabase,
    $ClientsTable,
    Client,
    $$ClientsTableFilterComposer,
    $$ClientsTableOrderingComposer,
    $$ClientsTableAnnotationComposer,
    $$ClientsTableCreateCompanionBuilder,
    $$ClientsTableUpdateCompanionBuilder,
    (Client, $$ClientsTableReferences),
    Client,
    PrefetchHooks Function({bool boutiqueId, bool dettesRefs})>;
typedef $$VentesTableCreateCompanionBuilder = VentesCompanion Function({
  required String id,
  required String boutiqueId,
  required String produitId,
  Value<String?> clientId,
  required String utilisateurId,
  required int quantite,
  required int prixUnitaire,
  required int montantTotal,
  required String typePaiement,
  Value<String> source,
  Value<bool> synced,
  Value<DateTime> date,
  Value<int> rowid,
});
typedef $$VentesTableUpdateCompanionBuilder = VentesCompanion Function({
  Value<String> id,
  Value<String> boutiqueId,
  Value<String> produitId,
  Value<String?> clientId,
  Value<String> utilisateurId,
  Value<int> quantite,
  Value<int> prixUnitaire,
  Value<int> montantTotal,
  Value<String> typePaiement,
  Value<String> source,
  Value<bool> synced,
  Value<DateTime> date,
  Value<int> rowid,
});

final class $$VentesTableReferences
    extends BaseReferences<_$AppDatabase, $VentesTable, Vente> {
  $$VentesTableReferences(super.$_db, super.$_table, super.$_typedResult);

  static $BoutiquesTable _boutiqueIdTable(_$AppDatabase db) => db.boutiques
      .createAlias($_aliasNameGenerator(db.ventes.boutiqueId, db.boutiques.id));

  $$BoutiquesTableProcessedTableManager get boutiqueId {
    final $_column = $_itemColumn<String>('boutique_id')!;

    final manager = $$BoutiquesTableTableManager($_db, $_db.boutiques)
        .filter((f) => f.id.sqlEquals($_column));
    final item = $_typedResult.readTableOrNull(_boutiqueIdTable($_db));
    if (item == null) return manager;
    return ProcessedTableManager(
        manager.$state.copyWith(prefetchedData: [item]));
  }

  static $ProduitsTable _produitIdTable(_$AppDatabase db) => db.produits
      .createAlias($_aliasNameGenerator(db.ventes.produitId, db.produits.id));

  $$ProduitsTableProcessedTableManager get produitId {
    final $_column = $_itemColumn<String>('produit_id')!;

    final manager = $$ProduitsTableTableManager($_db, $_db.produits)
        .filter((f) => f.id.sqlEquals($_column));
    final item = $_typedResult.readTableOrNull(_produitIdTable($_db));
    if (item == null) return manager;
    return ProcessedTableManager(
        manager.$state.copyWith(prefetchedData: [item]));
  }

  static $UtilisateursTable _utilisateurIdTable(_$AppDatabase db) =>
      db.utilisateurs.createAlias(
          $_aliasNameGenerator(db.ventes.utilisateurId, db.utilisateurs.id));

  $$UtilisateursTableProcessedTableManager get utilisateurId {
    final $_column = $_itemColumn<String>('utilisateur_id')!;

    final manager = $$UtilisateursTableTableManager($_db, $_db.utilisateurs)
        .filter((f) => f.id.sqlEquals($_column));
    final item = $_typedResult.readTableOrNull(_utilisateurIdTable($_db));
    if (item == null) return manager;
    return ProcessedTableManager(
        manager.$state.copyWith(prefetchedData: [item]));
  }

  static MultiTypedResultKey<$DettesTable, List<Dette>> _dettesRefsTable(
          _$AppDatabase db) =>
      MultiTypedResultKey.fromTable(db.dettes,
          aliasName: $_aliasNameGenerator(db.ventes.id, db.dettes.venteId));

  $$DettesTableProcessedTableManager get dettesRefs {
    final manager = $$DettesTableTableManager($_db, $_db.dettes)
        .filter((f) => f.venteId.id.sqlEquals($_itemColumn<String>('id')!));

    final cache = $_typedResult.readTableOrNull(_dettesRefsTable($_db));
    return ProcessedTableManager(
        manager.$state.copyWith(prefetchedData: cache));
  }
}

class $$VentesTableFilterComposer
    extends Composer<_$AppDatabase, $VentesTable> {
  $$VentesTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get clientId => $composableBuilder(
      column: $table.clientId, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get quantite => $composableBuilder(
      column: $table.quantite, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get prixUnitaire => $composableBuilder(
      column: $table.prixUnitaire, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get montantTotal => $composableBuilder(
      column: $table.montantTotal, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get typePaiement => $composableBuilder(
      column: $table.typePaiement, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get source => $composableBuilder(
      column: $table.source, builder: (column) => ColumnFilters(column));

  ColumnFilters<bool> get synced => $composableBuilder(
      column: $table.synced, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get date => $composableBuilder(
      column: $table.date, builder: (column) => ColumnFilters(column));

  $$BoutiquesTableFilterComposer get boutiqueId {
    final $$BoutiquesTableFilterComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.boutiqueId,
        referencedTable: $db.boutiques,
        getReferencedColumn: (t) => t.id,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$BoutiquesTableFilterComposer(
              $db: $db,
              $table: $db.boutiques,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return composer;
  }

  $$ProduitsTableFilterComposer get produitId {
    final $$ProduitsTableFilterComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.produitId,
        referencedTable: $db.produits,
        getReferencedColumn: (t) => t.id,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$ProduitsTableFilterComposer(
              $db: $db,
              $table: $db.produits,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return composer;
  }

  $$UtilisateursTableFilterComposer get utilisateurId {
    final $$UtilisateursTableFilterComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.utilisateurId,
        referencedTable: $db.utilisateurs,
        getReferencedColumn: (t) => t.id,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$UtilisateursTableFilterComposer(
              $db: $db,
              $table: $db.utilisateurs,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return composer;
  }

  Expression<bool> dettesRefs(
      Expression<bool> Function($$DettesTableFilterComposer f) f) {
    final $$DettesTableFilterComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.id,
        referencedTable: $db.dettes,
        getReferencedColumn: (t) => t.venteId,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$DettesTableFilterComposer(
              $db: $db,
              $table: $db.dettes,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return f(composer);
  }
}

class $$VentesTableOrderingComposer
    extends Composer<_$AppDatabase, $VentesTable> {
  $$VentesTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get clientId => $composableBuilder(
      column: $table.clientId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get quantite => $composableBuilder(
      column: $table.quantite, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get prixUnitaire => $composableBuilder(
      column: $table.prixUnitaire,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get montantTotal => $composableBuilder(
      column: $table.montantTotal,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get typePaiement => $composableBuilder(
      column: $table.typePaiement,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get source => $composableBuilder(
      column: $table.source, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<bool> get synced => $composableBuilder(
      column: $table.synced, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get date => $composableBuilder(
      column: $table.date, builder: (column) => ColumnOrderings(column));

  $$BoutiquesTableOrderingComposer get boutiqueId {
    final $$BoutiquesTableOrderingComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.boutiqueId,
        referencedTable: $db.boutiques,
        getReferencedColumn: (t) => t.id,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$BoutiquesTableOrderingComposer(
              $db: $db,
              $table: $db.boutiques,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return composer;
  }

  $$ProduitsTableOrderingComposer get produitId {
    final $$ProduitsTableOrderingComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.produitId,
        referencedTable: $db.produits,
        getReferencedColumn: (t) => t.id,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$ProduitsTableOrderingComposer(
              $db: $db,
              $table: $db.produits,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return composer;
  }

  $$UtilisateursTableOrderingComposer get utilisateurId {
    final $$UtilisateursTableOrderingComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.utilisateurId,
        referencedTable: $db.utilisateurs,
        getReferencedColumn: (t) => t.id,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$UtilisateursTableOrderingComposer(
              $db: $db,
              $table: $db.utilisateurs,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return composer;
  }
}

class $$VentesTableAnnotationComposer
    extends Composer<_$AppDatabase, $VentesTable> {
  $$VentesTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get clientId =>
      $composableBuilder(column: $table.clientId, builder: (column) => column);

  GeneratedColumn<int> get quantite =>
      $composableBuilder(column: $table.quantite, builder: (column) => column);

  GeneratedColumn<int> get prixUnitaire => $composableBuilder(
      column: $table.prixUnitaire, builder: (column) => column);

  GeneratedColumn<int> get montantTotal => $composableBuilder(
      column: $table.montantTotal, builder: (column) => column);

  GeneratedColumn<String> get typePaiement => $composableBuilder(
      column: $table.typePaiement, builder: (column) => column);

  GeneratedColumn<String> get source =>
      $composableBuilder(column: $table.source, builder: (column) => column);

  GeneratedColumn<bool> get synced =>
      $composableBuilder(column: $table.synced, builder: (column) => column);

  GeneratedColumn<DateTime> get date =>
      $composableBuilder(column: $table.date, builder: (column) => column);

  $$BoutiquesTableAnnotationComposer get boutiqueId {
    final $$BoutiquesTableAnnotationComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.boutiqueId,
        referencedTable: $db.boutiques,
        getReferencedColumn: (t) => t.id,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$BoutiquesTableAnnotationComposer(
              $db: $db,
              $table: $db.boutiques,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return composer;
  }

  $$ProduitsTableAnnotationComposer get produitId {
    final $$ProduitsTableAnnotationComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.produitId,
        referencedTable: $db.produits,
        getReferencedColumn: (t) => t.id,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$ProduitsTableAnnotationComposer(
              $db: $db,
              $table: $db.produits,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return composer;
  }

  $$UtilisateursTableAnnotationComposer get utilisateurId {
    final $$UtilisateursTableAnnotationComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.utilisateurId,
        referencedTable: $db.utilisateurs,
        getReferencedColumn: (t) => t.id,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$UtilisateursTableAnnotationComposer(
              $db: $db,
              $table: $db.utilisateurs,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return composer;
  }

  Expression<T> dettesRefs<T extends Object>(
      Expression<T> Function($$DettesTableAnnotationComposer a) f) {
    final $$DettesTableAnnotationComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.id,
        referencedTable: $db.dettes,
        getReferencedColumn: (t) => t.venteId,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$DettesTableAnnotationComposer(
              $db: $db,
              $table: $db.dettes,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return f(composer);
  }
}

class $$VentesTableTableManager extends RootTableManager<
    _$AppDatabase,
    $VentesTable,
    Vente,
    $$VentesTableFilterComposer,
    $$VentesTableOrderingComposer,
    $$VentesTableAnnotationComposer,
    $$VentesTableCreateCompanionBuilder,
    $$VentesTableUpdateCompanionBuilder,
    (Vente, $$VentesTableReferences),
    Vente,
    PrefetchHooks Function(
        {bool boutiqueId,
        bool produitId,
        bool utilisateurId,
        bool dettesRefs})> {
  $$VentesTableTableManager(_$AppDatabase db, $VentesTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$VentesTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$VentesTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$VentesTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback: ({
            Value<String> id = const Value.absent(),
            Value<String> boutiqueId = const Value.absent(),
            Value<String> produitId = const Value.absent(),
            Value<String?> clientId = const Value.absent(),
            Value<String> utilisateurId = const Value.absent(),
            Value<int> quantite = const Value.absent(),
            Value<int> prixUnitaire = const Value.absent(),
            Value<int> montantTotal = const Value.absent(),
            Value<String> typePaiement = const Value.absent(),
            Value<String> source = const Value.absent(),
            Value<bool> synced = const Value.absent(),
            Value<DateTime> date = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              VentesCompanion(
            id: id,
            boutiqueId: boutiqueId,
            produitId: produitId,
            clientId: clientId,
            utilisateurId: utilisateurId,
            quantite: quantite,
            prixUnitaire: prixUnitaire,
            montantTotal: montantTotal,
            typePaiement: typePaiement,
            source: source,
            synced: synced,
            date: date,
            rowid: rowid,
          ),
          createCompanionCallback: ({
            required String id,
            required String boutiqueId,
            required String produitId,
            Value<String?> clientId = const Value.absent(),
            required String utilisateurId,
            required int quantite,
            required int prixUnitaire,
            required int montantTotal,
            required String typePaiement,
            Value<String> source = const Value.absent(),
            Value<bool> synced = const Value.absent(),
            Value<DateTime> date = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              VentesCompanion.insert(
            id: id,
            boutiqueId: boutiqueId,
            produitId: produitId,
            clientId: clientId,
            utilisateurId: utilisateurId,
            quantite: quantite,
            prixUnitaire: prixUnitaire,
            montantTotal: montantTotal,
            typePaiement: typePaiement,
            source: source,
            synced: synced,
            date: date,
            rowid: rowid,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) =>
                  (e.readTable(table), $$VentesTableReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: (
              {boutiqueId = false,
              produitId = false,
              utilisateurId = false,
              dettesRefs = false}) {
            return PrefetchHooks(
              db: db,
              explicitlyWatchedTables: [if (dettesRefs) db.dettes],
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
                        $$VentesTableReferences._boutiqueIdTable(db),
                    referencedColumn:
                        $$VentesTableReferences._boutiqueIdTable(db).id,
                  ) as T;
                }
                if (produitId) {
                  state = state.withJoin(
                    currentTable: table,
                    currentColumn: table.produitId,
                    referencedTable:
                        $$VentesTableReferences._produitIdTable(db),
                    referencedColumn:
                        $$VentesTableReferences._produitIdTable(db).id,
                  ) as T;
                }
                if (utilisateurId) {
                  state = state.withJoin(
                    currentTable: table,
                    currentColumn: table.utilisateurId,
                    referencedTable:
                        $$VentesTableReferences._utilisateurIdTable(db),
                    referencedColumn:
                        $$VentesTableReferences._utilisateurIdTable(db).id,
                  ) as T;
                }

                return state;
              },
              getPrefetchedDataCallback: (items) async {
                return [
                  if (dettesRefs)
                    await $_getPrefetchedData<Vente, $VentesTable, Dette>(
                        currentTable: table,
                        referencedTable:
                            $$VentesTableReferences._dettesRefsTable(db),
                        managerFromTypedResult: (p0) =>
                            $$VentesTableReferences(db, table, p0).dettesRefs,
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

typedef $$VentesTableProcessedTableManager = ProcessedTableManager<
    _$AppDatabase,
    $VentesTable,
    Vente,
    $$VentesTableFilterComposer,
    $$VentesTableOrderingComposer,
    $$VentesTableAnnotationComposer,
    $$VentesTableCreateCompanionBuilder,
    $$VentesTableUpdateCompanionBuilder,
    (Vente, $$VentesTableReferences),
    Vente,
    PrefetchHooks Function(
        {bool boutiqueId,
        bool produitId,
        bool utilisateurId,
        bool dettesRefs})>;
typedef $$DettesTableCreateCompanionBuilder = DettesCompanion Function({
  required String id,
  required String clientId,
  required String venteId,
  required String boutiqueId,
  required int montant,
  Value<int> montantPaye,
  Value<String> statut,
  Value<DateTime?> dateEcheance,
  Value<bool> rappel1JourEnvoye,
  Value<bool> rappel3JoursEnvoye,
  Value<bool> rappel7JoursEnvoye,
  Value<bool> synced,
  Value<DateTime> createdAt,
  Value<DateTime> updatedAt,
  Value<int> rowid,
});
typedef $$DettesTableUpdateCompanionBuilder = DettesCompanion Function({
  Value<String> id,
  Value<String> clientId,
  Value<String> venteId,
  Value<String> boutiqueId,
  Value<int> montant,
  Value<int> montantPaye,
  Value<String> statut,
  Value<DateTime?> dateEcheance,
  Value<bool> rappel1JourEnvoye,
  Value<bool> rappel3JoursEnvoye,
  Value<bool> rappel7JoursEnvoye,
  Value<bool> synced,
  Value<DateTime> createdAt,
  Value<DateTime> updatedAt,
  Value<int> rowid,
});

final class $$DettesTableReferences
    extends BaseReferences<_$AppDatabase, $DettesTable, Dette> {
  $$DettesTableReferences(super.$_db, super.$_table, super.$_typedResult);

  static $ClientsTable _clientIdTable(_$AppDatabase db) => db.clients
      .createAlias($_aliasNameGenerator(db.dettes.clientId, db.clients.id));

  $$ClientsTableProcessedTableManager get clientId {
    final $_column = $_itemColumn<String>('client_id')!;

    final manager = $$ClientsTableTableManager($_db, $_db.clients)
        .filter((f) => f.id.sqlEquals($_column));
    final item = $_typedResult.readTableOrNull(_clientIdTable($_db));
    if (item == null) return manager;
    return ProcessedTableManager(
        manager.$state.copyWith(prefetchedData: [item]));
  }

  static $VentesTable _venteIdTable(_$AppDatabase db) => db.ventes
      .createAlias($_aliasNameGenerator(db.dettes.venteId, db.ventes.id));

  $$VentesTableProcessedTableManager get venteId {
    final $_column = $_itemColumn<String>('vente_id')!;

    final manager = $$VentesTableTableManager($_db, $_db.ventes)
        .filter((f) => f.id.sqlEquals($_column));
    final item = $_typedResult.readTableOrNull(_venteIdTable($_db));
    if (item == null) return manager;
    return ProcessedTableManager(
        manager.$state.copyWith(prefetchedData: [item]));
  }

  static MultiTypedResultKey<$PaiementsTable, List<Paiement>>
      _paiementsRefsTable(_$AppDatabase db) => MultiTypedResultKey.fromTable(
          db.paiements,
          aliasName: $_aliasNameGenerator(db.dettes.id, db.paiements.detteId));

  $$PaiementsTableProcessedTableManager get paiementsRefs {
    final manager = $$PaiementsTableTableManager($_db, $_db.paiements)
        .filter((f) => f.detteId.id.sqlEquals($_itemColumn<String>('id')!));

    final cache = $_typedResult.readTableOrNull(_paiementsRefsTable($_db));
    return ProcessedTableManager(
        manager.$state.copyWith(prefetchedData: cache));
  }
}

class $$DettesTableFilterComposer
    extends Composer<_$AppDatabase, $DettesTable> {
  $$DettesTableFilterComposer({
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

  ColumnFilters<int> get montant => $composableBuilder(
      column: $table.montant, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get montantPaye => $composableBuilder(
      column: $table.montantPaye, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get statut => $composableBuilder(
      column: $table.statut, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get dateEcheance => $composableBuilder(
      column: $table.dateEcheance, builder: (column) => ColumnFilters(column));

  ColumnFilters<bool> get rappel1JourEnvoye => $composableBuilder(
      column: $table.rappel1JourEnvoye,
      builder: (column) => ColumnFilters(column));

  ColumnFilters<bool> get rappel3JoursEnvoye => $composableBuilder(
      column: $table.rappel3JoursEnvoye,
      builder: (column) => ColumnFilters(column));

  ColumnFilters<bool> get rappel7JoursEnvoye => $composableBuilder(
      column: $table.rappel7JoursEnvoye,
      builder: (column) => ColumnFilters(column));

  ColumnFilters<bool> get synced => $composableBuilder(
      column: $table.synced, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get updatedAt => $composableBuilder(
      column: $table.updatedAt, builder: (column) => ColumnFilters(column));

  $$ClientsTableFilterComposer get clientId {
    final $$ClientsTableFilterComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.clientId,
        referencedTable: $db.clients,
        getReferencedColumn: (t) => t.id,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$ClientsTableFilterComposer(
              $db: $db,
              $table: $db.clients,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return composer;
  }

  $$VentesTableFilterComposer get venteId {
    final $$VentesTableFilterComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.venteId,
        referencedTable: $db.ventes,
        getReferencedColumn: (t) => t.id,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$VentesTableFilterComposer(
              $db: $db,
              $table: $db.ventes,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return composer;
  }

  Expression<bool> paiementsRefs(
      Expression<bool> Function($$PaiementsTableFilterComposer f) f) {
    final $$PaiementsTableFilterComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.id,
        referencedTable: $db.paiements,
        getReferencedColumn: (t) => t.detteId,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$PaiementsTableFilterComposer(
              $db: $db,
              $table: $db.paiements,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return f(composer);
  }
}

class $$DettesTableOrderingComposer
    extends Composer<_$AppDatabase, $DettesTable> {
  $$DettesTableOrderingComposer({
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

  ColumnOrderings<int> get montant => $composableBuilder(
      column: $table.montant, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get montantPaye => $composableBuilder(
      column: $table.montantPaye, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get statut => $composableBuilder(
      column: $table.statut, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get dateEcheance => $composableBuilder(
      column: $table.dateEcheance,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<bool> get rappel1JourEnvoye => $composableBuilder(
      column: $table.rappel1JourEnvoye,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<bool> get rappel3JoursEnvoye => $composableBuilder(
      column: $table.rappel3JoursEnvoye,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<bool> get rappel7JoursEnvoye => $composableBuilder(
      column: $table.rappel7JoursEnvoye,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<bool> get synced => $composableBuilder(
      column: $table.synced, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get updatedAt => $composableBuilder(
      column: $table.updatedAt, builder: (column) => ColumnOrderings(column));

  $$ClientsTableOrderingComposer get clientId {
    final $$ClientsTableOrderingComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.clientId,
        referencedTable: $db.clients,
        getReferencedColumn: (t) => t.id,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$ClientsTableOrderingComposer(
              $db: $db,
              $table: $db.clients,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return composer;
  }

  $$VentesTableOrderingComposer get venteId {
    final $$VentesTableOrderingComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.venteId,
        referencedTable: $db.ventes,
        getReferencedColumn: (t) => t.id,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$VentesTableOrderingComposer(
              $db: $db,
              $table: $db.ventes,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return composer;
  }
}

class $$DettesTableAnnotationComposer
    extends Composer<_$AppDatabase, $DettesTable> {
  $$DettesTableAnnotationComposer({
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

  GeneratedColumn<int> get montant =>
      $composableBuilder(column: $table.montant, builder: (column) => column);

  GeneratedColumn<int> get montantPaye => $composableBuilder(
      column: $table.montantPaye, builder: (column) => column);

  GeneratedColumn<String> get statut =>
      $composableBuilder(column: $table.statut, builder: (column) => column);

  GeneratedColumn<DateTime> get dateEcheance => $composableBuilder(
      column: $table.dateEcheance, builder: (column) => column);

  GeneratedColumn<bool> get rappel1JourEnvoye => $composableBuilder(
      column: $table.rappel1JourEnvoye, builder: (column) => column);

  GeneratedColumn<bool> get rappel3JoursEnvoye => $composableBuilder(
      column: $table.rappel3JoursEnvoye, builder: (column) => column);

  GeneratedColumn<bool> get rappel7JoursEnvoye => $composableBuilder(
      column: $table.rappel7JoursEnvoye, builder: (column) => column);

  GeneratedColumn<bool> get synced =>
      $composableBuilder(column: $table.synced, builder: (column) => column);

  GeneratedColumn<DateTime> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);

  GeneratedColumn<DateTime> get updatedAt =>
      $composableBuilder(column: $table.updatedAt, builder: (column) => column);

  $$ClientsTableAnnotationComposer get clientId {
    final $$ClientsTableAnnotationComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.clientId,
        referencedTable: $db.clients,
        getReferencedColumn: (t) => t.id,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$ClientsTableAnnotationComposer(
              $db: $db,
              $table: $db.clients,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return composer;
  }

  $$VentesTableAnnotationComposer get venteId {
    final $$VentesTableAnnotationComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.venteId,
        referencedTable: $db.ventes,
        getReferencedColumn: (t) => t.id,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$VentesTableAnnotationComposer(
              $db: $db,
              $table: $db.ventes,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return composer;
  }

  Expression<T> paiementsRefs<T extends Object>(
      Expression<T> Function($$PaiementsTableAnnotationComposer a) f) {
    final $$PaiementsTableAnnotationComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.id,
        referencedTable: $db.paiements,
        getReferencedColumn: (t) => t.detteId,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$PaiementsTableAnnotationComposer(
              $db: $db,
              $table: $db.paiements,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return f(composer);
  }
}

class $$DettesTableTableManager extends RootTableManager<
    _$AppDatabase,
    $DettesTable,
    Dette,
    $$DettesTableFilterComposer,
    $$DettesTableOrderingComposer,
    $$DettesTableAnnotationComposer,
    $$DettesTableCreateCompanionBuilder,
    $$DettesTableUpdateCompanionBuilder,
    (Dette, $$DettesTableReferences),
    Dette,
    PrefetchHooks Function({bool clientId, bool venteId, bool paiementsRefs})> {
  $$DettesTableTableManager(_$AppDatabase db, $DettesTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$DettesTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$DettesTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$DettesTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback: ({
            Value<String> id = const Value.absent(),
            Value<String> clientId = const Value.absent(),
            Value<String> venteId = const Value.absent(),
            Value<String> boutiqueId = const Value.absent(),
            Value<int> montant = const Value.absent(),
            Value<int> montantPaye = const Value.absent(),
            Value<String> statut = const Value.absent(),
            Value<DateTime?> dateEcheance = const Value.absent(),
            Value<bool> rappel1JourEnvoye = const Value.absent(),
            Value<bool> rappel3JoursEnvoye = const Value.absent(),
            Value<bool> rappel7JoursEnvoye = const Value.absent(),
            Value<bool> synced = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
            Value<DateTime> updatedAt = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              DettesCompanion(
            id: id,
            clientId: clientId,
            venteId: venteId,
            boutiqueId: boutiqueId,
            montant: montant,
            montantPaye: montantPaye,
            statut: statut,
            dateEcheance: dateEcheance,
            rappel1JourEnvoye: rappel1JourEnvoye,
            rappel3JoursEnvoye: rappel3JoursEnvoye,
            rappel7JoursEnvoye: rappel7JoursEnvoye,
            synced: synced,
            createdAt: createdAt,
            updatedAt: updatedAt,
            rowid: rowid,
          ),
          createCompanionCallback: ({
            required String id,
            required String clientId,
            required String venteId,
            required String boutiqueId,
            required int montant,
            Value<int> montantPaye = const Value.absent(),
            Value<String> statut = const Value.absent(),
            Value<DateTime?> dateEcheance = const Value.absent(),
            Value<bool> rappel1JourEnvoye = const Value.absent(),
            Value<bool> rappel3JoursEnvoye = const Value.absent(),
            Value<bool> rappel7JoursEnvoye = const Value.absent(),
            Value<bool> synced = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
            Value<DateTime> updatedAt = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              DettesCompanion.insert(
            id: id,
            clientId: clientId,
            venteId: venteId,
            boutiqueId: boutiqueId,
            montant: montant,
            montantPaye: montantPaye,
            statut: statut,
            dateEcheance: dateEcheance,
            rappel1JourEnvoye: rappel1JourEnvoye,
            rappel3JoursEnvoye: rappel3JoursEnvoye,
            rappel7JoursEnvoye: rappel7JoursEnvoye,
            synced: synced,
            createdAt: createdAt,
            updatedAt: updatedAt,
            rowid: rowid,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) =>
                  (e.readTable(table), $$DettesTableReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: (
              {clientId = false, venteId = false, paiementsRefs = false}) {
            return PrefetchHooks(
              db: db,
              explicitlyWatchedTables: [if (paiementsRefs) db.paiements],
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
                if (clientId) {
                  state = state.withJoin(
                    currentTable: table,
                    currentColumn: table.clientId,
                    referencedTable: $$DettesTableReferences._clientIdTable(db),
                    referencedColumn:
                        $$DettesTableReferences._clientIdTable(db).id,
                  ) as T;
                }
                if (venteId) {
                  state = state.withJoin(
                    currentTable: table,
                    currentColumn: table.venteId,
                    referencedTable: $$DettesTableReferences._venteIdTable(db),
                    referencedColumn:
                        $$DettesTableReferences._venteIdTable(db).id,
                  ) as T;
                }

                return state;
              },
              getPrefetchedDataCallback: (items) async {
                return [
                  if (paiementsRefs)
                    await $_getPrefetchedData<Dette, $DettesTable, Paiement>(
                        currentTable: table,
                        referencedTable:
                            $$DettesTableReferences._paiementsRefsTable(db),
                        managerFromTypedResult: (p0) =>
                            $$DettesTableReferences(db, table, p0)
                                .paiementsRefs,
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

typedef $$DettesTableProcessedTableManager = ProcessedTableManager<
    _$AppDatabase,
    $DettesTable,
    Dette,
    $$DettesTableFilterComposer,
    $$DettesTableOrderingComposer,
    $$DettesTableAnnotationComposer,
    $$DettesTableCreateCompanionBuilder,
    $$DettesTableUpdateCompanionBuilder,
    (Dette, $$DettesTableReferences),
    Dette,
    PrefetchHooks Function({bool clientId, bool venteId, bool paiementsRefs})>;
typedef $$PaiementsTableCreateCompanionBuilder = PaiementsCompanion Function({
  required String id,
  required String detteId,
  required String boutiqueId,
  required int montant,
  Value<String> modePaiement,
  Value<bool> synced,
  Value<DateTime> date,
  Value<int> rowid,
});
typedef $$PaiementsTableUpdateCompanionBuilder = PaiementsCompanion Function({
  Value<String> id,
  Value<String> detteId,
  Value<String> boutiqueId,
  Value<int> montant,
  Value<String> modePaiement,
  Value<bool> synced,
  Value<DateTime> date,
  Value<int> rowid,
});

final class $$PaiementsTableReferences
    extends BaseReferences<_$AppDatabase, $PaiementsTable, Paiement> {
  $$PaiementsTableReferences(super.$_db, super.$_table, super.$_typedResult);

  static $DettesTable _detteIdTable(_$AppDatabase db) => db.dettes
      .createAlias($_aliasNameGenerator(db.paiements.detteId, db.dettes.id));

  $$DettesTableProcessedTableManager get detteId {
    final $_column = $_itemColumn<String>('dette_id')!;

    final manager = $$DettesTableTableManager($_db, $_db.dettes)
        .filter((f) => f.id.sqlEquals($_column));
    final item = $_typedResult.readTableOrNull(_detteIdTable($_db));
    if (item == null) return manager;
    return ProcessedTableManager(
        manager.$state.copyWith(prefetchedData: [item]));
  }
}

class $$PaiementsTableFilterComposer
    extends Composer<_$AppDatabase, $PaiementsTable> {
  $$PaiementsTableFilterComposer({
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

  ColumnFilters<int> get montant => $composableBuilder(
      column: $table.montant, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get modePaiement => $composableBuilder(
      column: $table.modePaiement, builder: (column) => ColumnFilters(column));

  ColumnFilters<bool> get synced => $composableBuilder(
      column: $table.synced, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get date => $composableBuilder(
      column: $table.date, builder: (column) => ColumnFilters(column));

  $$DettesTableFilterComposer get detteId {
    final $$DettesTableFilterComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.detteId,
        referencedTable: $db.dettes,
        getReferencedColumn: (t) => t.id,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$DettesTableFilterComposer(
              $db: $db,
              $table: $db.dettes,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return composer;
  }
}

class $$PaiementsTableOrderingComposer
    extends Composer<_$AppDatabase, $PaiementsTable> {
  $$PaiementsTableOrderingComposer({
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

  ColumnOrderings<int> get montant => $composableBuilder(
      column: $table.montant, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get modePaiement => $composableBuilder(
      column: $table.modePaiement,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<bool> get synced => $composableBuilder(
      column: $table.synced, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get date => $composableBuilder(
      column: $table.date, builder: (column) => ColumnOrderings(column));

  $$DettesTableOrderingComposer get detteId {
    final $$DettesTableOrderingComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.detteId,
        referencedTable: $db.dettes,
        getReferencedColumn: (t) => t.id,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$DettesTableOrderingComposer(
              $db: $db,
              $table: $db.dettes,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return composer;
  }
}

class $$PaiementsTableAnnotationComposer
    extends Composer<_$AppDatabase, $PaiementsTable> {
  $$PaiementsTableAnnotationComposer({
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

  GeneratedColumn<int> get montant =>
      $composableBuilder(column: $table.montant, builder: (column) => column);

  GeneratedColumn<String> get modePaiement => $composableBuilder(
      column: $table.modePaiement, builder: (column) => column);

  GeneratedColumn<bool> get synced =>
      $composableBuilder(column: $table.synced, builder: (column) => column);

  GeneratedColumn<DateTime> get date =>
      $composableBuilder(column: $table.date, builder: (column) => column);

  $$DettesTableAnnotationComposer get detteId {
    final $$DettesTableAnnotationComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.detteId,
        referencedTable: $db.dettes,
        getReferencedColumn: (t) => t.id,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$DettesTableAnnotationComposer(
              $db: $db,
              $table: $db.dettes,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return composer;
  }
}

class $$PaiementsTableTableManager extends RootTableManager<
    _$AppDatabase,
    $PaiementsTable,
    Paiement,
    $$PaiementsTableFilterComposer,
    $$PaiementsTableOrderingComposer,
    $$PaiementsTableAnnotationComposer,
    $$PaiementsTableCreateCompanionBuilder,
    $$PaiementsTableUpdateCompanionBuilder,
    (Paiement, $$PaiementsTableReferences),
    Paiement,
    PrefetchHooks Function({bool detteId})> {
  $$PaiementsTableTableManager(_$AppDatabase db, $PaiementsTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$PaiementsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$PaiementsTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$PaiementsTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback: ({
            Value<String> id = const Value.absent(),
            Value<String> detteId = const Value.absent(),
            Value<String> boutiqueId = const Value.absent(),
            Value<int> montant = const Value.absent(),
            Value<String> modePaiement = const Value.absent(),
            Value<bool> synced = const Value.absent(),
            Value<DateTime> date = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              PaiementsCompanion(
            id: id,
            detteId: detteId,
            boutiqueId: boutiqueId,
            montant: montant,
            modePaiement: modePaiement,
            synced: synced,
            date: date,
            rowid: rowid,
          ),
          createCompanionCallback: ({
            required String id,
            required String detteId,
            required String boutiqueId,
            required int montant,
            Value<String> modePaiement = const Value.absent(),
            Value<bool> synced = const Value.absent(),
            Value<DateTime> date = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              PaiementsCompanion.insert(
            id: id,
            detteId: detteId,
            boutiqueId: boutiqueId,
            montant: montant,
            modePaiement: modePaiement,
            synced: synced,
            date: date,
            rowid: rowid,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (
                    e.readTable(table),
                    $$PaiementsTableReferences(db, table, e)
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
                        $$PaiementsTableReferences._detteIdTable(db),
                    referencedColumn:
                        $$PaiementsTableReferences._detteIdTable(db).id,
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

typedef $$PaiementsTableProcessedTableManager = ProcessedTableManager<
    _$AppDatabase,
    $PaiementsTable,
    Paiement,
    $$PaiementsTableFilterComposer,
    $$PaiementsTableOrderingComposer,
    $$PaiementsTableAnnotationComposer,
    $$PaiementsTableCreateCompanionBuilder,
    $$PaiementsTableUpdateCompanionBuilder,
    (Paiement, $$PaiementsTableReferences),
    Paiement,
    PrefetchHooks Function({bool detteId})>;
typedef $$SyncQueueTableCreateCompanionBuilder = SyncQueueCompanion Function({
  required String id,
  required String targetTable,
  required String recordId,
  required String operation,
  required String payload,
  Value<int> retryCount,
  Value<DateTime> createdAt,
  Value<int> rowid,
});
typedef $$SyncQueueTableUpdateCompanionBuilder = SyncQueueCompanion Function({
  Value<String> id,
  Value<String> targetTable,
  Value<String> recordId,
  Value<String> operation,
  Value<String> payload,
  Value<int> retryCount,
  Value<DateTime> createdAt,
  Value<int> rowid,
});

class $$SyncQueueTableFilterComposer
    extends Composer<_$AppDatabase, $SyncQueueTable> {
  $$SyncQueueTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get targetTable => $composableBuilder(
      column: $table.targetTable, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get recordId => $composableBuilder(
      column: $table.recordId, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get operation => $composableBuilder(
      column: $table.operation, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get payload => $composableBuilder(
      column: $table.payload, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get retryCount => $composableBuilder(
      column: $table.retryCount, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnFilters(column));
}

class $$SyncQueueTableOrderingComposer
    extends Composer<_$AppDatabase, $SyncQueueTable> {
  $$SyncQueueTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get targetTable => $composableBuilder(
      column: $table.targetTable, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get recordId => $composableBuilder(
      column: $table.recordId, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get operation => $composableBuilder(
      column: $table.operation, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get payload => $composableBuilder(
      column: $table.payload, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get retryCount => $composableBuilder(
      column: $table.retryCount, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get createdAt => $composableBuilder(
      column: $table.createdAt, builder: (column) => ColumnOrderings(column));
}

class $$SyncQueueTableAnnotationComposer
    extends Composer<_$AppDatabase, $SyncQueueTable> {
  $$SyncQueueTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get targetTable => $composableBuilder(
      column: $table.targetTable, builder: (column) => column);

  GeneratedColumn<String> get recordId =>
      $composableBuilder(column: $table.recordId, builder: (column) => column);

  GeneratedColumn<String> get operation =>
      $composableBuilder(column: $table.operation, builder: (column) => column);

  GeneratedColumn<String> get payload =>
      $composableBuilder(column: $table.payload, builder: (column) => column);

  GeneratedColumn<int> get retryCount => $composableBuilder(
      column: $table.retryCount, builder: (column) => column);

  GeneratedColumn<DateTime> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);
}

class $$SyncQueueTableTableManager extends RootTableManager<
    _$AppDatabase,
    $SyncQueueTable,
    SyncQueueData,
    $$SyncQueueTableFilterComposer,
    $$SyncQueueTableOrderingComposer,
    $$SyncQueueTableAnnotationComposer,
    $$SyncQueueTableCreateCompanionBuilder,
    $$SyncQueueTableUpdateCompanionBuilder,
    (
      SyncQueueData,
      BaseReferences<_$AppDatabase, $SyncQueueTable, SyncQueueData>
    ),
    SyncQueueData,
    PrefetchHooks Function()> {
  $$SyncQueueTableTableManager(_$AppDatabase db, $SyncQueueTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$SyncQueueTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$SyncQueueTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$SyncQueueTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback: ({
            Value<String> id = const Value.absent(),
            Value<String> targetTable = const Value.absent(),
            Value<String> recordId = const Value.absent(),
            Value<String> operation = const Value.absent(),
            Value<String> payload = const Value.absent(),
            Value<int> retryCount = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              SyncQueueCompanion(
            id: id,
            targetTable: targetTable,
            recordId: recordId,
            operation: operation,
            payload: payload,
            retryCount: retryCount,
            createdAt: createdAt,
            rowid: rowid,
          ),
          createCompanionCallback: ({
            required String id,
            required String targetTable,
            required String recordId,
            required String operation,
            required String payload,
            Value<int> retryCount = const Value.absent(),
            Value<DateTime> createdAt = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              SyncQueueCompanion.insert(
            id: id,
            targetTable: targetTable,
            recordId: recordId,
            operation: operation,
            payload: payload,
            retryCount: retryCount,
            createdAt: createdAt,
            rowid: rowid,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ));
}

typedef $$SyncQueueTableProcessedTableManager = ProcessedTableManager<
    _$AppDatabase,
    $SyncQueueTable,
    SyncQueueData,
    $$SyncQueueTableFilterComposer,
    $$SyncQueueTableOrderingComposer,
    $$SyncQueueTableAnnotationComposer,
    $$SyncQueueTableCreateCompanionBuilder,
    $$SyncQueueTableUpdateCompanionBuilder,
    (
      SyncQueueData,
      BaseReferences<_$AppDatabase, $SyncQueueTable, SyncQueueData>
    ),
    SyncQueueData,
    PrefetchHooks Function()>;
typedef $$AbonnementsTableCreateCompanionBuilder = AbonnementsCompanion
    Function({
  required String id,
  required String boutiqueId,
  Value<String> plan,
  Value<String> statut,
  Value<String?> modePaiement,
  Value<int> montant,
  Value<DateTime> dateDebut,
  Value<DateTime?> dateFin,
  Value<bool> synced,
  Value<int> rowid,
});
typedef $$AbonnementsTableUpdateCompanionBuilder = AbonnementsCompanion
    Function({
  Value<String> id,
  Value<String> boutiqueId,
  Value<String> plan,
  Value<String> statut,
  Value<String?> modePaiement,
  Value<int> montant,
  Value<DateTime> dateDebut,
  Value<DateTime?> dateFin,
  Value<bool> synced,
  Value<int> rowid,
});

final class $$AbonnementsTableReferences
    extends BaseReferences<_$AppDatabase, $AbonnementsTable, Abonnement> {
  $$AbonnementsTableReferences(super.$_db, super.$_table, super.$_typedResult);

  static $BoutiquesTable _boutiqueIdTable(_$AppDatabase db) =>
      db.boutiques.createAlias(
          $_aliasNameGenerator(db.abonnements.boutiqueId, db.boutiques.id));

  $$BoutiquesTableProcessedTableManager get boutiqueId {
    final $_column = $_itemColumn<String>('boutique_id')!;

    final manager = $$BoutiquesTableTableManager($_db, $_db.boutiques)
        .filter((f) => f.id.sqlEquals($_column));
    final item = $_typedResult.readTableOrNull(_boutiqueIdTable($_db));
    if (item == null) return manager;
    return ProcessedTableManager(
        manager.$state.copyWith(prefetchedData: [item]));
  }
}

class $$AbonnementsTableFilterComposer
    extends Composer<_$AppDatabase, $AbonnementsTable> {
  $$AbonnementsTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get plan => $composableBuilder(
      column: $table.plan, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get statut => $composableBuilder(
      column: $table.statut, builder: (column) => ColumnFilters(column));

  ColumnFilters<String> get modePaiement => $composableBuilder(
      column: $table.modePaiement, builder: (column) => ColumnFilters(column));

  ColumnFilters<int> get montant => $composableBuilder(
      column: $table.montant, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get dateDebut => $composableBuilder(
      column: $table.dateDebut, builder: (column) => ColumnFilters(column));

  ColumnFilters<DateTime> get dateFin => $composableBuilder(
      column: $table.dateFin, builder: (column) => ColumnFilters(column));

  ColumnFilters<bool> get synced => $composableBuilder(
      column: $table.synced, builder: (column) => ColumnFilters(column));

  $$BoutiquesTableFilterComposer get boutiqueId {
    final $$BoutiquesTableFilterComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.boutiqueId,
        referencedTable: $db.boutiques,
        getReferencedColumn: (t) => t.id,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$BoutiquesTableFilterComposer(
              $db: $db,
              $table: $db.boutiques,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return composer;
  }
}

class $$AbonnementsTableOrderingComposer
    extends Composer<_$AppDatabase, $AbonnementsTable> {
  $$AbonnementsTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get id => $composableBuilder(
      column: $table.id, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get plan => $composableBuilder(
      column: $table.plan, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get statut => $composableBuilder(
      column: $table.statut, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<String> get modePaiement => $composableBuilder(
      column: $table.modePaiement,
      builder: (column) => ColumnOrderings(column));

  ColumnOrderings<int> get montant => $composableBuilder(
      column: $table.montant, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get dateDebut => $composableBuilder(
      column: $table.dateDebut, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<DateTime> get dateFin => $composableBuilder(
      column: $table.dateFin, builder: (column) => ColumnOrderings(column));

  ColumnOrderings<bool> get synced => $composableBuilder(
      column: $table.synced, builder: (column) => ColumnOrderings(column));

  $$BoutiquesTableOrderingComposer get boutiqueId {
    final $$BoutiquesTableOrderingComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.boutiqueId,
        referencedTable: $db.boutiques,
        getReferencedColumn: (t) => t.id,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$BoutiquesTableOrderingComposer(
              $db: $db,
              $table: $db.boutiques,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return composer;
  }
}

class $$AbonnementsTableAnnotationComposer
    extends Composer<_$AppDatabase, $AbonnementsTable> {
  $$AbonnementsTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get plan =>
      $composableBuilder(column: $table.plan, builder: (column) => column);

  GeneratedColumn<String> get statut =>
      $composableBuilder(column: $table.statut, builder: (column) => column);

  GeneratedColumn<String> get modePaiement => $composableBuilder(
      column: $table.modePaiement, builder: (column) => column);

  GeneratedColumn<int> get montant =>
      $composableBuilder(column: $table.montant, builder: (column) => column);

  GeneratedColumn<DateTime> get dateDebut =>
      $composableBuilder(column: $table.dateDebut, builder: (column) => column);

  GeneratedColumn<DateTime> get dateFin =>
      $composableBuilder(column: $table.dateFin, builder: (column) => column);

  GeneratedColumn<bool> get synced =>
      $composableBuilder(column: $table.synced, builder: (column) => column);

  $$BoutiquesTableAnnotationComposer get boutiqueId {
    final $$BoutiquesTableAnnotationComposer composer = $composerBuilder(
        composer: this,
        getCurrentColumn: (t) => t.boutiqueId,
        referencedTable: $db.boutiques,
        getReferencedColumn: (t) => t.id,
        builder: (joinBuilder,
                {$addJoinBuilderToRootComposer,
                $removeJoinBuilderFromRootComposer}) =>
            $$BoutiquesTableAnnotationComposer(
              $db: $db,
              $table: $db.boutiques,
              $addJoinBuilderToRootComposer: $addJoinBuilderToRootComposer,
              joinBuilder: joinBuilder,
              $removeJoinBuilderFromRootComposer:
                  $removeJoinBuilderFromRootComposer,
            ));
    return composer;
  }
}

class $$AbonnementsTableTableManager extends RootTableManager<
    _$AppDatabase,
    $AbonnementsTable,
    Abonnement,
    $$AbonnementsTableFilterComposer,
    $$AbonnementsTableOrderingComposer,
    $$AbonnementsTableAnnotationComposer,
    $$AbonnementsTableCreateCompanionBuilder,
    $$AbonnementsTableUpdateCompanionBuilder,
    (Abonnement, $$AbonnementsTableReferences),
    Abonnement,
    PrefetchHooks Function({bool boutiqueId})> {
  $$AbonnementsTableTableManager(_$AppDatabase db, $AbonnementsTable table)
      : super(TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$AbonnementsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$AbonnementsTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$AbonnementsTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback: ({
            Value<String> id = const Value.absent(),
            Value<String> boutiqueId = const Value.absent(),
            Value<String> plan = const Value.absent(),
            Value<String> statut = const Value.absent(),
            Value<String?> modePaiement = const Value.absent(),
            Value<int> montant = const Value.absent(),
            Value<DateTime> dateDebut = const Value.absent(),
            Value<DateTime?> dateFin = const Value.absent(),
            Value<bool> synced = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              AbonnementsCompanion(
            id: id,
            boutiqueId: boutiqueId,
            plan: plan,
            statut: statut,
            modePaiement: modePaiement,
            montant: montant,
            dateDebut: dateDebut,
            dateFin: dateFin,
            synced: synced,
            rowid: rowid,
          ),
          createCompanionCallback: ({
            required String id,
            required String boutiqueId,
            Value<String> plan = const Value.absent(),
            Value<String> statut = const Value.absent(),
            Value<String?> modePaiement = const Value.absent(),
            Value<int> montant = const Value.absent(),
            Value<DateTime> dateDebut = const Value.absent(),
            Value<DateTime?> dateFin = const Value.absent(),
            Value<bool> synced = const Value.absent(),
            Value<int> rowid = const Value.absent(),
          }) =>
              AbonnementsCompanion.insert(
            id: id,
            boutiqueId: boutiqueId,
            plan: plan,
            statut: statut,
            modePaiement: modePaiement,
            montant: montant,
            dateDebut: dateDebut,
            dateFin: dateFin,
            synced: synced,
            rowid: rowid,
          ),
          withReferenceMapper: (p0) => p0
              .map((e) => (
                    e.readTable(table),
                    $$AbonnementsTableReferences(db, table, e)
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
                    referencedTable:
                        $$AbonnementsTableReferences._boutiqueIdTable(db),
                    referencedColumn:
                        $$AbonnementsTableReferences._boutiqueIdTable(db).id,
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

typedef $$AbonnementsTableProcessedTableManager = ProcessedTableManager<
    _$AppDatabase,
    $AbonnementsTable,
    Abonnement,
    $$AbonnementsTableFilterComposer,
    $$AbonnementsTableOrderingComposer,
    $$AbonnementsTableAnnotationComposer,
    $$AbonnementsTableCreateCompanionBuilder,
    $$AbonnementsTableUpdateCompanionBuilder,
    (Abonnement, $$AbonnementsTableReferences),
    Abonnement,
    PrefetchHooks Function({bool boutiqueId})>;

class $AppDatabaseManager {
  final _$AppDatabase _db;
  $AppDatabaseManager(this._db);
  $$BoutiquesTableTableManager get boutiques =>
      $$BoutiquesTableTableManager(_db, _db.boutiques);
  $$UtilisateursTableTableManager get utilisateurs =>
      $$UtilisateursTableTableManager(_db, _db.utilisateurs);
  $$ProduitsTableTableManager get produits =>
      $$ProduitsTableTableManager(_db, _db.produits);
  $$ClientsTableTableManager get clients =>
      $$ClientsTableTableManager(_db, _db.clients);
  $$VentesTableTableManager get ventes =>
      $$VentesTableTableManager(_db, _db.ventes);
  $$DettesTableTableManager get dettes =>
      $$DettesTableTableManager(_db, _db.dettes);
  $$PaiementsTableTableManager get paiements =>
      $$PaiementsTableTableManager(_db, _db.paiements);
  $$SyncQueueTableTableManager get syncQueue =>
      $$SyncQueueTableTableManager(_db, _db.syncQueue);
  $$AbonnementsTableTableManager get abonnements =>
      $$AbonnementsTableTableManager(_db, _db.abonnements);
}
