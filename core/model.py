"""Module for finding MMD model components in Blender objects. (from MMD Tools Helper)"""

import logging
import sys

import bpy

logger = logging.getLogger("mmd_batch_test")
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(handler)


def find_root(obj: bpy.types.Object) -> bpy.types.Object | None:
    if obj is not None:
        if hasattr(obj, "mmd_type") and obj.mmd_type == "ROOT":
            return obj
        else:
            return find_root(obj.parent)
    else:
        return None


def find_armature(obj: bpy.types.Object) -> bpy.types.Object | None:
    """Find armatures that are children of MMDRoot."""
    mmd_root = find_root(obj)
    if mmd_root is None:
        logger.info("No MMD model is selected")
        return None

    armatures = []
    for child in mmd_root.children:
        if child and child.type == "ARMATURE":
            armatures.append(child)

    if not armatures:
        return None
    elif len(armatures) == 1:
        return armatures[0]
    else:
        logger.error(f"More than 1 armature found: {armatures}")


def find_meshes(obj: bpy.types.Object) -> list[bpy.types.Object] | None:
    mmd_root = find_root(obj)
    if mmd_root is None:
        logger.info("No MMD model is selected")
        return None

    meshes = []
    for child in mmd_root.children_recursive:
        if child and child.type == "MESH" and child.mmd_type == "NONE":
            meshes.append(child)

    return meshes


def find_rigid_bodies(obj: bpy.types.Object) -> list[bpy.types.Object] | None:
    mmd_root = find_root(obj)
    if mmd_root is None:
        logger.info("No MMD model is selected")
        return None

    rigidbodies = None
    for child in mmd_root.children:
        if child.type == "EMPTY" and child.name == "rigidbodies":
            rigidbodies = child

    return list(rigidbodies.children) if rigidbodies else []


def find_joints(obj: bpy.types.Object) -> list[bpy.types.Object] | None:
    mmd_root = find_root(obj)
    if mmd_root is None:
        logger.info("No MMD model is selected")
        return None

    joints = None
    for child in mmd_root.children:
        if child.type == "EMPTY" and child.name == "joints":
            joints = child

    return list(joints.children) if joints else []
