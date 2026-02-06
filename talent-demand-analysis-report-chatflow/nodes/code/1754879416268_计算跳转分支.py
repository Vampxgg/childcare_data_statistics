# -*- coding: utf-8 -*-
"""
节点ID: 1754879416268
节点标题: 计算跳转分支
节点描述: 
节点类型: code
"""

def main(target_index: str, end_index: int) -> dict:
    """
    分支跳转判断函数
    :param end_index: 用户最后会话执行到的分支编号
    :param target_index: 用户传的目标分支编号
    :return: { "branch_to_run": int, "msg": str }
             branch_to_run = -1 表示不允许执行
    """
    target_index = int(target_index)

    # 检查输入范围
    if not (0 <= target_index <= 13):
        return {"branch_to_run": -1, "msg": f"目标分支 {target_index} 超出范围"}

    # 回退：允许执行
    if target_index <= end_index:
        return {"branch_to_run": target_index, "msg": ""}

    # 正常向前：只能一步一步往前
    if target_index == end_index + 1:
        return {"branch_to_run": target_index, "msg": ""}

    # 跳过中间分支 → 不允许
    return {"branch_to_run": -1, "msg": f"不能从 {end_index} 跳到 {target_index}，请按顺序执行"}

