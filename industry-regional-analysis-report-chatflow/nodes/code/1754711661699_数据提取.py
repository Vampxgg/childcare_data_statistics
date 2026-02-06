# -*- coding: utf-8 -*-
"""
节点ID: 1754711661699
节点标题: 数据提取
节点描述: 
节点类型: code
"""

import json
from typing import Any, Dict, List, Union

def _parse_input(data: Any, expected_type: type, input_name: str) -> Union[List, Dict]:
    """
    辅助函数：安全地解析输入，并能自动解包 `[{"result": [...]}]` 结构。
    (此函数由您提供，保持不变)
    """
    # 自动解包 `result` 结构（针对已经是Python对象的输入）
    if isinstance(data, list) and len(data) == 1 and isinstance(data[0], dict) and 'result' in data[0]:
        print(f"Dify Log: 在 '{input_name}' 中检测到并解包 'result' 结构。")
        data = data[0]['result']
    
    if isinstance(data, expected_type):
        return data
        
    if isinstance(data, str):
        try:
            # 处理空字符串
            parsed_data = json.loads(data) if data.strip() else expected_type()
            # 自动解包 `result` 结构（针对解析字符串后的输入）
            if isinstance(parsed_data, list) and len(parsed_data) == 1 and isinstance(parsed_data[0], dict) and 'result' in parsed_data[0]:
                 print(f"Dify Log: 在解析后的 '{input_name}' 中检测到并解包 'result' 结构。")
                 parsed_data = parsed_data[0]['result']
            
            if isinstance(parsed_data, expected_type):
                return parsed_data
            else:
                 raise TypeError(f"输入 '{input_name}' 解析后的JSON类型 ({type(parsed_data).__name__})与期望类型 ({expected_type.__name__}) 不符。")

        except json.JSONDecodeError:
            raise ValueError(f"输入 '{input_name}' 不是一个有效的JSON字符串。")
            
    if data is None:
        return expected_type()
    
    raise TypeError(f"输入 '{input_name}' 的类型不受支持或结构不正确: {type(data).__name__}。期望类型: {expected_type.__name__}")


def main(or_obj: Any, external_data: Any) -> Dict[str, Any]:
    """
    Dify代码节点主函数 (已重构)。
    将统一的外部数据源中的 `retrieve_data` 和 `online_data`
    根据 `doc_id` 合并到 `or_obj` (基础幻灯片结构) 中。
    
    :param or_obj: 基础结构，一个包含多个幻灯片(slide)对象的列表。
    :param external_data: 统一的外部数据源，已包含所有需要注入的数据。
    :return: 一个字典，包含合并后的列表及其字符串表示。
    """
    try:
        # 步骤 1: 解析输入
        base_list = _parse_input(or_obj, list, "or_obj")
        source_list = _parse_input(external_data, list, "external_data")

        # 步骤 2: 为统一的源数据创建一个以 doc_id 为键的查找表
        # 表的值是整个slide对象，方便后续获取多个字段
        source_lookup = {
            item.get('doc_id'): item 
            for item in source_list 
            if item.get('doc_id')
        }
        print(f"Dify Log: 已为 {len(source_lookup)} 个有效源数据项创建查找表。")

        # 步骤 3: 遍历基础结构，在 slide 层级注入数据
        for slide in base_list:
            doc_id = slide.get("doc_id")
            if not doc_id:
                # 确保即使没有id，这些字段也存在，保持数据结构一致性
                slide['retrieve_data'] = []
                slide['web_data'] = []
                continue
            
            # 从查找表中寻找匹配项
            match = source_lookup.get(doc_id)

            if match:
                # 如果找到匹配项，安全地获取数据并注入
                slide['retrieve_data'] = match.get('retrieve_data', [])
                slide['online_data'] = match.get('web_data', [])
            else:
                # 如果没有找到匹配项，明确地将空列表注入
                slide['retrieve_data'] = []
                slide['online_data'] = []
            
            slide.pop('hybrid_queries', None)
        
        print("Dify Log: 数据成功合并到 slide 层级。")
        # 步骤 4: 返回成功的结果 (保持您原有的双输出格式)
        output_str = json.dumps(base_list, ensure_ascii=False)
        return {"output": base_list, "output_str": output_str}

    except (ValueError, TypeError) as e:
        error_message = {"error": f"处理失败: {str(e)}"}
        print(f"Dify Log/Error: {e}")
        return {"output": error_message, "output_str": json.dumps(error_message)}

