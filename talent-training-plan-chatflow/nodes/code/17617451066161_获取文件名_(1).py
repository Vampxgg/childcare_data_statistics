# -*- coding: utf-8 -*-
"""
节点ID: 17617451066161
节点标题: 获取文件名 (1)
节点描述: 
节点类型: code
"""

def main(files) -> dict:
    # 提取每个对象的 filename 字段
    filenames = [f.get("filename", "") for f in files if isinstance(f, dict)]
    
    # 使用英文逗号连接
    arg1 = ",".join(filenames)
    
    return {
        "result": arg1
    }

