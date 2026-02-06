# -*- coding: utf-8 -*-
"""
节点ID: 1754991511949
节点标题: echart转图片
节点描述: 
节点类型: code
"""

import requests
from typing import Dict, Optional

user_token = "123456789"  # 请赋值你的token

def main(md_content: str) -> Dict[str, Optional[str]]:
    api_url = "http://119.45.167.133:17752/api/echarts/convert-markdown"
    headers = {
        "Authorization": f"Bearer {user_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "md_content": md_content,
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=(10, 60))
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"❌ 网络请求失败: {str(e)}")

    try:
        result = response.json()
    except ValueError:
        raise RuntimeError("❌ 返回内容非 JSON 格式")

    # 检查接口状态
    if not result.get("status", True):
        raise RuntimeError(f"❌ 接口调用失败: {result.get('message', '未知错误')}")

    data = result.get("data", {})
    if not isinstance(data, dict):
        raise RuntimeError("❌ 返回数据格式异常")

    return {
         "md_content": data.get("md_content")
    }

