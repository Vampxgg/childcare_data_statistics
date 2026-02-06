# -*- coding: utf-8 -*-
"""
节点ID: 1765164153379
节点标题: 剔除不相干内容
节点描述: 
节点类型: code
"""

# import json
# from typing import List, Dict, Any

# def is_empty_dict(data: Any) -> bool:
#     """Checks if a dictionary is considered empty.
#     Handles nested structures as well."""

#     if isinstance(data, dict):
#         return not any(data.values())  # If *all* values are falsy, it's empty.
#     return False

# def main(
#     original_search_results: Dict[str, Any],
#     llm_evaluation_output: str = None
# ) -> Dict[str, Any]:
#     """Optimized version for speed and removes empty objects."""

#     evaluation_map = {}
#     if llm_evaluation_output:
#         try:
#             llm_evaluation_output: List[Dict[str, Any]] = json.loads(llm_evaluation_output)
#             evaluation_map = {item["source_id"]: item for item in llm_evaluation_output}
#         except json.JSONDecodeError as e:
#             print(f"Warning: Error parsing LLM output: {e}. Ignoring filtering.")

#     career_postings = []
#     enterprise_infos = []
#     filtered_results = []

#     original_search_results_list = original_search_results[0].get("result", [])

#     for doc_item in original_search_results_list:
#         web_data = doc_item.get("web_data")
#         if not web_data:
#             filtered_results.append(doc_item)
#             continue

#         # Extract career postings, filtering out empty dicts
#         if "career_postings" in web_data and "data" in web_data["career_postings"]:
#             career_postings.extend([item for item in web_data["career_postings"]["data"] if not is_empty_dict(item)])

#         # Extract enterprise info, filtering out empty dicts
#         if "enterprise_infos" in web_data:
#             enterprise_data = web_data["enterprise_infos"]
#             if "data" in enterprise_data:
#                 enterprise_infos.extend([item for item in enterprise_data["data"] if not is_empty_dict(item)])
#             elif not is_empty_dict(enterprise_data):  # Handle the case where enterprise_infos is a single dict
#                 enterprise_infos.append(enterprise_data)

#         # Process all_source_list based on LLM evaluation
#         comprehensive_data = web_data.get("comprehensive_data", {})
#         all_source_list = comprehensive_data.get("all_source_list", [])

#         if all_source_list:  # Skip processing when all_source_list is empty
#             filtered_all_source_list = []
#             if evaluation_map:
#                 for source_data in all_source_list:
#                     source_id = source_data.get("source_id")
#                     if source_id:
#                         evaluation = evaluation_map.get(source_id)
#                         if evaluation is None or evaluation.get("relevance") != "不相关":
#                             filtered_all_source_list.append(source_data)
#                     else:
#                         filtered_all_source_list.append(source_data)
#             else:
#                 filtered_all_source_list = all_source_list

#             if filtered_all_source_list: #Check if filtered all source list isnt empty before setting
#                 if "comprehensive_data" not in web_data:
#                    web_data["comprehensive_data"]={}

#                 web_data["comprehensive_data"]["all_source_list"] = filtered_all_source_list
#                 filtered_results.append(doc_item)

#     career_postings = [item for item in career_postings if not is_empty_dict(item)] #Remove empty stuff last
#     enterprise_infos = [item for item in enterprise_infos if not is_empty_dict(item)]

#     # String conversion SHOULD happen only ONCE at the OUTPUT stage
#     career_postings_str = str(career_postings)
#     enterprise_infos_str = str(enterprise_infos)
#     filtered_results_str = str(filtered_results)

#     return {
#         "output_str": filtered_results_str,
#         "output": filtered_results,
#         "career_postings": career_postings,
#         "career_postings_str": career_postings_str,
#         "enterprise_infos": enterprise_infos,
#         "enterprise_infos_str": enterprise_infos_str
        
#     }
import json
from typing import List, Dict, Any

def is_empty_dict(data: Any) -> bool:
    """
    检查一个字典是否为空。
    也适用于检查嵌套结构。
    """
    if isinstance(data, dict):
        return not any(data.values())  # 如果所有值都为假值 (如 None, '', [], {}), 则视为空
    return False

