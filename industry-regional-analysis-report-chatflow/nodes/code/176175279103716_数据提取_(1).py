# -*- coding: utf-8 -*-
"""
节点ID: 176175279103716
节点标题: 数据提取 (1)
节点描述: 
节点类型: code
"""

import json
import re
from typing import Any, Dict, List, Union
try:
    import json_repair
except ImportError:
    raise ImportError("依赖 'json-repair' 未安装。请在Dify的 '设置' -> '依赖管理' 中添加它。")

# ==============================================================================
# 用户配置区: 在这里定义你期望的JSON输出结构模板！
# ==============================================================================
CONFIG = {
    "expected_json_template": {
        "title": "",
        "text": "",
        "references": [],
        "confirm": -1
    }
}
# ==============================================================================

# V3.1 核心修改点
def _clean_code_block_content(match: re.Match) -> str:
    """
    回调函数：针对性修复/解码单个代码块内部的内容。
    
    V3.1 核心逻辑变更:
    对于 echarts/json 块, 我们不再执行 'json_repair.loads -> json.dumps' 的 "修复再编码" 流程。
    因为这会导致后续整个大JSON编码时, 对已经干净的JSON字符串再次转义, 造成双重转义。

    正确思路是 "解码": 原始的 `content` 是一个被JSON转义过的字符串 (如 `{\\"key\\": \\"value\\"}`),
    我们要做的是把它解码回它在Markdown中应有的样子 (即 `{"key": "value"}`), 也就是去除那层额外的转义。
    """
    lang = match.group(1).lower().strip() if match.group(1) else ""
    content = match.group(2)
    
    # 默认使用原始内容，防止解码失败
    decoded_content = content

    if lang in ['echarts', 'json']:
        try:
            # 关键操作：使用 json.loads 将JSON字面量字符串解码为正常的Python字符串。
            # 例如，输入 `{\\"key\\": \\"value\\"}` (Python中表示为 '{\\"key\\": \\"value\\"}') 
            # `json.loads` 会将其转换为 `{"key": "value"}` (普通的Python字符串)。
            # 这正是我们想要的、可以直接嵌入Markdown的干净代码。
            # 我们需要先把它包装成一个有效的JSON字符串字面量，即 `"` + content + `"`。
            temp_json_string_literal = f'"{content}"'
            decoded_content = json.loads(temp_json_string_literal)
            
        except (json.JSONDecodeError, TypeError):
            # 如果解码失败，说明内容可能不是一个标准的JSON字符串字面量，
            # 可能是因为 LLM 输出不稳定。此时退回使用原始 content 是一种安全的策略。
            # 同时, 执行一次基础的、手动的替换作为降级方案，应对简单情况。
            decoded_content = content.replace('\\n', '\n').replace('\\"', '"').replace("\\'", "'").replace('\\`', '`')
    else:
        # 其他类型代码块的通用清理，逻辑保持不变
        decoded_content = content.replace('\\n', '\n').replace('\\"', '"').replace("\\'", "'")
        decoded_content = decoded_content.replace('\\`', '`')
        
    return f"```{lang}\n{decoded_content}\n```"


def _clean_markdown_string_aggressively(md_string: str) -> str:
    """
    攻击性地清洗Markdown字符串，修复内部代码块。
    (此函数沿用V2版本的强大逻辑, 调用了更新后的回调函数)
    """
    code_block_pattern = re.compile(r'```([\w]*)?\n([\s\S]*?)\n```', re.DOTALL)
    cleaned_string = code_block_pattern.sub(_clean_code_block_content, md_string)
    # 额外清理：有时在代码块之外也可能残留 `\\n` 等，做一次全局清理更保险。
    return cleaned_string.replace('\\n', '\n').replace('\\"', '"')

# 以下的 main 函数及其他辅助函数无需修改，它们的设计是稳健的。
# ... (main, _extract_and_clean_field_content 函数保持原样) ...

def main(raw_input: Any) -> Dict[str, Any]:
    """
    超级智能代码执行节点 (V3.1 - 精准去转义版)。
    """
    if not isinstance(raw_input, str):
        input_str = str(raw_input)
    else:
        input_str = raw_input

    if not input_str.strip():
        raise ValueError("输入为空或只包含空白字符。")

    # 准备工作
    template = CONFIG["expected_json_template"]
    field_names = list(template.keys())
    cleaned_object = template.copy() # 使用模板作为基础

    # 核心流程：遍历模板中的字段，去原始字符串中提取并清洗对应内容
    for i, field_name in enumerate(field_names):
        next_field_name = field_names[i + 1] if i + 1 < len(field_names) else None

        if next_field_name:
            pattern = re.compile(f'"{re.escape(field_name)}"\s*:\s*(.*?)\s*,\s*"{re.escape(next_field_name)}"', re.DOTALL)
        else:
            pattern = re.compile(f'"{re.escape(field_name)}"\s*:\s*(.*)\s*}}?$', re.DOTALL)

        match = pattern.search(input_str)
        
        if match:
            content_str = match.group(1).strip()
            cleaned_content = None
            if content_str.startswith('"'):
                cleaned_str_value = content_str[1:-1]
                cleaned_content = _clean_markdown_string_aggressively(cleaned_str_value)
            elif content_str.startswith('[') or content_str.startswith('{'):
                try:
                    cleaned_content = json_repair.loads(content_str)
                except Exception:
                    cleaned_content = template[field_name]
            else:
                try:
                    cleaned_content = json.loads(content_str)
                except Exception:
                    cleaned_content = template[field_name]
            
            cleaned_object[field_name] = cleaned_content
        else:
            pass

    # 返回最终结果
    output = {
        "cleaned_object": cleaned_object,
        "cleaned_string": json.dumps(cleaned_object, ensure_ascii=False, indent=2)
    }

    return output
