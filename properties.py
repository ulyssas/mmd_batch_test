import bpy

from .core import test


class MMDBatchTestProperties(bpy.types.PropertyGroup):
    tester: bpy.props.EnumProperty(
        items=test.TESTERS.blender_enum,
        description="Choose the tester you want to use",
    )
    directory: bpy.props.StringProperty(maxlen=1024, subtype="DIR_PATH")
    is_active: bpy.props.BoolProperty(default=False)
    progress: bpy.props.FloatProperty(default=0.0)

    @staticmethod
    def register():
        bpy.types.WindowManager.mmd_batch_test = bpy.props.PointerProperty(type=MMDBatchTestProperties)

    @staticmethod
    def unregister():
        del bpy.types.WindowManager.mmd_batch_test
