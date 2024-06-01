import bpy
from typing import List
from bpy.types import Context, Object, Collection
from bpy.props import PointerProperty, BoolProperty

class EasyWeightsProperty(bpy.types.PropertyGroup):
    # Mesh only selection function for poll property
    def poll_mesh(self, object: Object):
        return object.type == 'MESH'
    
    def poll_collection(self, collection:Collection):
        return any(obj.type == 'MESH' for obj in collection.objects)
    
    SOURCE: PointerProperty(
        name="Source",
        description="Select the source mesh from which weights will be transferred from",
        type=Object,
        poll=poll_mesh
    )

    TARGET: PointerProperty(
        name="Target",
        description="Mesh that will have weights transferred to",
        type=Object,
        poll=poll_mesh
    )

    TARGETS: PointerProperty(
        name="Targets",
        description="Objects that will have weights transferred to",
        type=Collection,
        poll=poll_collection
    )
    
    SELECT_ONE: BoolProperty(
        name="Mesh",
        description="Target a single mesh",
        default=True 
    )

    SELECT_MULTIPLE: BoolProperty(
        name="Collection",
        description="Target all mesh in a collection",
        default=False
    )

class TransferWeightOperator(bpy.types.Operator):
    bl_idname = "object.transfer_weights"
    bl_label = "Weight Transfer"

    def execute(self, context: Context):
        ew_properties: EasyWeightsProperty = context.scene.EasyWeightsProperty
        
        selected_objects = context.selected_objects
        
        source: Object = ew_properties.SOURCE
        targets: Collection = ew_properties.TARGETS

        # source = selected_objects[-1]
        # targets = selected_objects[:len(selected_objects)-1]

        # for obj in targets:
        #     bpy.ops.object.data_transfer(data_type="VGROUP_WEIGHTS", layers_select_src="NAME", layers_select_dst="ALL")

        # message: str = "List[objects]: " + str(selected_objects)

        for obj in targets.objects:
            if obj.type == 'MESH' and obj != source:
                message: str = f"Transferring weights from {source.name} to {obj.name}"
            elif obj == source:
                message: str = f"Skipping source mesh: {source.name}"
            else:
                message: str = f"Skipping non-mesh object: {obj.name}"
                
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
        selected_objects: List[Object] = context.selected_objects
        
        for obj in selected_objects:
            if obj.type == 'INFO':
                obj.vertex_groups.clear()
        
        message: str = "Deleted all vertex groups from selected objects."
        self.report({'INFO'}, message=message)

class MainPanel:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Easy Weights"

class EasyWeightPanel(MainPanel, bpy.types.Panel):
    bl_label = "Easy Weights"

    @classmethod
    def poll(cls, context: Context) -> bool:
        return context.active_object is not None
    
    def draw_header(self, context: Context):
        layout = self.layout
        obj = context.object
        layout.prop(obj, "select", text="")


    def draw(self, context: Context):
        layout = self.layout
        properties: EasyWeightsProperty = context.scene.EasyWeightsProperty

        section = layout.box()
        row = section.row()
        row.label(text="Settings", icon='MODIFIER')

        row = section.row()
        row.prop(properties, 'SOURCE')

        row = section.row()
        row.prop(properties, 'TARGETS')

        row = section.row()
        row.prop(properties, 'SELECT_ONE')
        row.prop(properties, 'SELECT_MULTIPLE')

        

        selected_objects = context.selected_objects

        # if selected_objects:
        #     source = context.active_object
        #     if source in selected_objects:
        #         row.prop(source, "name", icon='OBJECT_DATA', placeholder='Object')
        # else:
        #     row.label(text="No object selected")
        
        row = layout.row()
        row.label(text="Transfer Weights", icon="GROUP_VERTEX")

        row = layout.row()
        row.operator(TransferWeightOperator.bl_idname, text="Transfer Weights", icon="MOD_DATA_TRANSFER")



classes = [
    EasyWeightsProperty,
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
    
    bpy.types.Scene.EasyWeightsProperty = bpy.props.PointerProperty(type=EasyWeightsProperty)
    bpy.app.handlers.depsgraph_update_post.append(updatePanel)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.app.handlers.depsgraph_update_post.remove(updatePanel)
    
if __name__ == "__main__":
    register()