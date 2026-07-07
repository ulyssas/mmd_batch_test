import bpy


class MMDBatchTestProperties(bpy.types.PropertyGroup):
    directory: bpy.props.StringProperty(maxlen=1024, subtype="DIR_PATH")

    @staticmethod
    def register():
        bpy.types.Scene.mmd_batch_test = bpy.props.PointerProperty(type=MMDBatchTestProperties)

    @staticmethod
    def unregister():
        del bpy.types.Scene.mmd_batch_test
