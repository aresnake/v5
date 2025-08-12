# Pipeline vocal – Blade v5

[PIPELINE]
🎤 Phrase utilisateur
   ↓
🧠 intent_parser.py
   ↓
🧩 intent_resolver.py
   ↓
🚀 intent_executor.py
   ↓
🧬 session_log_enricher_bot.py
   ↓
🗂 voice_config_manager.py (enregistrement si besoin)

Chaque étape est modulaire et testable.
Le fallback IA Codex peut intervenir après le parsing si l’intent est inconnu.
