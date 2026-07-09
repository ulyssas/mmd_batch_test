# MMD Batch Test

MMD Batch Test is a Blender addon for testing multiple MMD models and find ones that have unexpected structure. It creates log files in temp directory set in Blender preferences.

Select a folder that contains PMX files, then press execute. Right now, it will check if the model has Local axis in Leg D bones.

Edit `core/test.py` to add your own testing classes and use it in `BatchTestOperator` (operators.py)

## Warning

- Everything in the Blender scene will be removed!
- The test might take a while. You can cancel it with esc key.

## Credit

- [MMD Tools](https://github.com/MMD-Blender/blender_mmd_tools) (GPLv3)
- [MMD Tools Helper](https://github.com/Hogarth-MMD/mmd_tools_helper) (GPLv3)
