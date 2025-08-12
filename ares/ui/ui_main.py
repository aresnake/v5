# ares/ui/ui_main.py

from __future__ import annotations

import bpy

# ---------------------------------------------------------------------------
# Logger paresseux (évite boucles d'import lors du rechargement d'addon)
# ---------------------------------------------------------------------------


def _get_logger():
    try:
        from ares.core.logger import get_logger

        return get_logger("UI_Main")
    except Exception:

        class _L:
            def info(self, *a, **k):
                pass

            def warning(self, *a, **k):
                pass

            def error(self, *a, **k):
                pass

            def exception(self, *a, **k):
                pass

            def debug(self, *a, **k):
                pass

        return _L()


log = _get_logger()


# ---------------------------------------------------------------------------
# VoiceEngine singleton (évite multiples instances après reload)
# ---------------------------------------------------------------------------


def _get_voice_engine_singleton():
    ns = bpy.app.driver_namespace
    inst = ns.get("BLADE_ENGINE")
    if inst is not None:
        return inst
    try:
        from ares.voice.voice_engine import VoiceEngine

        inst = VoiceEngine()
        ns["BLADE_ENGINE"] = inst
        log.info("VoiceEngine singleton créé et stocké dans driver_namespace.")
        return inst
    except Exception as e:
        log.exception(f"VoiceEngine import/init failed: {e}")

        class _Dummy:
            listening = False
            last_transcript = ""

            def start_listening(self):
                pass

            def stop_listening(self):
                pass

            def set_auto_execute(self, *_a, **_k):
                pass

        ns["BLADE_ENGINE"] = _Dummy()
        return ns["BLADE_ENGINE"]


# Instance globale (réutilisable partout)
voice_engine = _get_voice_engine_singleton()


# ---------------------------------------------------------------------------
# Propriétés Scene
# ---------------------------------------------------------------------------


def _ensure_scene_props():
    S = bpy.types.Scene
    if not hasattr(S, "blade_manual_phrase"):
        S.blade_manual_phrase = bpy.props.StringProperty(
            name="Phrase manuelle",
            description="Entrez une phrase vocale manuellement",
            default="",
        )
    if not hasattr(S, "blade_transcript"):
        S.blade_transcript = bpy.props.StringProperty(
            name="Reconnaissance (pré-édition)",
            description="Dernière phrase reconnue (modifiable avant envoi)",
            default="",
        )
    if not hasattr(S, "blade_last_phrase"):
        S.blade_last_phrase = bpy.props.StringProperty(
            name="Dernière phrase exécutée",
            default="",
            options={'SKIP_SAVE'},
        )
    if not hasattr(S, "blade_pending_validation"):
        S.blade_pending_validation = bpy.props.BoolProperty(
            name="Validation en attente",
            default=False,
            options={'SKIP_SAVE'},
        )
    if not hasattr(S, "blade_auto_execute"):
        S.blade_auto_execute = bpy.props.BoolProperty(
            name="Exécuter automatiquement",
            description="Quand activé, la phrase reconnue est exécutée sans validation manuelle",
            default=False,
        )


_ensure_scene_props()


# ---------------------------------------------------------------------------
# OPERATORS
# ---------------------------------------------------------------------------


class BLADE_OT_start_voice(bpy.types.Operator):
    bl_idname = "blade.start_voice"
    bl_label = "Démarrer l’écoute"

    def execute(self, context):
        try:
            engine = _get_voice_engine_singleton()
            if hasattr(engine, "start_listening"):
                engine.start_listening()
                # synchroniser auto_execute avec la prop Scene
                if hasattr(engine, "set_auto_execute"):
                    engine.set_auto_execute(bool(context.scene.blade_auto_execute))
                log.info("UI : Voice engine démarré via bouton.")
                self.report({'INFO'}, "Écoute démarrée.")
            else:
                self.report({'WARNING'}, "VoiceEngine indisponible.")
        except Exception as e:
            log.exception(e)
            self.report({'ERROR'}, f"Erreur : {e}")
        return {'FINISHED'}


