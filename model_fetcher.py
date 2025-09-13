#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
实时模型获取模块
根据用户输入的API Key和选择的厂商，实时获取可用模型列表
"""

import requests
import json
import time
from typing import List, Dict, Optional

class ModelFetcher:
    """模型获取器，支持从各厂商API实时获取模型列表"""
    
    def __init__(self):
        self.timeout = 10
        
    def fetch_openai_models(self, api_key: str, base_url: str = "https://api.openai.com/v1") -> List[str]:
        """获取OpenAI模型列表"""
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(f"{base_url}/models", headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                models = []
                for model in data.get("data", []):
                    model_id = model.get("id", "")
                    # 过滤出常用的聊天和文本模型
                    if any(keyword in model_id.lower() for keyword in ["gpt", "davinci", "embedding", "dall-e", "whisper", "tts"]):
                        models.append(model_id)
                return sorted(models)
            elif response.status_code == 401:
                return ["错误: API Key无效"]
            else:
                return ["错误: 无法连接到API"]
                
        except requests.exceptions.Timeout:
            return ["错误: 请求超时"]
        except requests.exceptions.ConnectionError:
            return ["错误: 网络连接失败"]
        except Exception as e:
            return [f"错误: {str(e)}"]
    
    def fetch_anthropic_models(self, api_key: str, base_url: str = "https://api.anthropic.com/v1") -> List[str]:
        """获取Anthropic模型列表"""
        try:
            headers = {
                "x-api-key": api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            # Anthropic没有直接的models端点，返回已知模型
            # 但我们可以通过尝试请求来验证API Key
            test_data = {
                "model": "claude-3-haiku-20240307",
                "max_tokens": 1,
                "messages": [{"role": "user", "content": "test"}]
            }
            
            response = requests.post(f"{base_url}/messages", 
                                   headers=headers, 
                                   json=test_data, 
                                   timeout=self.timeout)
            
            if response.status_code in [200, 400]:  # 400可能是因为消息格式，但API Key有效
                return [
                    "claude-3-opus-20240229",
                    "claude-3-sonnet-20240229", 
                    "claude-3-haiku-20240307",
                    "claude-2.1",
                    "claude-2.0",
                    "claude-instant-1.2"
                ]
            elif response.status_code == 401:
                return ["错误: API Key无效"]
            else:
                return ["错误: 无法验证API Key"]
                
        except requests.exceptions.Timeout:
            return ["错误: 请求超时"]
        except requests.exceptions.ConnectionError:
            return ["错误: 网络连接失败"]
        except Exception as e:
            return [f"错误: {str(e)}"]
    
    def fetch_google_models(self, api_key: str, base_url: str = "https://generativelanguage.googleapis.com/v1beta") -> List[str]:
        """获取Google模型列表"""
        try:
            response = requests.get(f"{base_url}/models?key={api_key}", timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                models = []
                for model in data.get("models", []):
                    model_name = model.get("name", "")
                    if model_name.startswith("models/"):
                        model_id = model_name.replace("models/", "")
                        models.append(model_id)
                return sorted(models) if models else [
                    "gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro", "gemini-pro-vision"
                ]
            elif response.status_code in [400, 403]:
                return ["错误: API Key无效"]
            else:
                return ["错误: 无法连接到API"]
                
        except requests.exceptions.Timeout:
            return ["错误: 请求超时"]
        except requests.exceptions.ConnectionError:
            return ["错误: 网络连接失败"]
        except Exception as e:
            return [f"错误: {str(e)}"]
    
    def fetch_cohere_models(self, api_key: str, base_url: str = "https://api.cohere.ai/v1") -> List[str]:
        """获取Cohere模型列表"""
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(f"{base_url}/models", headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                models = []
                for model in data.get("models", []):
                    model_name = model.get("name", "")
                    if model_name:
                        models.append(model_name)
                return sorted(models)
            elif response.status_code == 401:
                return ["错误: API Key无效"]
            else:
                return ["错误: 无法连接到API"]
                
        except requests.exceptions.Timeout:
            return ["错误: 请求超时"]
        except requests.exceptions.ConnectionError:
            return ["错误: 网络连接失败"]
        except Exception as e:
            return [f"错误: {str(e)}"]
    
    def fetch_groq_models(self, api_key: str, base_url: str = "https://api.groq.com/openai/v1") -> List[str]:
        """获取Groq模型列表"""
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(f"{base_url}/models", headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                models = []
                for model in data.get("data", []):
                    model_id = model.get("id", "")
                    if model_id:
                        models.append(model_id)
                return sorted(models)
            elif response.status_code == 401:
                return ["错误: API Key无效"]
            else:
                return ["错误: 无法连接到API"]
                
        except requests.exceptions.Timeout:
            return ["错误: 请求超时"]
        except requests.exceptions.ConnectionError:
            return ["错误: 网络连接失败"]
        except Exception as e:
            return [f"错误: {str(e)}"]
    
    def fetch_deepseek_models(self, api_key: str, base_url: str = "https://api.deepseek.com/v1") -> List[str]:
        """获取DeepSeek模型列表"""
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(f"{base_url}/models", headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                models = []
                for model in data.get("data", []):
                    model_id = model.get("id", "")
                    if model_id:
                        models.append(model_id)
                return sorted(models) if models else [
                    "deepseek-chat", "deepseek-coder", "deepseek-math", "deepseek-v2"
                ]
            elif response.status_code == 401:
                return ["错误: API Key无效"]
            else:
                return ["错误: 无法连接到API"]
                
        except requests.exceptions.Timeout:
            return ["错误: 请求超时"]
        except requests.exceptions.ConnectionError:
            return ["错误: 网络连接失败"]
        except Exception as e:
            return [f"错误: {str(e)}"]
    
    def get_models_for_vendor(self, vendor: str, api_key: str, api_url: str = None) -> List[str]:
        """根据厂商获取模型列表"""
        if not api_key or not api_key.strip():
            return ["请先输入API Key"]
        
        api_key = api_key.strip()
        
        # 根据厂商选择对应的获取方法
        if vendor == "OpenAI":
            base_url = api_url or "https://api.openai.com/v1"
            return self.fetch_openai_models(api_key, base_url)
        
        elif vendor == "Anthropic":
            base_url = api_url or "https://api.anthropic.com/v1"
            return self.fetch_anthropic_models(api_key, base_url)
        
        elif vendor == "Google":
            base_url = api_url or "https://generativelanguage.googleapis.com/v1beta"
            return self.fetch_google_models(api_key, base_url)
        
        elif vendor == "Cohere":
            base_url = api_url or "https://api.cohere.ai/v1"
            return self.fetch_cohere_models(api_key, base_url)
        
        elif vendor == "Groq":
            base_url = api_url or "https://api.groq.com/openai/v1"
            return self.fetch_groq_models(api_key, base_url)
        
        elif vendor == "DeepSeek":
            base_url = api_url or "https://api.deepseek.com/v1"
            return self.fetch_deepseek_models(api_key, base_url)
        
        elif vendor in ["Microsoft Azure"]:
            # Azure使用OpenAI格式
            if api_url:
                return self.fetch_openai_models(api_key, api_url)
            else:
                return ["请填写Azure资源的API URL"]
        
        elif vendor in ["智谱AI", "百度文心", "阿里通义", "字节豆包", "腾讯混元", "讯飞星火", "Moonshot"]:
            # 中国厂商，返回预设模型列表（需要特殊认证方式）
            return self.get_chinese_vendor_models(vendor)
        
        elif vendor == "自定义":
            return ["请手动输入模型名称"]
        
        else:
            return ["不支持的厂商"]
    
    def get_chinese_vendor_models(self, vendor: str) -> List[str]:
        """获取中国厂商的预设模型列表"""
        chinese_models = {
            "智谱AI": ["glm-4", "glm-4v", "glm-3-turbo", "chatglm3-6b", "chatglm2-6b"],
            "百度文心": ["ernie-bot-4.0", "ernie-bot-turbo", "ernie-bot", "ernie-speed", "ernie-lite"],
            "阿里通义": ["qwen-turbo", "qwen-plus", "qwen-max", "qwen-max-longcontext", "qwen-vl-plus"],
            "字节豆包": ["doubao-lite-4k", "doubao-pro-4k", "doubao-pro-32k", "doubao-pro-128k"],
            "腾讯混元": ["hunyuan-lite", "hunyuan-standard", "hunyuan-pro"],
            "讯飞星火": ["spark-v3.5", "spark-v3.0", "spark-v2.0", "spark-lite"],
            "Moonshot": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
            "DeepSeek": ["deepseek-chat", "deepseek-coder", "deepseek-math", "deepseek-v2"]
        }
        return chinese_models.get(vendor, ["请手动输入模型名称"])

# 全局模型获取器实例
model_fetcher = ModelFetcher()

if __name__ == "__main__":
    # 测试模型获取功能
    fetcher = ModelFetcher()
    
    print("🧪 模型获取器测试")
    print("=" * 40)
    
    # 测试OpenAI（需要有效的API Key）
    test_key = input("输入OpenAI API Key进行测试（可选）: ").strip()
    if test_key:
        print("正在获取OpenAI模型...")
        models = fetcher.get_models_for_vendor("OpenAI", test_key)
        print(f"获取到 {len(models)} 个模型: {models[:5]}...")
    
    # 测试中国厂商
    print("\n测试中国厂商模型列表:")
    for vendor in ["智谱AI", "百度文心", "阿里通义"]:
        models = fetcher.get_models_for_vendor(vendor, "dummy_key")
        print(f"{vendor}: {len(models)} 个模型")
