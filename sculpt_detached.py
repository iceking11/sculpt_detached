bl_info = {
    "name": "Sculpt Detached",
    "author": "Ian Lloyd Dela Cruz",
    "version": (1, 0),
    "blender": (2, 7, 5),
    "location": "3d View > Tool shelf",
    "description": "Detach Sculpt Areas",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Sculpt Tools"}

import bpy
import math
import bmesh
from bpy.props import *

class SculptDetached(bpy.types.Operator):
    '''Isolate Sculpt Areas'''
    bl_idname = "sculpt.detached"
    bl_label = "Detach sculpt areas via vertex group"
    
    def detach(self, ob):
        
        bm = bmesh.new()
        bm.from_mesh(ob.data)

        group_index = bpy.context.active_object.vertex_groups.active_index
        dvert_lay = bm.verts.layers.deform.active

        for v in bm.verts:
            if v.select == True:
                v.select_set(False)
        bm.select_flush_mode()                
       
        for v in bm.verts:

            dvert = v[dvert_lay]
            if group_index in dvert: v.select = True

        bm.select_flush(False) 
        bm.to_mesh(ob.data)
        bm.free()
        
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_mode(type='VERT')
        bpy.ops.mesh.separate(type='SELECTED')
        bpy.ops.object.editmode_toggle()

    def rejoin(self, context):
 
        ob = context.active_object
        ob_dat = ob.data.name
        
        if context.active_object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode='OBJECT')            
 
        for selObj in context.selected_objects :
            if selObj != ob :
                context.scene.objects.active = bpy.data.objects[selObj.name]
        
        bpy.ops.object.join()
        
        bpy.data.meshes.remove(bpy.data.meshes[ob_dat])
        
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all()
        bpy.ops.mesh.remove_doubles()
        bpy.ops.mesh.select_all(action='DESELECT')        
        bpy.ops.object.editmode_toggle()                     
 
    def modal(self, context, event):
        
        if event.type in ['SPACE'] or context.active_object.mode == "OBJECT" or context.active_object.mode == "EDIT":
            self.report({'INFO'}, "Sculpt Detached Done.")
            self.rejoin(context)
            return {'CANCELLED'}
        return {'PASS_THROUGH'}    
    
    def invoke(self, context, event):

        if context.active_object.mode != "OBJECT":
            self.report({'WARNING'}, "Must be in Object Mode!")
            return {'FINISHED'}        
        
        obj =  context.active_object
        split_vg = context.active_object.vertex_groups.active.name

        self.detach(bpy.data.objects[obj.name])
        
        for selObj in context.selected_objects:
            
            if selObj != obj:
            
                selObj.select = True
                context.scene.objects.active = bpy.data.objects[selObj.name]
                selObj.name = obj.name + "_" + split_vg
                
        bpy.ops.object.mode_set(mode='SCULPT')
        context.window_manager.modal_handler_add(self)
                                
        return {'RUNNING_MODAL'}         
        
class SculptDetachedPanel(bpy.types.Panel):
    """Sculpt Detached Functions"""
    bl_label = "Sculpt Detached"
    bl_idname = "OBJECT_PT_sculpt_detached"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Sculpt Tools'

    def draw(self, context):
        layout = self.layout

        ob = context.object
        
        if ob.type == "MESH":
            group = ob.vertex_groups.active

            rows = 2
            if group:
                rows = 4

            row = layout.row()
            row.template_list("MESH_UL_vgroups", "", ob, "vertex_groups", ob.vertex_groups, "active_index", rows=rows)        

        row_sw = layout.row(align=True)
        row_sw.alignment = 'EXPAND'
        row_sw.operator("sculpt.detached", "Sculpt Detached")                        
       
def register():
    bpy.utils.register_module(__name__)
    
def unregister():
    bpy.utils.unregister_module(__name__)
    
if __name__ == "__main__":
    register()