class BLADE_OT_stop_voice(bpy.types.Operator):
    bl_idname = "blade.stop_voice"
    bl_label = "Arrêter l’écoute"

    def execute(self, context):
        try:
            engine = _get_voice_engine_singleton()
            if hasattr(engine, "stop_listening"):
                engine.stop_listening()
                log.info("UI : Voice engine arrêté via bouton.")
                self.report({'INFO'}, "Écoute arrêtée.")
            else:
                self.report({'WARNING'}, "VoiceEngine indisponible.")
        except Exception as e:
            log.exception(e)
            self.report({'ERROR'}, f"Erreur : {e}")
        return {'FINISHED'}


class BLADE_OT_toggle_auto_execute(bpy.types.Operator):
    """Synchronise la prop Scene et le moteur voix"""

    bl_idname = "blade.toggle_auto_execute"
    bl_label = "Basculer Auto-Execute"

    def execute(self, context):
        try:
            scn = context.scene
            scn.blade_auto_execute = not scn.blade_auto_execute
            engine = _get_voice_engine_singleton()
            if hasattr(engine, "set_auto_execute"):
                engine.set_auto_execute(bool(scn.blade_auto_execute))
            state = "activé" if scn.blade_auto_execute else "désactivé"
            self.report({'INFO'}, f"Auto-Execute {state}.")
        except Exception as e:
            log.exception(e)
            self.report({'ERROR'}, f"Erreur : {e}")
        return {'FINISHED'}


class _SendPhraseBase:
    def _run_and_mark(self, context, phrase: str):
        phrase = (phrase or "").strip()
        if not phrase:
            return False, "Aucune phrase à envoyer."
        try:
            # Point d'undo optionnel avant exécution
            try:
                bpy.ops.ed.undo_push(message="Blade: before intent")
            except Exception:
                pass

            from ares.core.run_pipeline import run_pipeline

            ok = run_pipeline(phrase)
            if ok:
                context.scene.blade_last_phrase = phrase
                context.scene.blade_pending_validation = True
                return True, None
            else:
                return False, "Intent non résolu ou échec d'exécution."
        except Exception as e:
            log.exception(e)
            return False, f"Erreur pipeline : {e}"


class BLADE_OT_send_manual_phrase(bpy.types.Operator, _SendPhraseBase):
    bl_idname = "blade.send_manual_phrase"
    bl_label = "Envoyer la phrase"

    def execute(self, context):
        phrase = context.scene.blade_manual_phrase
        ok, err = self._run_and_mark(context, phrase)
        if ok:
            self.report({'INFO'}, f"Phrase envoyée : {phrase}")
        else:
            self.report({'ERROR'}, err)
        return {'FINISHED'}


class BLADE_OT_send_transcript_phrase(bpy.types.Operator, _SendPhraseBase):
    bl_idname = "blade.send_transcript_phrase"
    bl_label = "Envoyer transcript"

    def execute(self, context):
        phrase = context.scene.blade_transcript
        ok, err = self._run_and_mark(context, phrase)
        if ok:
            self.report({'INFO'}, f"Transcript envoyé : {phrase}")
        else:
            self.report({'ERROR'}, err)
        return {'FINISHED'}


class BLADE_OT_refresh_transcript(bpy.types.Operator):
    bl_idname = "blade.refresh_transcript"
    bl_label = "Rafraîchir transcript"

    def execute(self, context):
        try:
            engine = _get_voice_engine_singleton()
            txt = getattr(engine, "last_transcript", "")
            if txt:
                context.scene.blade_transcript = txt
                self.report({'INFO'}, "Transcript mis à jour.")
            else:
                self.report({'INFO'}, "Aucun transcript disponible.")
        except Exception as e:
            log.exception(e)
            self.report({'ERROR'}, f"Erreur : {e}")
        return {'FINISHED'}


class BLADE_OT_confirm_last_intent(bpy.types.Operator):
    bl_idname = "blade.confirm_last_intent"
    bl_label = "Valider l'exécution"

    def execute(self, context):
        context.scene.blade_pending_validation = False
        self.report({'INFO'}, "Intent validé.")
        return {'FINISHED'}


class BLADE_OT_reject_last_intent(bpy.types.Operator):
    bl_idname = "blade.reject_last_intent"
    bl_label = "Rejeter (Undo)"

    def execute(self, context):
        try:
            bpy.ops.ed.undo()
            context.scene.blade_pending_validation = False
            self.report({'INFO'}, "Intent rejeté, Undo appliqué.")
        except Exception as e:
            log.exception(e)
            self.report({'ERROR'}, f"Impossible d'annuler : {e}")
        return {'FINISHED'}


