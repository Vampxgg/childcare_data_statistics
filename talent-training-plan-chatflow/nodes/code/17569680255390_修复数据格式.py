# -*- coding: utf-8 -*-
"""
节点ID: 17569680255390
节点标题: 修复数据格式
节点描述: 
节点类型: code
"""

import re
import sys
from typing import Tuple, Dict, Any
 
def normalize_md_newlines(md_text: str) -> Tuple[str, int]:
    """
    规范化 Markdown 文本中的换行符，确保段落、列表和表格间有正确的空行。
    此函数执行三项关键操作：
    1.  将常规段落间的单个换行符 `\n` 替换为双换行符 `\n\n`。
    2.  确保普通文本行与紧随其后的列表（有序或无序）之间有空行。
    3.  确保任何文本行与紧随其后的表格之间由两个换行符分隔。
 
    此函数设计为“失败安全”：如果处理过程中发生任何错误，它将返回原始文本。
 
    Args:
        md_text (str): 包含 Markdown 格式的原始字符串。
 
    Returns:
        Tuple[str, int]: 一个元组，包含处理结果。
            - 成功时: (fixed_text, num_fixes) -> 修复后的文本和修复总数（>= 0）。
            - 失败时: (original_md_text, -1) -> 原始文本和一个负数错误码。
    """
    if not isinstance(md_text, str):
        print("错误: 内部处理函数接收到的内容不是字符串。", file=sys.stderr)
        return md_text, -1
 
    try:
        total_fixes = 0
        current_text = md_text
 
        # --- 步骤 1: 通用单换行符修复 (保守策略) ---
        # 这个模式寻找一个以[字母/数字/常见标点/中日韩字符]结尾的行，后跟一个以[字母/中日韩字符]开头的行。
        # \u4e00-\u9fa5 是中文字符的基本范围。
        # 这是一个相对安全的模式，用于修复最常见的段落错误。
        general_pattern = re.compile(r"([a-zA-Z0-9\.\?\]\)\u4e00-\u9fa5。])\n([a-zA-Z\(\[\u4e00-\u9fa5])")
        current_text, fixes1 = re.subn(general_pattern, r'\1\n\n\2', current_text)
        total_fixes += fixes1
        
        # --- 步骤 2: 列表前的特定修复 (新功能) ---
        # 这个模式专门处理文本行和列表（有序或无序）之间的间距问题。
        # ([^\n])          - 捕获组1: 匹配任何非换行符的字符（通用，处理中文标点）。
        # \n               - 匹配一个换行符（我们只关心一个换行符的情况）。
        # (\s*              - 捕获组2: 匹配整个列表项的行。
        #    (?:(?:\d+\.)|[\*\-\+])  - 列表标记: 匹配 "1." 或 "*" 或 "-" 或 "+"。
        #    \s+.*)          - 列表标记后的空格和该行的其余所有内容。
        list_pattern = re.compile(r"([^\n])\n(\s*(?:(?:\d+\.)|[\*\-\+])\s+.*)")
        current_text, fixes2 = re.subn(list_pattern, r'\1\n\n\2', current_text)
        total_fixes += fixes2
        
        # --- 步骤 3: 表格前的特定修复 ---
        # 这个模式专门处理文本行和表格之间的间距问题（0个或1个\n）。
        table_pattern = re.compile(r"([^\n])\n?(\s*\|[^\n]+\n\s*\|[:\s|-]*-[^|\n]*\|?)")
        current_text, fixes3 = re.subn(table_pattern, r'\1\n\n\2', current_text)
        total_fixes += fixes3
 
        return current_text, total_fixes
 
    except Exception as e:
        print(f"错误: 在执行正则表达式替换时发生未知错误: {e}", file=sys.stderr)
        return md_text, -1
 
def main(md_text: str) -> dict:
    """
    主函数。
    """
    
    fixed_text, num_fixes = normalize_md_newlines(md_text)

    if num_fixes > 0:
        print(f"处理成功！修复了 {num_fixes} 处。")
    elif num_fixes == 0:
        print(f"处理成功！文本格式正确，无需修复。")
    else:
        print(f"处理失败！")
    return {
        "md_text": fixed_text,
    }
