import logging
import os
import traceback

import bpy
from bpy.types import Operator


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
            context.scene.mmd_batch_test.directory = self.directory
            self.report({"INFO"}, f'Opened folders in "{self.directory}"')

        except Exception:
            err_msg = traceback.format_exc()
            self.report({"ERROR"}, err_msg)
            return {"CANCELLED"}

        return {"FINISHED"}

    def invoke(self, context, _event):
        previous_dir = context.scene.mmd_batch_test.directory

        if previous_dir and os.path.isdir(previous_dir):
            self.directory = previous_dir

        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}