def extract_web_data(original_search_results: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    从嵌套的 all_source_list 中提取 {url, query, snippet, title} 列表。
    此函数能安全地处理可能缺失的字段和不正确的数据类型。
    输入 `original_search_results` 预期为一个列表, 例如: `[{ "result": [...] }]`
    """
    web_data_list = []

    if not isinstance(original_search_results, list):
        print("警告：extract_web_data 的输入不是列表。返回空列表。")
        return []

    for result_level1 in original_search_results:
        # 使用 .get() 安全地获取 "result" 列表
        result_list = result_level1.get("result", [])
        if not isinstance(result_list, list):
            continue

        for item in result_list:
            if not isinstance(item, dict):
                continue
            
            # 使用 .get() 链式调用安全地导航到 all_source_list，防止 KeyError
            all_source_list = item.get("web_data", {}).get("comprehensive_data", {}).get("all_source_list", [])

            if not isinstance(all_source_list, list):
                continue

            for source in all_source_list:
                if isinstance(source, dict):
                    title = source.get("title", "")
                    snippet = source.get("snippet", "")
                    query = source.get("query", "")  # 获取 'query'
                    url = source.get("url", "")
                    source = source.get("source", "")

                    if not isinstance(url, str):
                        url = ""

                    web_data_list.append({
                        "url": url,
                        # "query": query,
                        "snippet": snippet,
                        "title": title,
                        "source":source
                    })

    return web_data_list

def main(
    original_search_results: List[Dict[str, Any]],  # <-- 修复1: 类型应为 List
    llm_evaluation_output: str = None
) -> Dict[str, Any]:
    """
    优化版本，用于快速处理数据并移除空对象。
    处理的 `original_search_results` 结构为 `[{ "result": [...] }]`。
    """

    evaluation_map = {}
    if llm_evaluation_output:
        try:
            llm_evaluation_list: List[Dict[str, Any]] = json.loads(llm_evaluation_output)
            evaluation_map = {item["source_id"]: item for item in llm_evaluation_list}
        except (json.JSONDecodeError, TypeError) as e:
            print(f"警告: 解析LLM输出时出错: {e}。将忽略筛选。")

    career_postings = []
    enterprise_infos = []
    filtered_results = []

    # --- 修复2: 增加健壮性检查，防止因输入格式问题导致的崩溃 ---
    original_search_results_list = []
    # 检查 `original_search_results` 是否是一个非空列表
    if original_search_results and isinstance(original_search_results, list):
        # 检查列表的第一个元素是否是字典
        first_item = original_search_results[0]
        if isinstance(first_item, dict):
            # 安全地获取 "result" 列表
            original_search_results_list = first_item.get("result", [])
    
    if not isinstance(original_search_results_list, list):
        original_search_results_list = []

    for doc_item in original_search_results_list:
        if not isinstance(doc_item, dict): # 增加健壮性
            continue
            
        web_data = doc_item.get("web_data")
        if not web_data:
            filtered_results.append(doc_item)
            continue

        # 提取 career postings, 过滤空字典
        career_postings_data = web_data.get("career_postings", {})
        if isinstance(career_postings_data, dict) and "data" in career_postings_data and isinstance(career_postings_data.get("data"), list):
            career_postings.extend([item for item in career_postings_data["data"] if not is_empty_dict(item)])

        # 提取 enterprise info, 过滤空字典
        enterprise_data = web_data.get("enterprise_infos")
        if enterprise_data:
            if isinstance(enterprise_data, dict) and "data" in enterprise_data and isinstance(enterprise_data.get("data"), list):
                enterprise_infos.extend([item for item in enterprise_data["data"] if not is_empty_dict(item)])
            elif isinstance(enterprise_data, dict) and not is_empty_dict(enterprise_data):
                enterprise_infos.append(enterprise_data)

        # 基于 LLM 评估处理 all_source_list
        comprehensive_data = web_data.get("comprehensive_data", {})
        all_source_list = comprehensive_data.get("all_source_list", [])

        if isinstance(all_source_list, list) and all_source_list:
            filtered_all_source_list = []
            if evaluation_map:
                for source_data in all_source_list:
                    if not isinstance(source_data, dict): continue
                    source_id = source_data.get("source_id")
                    if source_id:
                        evaluation = evaluation_map.get(source_id)
                        if evaluation is None or evaluation.get("relevance") != "不相关":
                            filtered_all_source_list.append(source_data)
                    else:
                        filtered_all_source_list.append(source_data)
            else:
                filtered_all_source_list = all_source_list

            if filtered_all_source_list:
                if "comprehensive_data" not in web_data or not isinstance(web_data.get("comprehensive_data"), dict):
                   web_data["comprehensive_data"] = {}
                web_data["comprehensive_data"]["all_source_list"] = filtered_all_source_list
                filtered_results.append(doc_item)
    
    # 最终清理
    career_postings = [item for item in career_postings if not is_empty_dict(item)]
    enterprise_infos = [item for item in enterprise_infos if not is_empty_dict(item)]

    # --- 修复3: 重新集成 web_data 的提取与输出 ---
    final_web_data = extract_web_data(original_search_results)
    
    # 在输出阶段统一进行字符串转换
    final_web_data_str = str(final_web_data)
    career_postings_str = str(career_postings)
    enterprise_infos_str = str(enterprise_infos)
    filtered_results_str = str(filtered_results)

    # --- 修复4: 在返回字典中添加所需字段 ---
    return {
        "output_str": filtered_results_str,
        "output": filtered_results,
        "career_postings": career_postings,
        "career_postings_str": career_postings_str,
        "enterprise_infos": enterprise_infos,
        "enterprise_infos_str": enterprise_infos_str,
        "web_data": final_web_data,
        "web_data_str": final_web_data_str
    }

