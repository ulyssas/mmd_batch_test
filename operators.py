import os
import traceback
from pathlib import Path

import bpy
from bpy.types import Operator

from .core import test


class OpenFolderOperator(Operator):
    bl_idname = "mmd_batch_test.open_folder"
    bl_label = "Open Folder"
    bl_description = "Open root folder that contains models"
    bl_options = {"REGISTER", "UNDO"}

    directory: bpy.props.StringProperty(maxlen=1024, subtype="DIR_PATH", options={"HIDDEN", "SKIP_SAVE"})
    filter_folder: bpy.props.BoolProperty(default=True, options={"HIDDEN"})

    def execute(self, context):
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
    bl_options = {"REGISTER"}

    def execute(self, context):
        bpy.ops.object.select_all(action="DESELECT")
        for obj in context.scene.objects:
            obj.select_set(True)

        bpy.ops.object.delete()
        bpy.ops.outliner.orphans_purge()

        return {"FINISHED"}


class BatchTestOperator(Operator):
    bl_idname = "mmd_batch_test.batch_test"
    bl_label = "Run Test"
    # bl_description = "Open root folder that contains models"
    bl_options = {"REGISTER"}

    # for toggling log file
    enable_log = True

    _timer = None
    _pmx_files = []
    _total_count = 0
    _current_index = 0
    _log_filepath = None

    @staticmethod
    def print_log(text: str):
        if text.startswith("PASS:"):
            print("✅ " + text)
        elif text.startswith("FAIL:"):
            print("⚠️ " + text)
        elif text.startswith("ERROR:"):
            print("❌ " + text)

    @classmethod
    def poll(cls, context: bpy.types.Context):
        wm = context.window_manager
        if wm.mmd_batch_test.is_active:
            return False
        return bool(wm.mmd_batch_test.directory)

    def modal(self, context, event):
        wm = context.window_manager
        prop = wm.mmd_batch_test

        if event.type == "ESC":
            self.cancel(context)
            self.report({"INFO"}, "Batch test was cancelled.")
            return {"CANCELLED"}

        if event.type == "TIMER":
            if self._current_index < self._total_count:
                pmx = self._pmx_files[self._current_index]
                try:
                    # TODO add random selection (limit to 20 (too slow)?)
                    # import PMX file
                    bpy.ops.mmd_tools.import_model(
                        filepath=str(pmx.absolute()),
                        types={"ARMATURE"},
                        scale=0.08,
                        clean_model=False,
                        remove_doubles=False,
                        log_level="ERROR",
                    )

                    # Test the model
                    msg = ""
                    result = test.TESTERS[prop.tester](context).tester()
                    if result is True:
                        msg = f"PASS: {pmx.name} ({self._current_index + 1}/{self._total_count})"
                        self.report({"INFO"}, msg)
                    elif result is False:
                        msg = f"FAIL: {pmx.name} ({self._current_index + 1}/{self._total_count})"
                        self.report({"WARNING"}, msg)
                    else:
                        msg = f"ERROR: {pmx.name} ({result}) ({self._current_index + 1}/{self._total_count})"
                        self.report({"ERROR"}, msg)

                    self.print_log(msg)
                    if self.enable_log:
                        with open(self._log_filepath, "a", encoding="utf-8") as f:
                            f.write(msg + "\n")

                except Exception as e:
                    err_msg = traceback.format_exc()
                    self.report({"ERROR"}, f"Error while processing {pmx.name}: {e}")
                    self.report({"ERROR"}, err_msg)

                    if self.enable_log:
                        with open(self._log_filepath, "a", encoding="utf-8") as f:
                            f.write(f"ERROR_EXCEPTION: {pmx.name}\n")
                            f.write(f"Reason: {e}\n")
                            f.write(f"{err_msg}\n")
                            f.write("-" * 20 + "\n")

                # for next process
                bpy.ops.mmd_batch_test.cleanup_scene()

                self._current_index += 1
                prop.progress = self._current_index / self._total_count

                # force redraw
                for window in wm.windows:
                    for area in window.screen.areas:
                        area.tag_redraw()
            else:
                if self.enable_log:
                    with open(self._log_filepath, "a", encoding="utf-8") as f:
                        f.write("\n=== Batch Test Completed ===\n")

                self.cancel(context)
                self.report({"INFO"}, "Batch test DONE!")
                return {"CANCELLED"}

        return {"PASS_THROUGH"}

    def execute(self, context):
        wm = context.window_manager
        prop = wm.mmd_batch_test
        directory = prop.directory

        # find PMX files
        root_dir = Path(directory)
        self._pmx_files = list(root_dir.rglob("*.[Pp][Mm][XxDd]"))
        if not self._pmx_files:
            self.report({"WARNING"}, "No PMX files found in the folder.")
            return {"CANCELLED"}

        # logging
        if self.enable_log:
            temp_dir = Path(context.preferences.filepaths.temporary_directory)
            self._log_filepath = temp_dir / "test_results.txt"
            with open(self._log_filepath, "w", encoding="utf-8") as f:
                f.write("=== MMD Batch Test Results ===\n")
                f.write(f"Target Directory: {directory}\n")
                f.write(f"Total Models Found: {len(self._pmx_files)}\n")
                f.write("-" * 40 + "\n\n")

        # initialize
        self._total_count = len(self._pmx_files)
        self._current_index = 0

        prop.is_active = True
        prop.progress = 0.0

        # bpy.ops.view3d.view_axis(type="FRONT")
        bpy.ops.mmd_batch_test.cleanup_scene()

        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)

        self.report({"INFO"}, f"Started batch test for {self._total_count} models.")
        return {"RUNNING_MODAL"}

    def cancel(self, context):
        wm = context.window_manager
        prop = wm.mmd_batch_test

        prop.is_active = False
        prop.progress = 0.0

        if self._timer:
            wm.event_timer_remove(self._timer)
            self._timer = None
