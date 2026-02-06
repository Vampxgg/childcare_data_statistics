# -*- coding: utf-8 -*-
"""
节点ID: 1754647350021
节点标题: 提取器
节点描述: 
节点类型: code
"""

import re
import json

def main(arg1: str) -> dict:
    m = re.search(r"<think>.*?</think>", arg1, flags=re.DOTALL)
    thout = m.group(0) if m else ""
    res = re.sub(r"<think>.*?</think>", "", arg1, flags=re.DOTALL).strip()
    pattern = r"```json\s*([\s\S]*?)\s*```"
    m2 = re.search(pattern, res, flags=re.DOTALL)
    if m2:
        extracted = m2.group(1).strip()
    else:
        start = res.find('[')
        end = res.rfind(']')
        if start != -1 and end != -1 and end > start:
            extracted = res[start:end+1].strip()
        else:
            extracted = ""
    return {
        "querier_thout": thout,
        "querier_res": extracted,
    }

