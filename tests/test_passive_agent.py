# tests/test_passive_agent.py

"""
Test passif de Blade – Simule des actions dans Blender
Vérifie que PassiveAgent + EditorWatcher capturent des événements
et enregistre un résumé markdown
"""

import bpy
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ares.editor_watcher import register, unregister
from ares.agents.agent_passif import PassiveAgent
from ares.summary.summary_builder import save_session_summary

# 🔁 Initialisation
agent = PassiveAgent()
agent.start()
register()

# 🔧 Création et modification forcée
mesh = bpy.data.meshes.new(name="PassifMesh")
obj = bpy.data.objects.new("Cube_Passif", mesh)
bpy.context.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
obj.location.z += 1.0
obj.name = "Cube_Modifié"

bpy.context.view_layer.update()

# 💬 Fallback manuel pour test garanti
agent.record_action("⚙️ Simulation manuelle : test_passive_agent()")

# 🛑 Clean
unregister()
agent.stop()

# 📋 Affichage console
print("\n=== Historique passif détecté ===")
for act in agent.history:
    print(f" - {act}")

# 📝 Sauvegarde d’un résumé markdown
results = [(act, "observed") for act in agent.history]
save_session_summary(results, session_id="passive_test")
