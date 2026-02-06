# -*- coding: utf-8 -*-
"""
节点ID: 1765164099685
节点标题: 提取json
节点描述: 
节点类型: code
"""

import re
import json
from typing import Dict, Optional, Any
def extract_json_block(text: str) -> Optional[str]:
    """
    从输入文本中提取 JSON 代码块。
    优先匹配 markdown 中的 ```json``` 块。
    如果失败，则尝试直接解析整个文本是否为 JSON。
    """
    if not isinstance(text, str):
        print(f"Error: extract_json_block received non-string input: {type(text)}. Attempting conversion.")
        try:
            text = str(text)
        except Exception as e:
            print(f"Error: Failed to convert input to string: {e}")
            return None
    # 1. 优先提取 ```json``` 代码块
    json_block_match = re.search(r"```json\s*([\s\S]*?)\s*```", text, re.IGNORECASE | re.DOTALL)
    if json_block_match:
        json_content = json_block_match.group(1).strip()
        try:
            json.loads(json_content) # 尝试解析以验证
            return json_content # 如果有效，则返回这个 JSON 字符串
        except json.JSONDecodeError:
            print(f"Warning: Content within ```json``` block is not valid JSON. Full content: \n{json_content}\n")
            # 如果代码块内容无效，不做回退，因为明确指定了要代码块中的内容
            # 所以这里继续返回 None，或者如果希望回退，则可以在这里添加回退逻辑
            pass # 发生错误，继续尝试下一个逻辑 (即整个文本是否为JSON)
    # 2. 如果没有 ```json``` 块，或者 ```json``` 块内容不合法，则尝试将整个文本作为 JSON 解析
    try:
        stripped_text = text.strip()
        json.loads(stripped_text) # 尝试解析以验证
        return stripped_text # 如果整个文本是有效 JSON，则返回它
    except json.JSONDecodeError:
        print(f"Info: No ```json``` block found or entire text is not valid JSON. Full text: \n{text}\n")
        return None # 无法提取或解析 JSON
def main(llm_output_text: Optional[str]) -> Dict[str, Any]:
    """
    从 llm_output_text 中提取 ```json``` 代码块内容，并作为字符串返回。
    """
    if not isinstance(llm_output_text, str) or not llm_output_text.strip():
        print("Warning: llm_output_text is not a valid string or is empty.")
        return {
            "result": None, # 返回 None 更准确，表示未找到有效 JSON
        }
    # 直接从 llm_output_text 中提取 JSON
    extracted_json_str = extract_json_block(llm_output_text)
    return {
        "result": extracted_json_str,
    }
