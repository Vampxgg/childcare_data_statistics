# -*- coding: utf-8 -*-
"""
节点ID: 1757507775635
节点标题: token量安全保证器
节点描述: 
节点类型: code
"""

# # -*- coding: utf-8 -*-
# # 该版本不依赖 tiktoken 库，完全基于字符数估算和操作
# from typing import Dict, Any

# def main(markdown_content: str) -> Dict[str, Any]:
#     """
#     通过估算检查输入文本的 token 数量，如果超过限制，则从中间裁剪以适应模型的上下文窗口。
#     注意：此版本不使用 tiktoken，所有计算都是基于字符数的粗略估算。

#     Args:
#         markdown_content (str): 需要检查和可能需要裁剪的 Markdown 文本。

#     Returns:
#         Dict[str, Any]: 包含裁剪后文本和处理状态的字典。
#     """
#     # --- 1. 配置 Token 限制 ---
#     # 这些值可以根据您的具体模型和错误信息进行调整
#     try:
#         MAX_CONTEXT_TOKENS = 258576 
#         RESERVED_OUTPUT_TOKENS = 65501
#         SAFETY_MARGIN = 5000 
#         MAX_INPUT_TOKENS = MAX_CONTEXT_TOKENS - RESERVED_OUTPUT_TOKENS - SAFETY_MARGIN

#         # 定义字符与 token 的估算比例 (一个 token 约等于 4 个英文字符)
#         CHAR_TO_TOKEN_RATIO = 4

#         print(f"[+] Dify Log: 模型总限制={MAX_CONTEXT_TOKENS}, 预留输出={RESERVED_OUTPUT_TOKENS}")
#         print(f"[+] Dify Log: 计算得出最大允许输入 Token 数为: {MAX_INPUT_TOKENS}")

#     except Exception as e:
#         # 捕获可能的配置错误
#         print(f"[-] Dify Log: 配置初始化失败: {e}")
#         return {
#             "trimmed_markdown_content": markdown_content,
#             "status": f"Error: Configuration failed with exception: {e}",
#             "original_tokens": -1,
#             "new_tokens": -1,
#             "max_input_tokens": -1
#         }

#     # --- 2. 基于字符数估算 Token ---
#     original_char_count = len(markdown_content)
#     input_token_count = original_char_count // CHAR_TO_TOKEN_RATIO
#     print(f"[~] Dify Log: 当前输入文本有 {original_char_count} 个字符。")
#     print(f"[~] Dify Log: 估算的输入 Token 数为: {input_token_count}")


#     # --- 3. 判断是否需要裁剪 ---
#     if input_token_count <= MAX_INPUT_TOKENS:
#         print("[+] Dify Log: 估算的 Token 数量在限制范围内，无需裁剪。")
#         return {
#             "trimmed_markdown_content": markdown_content,
#             "status": "No trimming needed (based on character estimate).",
#             "original_tokens": input_token_count,
#             "new_tokens": input_token_count, # 无需裁剪时，新旧 token 数一致
#             "max_input_tokens": MAX_INPUT_TOKENS
#         }
#     else:
#         tokens_to_remove = input_token_count - MAX_INPUT_TOKENS
#         print(f"[-] Dify Log: 估算的 Token 超出限制！需要移除约 {tokens_to_remove} 个 Token。")
        
#         # --- 4. 执行基于字符的“中间裁切”策略 ---
#         # 将需要移除的 token 数量转换回字符数量
#         chars_to_remove = tokens_to_remove * CHAR_TO_TOKEN_RATIO
        
#         # 找到字符串的中心点
#         mid_index = original_char_count // 2
        
#         # 计算要移除的字符切片的起始和结束索引
#         start_remove_index = mid_index - chars_to_remove // 2
#         end_remove_index = mid_index + (chars_to_remove + 1) // 2 # +1处理奇数情况

#         # 确保索引不会越界
#         start_remove_index = max(0, start_remove_index)
#         end_remove_index = min(original_char_count, end_remove_index)
        
#         if start_remove_index >= end_remove_index:
#              # 如果计算结果异常，则返回原始文本并附上警告
#              return {
#                 "trimmed_markdown_content": markdown_content,
#                 "status": "Warning: Calculated trimming resulted in an invalid range. No changes made.",
#                 "original_tokens": input_token_count,
#                 "new_tokens": input_token_count,
#                 "max_input_tokens": MAX_INPUT_TOKENS
#             }

#         # 构造新的文本，并在中间插入一个标记
#         truncation_marker = "\n\n... [部分内容因超长已从中间省略] ...\n\n"
#         trimmed_text = markdown_content[:start_remove_index] + truncation_marker + markdown_content[end_remove_index:]
        
#         new_char_count = len(trimmed_text)
#         new_token_count = new_char_count // CHAR_TO_TOKEN_RATIO
#         print(f"[+] Dify Log: 裁剪完成。新的字符数为: {new_char_count}，新的估算 Token 数为: {new_token_count}")

#         return {
#             "trimmed_markdown_content": trimmed_text,
#             "status": f"Trimmed from middle based on character count. Removed approx. {tokens_to_remove} tokens.",
#             "original_tokens": input_token_count,
#             "new_tokens": new_token_count,
#             "max_input_tokens": MAX_INPUT_TOKENS
#         }




