# -*- coding: utf-8 -*-
"""
节点ID: 17547367336160
节点标题: 提取器
节点描述: 
节点类型: code
"""

import re
from typing import Dict

def main(arg1: str) -> Dict[str, str]:
    # 提取 <think> 区块（包含标签）
    think_match = re.search(r"<think>.*?</think>", arg1, flags=re.DOTALL | re.IGNORECASE)
    thout = think_match.group(0).strip() if think_match else ""

    # 提取 <think> 之后的剩余部分
    remaining = re.sub(r"<think>.*?</think>", "", arg1, flags=re.DOTALL | re.IGNORECASE).strip()

    # 优先尝试提取 markdown 代码块
    md_match = re.search(r"```markdown\s*([\s\S]*?)\s*```", remaining, flags=re.IGNORECASE)
    if md_match:
        extracted = md_match.group(1).strip()
    else:
        # 无 markdown 代码块，直接使用剩余文本作为 markdown 内容
        extracted = remaining

    return {
        "querier_thout": thout,
        "querier_res": extracted
    }

