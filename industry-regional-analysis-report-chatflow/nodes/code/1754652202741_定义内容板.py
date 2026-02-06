# -*- coding: utf-8 -*-
"""
节点ID: 1754652202741
节点标题: 定义内容板
节点描述: 
节点类型: code
"""

import json
from typing import Dict, Any, Union

def main(raw_input: Union[Dict[str, Any], str, None]) -> Dict[str, Any]:
    structured_report = {}
    # 步骤 1: 输入验证和标准化 (与之前版本相同)
    data_dict = None
    if not raw_input:
        print("[!] Input is empty (None or empty string), cannot perform conversion. Returning empty report.")
        return {"report": {}}

    if isinstance(raw_input, str):
        try:
            data_dict = json.loads(raw_input)
        except json.JSONDecodeError:
            return {"error": f"Input is a string, but cannot be parsed as valid JSON. Content: '{raw_input[:100]}...'"}
    elif isinstance(raw_input, dict):
        data_dict = raw_input
    else:
        return {"error": f"Unsupported input type. Must be an object or JSON string, but received {type(raw_input).__name__}."}

    # 步骤 2: 安全地提取 'mockAnalysisSteps' 数组 (与之前版本相同)
    steps_list = data_dict.get("mockAnalysisSteps")

    if not isinstance(steps_list, list):
        error_msg = "'mockAnalysisSteps' key is missing or its value is not a list (array)."
        print(f"[!] {error_msg}")
        return {"report": {}}

    # 步骤 3: 遍历数组并构建新的对象结构 (已更新)
    print(f"[~] Found {len(steps_list)} steps, starting conversion...")
    for index, step in enumerate(steps_list):
        if not isinstance(step, dict):
            print(f"[!] Warning: Element at index {index} in 'mockAnalysisSteps' array is not an object, skipping.")
            continue

        step_id = step.get("id")
        step_title = step.get("title")

        if isinstance(step_id, str) and step_id and step_title is not None:
            # === 改动点在这里 ===
            # 在构建对象时，添加了 confirm 和 check 字段
            structured_report[step_id] = {
                "title": step_title,
                "text": "",
                "references": [],
                "confirm": -1    
            }
            print(f"[+] Processed ID: '{step_id}'")
        else:
            print(f"[!] Warning: Step at index {index} is missing a valid 'id' or 'title', skipping. Content: {step}")

    # 步骤 4: 返回最终结果 (与之前版本相同)
    print("[+] Data conversion complete.")
    return {
        "mockAnalysisContent": structured_report
    }

