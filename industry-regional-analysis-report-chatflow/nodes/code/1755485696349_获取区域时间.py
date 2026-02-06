# -*- coding: utf-8 -*-
"""
节点ID: 1755485696349
节点标题: 获取区域时间
节点描述: 
节点类型: code
"""

import os
from typing import Dict

def main(input_a: str, input_b: str) -> Dict[str, str]:
    print(f"Dify Log: 接收到输入 A: '{input_a}'")
    print(f"Dify Log: 接收到输入 B: '{input_b}'")
    if input_a and input_a.strip():
        return {"time_range": input_a}
    elif input_b and input_b.strip():
        return {"time_range": input_b}
    else:
        return {"time_range": ""}


