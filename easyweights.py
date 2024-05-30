import bpy
from bpy.types import Context, Event


class TransferWeightOperator(bpy.types.Operator):
    bl_idname = "object.transfer_weights"
    bl_label = "Weight Transfer"

    def execute(self, context: Context):
        selected_objects = context.selected_objects
        source = selected_objects[-1]


        self.report({"INFO"}, str(selected_objects))
        return {"FINISHED"}

class EasyWeightPanel(bpy.types.Panel):
    bl_label = "Easy Weights"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Easy Weights"

    @classmethod
    def poll(cls, context: Context) -> bool:
        return context.active_object is not None
    
    def draw_header(self, context: Context):
        layout = self.layout
        obj = context.object
        layout.prop(obj, "select", text="")

    def draw(self, context: Context):

        layout = self.layout

        selected_objects = context.selected_objects
        
        row = layout.row()
        row.label(text="Source Object: ")
        
        source = None
        if selected_objects:
            source = selected_objects[-1]
            row.label(text="Source Object: " + source.name)


        row = layout.row()
        row.label(text="Target Objects:") 

        if len(target_objects) < 1:
            row = layout.row()
            row.label(text="None selected", icon="ERROR")

        for obj in target_objects:
            row = layout.row()
            row.label(text="->\t" + obj.name)

        row = layout.row()
        row.label(text="Transfer Weights", icon="GROUP_VERTEX")

        row = layout.row()
        row.operator(TransferWeightOperator.bl_idname, text="Transfer Weights", icon="MOD_DATA_TRANSFER")
    
bpy.utils.register_class(TransferWeightOperator)
bpy.utils.register_class(EasyWeightPanel)