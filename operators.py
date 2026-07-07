import logging
import os
import traceback

import bpy
from bpy.types import Operator, OperatorFileListElement
from bpy_extras.io_utils import ImportHelper


class OpenFolderOperator(Operator, ImportHelper):
    bl_idname = "mmd_batch_test.open_folder"
    bl_label = "Open Folder"
    bl_description = "Open root folder that contains models. Subfolders will be added to the list"
    bl_options = {"REGISTER", "UNDO"}

    files: bpy.props.CollectionProperty(type=OperatorFileListElement, options={"HIDDEN", "SKIP_SAVE"})
    directory: bpy.props.StringProperty(maxlen=1024, subtype="DIR_PATH", options={"HIDDEN", "SKIP_SAVE"})

    def execute(self, context):
        try:
            if self.directory:
                for f in self.files:
                    n = f.name
                    if n.startswith("//"):
                        # Blender relative path (e.g. "//a.pmx")
                        n = n[2:]
                    self.filepath = os.path.join(self.directory, n)
                    self._do_execute(context)
            elif self.filepath:
                self._do_execute(context)
        except Exception:
            err_msg = traceback.format_exc()
            self.report({"ERROR"}, err_msg)
            return {"CANCELLED"}
        return {"FINISHED"}

    def _do_execute(self, _context):
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        try:
            self.report({"INFO"}, f'Opened folders in "{self.filepath}"')
        except Exception:
            logging.exception("Error occurred")
            raise

        return {"FINISHED"}
