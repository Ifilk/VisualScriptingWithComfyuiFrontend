import os
import sys
import json
import hashlib
import threading
import traceback
import math
import time
import random
import logging

# from PIL import Image, ImageOps, ImageSequence, ImageFile
# from PIL.PngImagePlugin import PngInfo

import numpy as np

from comfy.model_management import InterruptProcessingException

# import safetensors.torch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "comfy"))

import importlib
import folder_paths


class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False


any = AnyType("*")

interrupt_processing_mutex = threading.RLock()
interrupt_processing_v = False

global_variable = {}


def before_node_execution():
    # comfy.model_management.throw_exception_if_processing_interrupted()
    global interrupt_processing_v
    global interrupt_processing_mutex
    with interrupt_processing_mutex:
        if interrupt_processing_v:
            interrupt_processing_v = False
            raise InterruptProcessingException()


def interrupt_processing(value=True):
    # comfy.model_management.interrupt_current_processing(value)
    global interrupt_processing_v
    global interrupt_processing_mutex
    with interrupt_processing_mutex:
        interrupt_processing_v = value
    pass


class PutVariable:
    @classmethod
    def INPUT_TYPES(s):
        return {"required":
                    {'value': (any, []),
                     "name": ("STRING", {"default": "var1"})},
                }

    RETURN_TYPES = ()
    OUTPUT_NODE = True
    FUNCTION = "provide"
    CATEGORY = "base"

    def provide(self, value, name):
        global_variable[name] = value
        return {}


class GetVariable:
    @classmethod
    def INPUT_TYPES(s):
        return {"required":
                    {"name": ("STRING", {"default": "var1"})},
                }

    RETURN_TYPES = (any, )
    FUNCTION = "provide"
    CATEGORY = "base"

    def provide(self, name):
        if not name in global_variable.keys():
            raise KeyError(name)
        return {"result": (global_variable[name],)}


class Number:
    @classmethod
    def INPUT_TYPES(s):
        return {"required":
                    {"text": ("STRING", {"dynamicPrompts": True})}}

    RETURN_TYPES = ('INT', 'FLOAT')
    FUNCTION = "provide"
    CATEGORY = "base"

    def provide(self, text):
        return {"ui": {"text": text}, "result": (int(text), float(text),)}


class String:
    @classmethod
    def INPUT_TYPES(s):
        return {"required":
                    {"text": ("STRING", {"multiline": True, "dynamicPrompts": True})}}

    RETURN_TYPES = ('STRING',)
    FUNCTION = "provide"
    CATEGORY = "base"

    def provide(self, text):
        return {"ui": {"text": text}, "result": (text,)}


NODE_CLASS_MAPPINGS = {
    'PutVariable': PutVariable,
    'GetVariable': GetVariable,
    'Number': Number,
    'String': String,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    'PutVariable': 'Put Variable',
    'GetVariable': 'Get Variable',
    'Number': 'Number',
    'String': 'String',
}

EXTENSION_WEB_DIRS = {}


def get_module_name(module_path: str) -> str:
    """
    Returns the module name based on the given module path.
    Examples:
        get_module_name("C:/Users/username/ComfyUI/custom_nodes/my_custom_node.py") -> "my_custom_node"
        get_module_name("C:/Users/username/ComfyUI/custom_nodes/my_custom_node") -> "my_custom_node"
        get_module_name("C:/Users/username/ComfyUI/custom_nodes/my_custom_node/") -> "my_custom_node"
        get_module_name("C:/Users/username/ComfyUI/custom_nodes/my_custom_node/__init__.py") -> "my_custom_node"
        get_module_name("C:/Users/username/ComfyUI/custom_nodes/my_custom_node/__init__") -> "my_custom_node"
        get_module_name("C:/Users/username/ComfyUI/custom_nodes/my_custom_node/__init__/") -> "my_custom_node"
        get_module_name("C:/Users/username/ComfyUI/custom_nodes/my_custom_node.disabled") -> "custom_nodes
    Args:
        module_path (str): The path of the module.
    Returns:
        str: The module name.
    """
    base_path = os.path.basename(module_path)
    if os.path.isfile(module_path):
        base_path = os.path.splitext(base_path)[0]
    return base_path


