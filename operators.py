import logging
import os
import traceback
from pathlib import Path

import bpy
from bpy.types import Operator

from .core.test import MMDTestIKLimit


class OpenFolderOperator(Operator):
    bl_idname = "mmd_batch_test.open_folder"
    bl_label = "Open Folder"
    bl_description = "Open root folder that contains models"
    bl_options = {"REGISTER", "UNDO"}

    directory: bpy.props.StringProperty(maxlen=1024, subtype="DIR_PATH", options={"HIDDEN", "SKIP_SAVE"})
    filter_folder: bpy.props.BoolProperty(default=True, options={"HIDDEN"})

    def execute(self, context):
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        try:
            context.window_manager.mmd_batch_test.directory = self.directory
            self.report({"INFO"}, f'Set root directory: "{self.directory}"')

        except Exception:
            err_msg = traceback.format_exc()
            self.report({"ERROR"}, err_msg)
            return {"CANCELLED"}

        return {"FINISHED"}

    def invoke(self, context, _event):
        previous_dir = context.window_manager.mmd_batch_test.directory

        if previous_dir and os.path.isdir(previous_dir):
            self.directory = previous_dir

        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class CleanupSceneOperator(Operator):
    bl_idname = "mmd_batch_test.cleanup_scene"
    bl_label = "Remove Everything"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.ops.object.select_all(action="DESELECT")
        for obj in context.scene.objects:
            obj.select_set(True)

        bpy.ops.object.delete()
        bpy.ops.outliner.orphans_purge()

        return {"FINISHED"}

