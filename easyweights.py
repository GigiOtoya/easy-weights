import bpy
from bpy.types import Context, Object


class TransferWeightOperator(bpy.types.Operator):
    bl_idname = "object.transfer_weights"
    bl_label = "Weight Transfer"

    def execute(self, context: Context):
        selected_objects = context.selected_objects
        
        source = selected_objects[-1]
        targets = selected_objects[:len(selected_objects)-1]

        for obj in targets:
            bpy.ops.object.data_transfer(data_type="VGROUP_WEIGHTS", layers_select_src="NAME", layers_select_dst="ALL")

        message: str = "List[objects]: " + str(selected_objects)

        self.report({"INFO"}, message=message)
        return {"FINISHED"}
    
class CleanUpOperator(bpy.types.Operator):
    bl_idname = "object.weight_cleanup"
    bl_label = "Weight Cleanup"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context: Context) -> bool:
        return context.selected_objects

    def execute(self, context: Context):
        selected_objects: list[Object] = context.selected_objects
        
        for obj in selected_objects:
            if obj.type == 'INFO':
                obj.vertex_groups.clear()
        
        message: str = "Deleted all vertex groups from selected objects."
        self.report({'INFO'}, message=message)


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
        
        section = layout.box()
        
        row = section.row()
        row.label(text="Settings", icon='MODIFIER')

        row = section.row()
        row.label(text="Source Mesh: ")

        selected_objects = context.selected_objects

        if selected_objects:
            source = context.active_object
            if source in selected_objects:
                row.prop(source, "name", icon='OBJECT_DATA', placeholder='Object')
        else:
            row.label(text="No object selected")
        
        row = layout.row()
        row.label(text="Transfer Weights", icon="GROUP_VERTEX")

        row = layout.row()
        row.operator(TransferWeightOperator.bl_idname, text="Transfer Weights", icon="MOD_DATA_TRANSFER")



classes = [
    TransferWeightOperator,
    CleanUpOperator,
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