def load_custom_node(module_path: str, ignore=set(), module_parent="custom_nodes") -> bool:
    module_name = os.path.basename(module_path)
    if os.path.isfile(module_path):
        sp = os.path.splitext(module_path)
        module_name = sp[0]
    try:
        logging.debug("Trying to load custom node {}".format(module_path))
        if os.path.isfile(module_path):
            module_spec = importlib.util.spec_from_file_location(module_name, module_path)
            module_dir = os.path.split(module_path)[0]
        else:
            module_spec = importlib.util.spec_from_file_location(module_name, os.path.join(module_path, "__init__.py"))
            module_dir = module_path

        module = importlib.util.module_from_spec(module_spec)
        sys.modules[module_name] = module
        module_spec.loader.exec_module(module)

        if hasattr(module, "WEB_DIRECTORY") and getattr(module, "WEB_DIRECTORY") is not None:
            web_dir = os.path.abspath(os.path.join(module_dir, getattr(module, "WEB_DIRECTORY")))
            if os.path.isdir(web_dir):
                EXTENSION_WEB_DIRS[module_name] = web_dir

        if hasattr(module, "NODE_CLASS_MAPPINGS") and getattr(module, "NODE_CLASS_MAPPINGS") is not None:
            for name, node_cls in module.NODE_CLASS_MAPPINGS.items():
                if name not in ignore:
                    NODE_CLASS_MAPPINGS[name] = node_cls
                    node_cls.RELATIVE_PYTHON_MODULE = "{}.{}".format(module_parent, get_module_name(module_path))
            if hasattr(module, "NODE_DISPLAY_NAME_MAPPINGS") and getattr(module,
                                                                         "NODE_DISPLAY_NAME_MAPPINGS") is not None:
                NODE_DISPLAY_NAME_MAPPINGS.update(module.NODE_DISPLAY_NAME_MAPPINGS)
            return True
        else:
            logging.warning(f"Skip {module_path} module for custom nodes due to the lack of NODE_CLASS_MAPPINGS.")
            return False
    except Exception as e:
        logging.warning(traceback.format_exc())
        logging.warning(f"Cannot import {module_path} module for custom nodes: {e}")
        return False


def init_external_custom_nodes():
    """
    Initializes the external custom nodes.

    This function loads custom nodes from the specified folder paths and imports them into the application.
    It measures the import times for each custom node and logs the results.

    Returns:
        None
    """
    base_node_names = set(NODE_CLASS_MAPPINGS.keys())
    node_paths = folder_paths.get_folder_paths("custom_nodes")
    node_import_times = []
    for custom_node_path in node_paths:
        possible_modules = os.listdir(os.path.realpath(custom_node_path))
        if "__pycache__" in possible_modules:
            possible_modules.remove("__pycache__")

        for possible_module in possible_modules:
            module_path = os.path.join(custom_node_path, possible_module)
            if os.path.isfile(module_path) and os.path.splitext(module_path)[1] != ".py": continue
            if module_path.endswith(".disabled"): continue
            time_before = time.perf_counter()
            success = load_custom_node(module_path, base_node_names, module_parent="custom_nodes")
            node_import_times.append((time.perf_counter() - time_before, module_path, success))

    if len(node_import_times) > 0:
        logging.info("\nImport times for custom nodes:")
        for n in sorted(node_import_times):
            if n[2]:
                import_message = ""
            else:
                import_message = " (IMPORT FAILED)"
            logging.info("{:6.1f} seconds{}: {}".format(n[0], import_message, n[1]))
        logging.info("")


def init_builtin_extra_nodes():
    """
    Initializes the built-in extra nodes in ComfyUI.

    This function loads the extra node files located in the "comfy_extras" directory and imports them into ComfyUI.
    If any of the extra node files fail to import, a warning message is logged.

    Returns:
        None
    """
    extras_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "comfy_extras")
    extras_files = [
        # "nodes_latent.py",
        # "nodes_hypernetwork.py",
        # "nodes_upscale_model.py",
        # "nodes_post_processing.py",
        # "nodes_mask.py",
        # "nodes_compositing.py",
        # "nodes_rebatch.py",
        # "nodes_model_merging.py",
        # "nodes_tomesd.py",
        # "nodes_clip_sdxl.py",
        # "nodes_canny.py",
        # "nodes_freelunch.py",
        # "nodes_custom_sampler.py",
        # "nodes_hypertile.py",
        # "nodes_model_advanced.py",
        # "nodes_model_downscale.py",
        # "nodes_images.py",
        # "nodes_video_model.py",
        # "nodes_sag.py",
        # "nodes_perpneg.py",
        # "nodes_stable3d.py",
        # "nodes_sdupscale.py",
        # "nodes_photomaker.py",
        # "nodes_cond.py",
        # "nodes_morphology.py",
        # "nodes_stable_cascade.py",
        # "nodes_differential_diffusion.py",
        # "nodes_ip2p.py",
        # "nodes_model_merging_model_specific.py",
        # "nodes_pag.py",
        # "nodes_align_your_steps.py",
        # "nodes_attention_multiply.py",
        # "nodes_advanced_samplers.py",
        # "nodes_webcam.py",
        # "nodes_audio.py",
        # "nodes_sd3.py",
        # "nodes_gits.py",
        # "nodes_controlnet.py",
    ]

    import_failed = []
    for node_file in extras_files:
        if not load_custom_node(os.path.join(extras_dir, node_file), module_parent="comfy_extras"):
            import_failed.append(node_file)

    return import_failed


def init_extra_nodes(init_custom_nodes=True):
    import_failed = init_builtin_extra_nodes()

    if init_custom_nodes:
        init_external_custom_nodes()
    else:
        logging.info("Skipping loading of custom nodes")

    if len(import_failed) > 0:
        logging.warning(
            "WARNING: some comfy_extras/ nodes did not import correctly. This may be because they are missing some dependencies.\n")
        for node in import_failed:
            logging.warning("IMPORT FAILED: {}".format(node))
        logging.warning(
            "\nThis issue might be caused by new missing dependencies added the last time you updated ComfyUI.")
        # if args.windows_standalone_build:
        #     logging.warning("Please run the update script: update/update_comfyui.bat")
        # else:
        #     logging.warning("Please do a: pip install -r requirements.txt")
        # logging.warning("")
