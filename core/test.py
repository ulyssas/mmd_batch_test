import math
import traceback
from abc import ABC, abstractmethod

import bpy

from .model import find_armature, find_root


class MMDTestABC(ABC):
    id: str
    name: str
    description: str = ""

    def __init__(self, context: bpy.types.Context):
        self.context = context

        active_obj = context.active_object
        self.mmd_root = find_root(context.active_object) if active_obj else None
        self.mmd_arm = find_armature(context.active_object) if active_obj else None

    @abstractmethod
    def tester(self) -> bool:
        pass


class MMDTesters:
    def __init__(self, *testers: tuple[int, MMDTestABC]):
        self.testers: dict[str, MMDTestABC] = {tester.id: tester for _, tester in testers}
        self.blender_enum: list[tuple[str, str, str, int]] = [
            (tester.id, tester.name, tester.description, idx) for idx, tester in testers
        ]

    def __getitem__(self, tester_id: str) -> MMDTestABC:
        return self.testers[tester_id]


class MMDTestIKLimit(MMDTestABC):
    id: str = "IK_LIMIT"
    name: str = "IK Limit Test"
    description: str = "Test if the model has IK limit in X direction. (Most models should pass.)"

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


class MMDTestLegDLocal(MMDTestABC):
    id: str = "LEG_D_LOCAL"
    name: str = "Leg D Local Test"
    description: str = "Test if the model has Local axis in Leg D bones. (Most models should fail.)"

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

            bone_names = ("足D.L", "ひざD.L", "足首D.L")
            for bone in bone_names:
                if bone not in self.mmd_arm.pose.bones:
                    return Exception(f"Bone '{bone}' does not exist in this model.")

                if self.mmd_arm.pose.bones[bone].mmd_bone.enabled_local_axes:
                    return True

            return False

        except Exception as e:
            print(traceback.format_exc())
            return e
        finally:
            bpy.ops.object.mode_set(mode=previous_mode)


class MMDTestLegParent(MMDTestABC):
    id: str = "LEG_PARENT"
    name: str = "Leg Parent Test"
    description: str = (
        "Test if the parent of leg is 腰キャンセル if the model has 腰. (Most models should give error or pass.)"
    )

    def __init__(self, context):
        super().__init__(context)

    def tester(self) -> bool | None:
        if not self.mmd_arm:
            return Exception("Armature object could not be found.")

        try:
            bpy.ops.object.select_all(action="DESELECT")
            self.context.view_layer.objects.active = self.mmd_arm

            if self.mmd_arm.pose.bones.get("腰"):
                if not self.mmd_arm.pose.bones.get("腰キャンセル.L"):
                    return False
                return self.mmd_arm.pose.bones["足.L"].parent == self.mmd_arm.pose.bones["腰キャンセル.L"]
            else:
                return Exception("Bone '腰' does not exist in this model.")

        except Exception as e:
            print(traceback.format_exc())
            return e


TESTERS = MMDTesters(
    (0, MMDTestLegDLocal),
    (1, MMDTestIKLimit),
    (2, MMDTestLegParent),
)
