# -*- coding: utf-8 -*-
"""
节点ID: 17617527910375
节点标题: 代码执行 3 (1)
节点描述: 
节点类型: code
"""

import json
from typing import Dict, Any, Union

def _safe_to_dict(raw_input: Any) -> Dict:
    """
    一个非常健壮的辅助函数，尽最大努力将任何输入转换为字典。
    如果失败，则安全地返回一个空字典 {}。
    """
    if isinstance(raw_input, dict):
        return raw_input
    
    if isinstance(raw_input, str):
        try:
            if raw_input.strip():
                data = json.loads(raw_input)
                if isinstance(data, dict):
                    return data
        except json.JSONDecodeError:
            pass
            
    return {}

def main(raw_input: Union[Dict, str, None]) -> Dict[str, Any]:
    """
    健壮地从用户输入中提取 "confirm" 字段，并同时返回解析后的原始对象。
    - 能够处理对象、JSON字符串、空值和单层嵌套输入。
    - 如果 "confirm" 键不存在，会返回一个默认值。
    """
    # 步骤 1: 定义 'confirm' 的默认值
    DEFAULT_CONFIRM = -1

    # 步骤 2: 将任何形式的输入安全地转换为一个字典。
    # 这个解析后的对象就是我们最终要返回的“原始对象”。
    parsed_object = _safe_to_dict(raw_input)

    # 步骤 3: 确定从哪个字典里搜索 'confirm' (处理可能的嵌套)
    target_dict = parsed_object # 默认在顶层搜索
    # 如果是 {"some_key": {"confirm": ...}} 这样的单层嵌套结构，则自动进入内层
    if len(parsed_object) == 1 and isinstance(list(parsed_object.values())[0], dict):
        print("Dify Log: 检测到嵌套输入，将在内层对象中查找'confirm'。")
        target_dict = list(parsed_object.values())[0]

    # 步骤 4: 从目标字典中安全地提取 'confirm' 的值
    confirm_value = target_dict.get("confirm", DEFAULT_CONFIRM)

    # 步骤 5: 将提取出的值和解析后的原始对象一起打包返回
    # Dify会根据这里的键名，自动创建两个输出变量：'confirm_value' 和 'output_object'
    return {
        "confirm_value": confirm_value,
        "output_object": parsed_object 
    }

