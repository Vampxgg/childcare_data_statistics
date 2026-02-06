# -*- coding: utf-8 -*-
"""
节点ID: 1770109476978
节点标题: token量安全保证器 (1)
节点描述: 
节点类型: code
"""

# # -*- coding: utf-8 -*-
# # 健壮性最终版：本版本在原有基础上增加了全局错误捕获和安全降级机制。
# # 当主要逻辑遇到任何意外错误时，会切换到最简单的“字符数/4”模型进行强制截断，
# # 确保在任何情况下都能返回一个长度安全的结果，保障工作流的稳定运行。

# from typing import Dict, Any
# import math

# def estimate_token_count_for_sandbox(text: str) -> int:
#     """
#     一个为沙箱环境设计的、可靠的 token 估算函数。
#     - 中文字符: 1个字 ≈ 2个token (采用保守值确保安全)
#     - 其他字符 (英文、数字、空格等): 4个字符 ≈ 1个token
#     """
#     if not isinstance(text, str):
#         # 增加输入类型检查，防止非字符串输入导致下方循环报错
#         return 0

#     chinese_char_count = 0
#     other_char_count = 0

#     for char in text:
#         # 使用Unicode范围判断是否为CJK统一表意文字 (覆盖绝大部分汉字)
#         if '\u4e00' <= char <= '\u9fff':
#             chinese_char_count += 1
#         else:
#             other_char_count += 1
    
#     chinese_tokens = chinese_char_count * 2
#     other_tokens = math.ceil(other_char_count / 4)
    
#     total_tokens = chinese_tokens + other_tokens
#     return int(total_tokens)

# def main(markdown_content: str) -> Dict[str, Any]:
#     """
#     在不依赖tiktoken的情况下，检查并裁剪超长文本，并包含错误降级处理机制。
#     """
#     MAX_INPUT_TOKENS = 0  # 初始化以扩大作用域

#     # --- 1. 配置 Token 限制 ---
#     try:
#         MAX_CONTEXT_TOKENS = 258576 
#         RESERVED_OUTPUT_TOKENS = 65501
#         SAFETY_MARGIN = 5000 
#         MAX_INPUT_TOKENS = MAX_CONTEXT_TOKENS - RESERVED_OUTPUT_TOKENS - SAFETY_MARGIN

#         print(f"[+] Dify Log: 模型总限制={MAX_CONTEXT_TOKENS}, 预留输出={RESERVED_OUTPUT_TOKENS}, 最大输入={MAX_INPUT_TOKENS}")

#     except Exception as e:
#         print(f"[-] Dify Log: 配置初始化失败: {e}")
#         # 即使配置失败，也返回原始文本，避免工作流中断
#         return {
#             "trimmed_markdown_content": markdown_content, 
#             "status": f"Error: Configuration failed: {e}",
#             "original_tokens": -1, 
#             "new_tokens": -1, 
#             "max_input_tokens": -1
#         }

#     # --- 2. 主逻辑与错误捕获 ---
#     try:
#         original_char_count = len(markdown_content)
#         input_token_count = estimate_token_count_for_sandbox(markdown_content)
#         print(f"[~] Dify Log: 文本共 {original_char_count} 字符, 估算 Token 数为: {input_token_count}")

#         # --- 3. 判断是否需要裁剪 ---
#         if input_token_count <= MAX_INPUT_TOKENS:
#             print("[+] Dify Log: Token 在限制内，无需裁剪。")
#             return {
#                 "trimmed_markdown_content": markdown_content, 
#                 "status": "No trimming needed.",
#                 "original_tokens": input_token_count, 
#                 "new_tokens": input_token_count, 
#                 "max_input_tokens": MAX_INPUT_TOKENS
#             }
#         else:
#             # --- 4. 执行“中间裁切”（主方案） ---
#             tokens_to_remove = input_token_count - MAX_INPUT_TOKENS
#             print(f"[-] Dify Log: Token 超出限制！需移除约 {tokens_to_remove} 个 Token。")
            
#             avg_char_per_token = original_char_count / input_token_count if input_token_count > 0 else 2
#             chars_to_remove = math.ceil(tokens_to_remove * avg_char_per_token)
            
#             mid_index = original_char_count // 2
#             start_remove_index = max(0, mid_index - chars_to_remove // 2)
#             end_remove_index = min(original_char_count, mid_index + (chars_to_remove + 1) // 2)

#             if start_remove_index >= end_remove_index:
#                  return {
#                     "trimmed_markdown_content": markdown_content, 
#                     "status": "Warning: Trimming range invalid.",
#                     "original_tokens": input_token_count, 
#                     "new_tokens": input_token_count, 
#                     "max_input_tokens": MAX_INPUT_TOKENS
#                 }

