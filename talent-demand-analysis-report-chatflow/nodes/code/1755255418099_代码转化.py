# -*- coding: utf-8 -*-
"""
节点ID: 1755255418099
节点标题: 代码转化
节点描述: 
节点类型: code
"""

import json

def transform_to_chapter_based_structure(source_data: dict) -> list:
    """
    将策略性搜索JSON转换为以章节为单位的、包含多个文档的列表结构。

    Args:
        source_data: 从V2.0 prompt生成的原始字典数据。

    Returns:
        一个列表，其中每个元素都是一个代表章节的字典。
    """
    final_output_list = []
    strategy_data = source_data.get("search_strategy_for_report", {})

    # 预定义一个通用的local_queries，可以根据需要为每个章节定制
    # 在这个例子中，我们为所有章节使用相同的local_queries
    common_local_queries = [
    ]

    # 遍历每个章节的数据，将章节名作为doc_id
    for chapter_id, chapter_content in strategy_data.items():
        
        # 为当前章节收集所有的web queries
        current_chapter_web_queries = []
        if "queries" in chapter_content and chapter_content["queries"]:
            current_chapter_web_queries.extend(chapter_content["queries"])
        if "supply_queries" in chapter_content and chapter_content["supply_queries"]:
            current_chapter_web_queries.extend(chapter_content["supply_queries"])
        if "demand_queries" in chapter_content and chapter_content["demand_queries"]:
            current_chapter_web_queries.extend(chapter_content["demand_queries"])

        # 如果这个章节有查询，就创建一个文档
        if current_chapter_web_queries:
            chapter_doc = {
                "doc_id": chapter_id, # 使用章节名作为doc_id
                "local_queries": common_local_queries,
                "web_queries": current_chapter_web_queries
            }
            final_output_list.append(chapter_doc)

    return final_output_list

def main(arg1: str) -> dict:
    # 1. 将JSON字符串解析为Python字典
    source_dict = json.loads(arg1)
      # 2. 调用新的转换函数
    transformed_data = transform_to_chapter_based_structure(source_dict)
    # 3. 将结果格式化为美观的JSON字符串
    # final_json_output = json.dumps(transformed_data, indent=4, ensure_ascii=False)
    return {
        "querier": transformed_data,
        "querier_str": str(transformed_data),
    }

