import bpy

from .operators import OpenFolderOperator


class MMDBatchTestPanel(bpy.types.Panel):
    bl_idname = "MMD_BATCH_TEST_PT_main"
    bl_label = "MMD Batch Test"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MMD"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Batch Model Tester", icon="EXPERIMENTAL")
        col = layout.column()
        col.operator(OpenFolderOperator.bl_idname, text="Open", icon="FILEBROWSER")
        col.operator(OpenFolderOperator.bl_idname, text="Execute", icon="FILE_MOVIE")
