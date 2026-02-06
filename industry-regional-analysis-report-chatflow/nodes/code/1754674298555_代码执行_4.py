# -*- coding: utf-8 -*-
"""
节点ID: 1754674298555
节点标题: 代码执行 4
节点描述: 
节点类型: code
"""

import json
from typing import Any, Dict

def _parse_input(input_data: Any) -> Dict:
    """辅助函数，用于安全地解析输入，确保它是一个字典。"""
    if isinstance(input_data, dict):
        return input_data
    if isinstance(input_data, str):
        if not input_data.strip():
            return {}
        try:
            parsed = json.loads(input_data)
            # 这里允许解析后是任何类型，让主逻辑去判断
            return parsed
        except json.JSONDecodeError:
            # 对于无效JSON，返回空字典比抛出异常更灵活
            print("Dify Log/Warning: 输入的字符串不是一个有效的JSON格式，将视为空对象。")
            return {}
    # 如果输入为None或其他不支持的类型，也返回空字典
    return {}

def main(target_obj: Any, source_obj: Any) -> Dict[str, Any]:
    """
    根据源对象的'title'更新目标对象。
    此版本能智能处理扁平或单层嵌套的源对象和目标对象。
    """
    try:
        # 1. 安全地解析两个输入对象
        print("Dify Log: 开始解析输入对象...")
        target_data = _parse_input(target_obj)
        source_data_raw = _parse_input(source_obj)
        print("Dify Log: 输入对象解析成功。")
        
        # --- 智能解包 source_obj (此部分不变) ---
        data_to_use = source_data_raw
        if isinstance(source_data_raw, dict) and len(source_data_raw) == 1 and isinstance(list(source_data_raw.values())[0], dict):
            print(f"Dify Log: 检测到嵌套的源对象，自动进入内层对象 '{list(source_data_raw.keys())[0]}'。")
            data_to_use = list(source_data_raw.values())[0]
        
        # --- 提取源数据 (此部分不变) ---
        if not data_to_use or not isinstance(data_to_use, dict):
            raise ValueError("源对象解析后为空或不是有效对象，无法提取更新数据。")
        source_title = data_to_use.get("title")
        source_text = data_to_use.get("text")
        source_references = data_to_use.get("references")
        source_confirm = data_to_use.get("confirm")
        if source_title is None:
            raise ValueError("在源数据中未找到 'title' 字段，无法进行匹配。")
        print(f"Dify Log: 从源对象中提取到待匹配的 title: '{source_title}'")

        # --- 【核心修正】智能确定目标对象的搜索范围 ---
        search_area = target_data
        # 检查目标对象是否也是单层嵌套结构，如果是，则进入内层进行搜索
        if isinstance(target_data, dict) and len(target_data) == 1 and isinstance(list(target_data.values())[0], dict):
            key_name = list(target_data.keys())[0]
            print(f"Dify Log: 检测到嵌套的目标对象，将在内层 '{key_name}' 中进行搜索。")
            search_area = target_data[key_name] # 使用内层字典作为搜索区域
        # ---------------------------------------------------

        # 3. 遍历【正确的搜索区域】，查找并更新
        is_updated = False
        # 确保搜索区域是一个字典
        if isinstance(search_area, dict):
            for key, value in search_area.items(): # <--- 修改点：遍历 search_area 而不是 target_data
                if isinstance(value, dict) and value.get("title") == source_title:
                    print(f"Dify Log: 找到匹配项！正在更新目标对象中的 '{key}'...")
                    # 直接更新value，由于字典是可变对象，这将直接修改原始的target_data
                    value["text"] = source_text
                    value["references"] = source_references
                    value["confirm"] = source_confirm
                    is_updated = True
                    print(f"Dify Log: '{key}' 更新完成。")
                    break

        if not is_updated:
            print(f"Dify Log: 警告：在目标对象中未找到 title 为 '{source_title}' 的匹配项。未进行任何更新。")
        
        # 返回最外层的、被修改后的 target_data
        return {"result": target_data}

    except (ValueError, TypeError, KeyError, IndexError) as e:
        error_message = f"处理失败: {e}"
        print(f"Dify Log/Error: {error_message}")
        return {"error": error_message}
