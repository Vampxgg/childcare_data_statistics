# -*- coding: utf-8 -*-
"""
节点ID: 17548201419460
节点标题: 计算存储的end_index和execution_history
节点描述: 
节点类型: code
"""

def main(branch_id: int, end_index: int, execution_history: list) -> dict:
    if branch_id is None:
        raise ValueError("缺少 branch_id 参数")

    # 更新 end_index
    if branch_id >= end_index:
        end_index = branch_id
    else:
        # branch_id <= end_index，说明回退或访问之前节点，不更新 end_index
        pass

    execution_history.append(branch_id)

    return {
        "message": f"分支 {branch_id} 执行完成，状态已更新",
        "end_index": end_index,
        "execution_history": execution_history
    }