#             truncation_marker = "\n\n... [部分内容因超长已从中间省略] ...\n\n"
#             trimmed_text = markdown_content[:start_remove_index] + truncation_marker + markdown_content[end_remove_index:]
            
#             new_token_count = estimate_token_count_for_sandbox(trimmed_text)
#             print(f"[+] Dify Log: 裁剪完成。新估算 Token 数为: {new_token_count}")

#             return {
#                 "trimmed_markdown_content": trimmed_text,
#                 "status": f"Trimmed from middle. Removed approx. {tokens_to_remove} tokens.",
#                 "original_tokens": input_token_count, 
#                 "new_tokens": new_token_count, 
#                 "max_input_tokens": MAX_INPUT_TOKENS
#             }

#     except Exception as e:
#         # --- 5. 异常捕获与安全降级处理 ---
#         print(f"[-] Dify Log: 主逻辑执行出现意外错误: '{e}'. 启动安全降级裁剪模式。")
        
#         # 使用最保守的 字符/4 模型进行截断
#         # 乘以4是为了将Token限制转换为大致的字符限制
#         target_char_count = int(MAX_INPUT_TOKENS * 4)
        
#         if len(markdown_content) > target_char_count:
#             # 采用最简单的末尾截断，确保不会出错
#             safe_trimmed_text = markdown_content[:target_char_count]
#             truncation_marker_safe = "\n\n... [内容因程序意外错误被强制截断] ...\n\n"
#             safe_trimmed_text += truncation_marker_safe
#             status_msg = f"Error: Fallback trimming activated due to: {e}"
#         else:
#             # 如果文本本身不长，但依然报错，说明是其他问题，返回原文
#             safe_trimmed_text = markdown_content
#             status_msg = f"Error: An unexpected error occurred but no trimming was needed. Original error: {e}"

#         return {
#             "trimmed_markdown_content": safe_trimmed_text,
#             "status": status_msg,
#             "original_tokens": -1,  # 使用-1表示估算失败
#             "new_tokens": -1,       # 使用-1表示估算失败
#             "max_input_tokens": MAX_INPUT_TOKENS
#         }
# -*- coding: utf-8 -*-
# 健壮性最终版：本版本在原有基础上增加了全局错误捕获和安全降级机制。
# 当主要逻辑遇到任何意外错误时，会切换到最简单的“字符数/4”模型进行强制截断，
# 确保在任何情况下都能返回一个长度安全的结果，保障工作流的稳定运行。

from typing import Dict, Any
import math

def estimate_token_count_for_sandbox(text: str) -> int:
    """
    一个为沙箱环境设计的、可靠的 token 估算函数。
    - 中文字符: 1个字 ≈ 2个token (采用保守值确保安全)
    - 其他字符 (英文、数字、空格等): 4个字符 ≈ 1个token
    """
    if not isinstance(text, str):
        # 增加输入类型检查，防止非字符串输入导致下方循环报错
        return 0

    chinese_char_count = 0
    other_char_count = 0

    for char in text:
        # 使用Unicode范围判断是否为CJK统一表意文字 (覆盖绝大部分汉字)
        if '\u4e00' <= char <= '\u9fff':
            chinese_char_count += 1
        else:
            other_char_count += 1
    
    chinese_tokens = chinese_char_count * 2
    other_tokens = math.ceil(other_char_count / 4)
    
    total_tokens = chinese_tokens + other_tokens
    return int(total_tokens)

