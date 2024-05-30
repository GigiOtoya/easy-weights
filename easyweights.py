import bpy
from bpy.types import Context, Event


class TransferWeightOperator(bpy.types.Operator):
    bl_idname = "object.transfer_weights"
    bl_label = "Weight Transfer"

    def execute(self, context: Context):
        selected_objects = context.selected_objects
        
        source = selected_objects[-1]
        targets = selected_objects[:len(selected_objects)-1]

        for obj in targets:
            bpy.ops.object.data_transfer(data_type="VGROUP_WEIGHTS", layers_select_src="NAME", layers_select_dst="ALL")

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

        row = layout.row()
        row.label(text="Source Object: ")

        selected_objects = context.selected_objects

        if selected_objects:
            source = context.active_object
            if source in selected_objects:
                row.label(text=source.name)
        else:
            row.label(text="No object selected")
        
        row = layout.row()
        row.label(text="Transfer Weights", icon="GROUP_VERTEX")

        row = layout.row()
        row.operator(TransferWeightOperator.bl_idname, text="Transfer Weights", icon="MOD_DATA_TRANSFER")


classes = [
    TransferWeightOperator,
    EasyWeightPanel
]

def updatePanel(self, context):
    # This function forces the UI to update
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'UI':
                    region.tag_redraw()

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.app.handlers.depsgraph_update_post.append(updatePanel)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.app.handlers.depsgraph_update_post.remove(updatePanel)
    
if __name__ == "__main__":
    register()