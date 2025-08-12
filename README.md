\# 🧠 Blade v5.1 – Assistant Vocal + IA Adaptative pour Blender 4.5



Blade est un addon ultra-avancé pour Blender, conçu pour permettre le contrôle vocal, l'exécution d'intents intelligents, l'observation passive et la suggestion automatique d'actions.



\## 🚀 Fonctionnalités principales



\### 🎙 Contrôle vocal intelligent

\- Activation du micro

\- Reconnaissance Whisper + fallback Google

\- Exécution d'intents définis dans `voice\_config.yaml`



\### 🔄 Suggestions IA (Codex)

\- Analyse des logs passifs

\- Génération d'intents auto-suggérés

\- Injection dans l'interface pour validation



\### 🌀 Routines adaptatives

\- Historique des actions utilisateur

\- Détection de séquences récurrentes

\- Proposition de "super-intents" personnalisés



\### 📋 Interface Blender complète

\- Panneau vocal principal

\- Suggestions IA

\- Historique des routines

\- Lanceur Codex IA



---



\## 📦 Installation



1\. \*\*Zippez le dossier `ares/`\*\* uniquement :  

&nbsp;  Depuis `blade-v5/`, faites clic droit → compresser `ares/` en `blade-v5.zip`



2\. \*\*Dans Blender\*\* :

&nbsp;  - Menu `Edit > Preferences > Add-ons`

&nbsp;  - `Install...` → sélectionnez `blade-v5.zip`

&nbsp;  - Activez l'addon "Blade AI Control"



3\. ✅ L'addon apparaît dans le panneau latéral `View3D > Blade`



---



\## 📁 Structure



```

ares/

├── core/               # run\_pipeline, intent\_parser...

├── tools/              # exécuteurs, validateurs, trackers

├── ui/                 # tous les panneaux UI

├── bots/               # passive agent, routine tracker

├── codex/              # pipeline IA adaptative

├── config/             # fichiers YAML : voice\_config, suggestions, routines

├── logs/, summary/     # historiques et résumés de sessions

├── voice/              # VoiceEngine + gestion micro

```



---



\## 🔧 Dépendances



Blender 4.5 active les dépendances suivantes automatiquement :

\- `pyyaml`

\- `speechrecognition`

\- `openai` (optionnel)

\- `pyaudio`



---



\## 🛠 Développement \& debug



\- Tous les logs sont visibles dans `Text Editor > blade\_log`

\- Les scripts de test se trouvent dans `tests/`

\- Les prompts IA sont dans `codex\_prompts/`

\- Suggestions non validées : `config/suggestions\_pending.yaml`



---



\## 📍 Version actuelle : `Blade v5.1`



✅ Stable  

✅ Testé en mode `--background`  

✅ Fonctionnel avec UI, suggestions, routines, exécutions vocales et logs intelligents



