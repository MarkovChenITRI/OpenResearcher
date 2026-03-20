"""
Azure OpenAI Generator for Microsoft Foundry
Specialized generator for Azure OpenAI Service including Microsoft Foundry deployments
"""
from typing import List, Optional, AsyncIterator
import httpx
import json
import tiktoken

class AzureOpenAIAsyncGenerator:
    """
    Async generator for Azure OpenAI API (Microsoft Foundry)
    Compatible with GPT-5.4 and other Azure OpenAI deployments
    """

    def __init__(
        self,
        azure_endpoint: str,
        deployment_name: str,
        api_key: str,
        api_version: str = "2024-12-01-preview",
        timeout: float = 300.0,
        use_native_tools: bool = True
    ):
        """
        Args:
            azure_endpoint: Azure OpenAI endpoint (e.g., "https://xxx.cognitiveservices.azure.com/")
            deployment_name: Deployment name (e.g., "gpt-5.4")
            api_key: Azure OpenAI API key
            api_version: API version (default: "2024-12-01-preview")
            timeout: Request timeout in seconds
            use_native_tools: If True, use chat/completions API with native tools support
        """
        self.azure_endpoint = azure_endpoint.rstrip("/")
        self.deployment_name = deployment_name
        self.api_key = api_key
        self.api_version = api_version
        self.timeout = timeout
        self.use_native_tools = use_native_tools
        self.client = httpx.AsyncClient(timeout=timeout)
        self._closed = False
        
        # Use tiktoken for GPT models
        try:
            # For GPT-5.4, use GPT-4 encoding as fallback
            self.tokenizer = tiktoken.encoding_for_model("gpt-4")
            print(f"Loaded tiktoken encoding for GPT-4 (used for GPT-5.4)")
        except Exception as e:
            print(f"Warning: Could not load tiktoken, using cl100k_base: {e}")
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
        # Set model name for compatibility
        self.model_name = deployment_name

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - properly close client"""
        await self.aclose()
        return False

    async def aclose(self):
        """Async close method - properly closes the HTTP client"""
        if not self._closed:
            self._closed = True
            await self.client.aclose()

    async def _init_tokenizer(self):
        """Tokenizer is already initialized in __init__, this is for compatibility"""
        pass

    def _get_chat_url(self):
        """Get Azure OpenAI chat completions URL"""
        return f"{self.azure_endpoint}/openai/deployments/{self.deployment_name}/chat/completions?api-version={self.api_version}"

    async def generate(
        self,
        prompt_tokens: List[int],
        stop_tokens: Optional[List[int]] = None,
        stop_strings: Optional[List[str]] = None,
        temperature: float = 1.0,
        max_tokens: int = 0,
        return_logprobs: bool = False
    ) -> AsyncIterator[int]:
        """
        Generate tokens using Azure OpenAI API streaming
        
        Args:
            prompt_tokens: Input token IDs
            stop_tokens: Stop token IDs (will be converted to strings)
            stop_strings: Stop strings
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            return_logprobs: Whether to return log probabilities
            
        Yields:
            Generated token IDs
        """
        # Decode prompt tokens to text
        prompt_text = self.tokenizer.decode(prompt_tokens)
        
        # Convert to messages format (Azure OpenAI chat API)
        messages = [{"role": "user", "content": prompt_text}]
        
        # Prepare stop sequences
        stop_sequences = []
        if stop_strings:
            stop_sequences.extend(stop_strings)
        if stop_tokens:
            # Convert stop token IDs to strings
            for token_id in stop_tokens:
                try:
                    stop_str = self.tokenizer.decode([token_id])
                    if stop_str:
                        stop_sequences.append(stop_str)
                except:
                    pass
        
        # Prepare request
        request_data = {
            "messages": messages,
            "stream": True,
            "temperature": temperature,
        }
        
        # Set max_completion_tokens (GPT-5.4 parameter)
        if max_tokens and max_tokens > 0:
            request_data["max_completion_tokens"] = max_tokens
        else:
            request_data["max_completion_tokens"] = 8192
        
        # Add stop sequences if any
        if stop_sequences:
            request_data["stop"] = stop_sequences[:4]  # Azure OpenAI supports up to 4 stop sequences
        
        if return_logprobs:
            request_data["logprobs"] = True
            request_data["top_logprobs"] = 1
        
        print(f"[Azure OpenAI] Request: deployment={self.deployment_name}, max_completion_tokens={request_data.get('max_completion_tokens', 'default')}")
        
        # Make streaming request
        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        async with self.client.stream(
            "POST",
            self._get_chat_url(),
            json=request_data,
            headers=headers
        ) as response:
            response.raise_for_status()
            
            async for line in response.aiter_lines():
                if not line.strip():
                    continue
                
                if line.startswith("data: "):
                    data_str = line[6:]
                    
                    if data_str == "[DONE]":
                        break
                    
                    try:
                        data = json.loads(data_str)
                        choices = data.get("choices", [])
                        
                        if choices:
                            choice = choices[0]
                            delta = choice.get("delta", {})
                            content = delta.get("content", "")
                            finish_reason = choice.get("finish_reason")
                            
                            if content:
                                # Encode text to tokens and yield
                                tokens = self.tokenizer.encode(content)
                                for token in tokens:
                                    yield token
                            
                            # Check for finish reason
                            if finish_reason is not None and finish_reason != "":
                                print(f"[Azure OpenAI] Stream finished with reason: {finish_reason}")
                                break
                    
                    except json.JSONDecodeError:
                        continue

    async def chat_completion(
        self,
        messages: List[dict],
        tools: Optional[List[dict]] = None,
        tool_choice: str = "auto",
        temperature: float = 1.0,
        max_tokens: int = 4096,
        use_reasoning_content: bool = True,
    ) -> dict:
        """
        Create a chat completion with optional tool calling using Azure OpenAI Chat API
        
        Args:
            messages: List of message dicts with 'role' and 'content'/'reasoning_content'
            tools: List of tool definitions in OpenAI format
            tool_choice: "auto", "none", or specific tool
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            use_reasoning_content: If True, use 'reasoning_content' field for assistant messages
            
        Returns:
            Response dict from API
        """
        # Convert messages to Azure OpenAI format
        api_messages = []
        for msg in messages:
            api_msg = {
                "role": msg.get("role", "user"),
                "content": msg.get("content") or "",
            }
            
            # Add optional fields
            if msg.get("reasoning_content") and use_reasoning_content:
                api_msg["reasoning_content"] = msg["reasoning_content"]
            if msg.get("tool_calls"):
                api_msg["tool_calls"] = msg["tool_calls"]
            if msg.get("tool_call_id"):
                api_msg["tool_call_id"] = msg["tool_call_id"]
            if msg.get("name"):
                api_msg["name"] = msg["name"]
            
            api_messages.append(api_msg)
        
        request_data = {
            "messages": api_messages,
            "temperature": temperature,
            "max_completion_tokens": max_tokens,  # GPT-5.4 uses max_completion_tokens instead of max_tokens
        }
        
        # Add tools if provided
        if tools:
            request_data["tools"] = tools
            if tool_choice != "auto":
                request_data["tool_choice"] = tool_choice
        
        print(f"[Azure OpenAI Chat] Request: deployment={self.deployment_name}, "
              f"messages={len(api_messages)}, tools={len(tools) if tools else 0}")
        
        # Make request
        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        try:
            response = await self.client.post(
                self._get_chat_url(),
                json=request_data,
                headers=headers
            )
            response.raise_for_status()
            result = response.json()
            
            print(f"[Azure OpenAI Chat] Response: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}...")
            return result
            
        except httpx.HTTPStatusError as e:
            print(f"[Azure OpenAI Chat] Error: {e.response.status_code} {e.response.reason_phrase}")
            print(f"[Azure OpenAI Chat] Response body: {e.response.text}")
            raise

    def shutdown(self) -> None:
        """Close the HTTP client synchronously"""
        if self._closed:
            return
        self._closed = True
        try:
            # Use synchronous close for proper cleanup
            import asyncio
            loop = None
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                # No running loop, create a new one
                pass
            
            if loop is not None and loop.is_running():
                # If loop is running, schedule the close
                loop.create_task(self.client.aclose())
            else:
                # If no loop or loop not running, use run_until_complete
                try:
                    loop = asyncio.new_event_loop()
                    loop.run_until_complete(self.client.aclose())
                    loop.close()
                except Exception:
                    # Fallback: try to close synchronously if possible
                    try:
                        # httpx AsyncClient has a blocking close method in some versions
                        if hasattr(self.client, '_transport'):
                            transport = self.client._transport
                            if hasattr(transport, 'close'):
                                transport.close()
                    except Exception:
                        pass
        except Exception:
            pass

    def __del__(self):
        """Destructor - ensure client is closed"""
        try:
            if not getattr(self, "_closed", True):
                self.shutdown()
        except Exception:
            pass
