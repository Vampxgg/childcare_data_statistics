# -*- coding: utf-8 -*-
"""
节点ID: 1761725745439
节点标题: 传服务器
节点描述: 
节点类型: code
"""

import requests
import json
from typing import List, Dict, Any

# ==============================================================================
# ----------------------------> 用户配置区 <---------------------------------
# ==============================================================================
CONFIG = {
    "API_BASE_URL": "http://119.45.167.133:7751", # 提取基础URL，方便管理
    
    # 1. 认证相关配置
    "AUTH_DETAILS": {
        "login": "xt666666",      # 您的登录账号
        "password": "123456",    # 您的登录密码
        # 初始令牌（可选，可以留空）。如果提供，第一次请求会用它，过期后会自动刷新。
        "initial_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjIwMjAxMDExLCJyb2xlIjoxLCJpYXQiOjE3NjE3Mjg1NTAsImV4cCI6MTc2MTgxNDk1MH0.4YTszVwCiSZ3Ag-mDvvcCYPmIBoTWppnKBu9IpxguA0"
    },

    # 2. 功能接口路径
    "ENDPOINTS": {
        "upload": "/file/upload",
        "sign_in": "/auth/sign_in"
    }
}
# ==============================================================================
# ---------------------------> 认证管理模块 <---------------------------------
# ==============================================================================

class AuthManager:
    """
    一个专门用于管理认证令牌的类。
    - 负责存储当前有效的令牌。
    - 负责在需要时调用API刷新令牌。
    """
    def __init__(self, config: Dict[str, Any]):
        self.api_base_url = config["API_BASE_URL"]
        self.sign_in_endpoint = config["ENDPOINTS"]["sign_in"]
        self.credentials = config["AUTH_DETAILS"]
        self.token = self.credentials.get("initial_token") # 使用初始令牌

    def get_headers(self) -> Dict[str, str]:
        """获取带有当前 Authorization Token 的请求头"""
        if not self.token:
            print("当前无可用Token，立即尝试刷新。")
            self.refresh_token()
        return {'Authorization': f'Bearer {self.token}'}

    def refresh_token(self):
        """
        请求新的认证令牌并更新到实例中。
        """
        print("--- 开始刷新认证令牌 ---")
        refresh_url = f"{self.api_base_url}{self.sign_in_endpoint}"
        payload = {
            'login': self.credentials['login'],
            'password': self.credentials['password']
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        try:
            response = requests.post(refresh_url, data=payload, headers=headers, timeout=30)
            response.raise_for_status()
            response_data = response.json()

            if response_data.get("status") and 'data' in response_data and 'token' in response_data['data']:
                self.token = response_data['data']['token']
                print(f"令牌刷新成功！新的令牌已存储。")
            else:
                raise Exception(f"刷新令牌API返回错误: {response_data.get('message', '未知错误')}")
        except Exception as e:
            print(f"!!! 致命错误: 刷新令牌失败，程序无法继续。错误: {e}")
            # 在一个关键任务中，如果连认证都失败了，就应该直接抛出异常中断执行
            raise e

# ==============================================================================
# ---------------------------> 核心实现区 <---------------------------------
# ==============================================================================

def main(input_files: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    主函数，处理文件上传，并内置令牌过期自动刷新重试逻辑。
    """
    # 1. 输入验证
    if not isinstance(input_files, list):
        raise TypeError(f"输入应为文件数组 (List)，但收到了 {type(input_files)} 类型。")

    if not input_files:
        return {"output_files": [], "markdown_output": "没有文件需要处理。"}

    # 初始化认证管理器
    auth_manager = AuthManager(CONFIG)
    target_url = f"{CONFIG['API_BASE_URL']}{CONFIG['ENDPOINTS']['upload']}"
    processed_files = []

    # 2. 遍历处理每个文件
    for index, file_obj in enumerate(input_files):
        print(f"--- 开始处理第 {index + 1} 个文件: {file_obj.get('filename')} ---")
        updated_file_obj = file_obj.copy()

        try:
            # a. 参数校验 (逻辑不变)
            dify_download_url = file_obj.get('url')
            original_filename = file_obj.get('filename')
            mime_type = file_obj.get('mime_type')
            if not all([dify_download_url, original_filename, mime_type]):
                raise ValueError("文件对象缺少 'url', 'filename', 或 'mime_type' 关键字段。")

            # b. 下载文件 (逻辑不变)
            print("步骤 1/3: 正在从Dify下载文件...")
            # ... (下载逻辑保持完全一致)
            with requests.get(dify_download_url, stream=True, timeout=60) as download_response:
                download_response.raise_for_status()
                file_content = download_response.content
            
            files_to_upload = {'file': (original_filename, file_content, mime_type)}

            # c. 上传文件 - 包含重试逻辑
            print("步骤 2/3: 正在上传文件...")
            try:
                # 第一次尝试上传
                upload_response = requests.post(
                    target_url, 
                    headers=auth_manager.get_headers(), 
                    files=files_to_upload, 
                    timeout=120
                )
                upload_response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                # 关键：检查是否是401错误
                if e.response.status_code == 401:
                    print("上传失败 (401 Unauthorized)，疑似令牌过期。尝试刷新令牌并重试...")
                    auth_manager.refresh_token() # 刷新令牌
                    print("重试上传...")
                    # 第二次尝试上传
                    upload_response = requests.post(
                        target_url, 
                        headers=auth_manager.get_headers(), 
                        files=files_to_upload, 
                        timeout=120
                    )
                    upload_response.raise_for_status() # 如果再次失败，异常会向上抛出
                else:
                    # 如果是其他HTTP错误（如500, 404等），直接抛出
                    raise e
            
            # d. 解析API响应 (逻辑不变)
            response_data = upload_response.json()
            print("上传成功，API返回:", json.dumps(response_data, indent=2, ensure_ascii=False))
            if response_data.get("status") is True and 'data' in response_data and 'url' in response_data['data']:
                new_url = response_data['data']['url']
                print(f"步骤 3/3: 成功获取新URL: {new_url}")
                updated_file_obj['url'] = new_url
            else:
                raise Exception(f"API响应格式不正确或状态为false。消息: {response_data.get('message')}")

        except Exception as e:
            error_message = f"处理文件时发生错误: {e}"
            print(f"错误: {error_message}")
            updated_file_obj['error'] = error_message

        processed_files.append(updated_file_obj)
        print(f"--- 文件 {file_obj.get('filename')} 处理完毕 ---\n")

    # 3. 生成 Markdown 字符串 (逻辑不变)
    markdown_links = []
    for file_data in processed_files:
        if 'error' not in file_data:
            filename = file_data.get('filename')
            url = file_data.get('url')
            if filename and url:
                markdown_links.append(f"[{filename}]({url})")
    markdown_output_string = "\n".join(markdown_links)

    # 4. 返回结果 (逻辑不变)
    return {
        "output_files": processed_files,
        "markdown_output": markdown_output_string
    }
