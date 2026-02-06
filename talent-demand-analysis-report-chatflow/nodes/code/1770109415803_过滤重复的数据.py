# -*- coding: utf-8 -*-
"""
节点ID: 1770109415803
节点标题: 过滤重复的数据
节点描述: 
节点类型: code
"""

# import json

# def main(arg1):
#     """
#     本代码节点旨在过滤输入数据中重复的URL。
#     它会遍历输入JSON结构中的'all_source_list'，并根据'url'字段移除重复项，仅保留第一次出现的条目。
#     最终返回与入参格式相同但内容经过筛选的数据。
#     """

#     json_list = arg1

#     # 遍历最外层的 'json' 列表
#     for doc_group in json_list:
#         if not isinstance(doc_group, dict):
#             continue

#         # 'result' 也是一个列表，需要继续遍历
#         result_list = doc_group.get("result", [])
#         if not isinstance(result_list, list):
#             continue

#         for doc in result_list:
#             if not isinstance(doc, dict):
#                 continue
            
#             # 使用 try-except 来健壮地处理可能不一致的数据结构
#             try:
#                 # 定位到需要去重的列表路径
#                 source_list = doc["web_data"]["comprehensive_data"]["all_source_list"]
                
#                 # 检查 source_list 是否为列表
#                 if not isinstance(source_list, list):
#                     continue

#                 # 用于存储已经见过的URL
#                 seen_urls = set()
#                 # 用于存储去重后的结果
#                 unique_source_list = []
                
#                 # 遍历源列表进行去重
#                 for item in source_list:
#                     # 只有当条目是字典且包含URL时才进行处理
#                     if isinstance(item, dict):
#                         url = item.get("url")
                        
#                         # 只有当URL存在且是首次出现时，才将其加入结果列表和已见集合
#                         # 这个逻辑会隐式地过滤掉没有'url'字段或'url'为空的条目
#                         if url and url not in seen_urls:
#                             unique_source_list.append(item)
#                             seen_urls.add(url)
#                     else:
#                         # 如果列表中的项不是字典，无法按URL去重，则选择保留它
#                         unique_source_list.append(item)
                
#                 # 用去重后的列表替换原始列表
#                 doc["web_data"]["comprehensive_data"]["all_source_list"] = unique_source_list
#             except (KeyError, TypeError):
#                 # 如果数据结构不符合预期的嵌套路径（例如缺少某个键），则跳过该条目，继续处理下一个
#                 continue
                
#     # 按照要求，返回与入参结构相同的、经过处理的数据
#     return {
#         "result": arg1,
#         "result_str": str(arg1)
#     }

import json

def main(arg1):
    """
    本代码节点旨在过滤输入数据中重复的URL，并返回处理后的对象及其JSON字符串表示。
    它会遍历输入JSON结构中的'all_source_list'，并根据'url'字段移除重复项。
    最终返回处理后的Python对象和符合JSON格式的字符串。
    """
    # 检查 arg1 是否为列表
    if not isinstance(arg1, list):
        return {"result": arg1, "result_str": str(arg1)}

    # 遍历 arg1 列表
    for doc_group in arg1:
        if not isinstance(doc_group, dict):
            continue
        
        result_list = doc_group.get("result", [])
        if not isinstance(result_list, list):
            continue

        for doc in result_list:
            if not isinstance(doc, dict):
                continue
            
            try:
                source_list = doc["web_data"]["comprehensive_data"]["all_source_list"]
                if not isinstance(source_list, list):
                    continue

                seen_urls = set()
                unique_source_list = []
                
                for item in source_list:
                    if isinstance(item, dict):
                        url = item.get("url")
                        if url and url not in seen_urls:
                            unique_source_list.append(item)
                            seen_urls.add(url)
                    else:
                        unique_source_list.append(item)
                
                doc["web_data"]["comprehensive_data"]["all_source_list"] = unique_source_list
            except (KeyError, TypeError):
                continue
                
    # 返回处理后的Python对象，以及一个标准格式的JSON字符串
    return {
        "result": arg1,
        # 使用 json.dumps 生成标准的JSON字符串，ensure_ascii=False确保中文字符不被转义
        "result_str": json.dumps(arg1[0], ensure_ascii=False) 
    }


