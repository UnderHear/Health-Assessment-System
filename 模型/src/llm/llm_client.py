import time
import requests
from typing import Dict, Any, Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DeepSeekAPIClient:
    """DeepSeek大模型API客户端"""
    def __init__(self, config):
        self.config = config
        self.api_key = getattr(config, 'deepseek_api_key', '')
        self.api_base_url = getattr(config, 'deepseek_api_base_url', 'https://api.deepseek.com')
        self.model = getattr(config, 'deepseek_model', 'deepseek-chat')
        self.max_tokens = getattr(config, 'deepseek_max_tokens', 4096)
        
        # 重试配置
        self.max_retries = 3
        self.retry_delay = 2  # 秒
        self.retry_backoff = 2
    
    def _prepare_headers(self) -> Dict[str, str]:
        """准备API请求头"""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def _prepare_payload(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """准备API请求体"""
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": kwargs.get('max_tokens', self.max_tokens),
            "temperature": kwargs.get('temperature', 0.7),
            "top_p": kwargs.get('top_p', 0.9),
            "frequency_penalty": kwargs.get('frequency_penalty', 0.0),
            "presence_penalty": kwargs.get('presence_penalty', 0.0)
        }
        
        return payload
    
    def _call_api(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """调用DeepSeek API"""
        url = f"{self.api_base_url}/chat/completions"
        headers = self._prepare_headers()
        payload = self._prepare_payload(prompt, **kwargs)
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=60)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"API调用失败 (状态码: {response.status_code}): {response.text}")
                    
                    # 处理速率限制或临时错误
                    if response.status_code in [429, 502, 503, 504]:
                        if attempt < self.max_retries - 1:
                            delay = self.retry_delay * (self.retry_backoff ** attempt)
                            logger.info(f"等待 {delay} 秒后重试...")
                            time.sleep(delay)
                            continue
            except requests.RequestException as e:
                logger.warning(f"API请求异常: {str(e)}")
                
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (self.retry_backoff ** attempt)
                    logger.info(f"等待 {delay} 秒后重试...")
                    time.sleep(delay)
                    continue
            
        # 所有重试都失败
        error_msg = f"API调用失败，已重试 {self.max_retries} 次"
        logger.error(error_msg)
        raise Exception(error_msg)
    
    def generate_text(self, prompt: str, **kwargs) -> str:
        """生成文本响应"""
        try:
            response = self._call_api(prompt, **kwargs)
            
            # 解析响应
            if 'choices' in response and len(response['choices']) > 0:
                return response['choices'][0]['message']['content']
            else:
                raise Exception("API响应格式不正确")
        except Exception as e:
            logger.error(f"文本生成失败: {str(e)}")
            raise
    
    def stream_text(self, prompt: str, **kwargs):
        """流式生成文本响应（生成器函数）"""
        try:
            url = f"{self.api_base_url}/chat/completions"
            headers = self._prepare_headers()
            payload = self._prepare_payload(prompt, **kwargs)
            payload['stream'] = True
            
            with requests.post(url, headers=headers, json=payload, stream=True, timeout=120) as response:
                if response.status_code == 200:
                    for chunk in response.iter_lines():
                        if chunk:
                            # 处理SSE格式的响应
                            chunk_str = chunk.decode('utf-8').strip()
                            if chunk_str.startswith('data: '):
                                data = chunk_str[len('data: '):]
                                if data == '[DONE]':
                                    break
                                try:
                                    import json
                                    chunk_data = json.loads(data)
                                    if ('choices' in chunk_data and 
                                        len(chunk_data['choices']) > 0 and 
                                        'delta' in chunk_data['choices'][0] and 
                                        'content' in chunk_data['choices'][0]['delta']):
                                        content = chunk_data['choices'][0]['delta']['content']
                                        # 实时yield生成的内容，实现一边生成一边输出
                                        yield content
                                except json.JSONDecodeError:
                                    continue
                else:
                    raise Exception(f"流式请求失败 (状态码: {response.status_code}): {response.text}")
        except Exception as e:
            logger.error(f"流式文本生成失败: {str(e)}")
            raise
    
    def check_api_connection(self) -> bool:
        """检查API连接是否正常"""
        try:
            # 使用简单的请求测试连接
            test_prompt = "你好"
            response = self.generate_text(test_prompt, max_tokens=10)
            return response is not None
        except Exception:
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        try:
            url = f"{self.api_base_url}/models"
            headers = self._prepare_headers()
            
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"获取模型信息失败 (状态码: {response.status_code}): {response.text}")
                return {}
        except Exception as e:
            logger.error(f"获取模型信息异常: {str(e)}")
            return {}