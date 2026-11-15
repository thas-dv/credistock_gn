# -*- coding: utf-8 -*-
"""Studio Voix Mindset 24 — un champ de texte, un choix de voix, un fichier MP3.
Moteurs : Chatterbox Multilingual (clonage, émotions, licence MIT) et Piper (rapide, voix libres Tom / Pierre)."""
import os, re, subprocess, tarfile, urllib.request, datetime, numpy as np, gradio as gr

ICI = os.path.dirname(os.path.abspath(__file__)); VOIX = os.path.join(ICI, "voix"); os.makedirs(VOIX, exist_ok=True)
_CB = None
def chatterbox():
    global _CB
    if _CB is None:
        import torch
        from chatterbox.mtl_tts import ChatterboxMultilingualTTS
        _CB = ChatterboxMultilingualTTS.from_pretrained(device="cuda" if torch.cuda.is_available() else "cpu")
    return _CB

PIPER = {"Tom (rapide)": ("fr_FR-tom-medium", None), "Pierre (rapide)": ("fr_FR-upmc-medium", 1)}
def piper_model(nom):
    m, _ = PIPER[nom]; d = os.path.join(ICI, f"vits-piper-{m}")
    if not os.path.isdir(d):
        url = f"https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-{m}.tar.bz2"
        p, _ = urllib.request.urlretrieve(url); tarfile.open(p).extractall(ICI)
    return os.path.join(d, f"{m}.onnx")

def voix_clonees():
    return sorted(f[:-4] for f in os.listdir(VOIX) if f.endswith(".wav"))
def choix():
    return list(PIPER) + [f"{v} (clonée)" for v in voix_clonees()]

EMO = {"calme": (0.35, 0.6), "intense": (0.75, 0.4), "cri": (1.1, 0.3), "": (0.5, 0.5)}

def generer(texte, voix, vitesse, prog=gr.Progress()):
    texte = (texte or "").strip()
    if not texte: raise gr.Error("Écris un texte.")
    out = f"/tmp/voix_{datetime.datetime.now():%Y%m%d_%H%M%S}.mp3"
    if voix in PIPER:
        onnx = piper_model(voix); sid = PIPER[voix][1]
        propre = re.sub(r"\[(\w+)\]\s*", "", texte)
        cmd = ["python3", "-m", "piper", "-m", onnx, "-f", "/tmp/brut.wav"] + (["-s", str(sid)] if sid is not None else [])
        subprocess.run(cmd, input=propre.encode(), check=True)
        sr_in = "/tmp/brut.wav"
    else:
        m = chatterbox(); ref = os.path.join(VOIX, voix.replace(" (clonée)", "") + ".wav")
        lignes = [l.strip() for l in texte.split("\n")]
        parts = []; sil = lambda s: np.zeros(int(m.sr * s), dtype=np.float32)
        for i, l in enumerate(prog.tqdm(lignes, desc="Génération")):
            if not l: parts.append(sil(0.6)); continue
            mm = re.match(r"\[(\w+)\]\s*(.*)", l); emo, t = (mm.group(1).lower(), mm.group(2)) if mm else ("", l)
            ex, cfg = EMO.get(emo, EMO[""])
            for phrase in re.findall(r"[^.!?…]+[.!?…]*", t):   # phrases courtes = meilleure qualité
                if phrase.strip():
                    w = m.generate(phrase.strip(), language_id="fr", audio_prompt_path=ref, exaggeration=ex, cfg_weight=cfg)
                    parts += [w.squeeze(0).cpu().numpy(), sil(0.2)]
        import soundfile as sf
        sf.write("/tmp/brut.wav", np.concatenate(parts), m.sr); sr_in = "/tmp/brut.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", sr_in, "-af", f"atempo={vitesse},loudnorm=I=-14", "-b:a", "192k", out], check=True)
    return out, out

def ajouter(nom, fichier, accord):
    if not accord: raise gr.Error("Coche la case : la voix doit être libre de droits pour le clonage, ou la personne doit avoir donné son accord.")
    if not fichier or not (nom or "").strip(): raise gr.Error("Donne un nom et un extrait audio (10 à 30 s, sans musique).")
    nom = re.sub(r"[^\w-]", "_", nom.strip())
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", fichier, "-ac", "1", "-ar", "24000", "-t", "30", os.path.join(VOIX, nom + ".wav")], check=True)
    return gr.update(choices=choix(), value=f"{nom} (clonée)"), f"✅ Voix « {nom} » ajoutée."

with gr.Blocks(title="Studio Voix Mindset 24") as app:
    gr.Markdown("# 🎙️ Studio Voix Mindset 24\nÉcris ton texte, choisis la voix, clique sur **Générer**. "
                "Émotions possibles en début de ligne : `[calme]`, `[intense]`, `[cri]`. Une ligne vide = un silence.")
    with gr.Row():
        with gr.Column(scale=3):
            texte = gr.Textbox(label="Texte", lines=12, placeholder="[calme] Personne ne croyait en lui.\n\n[cri] ALORS MONTRE-LEUR QUI TU ES !")
            with gr.Row():
                voix = gr.Dropdown(choix(), value=choix()[0], label="Voix")
                vitesse = gr.Slider(0.8, 1.3, 1.0, step=0.01, label="Vitesse")
            bouton = gr.Button("🎧 Générer", variant="primary")
            audio = gr.Audio(label="Résultat", type="filepath"); fichier = gr.File(label="Télécharger le MP3")
        with gr.Column(scale=2):
            gr.Markdown("### ➕ Ajouter une voix\nExtrait propre de 10 à 30 s, une seule personne, sans musique.")
            nom = gr.Textbox(label="Nom de la voix"); ext = gr.Audio(label="Extrait", type="filepath", sources=["upload", "microphone"])
            accord = gr.Checkbox(label="Cette voix est sous licence libre qui autorise le clonage, ou la personne a donné son accord (pas de voix d'un site payant ni d'un comédien sans accord).")
            ajout = gr.Button("Ajouter la voix"); msg = gr.Markdown()
    bouton.click(generer, [texte, voix, vitesse], [audio, fichier])
    ajout.click(ajouter, [nom, ext, accord], [voix, msg])

if __name__ == "__main__":
    app.queue().launch(server_name="0.0.0.0")
