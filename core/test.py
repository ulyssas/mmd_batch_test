import math
import traceback
from abc import ABC, abstractmethod

import bpy

from .model import find_armature, find_root


class MMDTestABC(ABC):
    def __init__(self, context: bpy.types.Context):
        self.context = context

        active_obj = context.active_object
        self.mmd_root = find_root(context.active_object) if active_obj else None
        self.mmd_arm = find_armature(context.active_object) if active_obj else None

    @abstractmethod
    def tester(self) -> bool:
        pass


class MMDTestIKLimit(MMDTestABC):
    """Test if the model has IK limit in X direction."""

    def __init__(self, context):
        super().__init__(context)

    def tester(self) -> bool | None:
        if not self.mmd_arm:
            return Exception("Armature object could not be found.")

        previous_mode = self.context.mode
        try:
            bpy.ops.object.select_all(action="DESELECT")
            self.context.view_layer.objects.active = self.mmd_arm

            bpy.ops.object.mode_set(mode="POSE")

            bone_name = "ひざ.L"
            if bone_name not in self.mmd_arm.pose.bones:
                return Exception(f"Bone '{bone_name}' does not exist in this model.")

            return math.isclose(self.mmd_arm.pose.bones[bone_name].ik_max_x, math.pi, rel_tol=1e-5)

        except Exception as e:
            print(traceback.format_exc())
            return e
        finally:
            bpy.ops.object.mode_set(mode=previous_mode)
