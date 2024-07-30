# 1.项目介绍
`VisualScriptingWithComfyuiFrontend`是一个基于 [ComfyUI](https://github.com/comfyanonymous/ComfyUI) 的可视化脚本框架，
该项目将ComfyUI的工作流交互执行与stable diffusion运行解耦合，并且保证文件目录结构不变下移除了后者相关代码。所以该项目也可以作为ComfyUI自定义节点编写的教程
# 2.文件结构
## 2.1 目录结构
| 文件/目录           | 描述          | 用途                 |
|-----------------|-------------|--------------------|
| /app            | 前端与用户管理目录   | 多用户管理和前端初始化        |
| /comfy          | comfy核心代码目录 | comfy_core部分必要代码   |
| /custom_nodes   | 自定义节点目录     | 存放自定义节点包           |
| /input          | 默认输入目录      | 默认的输入文件路径          |
| /output         | 默认输出目录      | 默认的输出文件路径          |
| /web            | 前端代码目录      | 前端代码               |
| execution.py    | prompt执行器   | node执行逻辑           |
| folder_paths.py | 路径管理器       | 管理默认路径             |
| main.py         | 启动脚本        | 启动comfy            |
| node_helpers.py | 节点工具代码      | 留存                 |
| nodes.py        | 默认节点与节点解析   | 声明默认节点与自定义节点包的解析代码 |
| server.py       | 后端服务器代码     | 后端服务器代码            |

## 2.2 关键文件与目录
### 2.2.1 /custom_nodes
用于存放自定义节点包，节点加载器会获取包中`__init__.py`的
`NODE_CLASS_MAPPINGS`, `NODE_DISPLAY_NAME_MAPPINGS` 和
`WEB_DIRECTORY` (其中`WEB_DIRECTORY`可留空)。载入节点和自定义web文件。
该项目已存放会用到的节点包作为自定义节点包的一部分，若需要创建新的自定义节点包
请查看 [第3节 自定义节点](#3-自定义节点包)
### 2.2.2 /input
用户通过UPLOAD相关操作上传文件的默认存储位置，在编写自定义节点需要导入文件使
请使用`folder_paths.get_input_directory()`获取存储位置
### 2.2.3 /output
用户通过SAVE类节点保存数据的默认存储存储位置，在编写自定义节点需要写入文件作输出时
请使用`folder_paths.get_output_directory()`获取存储位置。
### 2.2.4 /web
前端页面代码文件，通过`WEB_DIRECTORY`声明web扩展包会被放置在此目录下，可通过`'/scripts/'`路径
访问到前端接口。一般使用`/scripts/app.js`, `/scripts/api.js`。
`/scripts/widgets.js`文件声明了所有的预制前端组件
### 2.2.5 main.py
启动脚本`python main.py`

# 3. 自定义节点
## 3.1 自定义节点包目录结构
这里推荐使用`ComfyUI-Custom-Scripts`的目录结构
```text
/py/            -存放节点代码
/web/           -存放web扩展
/__init__.py
```
若使用该目录结构，`__init__.py`可使用以下通用代码：
```python
import glob
import importlib.util
import os
import sys

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

dire = os.path.abspath(os.path.join(os.path.dirname(__file__), "py"))
files = glob.glob(os.path.join(dire, "*.py"), recursive=False)
for file in files:
    name = os.path.splitext(file)[0]
    spec = importlib.util.spec_from_file_location(name, file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    if hasattr(module, "NODE_CLASS_MAPPINGS") and getattr(module, "NODE_CLASS_MAPPINGS") is not None:
        NODE_CLASS_MAPPINGS.update(module.NODE_CLASS_MAPPINGS)
        if hasattr(module, "NODE_DISPLAY_NAME_MAPPINGS") and getattr(module, "NODE_DISPLAY_NAME_MAPPINGS") is not None:
            NODE_DISPLAY_NAME_MAPPINGS.update(module.NODE_DISPLAY_NAME_MAPPINGS)

WEB_DIRECTORY = "./web"
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
```
## 3.2 自定义节点声明
通常一个节点声明如下：
```python
class ExampleCustomNode:
    @classmethod
    def INPUT_TYPES(s):
        return {"required":
                    ...,
                "hidden":
                    ...
                }

    RETURN_TYPES = (... ,)
    FUNCTION = "run"
    CATEGORY = "example"

    def run(self, text):
        ...
        return (...)
    
NODE_CLASS_MAPPINGS = {
    'ExampleCustomNode': ExampleCustomNode
}
NODE_DISPLAY_NAME_MAPPINGS = {
    'ExampleCustomNode': 'Example Custom Node'
}
```
- 函数`INPUT_TYPES`用于声明该节点需要的参数。required表示显式声明该节点所需参数。
格式为`"name": ("TYPE", {})`
- --
- `name` 是节点展示该输入的名字
- `TYPE` 用于简单的类型检查，只有TYPE相同的才能相连。"TYPE"除了是字符串，还可以是字符串列表，表示该输入类型为枚举
- `{}` 表示设定属性值，一般情况下可为空。
```python
# 设置多行输入框
{"multiline": True, "dynamicPrompts": True}
# 设置默认值与范围
{"default": 0, "min": 0, "max": 0xffffffffffffffff}
```
---
- `RETURN_TYPES` 表示声明返回值类型列表，与TYPE对应。
- `FUNCTION` 表示调用的函数名
- `CATEGORY` 表示该节点所在的目录，显示在右键菜单里，可使用格式`.../.../...`表示多级目录
- `NODE_CLASS_MAPPINGS` 节点声明字典。key为节点名字，value为类名
- `NODE_DISPLAY_NAME_MAPPINGS` 节点展示名声明字典。key为节点名字，value为展示名