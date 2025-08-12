# ares/ui/ui_spider_generator.py

import bpy

try:
    from ares.tools.text2mesh_manager import get_manager
except Exception:
    get_manager = None


class BLADE_OT_generate_spider(bpy.types.Operator):
    bl_idname = "blade.generate_spider"
    bl_label = "Generate Spider"
    bl_description = "Generate a procedural spider (or import local asset if provider=offline_stub)"

    provider: bpy.props.EnumProperty(
        name="Provider",
        items=[
            ('procedural_spider', "Procedural Spider", ""),
            ('offline_stub', "Offline Stub (import)", ""),
        ],
        default='procedural_spider',
    )
    leg_length: bpy.props.FloatProperty(name="Leg Length", default=0.9, min=0.2, max=3.0)
    leg_bevel: bpy.props.FloatProperty(name="Leg Thickness", default=0.02, min=0.005, max=0.1)
    body_radius: bpy.props.FloatProperty(name="Body Radius", default=0.25, min=0.05, max=1.5)
    auto_scale_to: bpy.props.FloatProperty(
        name="Auto Scale Max Dim", default=2.0, min=0.1, max=10.0
    )

    def execute(self, context):
        if get_manager is None:
            self.report({'ERROR'}, "Text2MeshManager not available.")
            return {'CANCELLED'}
        jm = get_manager()
        job_id = jm.start(
            provider=self.provider,
            prompt="spider",
            body_radius=float(self.body_radius),
            leg_length=float(self.leg_length),
            leg_bevel=float(self.leg_bevel),
            auto_scale_to=float(self.auto_scale_to),
            auto_origin=True,
            smooth=True,
        )
        info = jm.get(job_id)
        self.report({'INFO'}, f"{info['status']}: {info['message']}")
        return {'FINISHED'}


class BLADE_PT_spider_panel(bpy.types.Panel):
    bl_label = "Spider Generator"
    bl_idname = "BLADE_PT_spider_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Blade'

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.label(text="Spider Generator")
        col.operator("blade.generate_spider")


classes = (BLADE_OT_generate_spider, BLADE_PT_spider_panel)


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
