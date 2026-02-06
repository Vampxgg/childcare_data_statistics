# -*- coding: utf-8 -*-
"""
节点ID: 1754651516960
节点标题: 整理数据结构
节点描述: 
节点类型: code
"""

from typing import List, Dict, Any
import json
def is_empty_dict(data: Any) -> bool:
    """Checks if a dictionary is considered empty."""
    if isinstance(data, dict):
        return not any(data.values())
    return False
def main(network: List[Dict[Any, Any]], postData: List[Dict[Any, Any]], private: List[Dict[Any, Any]]) -> Dict[str, Any]:
    """
    Filters out empty dictionaries from the input lists and returns a dictionary
    containing the filtered lists and a string representation of the result.
    """
    filtered_network = [item for item in network if not is_empty_dict(item)]
    filtered_postData = [item for item in postData if not is_empty_dict(item)]
    filtered_private = [item for item in private if not is_empty_dict(item)]
    result = {
        "network": filtered_network,
        "postData": filtered_postData,
        "private": filtered_private,
    }
    result_str = json.dumps(result, ensure_ascii=False)  # Convert to JSON string
    return {
        "result": result,
        "result_str": result_str
    }
