# Pipeline quotidien Mindset 24 — mode d'emploi pour la tâche planifiée

Style validé : hologramme blanc (corps anatomique maillé + squelette visible, étoiles qui jaillissent,
sol quadrillé blanc), voix ElevenLabs « Sid » (voice_id V8kvppYJoYqSL61Tr8Dn, modèle eleven_v4),
texte agressif, question finale qui pousse à commenter, slogan « Mindset 24. Change ton mental. Change ta vie. »,
logo MINDSET 24 doré. Vidéo publiée à 20h30 (Africa/Conakry) sur TikTok @mindset24officiel via Metricool (blogId 7642566).

## Structure fixe en 11 temps (une scène 3D par temps — garder cet ordre)
1. stairs   : accroche « Le plus grand mensonge sur … » ([chuckles] au début)      rôle hook = mot choc
2. dice     : la fausse croyance (chance, talent, moment parfait…)
3. chair    : « Réveille-toi » + quelqu'un qui reste assis / attend
4. room     : « Regarde … autour de toi » (enfermement)
5. words    : 3 ennemis -> 3 MOTS 3D qui tombent (words3d, 1 mot court chacun, ≤ 9 lettres idéalement)
6. build    : « c'est toi qui les as construits … brique par brique »          build_start, build_end
7. explode  : ordre de détruire, crié ([shouting])                              boom = le mot crié
8. gates    : une action par jour / un mur à la fois / sans excuse              gate1, gate2
9. sunrise  : la percée (« Et un matin… … ton potentiel »)                      sunrise, arms_up
10. question: [intense] question en commentaire + menace d'abandon             q_line1, q_line2, q_cta, q_end
11. logo    : [serious] Mindset 24. Change ton mental. Change ta vie.           brand, slogan1, slogan2
Durée visée : 61–75 s (PLUS d'1 minute : seules ces vidéos comptent pour le Programme de récompenses des créateurs TikTok ; accroche forte dans les 3 premières secondes pour garder la rétention). Si la voix fait < 61 s, ajouter une phrase à l'histoire plutôt que ralentir. Changer CHAQUE JOUR le sujet (voir HISTORIQUE.md pour ne pas répéter),
les 3 mots, la question et la légende. Niche : réveiller son potentiel, identifier ce qui bloque,
prendre ses responsabilités, confiance, discipline. Ne jamais mentionner de vente du PDF.

## Calendrier hebdomadaire (décision utilisateur du 31/10/2026)
- Lundi -> samedi : une NOUVELLE vraie histoire (format qui marche : un seul personnage, accroche = un jugement qu'on a tous reçu, décor concret, question chiffrée « sur 10 »).
- DIMANCHE : vidéo RÉCAPITULATIVE de la semaine, ton SÉRIEUX et argumenté : « quelles leçons tirer de ces personnes qui se sont relevées ».
  • Reprendre UNIQUEMENT les faits déjà vérifiés dans HISTORIQUE.md (aucun fait nouveau non vérifié, aucune citation).
  • ATTENTION enseignement 7 (compilation du 26/10 = 277 vues, 0 comm.) : ce n'est PAS une liste de célébrités. C'est UN fil : une accroche universelle,
    puis chaque histoire en 1 flash = 1 LEÇON en un mot (ex. TROP TARD ? / REFUSÉ / TROP LOIN / TROP FRÊLE / RECALÉ), puis la règle commune
    qui s'adresse au spectateur (« personne ne croyait en eux au départ… ils ont refusé d'arrêter »).
  • Décor propre au dimanche, différent des histoires (ex. tableau noir de vestiaire / salle tactique où les 5 leçons s'écrivent à la craie).
  • Question en un chiffre : « Laquelle de ces leçons tu appliques dès demain ? Écris son numéro » ou une note sur 10 ; 61–75 s ; mêmes règles de conformité
    (noms dits à l'oral seulement, jamais à l'écran ni en hashtag).
  • 1er récap : dimanche 01/11/2026 = Drogba (27/10), Stephen King (28/10), Salah (29/10), Mahrez (30/10), Guirassy (31/10).

## Idées de sujets proposées par la communauté (à piocher lundi -> samedi)
- Antoine Semenyo (Ghana) — suggéré en commentaire le 31/10. Faits vérifiés (Wikipédia + premierleague.com) : né le 7/1/2000 à Londres ; recalé par Arsenal, Tottenham, Fulham, Millwall,
  puis par Crystal Palace à 15 ans après 8 semaines d'essai -> il arrête le foot environ un an ; reprend dans un programme foot d'un lycée/college à 160 km de chez lui ;
  académie de Bristol City à 17 ans (2017), pro à 18 ans (janv. 2018) ; prêts Bath City (6e division), Newport (4e div.), Sunderland (3e div., 0 but) ;
  Bournemouth janv. 2023 (≈ 10 M£, 23 ans) ; 8 puis 11 buts en championnat ; Man City 9/1/2026 (≈ 64 M£) ; international ghanéen depuis 2022.
  NE PAS évoquer sa blessure au genou d'octobre 2026 (santé = interdit). Accroche possible : « On t'a fermé toutes les portes ? ». Question « sur 10 ».

## Conformité TikTok
Lire et appliquer CONFORMITE.md à chaque vidéo (sujet, texte, légende, hashtags) — compte monétisé.

## Étapes
1. `git clone --depth 1 -b mindset24-pipeline https://github.com/thas-dv/credistock_gn pipeline` (demander l'accès push
   avec l'outil add_repo owner=thas-dv repo=credistock_gn access=push).
2. Écrire `story.json` (copier la structure de l'exemple : voice_prompt, caption, pinned_comment, scenes[].at,
   roles, words3d, q_pulses, punches, keywords, question{lines, highlight, cta}). Les `at`/rôles désignent
   un mot prononcé ([mot, n-ième occurrence]) — utiliser des mots qui apparaissent exactement dans le texte.
3. Voix : creative_generate_speech (voice_id Sid, eleven_v4, prompt = voice_prompt). Choisir la meilleure prise,
   la télécharger en `voix.mp3`.
4. Horodatage : creative_add_flow_asset_node (generation_id de la prise, même flow) puis creative_transcribe_audio
   (eleven_scribe_v1) ; télécharger `words_download_url` en `words.json`.
5. `./make_video.sh AAAAMMJJ` (~10–15 min) puis contrôler quelques images (ffmpeg -ss … -frames:v 1).
6. ENVOYER la vidéo à l'utilisateur (SendUserFile) + message (SendUserMessage) : thème, texte, légende,
   commentaire à épingler, et demander « publie » ou des corrections. NE RIEN PROGRAMMER AVANT SON ACCORD.
7. Corrections demandées -> modifier story/voix/rendu, renvoyer, redemander.
8. Accord reçu -> pousser la vidéo sur la branche `mindset24-videos` (fichier mindset24_AAAAMMJJ.mp4) ;
   lien public : https://raw.githubusercontent.com/thas-dv/credistock_gn/mindset24-videos/mindset24_AAAAMMJJ.mp4
   -> Metricool createScheduledPost (blogId 7642566, provider tiktok, autoPublish true, date du jour 20:30
   Africa/Conakry, tiktokData.title = légende, isAigc FALSE — ne pas cocher « Contenu généré par IA », demandé par l utilisateur —, privacyOption PUBLIC_TO_EVERYONE).
   Si 20h30 est déjà passé, demander à l'utilisateur l'heure voulue.
9. Ajouter une ligne à HISTORIQUE.md (branche mindset24-pipeline) et pousser.

## Styles visuels (champ "style" de story.json)
- "holo" (défaut, scenes.py + render.py) : hologramme blanc — utilisé le 25/10. Jugé trop répétitif par l'utilisateur.
- "city" (scenes_city.py) : ville néon de nuit bleu/rouge, mannequin blanc. Types : skyline loading busstop eye neon chains snap lasers dawn phoneq logo.
- "doc" (render_doc.py, 2D) : dossiers/archives, tampons rouges, or, grain — VALIDÉ le 26/10 (exemple : story_2026-10-26_doc.json).
  Types : hook musk ma mane stamps graph slam wins you question logo ; "marks" = temps de mots nommés utilisés par les scènes.
  Les scènes musk/ma/mane sont propres à cette histoire : pour un autre sujet, écrire de nouvelles fonctions de scène.
Retour utilisateur (26/10) : changer d'ENVIRONNEMENT et d'ANGLE à chaque vidéo (ne pas refaire la même ambiance que la veille) ;
il aime les EXEMPLES CONCRETS de vraies personnes qui ont échoué puis réussi, pour que le spectateur se reconnaisse dans la situation.
Vérifier les faits sur les personnes réelles avant d'écrire le texte.
- "stade" (render_stade.py, 2D) : stade de nuit, joueur n°11 en silhouette (maillot orange), orange/blanc/vert — VALIDÉ le 27/10
  (exemple : story_2026-10-27_stade.json, histoire de Didier Drogba — ATTENTION : ses hashtags avec nom propre (#drogba) sont INTERDITS, voir CONFORMITE.md). Types : hook exil lemans stamps slam rise chelsea final you question logo.
  Les scènes exil/lemans/rise/chelsea/final sont propres à cette histoire : pour un autre sportif, écrire de nouvelles fonctions de scène.
Retour utilisateur (27/10) : raconter une VRAIE histoire d'une célébrité très connue, du début à la fin (situation bloquée -> refus d'abandonner -> réussite),
et CHANGER DE PERSONNAGE à chaque vidéo (le mannequin hologramme a été jugé trop répétitif).
- "ecrivain" (render_ecrivain.py, 2D) : bureau de caravane la nuit, lampe ambrée, machine à écrire, lettres de refus, écrivain en silhouette générique — 28/10
  (exemple : story_2026-10-28_ecrivain.json, histoire de Stephen King). Types : hook letters nail trailer stamps trash slam deal books you question logo.
  Les scènes letters/nail/trailer/trash/deal/books sont propres à cette histoire.
- "route" (render_route.py, 2D) : route de nuit dans le désert (étoiles, dunes, palmiers) qui passe à l'aube orange, bus, banc, joueur en silhouette
  générique (maillot rouge, sans numéro) — 29/10 (exemple : story_2026-10-29_route.json, histoire de Mohamed Salah ; aucun club nommé, ni à l'écran ni dans le texte).
  Types : hook village bus bench loan stamps slam rise record trophy legend you question logo (scènes propres à cette histoire sauf stamps/slam/you/question/logo).
- "cite" (render_cite.py, 2D) : quartier d'immeubles la nuit (fenêtres allumées), city-stade en béton grillagé, lampadaires sodium -> projecteurs blancs,
  accents cyan/or, joueur en silhouette générique (maillot bleu, sans numéro), recruteurs en silhouette, pyramide des divisions — 30/10
  (exemple : story_2026-10-30_cite.json, histoire de Riyad Mahrez). Types : hook cite frail quimper havre stamps slam england champion award giant you question logo.
Voix sans crédits ElevenLabs : si le compte ElevenLabs est à court, générer la voix Sid via Speko audio_synthesize
(voice V8kvppYJoYqSL61Tr8Dn, model eleven_v4, allowedProviders elevenlabs ; le modèle servi peut être eleven_v3_conversational),
puis transcrire avec Speko audio_transcribe (word_timestamps true, language fr) et corriger le texte des mots (chiffres écrits en lettres) dans words.json.