# -*- coding: utf-8 -*-
# -- Dify Code Block --
# This version uses the 'tiktoken' library for precise token counting and trimming.
# Make sure 'tiktoken' is installed in your Dify environment's Python packages.
# from typing import Dict, Any

# try:
#     import tiktoken
# except ImportError:
#     # If tiktoken is not installed, raise an exception to stop execution
#     # and provide a clear error message in the Dify logs.
#     raise ImportError("The 'tiktoken' library is not installed. Please add it to the Python packages in your Dify environment settings.")

# def main(markdown_content: str) -> Dict[str, Any]:
#     """
#     通过 tiktoken 精确检查输入文本的 token 数量，如果超过限制，则从中间裁剪以适应模型的上下文窗口。

#     Args:
#         markdown_content (str): 需要检查和可能需要裁剪的 Markdown 文本。

#     Returns:
#         Dict[str, Any]: 包含裁剪后文本和处理状态的字典。
#     """
#     # --- 1. 配置 Token 限制 (与原代码保持一致) ---
#     MAX_CONTEXT_TOKENS = 258576 
#     RESERVED_OUTPUT_TOKENS = 65501
#     SAFETY_MARGIN = 5000 
#     MAX_INPUT_TOKENS = MAX_CONTEXT_TOKENS - RESERVED_OUTPUT_TOKENS - SAFETY_MARGIN

#     print(f"[+] Dify Log: 模型总限制={MAX_CONTEXT_TOKENS}, 预留输出={RESERVED_OUTPUT_TOKENS}")
#     print(f"[+] Dify Log: 计算得出最大允许输入 Token 数为: {MAX_INPUT_TOKENS}")

#     # --- 2. 初始化 tiktoken 编码器并精确计算 Token ---
#     try:
#         # 使用 cl100k_base 编码器，适用于 gpt-4, gpt-3.5-turbo, text-embedding-ada-002 等模型
#         encoding = tiktoken.get_encoding("cl100k_base")
#     except Exception as e:
#         print(f"[-] Dify Log: 初始化 tiktoken 编码器失败: {e}")
#         return {
#             "trimmed_markdown_content": markdown_content,
#             "status": f"Error: Failed to initialize tiktoken encoder: {e}",
#             "original_tokens": -1, "new_tokens": -1, "max_input_tokens": MAX_INPUT_TOKENS
#         }

#     # 对输入内容进行编码，得到 token ID 列表
#     input_tokens_list = encoding.encode(markdown_content)
#     input_token_count = len(input_tokens_list)
#     print(f"[~] Dify Log: [tiktoken] 精确计算的输入 Token 数为: {input_token_count}")

#     # --- 3. 判断是否需要裁剪 ---
#     if input_token_count <= MAX_INPUT_TOKENS:
#         print("[+] Dify Log: [tiktoken] Token 数量在限制范围内，无需裁剪。")
#         return {
#             "trimmed_markdown_content": markdown_content,
#             "status": "No trimming needed (based on precise tiktoken count).",
#             "original_tokens": input_token_count,
#             "new_tokens": input_token_count, # 无需裁剪时，新旧 token 数一致
#             "max_input_tokens": MAX_INPUT_TOKENS
#         }
#     else:
#         tokens_to_remove = input_token_count - MAX_INPUT_TOKENS
#         print(f"[-] Dify Log: [tiktoken] Token 超出限制！需要精确移除 {tokens_to_remove} 个 Token。")

#         # --- 4. 执行基于 Token 的“中间裁切”策略 ---
#         # 找到 token 列表的中心点
#         mid_index = len(input_tokens_list) // 2

#         # 计算要移除的 token 切片的起始和结束索引
#         half_tokens_to_remove = tokens_to_remove // 2
#         start_remove_index = mid_index - half_tokens_to_remove
#         # 确保奇数个 token 也能被完全移除
#         end_remove_index = start_remove_index + tokens_to_remove

#         # 从 token 列表中移除中间部分
#         trimmed_tokens_list = input_tokens_list[:start_remove_index] + input_tokens_list[end_remove_index:]

#         # 将裁剪后的 token 列表解码回文本
#         # 注意：直接解码可能会导致UTF-8字符被截断而产生乱码，但 tiktoken 的 decode 通常能很好地处理
#         # 更好的方式是分开解码再拼接，确保万无一失
#         first_part_text = encoding.decode(input_tokens_list[:start_remove_index])
#         second_part_text = encoding.decode(input_tokens_list[end_remove_index:])

#         truncation_marker = "\n\n... [部分内容因超长已从中间省略] ...\n\n"
#         trimmed_text = first_part_text + truncation_marker + second_part_text

#         # 重新计算裁剪后文本的 token 数，以获得最精确的结果（因为标记本身也占 token）
#         new_token_count = len(encoding.encode(trimmed_text))
#         print(f"[+] Dify Log: 裁剪完成。新的精确 Token 数为: {new_token_count}")

#         return {
#             "trimmed_markdown_content": trimmed_text,
#             "status": f"Trimmed from middle. Removed {tokens_to_remove} tokens.",
#             "original_tokens": input_token_count,
#             "new_tokens": new_token_count,
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
        MAX_CONTEXT_TOKENS = 258576 
        RESERVED_OUTPUT_TOKENS = 65501
        SAFETY_MARGIN = 5000 
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

