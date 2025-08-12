\# 🗒️ CHANGELOG – Blade v5.1



\## 🔄 Version 5.1.0 – Août 2025



\### ✅ Nouvelles fonctionnalités majeures

\- \[x] 🎙 Activation automatique du micro (VoiceEngine)

\- \[x] 🧠 Résolution intelligente des intents (ops + context + fallback)

\- \[x] 🌀 Routines IA passives : tracker, suggester, validateur, exécuteur

\- \[x] 📡 Observation depsgraph avec EditorWatcher

\- \[x] 🔁 Exécution d’intents en chaîne depuis YAML (super-intents)

\- \[x] 📋 UI complète avec :

&nbsp; - Panneau vocal principal

&nbsp; - Suggestions IA Codex

&nbsp; - Validation des routines

&nbsp; - Bouton “Régénérer suggestions”



\### 💡 IA adaptative (Codex)

\- \[x] Génération automatique de prompts YAML depuis logs

\- \[x] Suggestions d’intents via parsing `summary/\*.json`

\- \[x] Fusion vers `suggestions\_pending.yaml`

\- \[x] Validation manuelle en UI

\- \[x] Injection dans `voice\_config.yaml`



\### 📁 Organisation \& modules

\- \[x] Structure modulaire `ares/` (tools, core, ui, bots, voice...)

\- \[x] Pipeline exécutable en background

\- \[x] Historique des routines dans `logs/routine\_history.json`

\- \[x] Résumés Markdown générés automatiquement (`summary/`)



\### 🧪 Tests

\- \[x] Script `test\_passive\_agent.py` : simulation d’actions + génération log

\- \[x] Résumés Codex compatibles (`for\_learning/\*.yaml`)



---



\### ✅ Statut : \*\*STABLE – prêt à l’emploi pour Blender 4.5\*\*
