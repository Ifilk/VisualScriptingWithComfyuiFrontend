import ast
import os

import numpy as np

import folder_paths


class String2Matrix:
    @classmethod
    def INPUT_TYPES(s):
        return {"required":
                    {"text": ("STRING", {"multiline": True, "dynamicPrompts": True})}}

    RETURN_TYPES = ('ND_ARRAY',)
    FUNCTION = "mat"
    CATEGORY = "numpy"

    def mat(self, text):
        s = text.replace(' ', ',').replace('\n', ',').replace(',,', ',')
        try:
            array = ast.literal_eval(s)
        except (ValueError, SyntaxError):
            raise ValueError("Error syntax")
        return {"result": (np.array(array, dtype=float),)}


class LoadMat:
    def __init__(self):
        self.input_dir = folder_paths.get_input_directory()

    @classmethod
    def INPUT_TYPES(s):
        input_dir = folder_paths.get_input_directory()
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f)) and f.endswith('.npy')]
        return {"required":
                    {"file": (sorted(files), {"file_upload": True})},
        }

    RETURN_TYPES = ('ND_ARRAY',)
    FUNCTION = "mat"
    CATEGORY = "numpy"

    def mat(self, file):

        return {"result": (np.load(os.path.join(self.input_dir, file)),)}


class MatTranspose:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "mat1": ("ND_ARRAY",),
        },
        }

    RETURN_TYPES = ('ND_ARRAY',)
    FUNCTION = "t"
    CATEGORY = "numpy"

    def t(self, mat1):
        return {"result": (mat1.T,)}


class RandMat:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "raw": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            "col": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff})
        },
        }

    RETURN_TYPES = ('ND_ARRAY',)
    FUNCTION = "mat"
    CATEGORY = "numpy"

    def mat(self, raw, col):
        mat3 = np.random.rand(raw, col)
        return {"result": (mat3,)}


class MatAdd:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "mat1": ("ND_ARRAY",),
            "mat2": ("ND_ARRAY",)
        },
        }

    RETURN_TYPES = ('ND_ARRAY',)
    FUNCTION = "add"
    CATEGORY = "numpy"

    def add(self, mat1, mat2):
        mat3 = mat1 + mat2
        return {"result": (mat3,)}


class MatSub:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "mat1": ("ND_ARRAY",),
            "mat2": ("ND_ARRAY",)
        },
        }

    RETURN_TYPES = ('ND_ARRAY',)
    FUNCTION = "add"
    CATEGORY = "numpy"

    def add(self, mat1, mat2):
        mat3 = mat1 - mat2
        return {"result": (mat3,)}


class MatHadamardProduct:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "mat1": ("ND_ARRAY",),
            "mat2": ("ND_ARRAY",)
        },
        }

    RETURN_TYPES = ('ND_ARRAY',)
    FUNCTION = "add"
    CATEGORY = "numpy"

    def add(self, mat1, mat2):
        mat3 = mat1 * mat2
        return {"result": (mat3,)}


class MatMul:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "left": ("ND_ARRAY",),
            "right": ("ND_ARRAY",)
        },
        }

    RETURN_TYPES = ('ND_ARRAY',)
    FUNCTION = "mat"
    CATEGORY = "numpy"

    def mat(self, left, right):
        mat3 = np.matmul(left, right)
        return {"result": (mat3,)}


class MatMulEle:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "mat1": ("ND_ARRAY",),
            "num": ("FLOAT",)
        },
        }

    RETURN_TYPES = ('ND_ARRAY',)
    FUNCTION = "mat"
    CATEGORY = "numpy"

    def mat(self, mat1, num):
        return {"result": (mat1 * num,)}


class Mat2String:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "mat": ("ND_ARRAY",),
        },
        }

    RETURN_TYPES = ('STRING',)
    FUNCTION = "mat"
    CATEGORY = "numpy"

    def mat(self, mat):
        return {"result": (str(mat),)}


class SaveMat:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "mat": ("ND_ARRAY",),
            "filename_prefix": ("STRING", {"default": "ComfyUI"})
        },
        }

    RETURN_TYPES = ()
    OUTPUT_NODE = True
    FUNCTION = "mat"
    CATEGORY = "numpy"

    def mat(self, mat, filename_prefix="ComfyUI",):
        subfolder = os.path.dirname(os.path.normpath(filename_prefix))
        filename = os.path.basename(os.path.normpath(filename_prefix))
        full_output_folder = os.path.join(self.output_dir, subfolder)
        if not os.path.exists(full_output_folder):
            os.makedirs(full_output_folder)
        np.save(full_output_folder + filename + '.npy', mat)
        return {}


class GetMatShape:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "mat": ("ND_ARRAY",),
        },
        }

    RETURN_TYPES = ('INT', 'INT')
    FUNCTION = "shape"
    CATEGORY = "numpy"

    def shape(self, mat):
        r, c = (mat.shape[0], mat.shape[1])
        return {"result": (r, c)}


NODE_CLASS_MAPPINGS = {
    'LoadMat': LoadMat,
    'RandMat': RandMat,
    'MatTranspose': MatTranspose,
    'MatAdd': MatAdd,
    'MatMul': MatMul,
    'Mat2String': Mat2String,
    'MatSub': MatSub,
    'MatHadamardProduct': MatHadamardProduct,
    'SaveMat': SaveMat,
    'GetMatShape': GetMatShape,
    'String2Matrix': String2Matrix

}
NODE_DISPLAY_NAME_MAPPINGS = {
    'LoadMat': 'Load Matrix',
    'RandMat': 'Random Matrix',
    'MatTranspose': 'Transpose Matrix',
    'MatAdd': 'Matrix Add',
    'MatMul': 'Matrix Multiply',
    'Mat2String': 'Matrix To String',
    'MatSub': 'Matrix Subtract',
    'MatHadamardProduct': 'Matrix Hadamard Product',
    'SaveMat': 'Save Matrix',
    'GetMatShape': 'Get Matrix Shape',
    'String2Matrix': 'Paser String To Matrix',
}
