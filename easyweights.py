import bpy
from typing import List
from bpy.types import Context, Object, Collection, MeshVertices
from bpy.props import PointerProperty, BoolProperty, EnumProperty

class EasyWeightsProperty(bpy.types.PropertyGroup):
    def poll_source(self, object: Object):
        return object.type == 'MESH' and object != self.TARGET
    
    def poll_target(self, object: Object):
        return object.type == 'MESH' and object != self.SOURCE

    def poll_collection(self, collection:Collection):
        return any(obj.type == 'MESH' for obj in collection.objects)
    
    def update(self, context):
        self.TARGET = None
        self.TARGETS = None
    
    SOURCE: PointerProperty(
        name="Source",
        description="Select the source mesh from which weights will be transferred from",
        type=Object,
        poll=poll_source
    )

    TARGET: PointerProperty(
        name="Target",
        description="Mesh that will have weights transferred to",
        type=Object,
        poll=poll_target
    )

    TARGETS: PointerProperty(
        name="Targets",
        description="Objects that will have weights transferred to",
        type=Collection,
        poll=poll_collection
    )

    SELECTION_MODE: EnumProperty(
        name = "Mode",
        description = "Mode",
        items = (
            (
                "MESH_SINGLE",
                "Single Mesh",
                "Transfer weights to a single mesh",
                "MESH_DATA",
                0
            ),
            (
                "COLLECTION",
                "Collection",
                "Transfer weights to all mesh in a collection",
                "COLLECTION_COLOR_02",
                1
            ),
        ),
        update=update
    )

    CLEAN: BoolProperty(
        name="Clean",
        description="Exclude vertex groups with weight_value = 0 from target mesh",
        default=False
    )

    SMOOTH: BoolProperty(
        name="Smooth",
        description="Smooth weights for vertex groups",
        default=False
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
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Transfer weights from source to target"

    @classmethod
    def poll(cls, context: Context)-> bool:
        properties: EasyWeightsProperty = context.scene.EasyWeightsProperty
        
        if properties.SELECTION_MODE == 'MESH_SINGLE':
            return properties.TARGET != None and properties.SOURCE != None
        else:
            return properties.TARGETS != None and properties.SOURCE != None

    def transferWeights(source: Object, target: Object):
        for v_group in source.vertex_groups:
            target.vertex_groups.new(name=v_group.name)

            {'TODO'}
        

    def execute(self, context: Context):
        properties: EasyWeightsProperty = context.scene.EasyWeightsProperty
        
        source: Object = properties.SOURCE
        targets: List[Object] = []
        
        if properties.SELECTION_MODE == 'MESH_SINGLE':
            targets.append(properties.TARGET)
        else:
            targets = getMeshObjects(properties.TARGETS)

        for target in targets:
            if target == properties.SOURCE:
                self.report({'INFO'}, f"Skipping source mesh: {source.name}")
                continue

            message: str = f"Transferring weights from {source.name} to {target.name}"
            self.report({"INFO"}, message=message)
            
            bpy.ops.object.select_all(action='DESELECT')
            
            source.select_set(True)
            target.select_set(True)
            context.view_layer.objects.active = target

            bpy.ops.object.mode_set(mode='OBJECT')
            
            bpy.ops.object.data_transfer(
                use_reverse_transfer=True,
                data_type='VGROUP_WEIGHTS',
                layers_select_src='NAME',
                layers_select_dst='ALL'
            )
        
        bpy.ops.object.select_all(action='DESELECT')
        context.view_layer.objects.active = None 
            
        return {"FINISHED"}
    
class CleanUpOperator(bpy.types.Operator):
    bl_idname = "object.weight_cleanup"
    bl_label = "Weight Cleanup"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = "Remove vertex groups with weight_value = 0 from target"
    
    @classmethod
    def poll(cls, context: Context) -> bool:
        properties: EasyWeightsProperty = context.scene.EasyWeightsProperty

        if properties.SELECTION_MODE == 'MESH_SINGLE':
            return properties.TARGET != None
        else:
            return properties.TARGETS != None
        
    def deleteZeroWeights(self, target: Object):
        vgroup_used = {i: False for i,k in enumerate(target.vertex_groups)}
        for v in target.data.vertices:
            for g in v.groups:
                if g.weight > 0.0:
                    vgroup_used[g.group] = True
        
        for i, used in sorted(vgroup_used.items(), reverse=True):
            if not used:
                target.vertex_groups.remove(target.vertex_groups[i])

    def execute(self, context: Context):
        properties: EasyWeightsProperty = context.scene.EasyWeightsProperty
        
        targets: List[Object] = []
        if properties.SELECTION_MODE == 'MESH_SINGLE':
            targets.append(properties.TARGET)
        else:
            targets = getMeshObjects(properties.TARGETS)

        for target in targets:
            self.report({'INFO'}, f"Removing unweighted vertex groups from {target.name}")
            self.deleteZeroWeights(target)
        
        message: str = "Removed unweighted vertex groups from selected objects."
        self.report({'INFO'}, message=message)

        return {'FINISHED'}

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
        row.prop(properties, 'SELECTION_MODE', expand=True)
        
        row = section.row()
        if properties.SELECTION_MODE == 'MESH_SINGLE':
            row.prop(properties, 'TARGET')
        else:
            row.prop(properties, 'TARGETS')

        row = section.row()
        row.prop(properties, 'CLEAN')

        row = section.row()
        row.prop(properties, 'SMOOTH')
        
        section = layout.box()
        row = section.row()
        row.label(text="Actions", icon="OPTIONS")

        row = section.row()
        row.operator(
            TransferWeightOperator.bl_idname, 
            text="Transfer Weights", 
            icon="MOD_DATA_TRANSFER"
        )

        row =section.row()
        row.operator(
            CleanUpOperator.bl_idname,
            text="Clean Vertex Groups",
            icon="GROUP_VERTEX"
        )


classes = [
    EasyWeightsProperty,
    TransferWeightOperator,
    CleanUpOperator,
    EasyWeightPanel
]


def getMeshObjects(objects: List[Object] | Collection) -> List[Object]:

    if isinstance(objects, list):
        return [obj for obj in objects if obj.type == 'MESH']
    
    return [obj for obj in objects.objects if obj.type == 'MESH']



def updatePanel(self, context):
    # Force UI to update
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