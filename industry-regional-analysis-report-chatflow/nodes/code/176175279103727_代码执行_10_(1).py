# -*- coding: utf-8 -*-
"""
节点ID: 176175279103727
节点标题: 代码执行 10 (1)
节点描述: 
节点类型: code
"""

import json
from typing import Any, List, Dict

def _parse_input_to_list(input_data: Any) -> List:
    # 1. 如果已经是列表，直接返回
    if isinstance(input_data, list):
        return input_data
    # 2. 如果是字符串，尝试解析为JSON
    if isinstance(input_data, str):
        # 去除前后空白和常见的LLM代码块标记
        clean_str = input_data.strip()
        if clean_str.startswith("```json"):
            clean_str = clean_str[7:]
        if clean_str.endswith("```"):
            clean_str = clean_str[:-3]
        clean_str = clean_str.strip()
        # 如果字符串为空，视为空列表
        if not clean_str:
            return []
        try:
            # 解析JSON字符串为Python对象
            parsed_data = json.loads(clean_str)
            # 确保解析后是列表类型
            if isinstance(parsed_data, list):
                return parsed_data
            else:
                # 如果解析出来不是列表（比如是个对象），则抛出类型错误
                raise TypeError(f"输入字符串解析后不是一个数组（列表），而是一个 {type(parsed_data).__name__}。")
        except json.JSONDecodeError:
            # 如果JSON格式无效，则抛出值错误
            raise ValueError("输入的字符串不是一个有效的JSON格式。")
    # 3. 如果是None，视为空列表
    if input_data is None:
        return []

    # 4. 对于其他所有不支持的类型，抛出类型错误
    raise TypeError(f"不支持的输入类型: {type(input_data).__name__}。请输入一个列表或JSON数组字符串。")


def main(input_array: Any) -> Dict[str, str]:
    try:
        print("Dify Log: 开始解析输入...")
        python_list = _parse_input_to_list(input_array)
        print("Dify Log: 输入解析为Python列表成功。")
        json_output_string = json.dumps(python_list, ensure_ascii=False, indent=2)
        print("Dify Log: 转换为JSON字符串成功。")
        return {
            "data": json_output_string
        }
    except (ValueError, TypeError, Exception) as e:
        # 捕获所有可能的错误（包括解析错误和转换错误）
        error_message = f"代码执行失败: {e}"
        print(f"Dify Log/Error: {error_message}")
        # 返回一个包含错误信息的字典
        return {
            "error": error_message
        }