def main(markdown_content: str) -> Dict[str, Any]:
    """
    在不依赖tiktoken的情况下，检查并裁剪超长文本，并包含错误降级处理机制。
    """
    MAX_INPUT_TOKENS = 0  # 初始化以扩大作用域

    # --- 1. 配置 Token 限制 ---
    try:
        MAX_CONTEXT_TOKENS = 1048576#258576  # Based on error message
        RESERVED_OUTPUT_TOKENS = 10000#65501  # Prompt预留1wtoken
        SAFETY_MARGIN = 0#5000  # Removed safety margin as reserved tokens cover it
        MAX_INPUT_TOKENS = MAX_CONTEXT_TOKENS - RESERVED_OUTPUT_TOKENS - SAFETY_MARGIN

        print(f"[+] Dify Log: 模型总限制={MAX_CONTEXT_TOKENS}, 预留输出={RESERVED_OUTPUT_TOKENS}, 最大输入={MAX_INPUT_TOKENS}")

    except Exception as e:
        print(f"[-] Dify Log: 配置初始化失败: {e}")
        # 即使配置失败，也返回原始文本，避免工作流中断
        return {
            "trimmed_markdown_content": markdown_content, 
            "status": f"Error: Configuration failed: {e}",
            "original_tokens": -1, 
            "new_tokens": -1, 
            "max_input_tokens": -1
        }

    # --- 2. 主逻辑与错误捕获 ---
    try:
        original_char_count = len(markdown_content)
        input_token_count = estimate_token_count_for_sandbox(markdown_content)
        print(f"[~] Dify Log: 文本共 {original_char_count} 字符, 估算 Token 数为: {input_token_count}")

        # --- 3. 判断是否需要裁剪 ---
        if input_token_count <= MAX_INPUT_TOKENS:
            print("[+] Dify Log: Token 在限制内，无需裁剪。")
            return {
                "trimmed_markdown_content": markdown_content, 
                "status": "No trimming needed.",
                "original_tokens": input_token_count, 
                "new_tokens": input_token_count, 
                "max_input_tokens": MAX_INPUT_TOKENS
            }
        else:
            # --- 4. 执行“中间裁切”（主方案） ---
            tokens_to_remove = input_token_count - MAX_INPUT_TOKENS
            print(f"[-] Dify Log: Token 超出限制！需移除约 {tokens_to_remove} 个 Token。")
            
            avg_char_per_token = original_char_count / input_token_count if input_token_count > 0 else 2
            chars_to_remove = math.ceil(tokens_to_remove * avg_char_per_token)
            
            mid_index = original_char_count // 2
            start_remove_index = max(0, mid_index - chars_to_remove // 2)
            end_remove_index = min(original_char_count, mid_index + (chars_to_remove + 1) // 2)

            if start_remove_index >= end_remove_index:
                 return {
                    "trimmed_markdown_content": markdown_content, 
                    "status": "Warning: Trimming range invalid.",
                    "original_tokens": input_token_count, 
                    "new_tokens": input_token_count, 
                    "max_input_tokens": MAX_INPUT_TOKENS
                }

            truncation_marker = "\n\n... [部分内容因超长已从中间省略] ...\n\n"
            trimmed_text = markdown_content[:start_remove_index] + truncation_marker + markdown_content[end_remove_index:]
            
            new_token_count = estimate_token_count_for_sandbox(trimmed_text)
            print(f"[+] Dify Log: 裁剪完成。新估算 Token 数为: {new_token_count}")

            # Double check and trim again if still over the limit
            if new_token_count > MAX_INPUT_TOKENS:
                tokens_to_remove = new_token_count - MAX_INPUT_TOKENS
                avg_char_per_token = original_char_count / input_token_count if input_token_count > 0 else 2
                chars_to_remove = math.ceil(tokens_to_remove * avg_char_per_token)
                safe_trimmed_text = trimmed_text[:len(trimmed_text) - chars_to_remove] + truncation_marker # Trim from end for safety.
                new_token_count = estimate_token_count_for_sandbox(safe_trimmed_text)  # Recalculate token count after fallback trim
                print(f"[+] Dify Log: 再次裁剪完成。新估算 Token 数为: {new_token_count}")
                return {
                    "trimmed_markdown_content": safe_trimmed_text,
                    "status": f"Trimmed from middle, then fallback trimmed from end. Removed approx. {tokens_to_remove} tokens.",
                    "original_tokens": input_token_count,
                    "new_tokens": new_token_count,
                    "max_input_tokens": MAX_INPUT_TOKENS
                }

            return {
                "trimmed_markdown_content": trimmed_text,
                "status": f"Trimmed from middle. Removed approx. {tokens_to_remove} tokens.",
                "original_tokens": input_token_count, 
                "new_tokens": new_token_count, 
                "max_input_tokens": MAX_INPUT_TOKENS
            }

    except Exception as e:
        # --- 5. 异常捕获与安全降级处理 ---
        print(f"[-] Dify Log: 主逻辑执行出现意外错误: '{e}'. 启动安全降级裁剪模式。")
        
        # 使用最保守的 字符/4 模型进行截断
        # 乘以4是为了将Token限制转换为大致的字符限制
        target_char_count = int(MAX_INPUT_TOKENS * 4)
        
        if len(markdown_content) > target_char_count:
            # 采用最简单的末尾截断，确保不会出错
            safe_trimmed_text = markdown_content[:target_char_count]
            truncation_marker_safe = "\n\n... [内容因程序意外错误被强制截断] ...\n\n"
            safe_trimmed_text += truncation_marker_safe
            status_msg = f"Error: Fallback trimming activated due to: {e}"
        else:
            # 如果文本本身不长，但依然报错，说明是其他问题，返回原文
            safe_trimmed_text = markdown_content
            status_msg = f"Error: An unexpected error occurred but no trimming was needed. Original error: {e}"

        return {
            "trimmed_markdown_content": safe_trimmed_text,
            "status": status_msg,
            "original_tokens": -1,  # 使用-1表示估算失败
            "new_tokens": -1,       # 使用-1表示估算失败
            "max_input_tokens": MAX_INPUT_TOKENS
        }

