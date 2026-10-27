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
Durée visée : 38–45 s. Changer CHAQUE JOUR le sujet (voir HISTORIQUE.md pour ne pas répéter),
les 3 mots, la question et la légende. Niche : réveiller son potentiel, identifier ce qui bloque,
prendre ses responsabilités, confiance, discipline. Ne jamais mentionner de vente du PDF.

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
  (exemple : story_2026-10-27_stade.json, histoire de Didier Drogba). Types : hook exil lemans stamps slam rise chelsea final you question logo.
  Les scènes exil/lemans/rise/chelsea/final sont propres à cette histoire : pour un autre sportif, écrire de nouvelles fonctions de scène.
Retour utilisateur (27/10) : raconter une VRAIE histoire d'une célébrité très connue, du début à la fin (situation bloquée -> refus d'abandonner -> réussite),
et CHANGER DE PERSONNAGE à chaque vidéo (le mannequin hologramme a été jugé trop répétitif).
Voix sans crédits ElevenLabs : si le compte ElevenLabs est à court, générer la voix Sid via Speko audio_synthesize
(voice V8kvppYJoYqSL61Tr8Dn, model eleven_v4, allowedProviders elevenlabs ; le modèle servi peut être eleven_v3_conversational),
puis transcrire avec Speko audio_transcribe (word_timestamps true, language fr) et corriger le texte des mots (chiffres écrits en lettres) dans words.json.
