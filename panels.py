import bpy

from .operators import BatchTestOperator, OpenFolderOperator


class MMDBatchTestPanel(bpy.types.Panel):
    bl_idname = "MMD_BATCH_TEST_PT_main"
    bl_label = "MMD Batch Test"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MMD"

    def draw(self, context):
        wm = context.window_manager
        layout = self.layout
        layout.label(text="Batch Model Tester", icon="EXPERIMENTAL")

        col = layout.column()
        if wm.mmd_batch_test.directory:
            col.label(text=f"Source: {wm.mmd_batch_test.directory}")

        col.operator(OpenFolderOperator.bl_idname, text="Open", icon="FILEBROWSER")
        if wm.mmd_batch_test.is_active:
            col.progress(text="Press esc to cancel", factor=wm.mmd_batch_test.progress)
        else:
            col.operator(BatchTestOperator.bl_idname, text="Execute", icon="FILE_MOVIE")