class BLADE_OT_render_background(bpy.types.Operator):
    """Lancer un rendu .mp4 en tâche de fond (module optionnel)"""

    bl_idname = "blade.render_background"
    bl_label = "Rendu MP4 (background)"

    def execute(self, context):
        try:
            from ares.tools.render_background import run_background_render
        except Exception:
            self.report({'WARNING'}, "Module de rendu background indisponible.")
            return {'CANCELLED'}
        try:
            run_background_render()
            self.report({'INFO'}, "Rendu .mp4 lancé en background.")
        except Exception as e:
            log.exception(e)
            self.report({'ERROR'}, f"Erreur de rendu background : {e}")
        return {'FINISHED'}


# ---------------------------------------------------------------------------
# PANNEAU PRINCIPAL
# ---------------------------------------------------------------------------


class BLADE_PT_main_panel(bpy.types.Panel):
    bl_label = "Blade Voice Assistant"
    bl_idname = "BLADE_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Blade'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        engine = _get_voice_engine_singleton()

        # --- Bloc statut & contrôle ---
        box = layout.box()
        row = box.row(align=True)
        status = "Écoute ON" if getattr(engine, "listening", False) else "Écoute OFF"
        row.label(text=f"Statut : {status}", icon='OUTLINER_OB_SPEAKER')

        row = box.row(align=True)
        if getattr(engine, "listening", False):
            row.operator("blade.stop_voice", text="Arrêter l’écoute", icon='PAUSE')
        else:
            row.operator("blade.start_voice", text="Démarrer l’écoute", icon='PLAY')

        row = box.row(align=True)
        row.prop(scene, "blade_auto_execute", text="Auto-Execute")
        row.operator("blade.toggle_auto_execute", text="", icon='CHECKMARK')

        # --- Rendu rapide ---
        row = box.row(align=True)
        row.operator(
            "blade.render_background", text="Rendu MP4 (background)", icon="RENDER_ANIMATION"
        )

        # --- Conversation (pré-édition + validation) ---
        conv = layout.box()
        conv.label(text="Conversation")
        r = conv.row(align=True)
        r.prop(scene, "blade_transcript", text="Reconnaissance")
        r.operator("blade.refresh_transcript", text="", icon="FILE_REFRESH")

        r = conv.row(align=True)
        r.operator(
            "blade.send_transcript_phrase",
            text="Envoyer (transcript)",
            icon="OUTLINER_DATA_SPEAKER",
        )
        r.operator(
            "blade.send_manual_phrase", text="Envoyer (champ manuel)", icon="OUTLINER_DATA_SPEAKER"
        )

        if scene.blade_pending_validation:
            conv.separator()
            conv.label(text=f"Dernière exécution : « {scene.blade_last_phrase} »")
            r = conv.row(align=True)
            r.operator("blade.confirm_last_intent", text="Valider", icon="CHECKMARK")
            r.operator("blade.reject_last_intent", text="Rejeter (Undo)", icon="CANCEL")

        # --- Champ manuel séparé ---
        manual = layout.box()
        manual.prop(scene, "blade_manual_phrase", text="Phrase manuelle")
        manual.operator(
            "blade.send_manual_phrase", text="Envoyer la phrase", icon="OUTLINER_DATA_SPEAKER"
        )


# ---------------------------------------------------------------------------
# REGISTER
# ---------------------------------------------------------------------------

_CLASSES = (
    BLADE_OT_start_voice,
    BLADE_OT_stop_voice,
    BLADE_OT_toggle_auto_execute,
    BLADE_OT_send_manual_phrase,
    BLADE_OT_send_transcript_phrase,
    BLADE_OT_refresh_transcript,
    BLADE_OT_confirm_last_intent,
    BLADE_OT_reject_last_intent,
    BLADE_OT_render_background,
    BLADE_PT_main_panel,
)


def register():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)
    _ensure_scene_props()
    # Assure la présence d'un VoiceEngine singleton
    _get_voice_engine_singleton()
    log.info("UI_Main enregistré.")


def unregister():
    for cls in reversed(_CLASSES):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
    # Ne pas supprimer les props pour garder l'état (SKIP_SAVE gère la persistance réduite)
    log.info("UI_Main désenregistré.")
