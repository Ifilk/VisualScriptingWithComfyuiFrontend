import logging
from http import HTTPStatus
from typing import Any

import dashscope
from dashscope.api_entities.dashscope_response import Message


class ApiCallException(Exception):
    status_code: int
    message: str
    raw_response: Any

    def __init__(self, message: str, status_code: int, raw_response: Any):
        self.status_code = status_code
        self.message = message
        self.raw_response = raw_response

    def __str__(self):
        return f'[code={self.status_code}, message={self.message}]'


class AlibabaLLM:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "prompt": ("STRING", {"multiline": True, "dynamicPrompts": True}),
            "model": (('bailian-v1', 'dolly-12b-v2', 'qwen-turbo', 'qwen-plus', 'qwen-max'),)
        }
        }

    RETURN_TYPES = ('STRING',)
    RETURN_NAMES = ("response",)
    FUNCTION = "call"
    CATEGORY = "llm"

    def call(self, prompt: str, model: str):
        try:
            return (self.make_api_call(prompt, model), )
        except Exception as e:
            logging.error(f"Error in LLM _call: {e}", exc_info=True)
            raise e

    def make_api_call(self, prompt: str, model: str) -> str:
        messages = [Message(role='user', content=prompt)]
        response = dashscope.Generation.call(
            model=model,
            messages=messages,
            result_format='message'
        )
        if response.status_code == HTTPStatus.OK:
            return response.output.choices[0].message.content
        else:
            raise ApiCallException(status_code=response.status_code,
                                   message=response.message,
                                   raw_response=response)


class AlibabaLLMAdvanced:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "prompt": ("STRING", {"multiline": True, "dynamicPrompts": True}),
            "instructions": ("STRING", {"multiline": True, "dynamicPrompts": True}),
            "model": (('bailian-v1', 'dolly-12b-v2', 'qwen-turbo', 'qwen-plus', 'qwen-max'),)
        }
        }

    RETURN_TYPES = ('STRING', 'INT')
    RETURN_NAMES = ("response", 'total token usage')
    FUNCTION = "call"
    CATEGORY = "llm"

    total_input_tokens = 0
    total_output_tokens = 0
    total_usage = 0

    def call(self, prompt: str, instructions: str, model: str):
        try:
            return self.make_api_call(prompt, instructions, model), self.total_usage
        except Exception as e:
            logging.error(f"Error in LLM _call: {e}", exc_info=True)
            raise e

    def make_api_call(self, prompt: str, instructions: str, model: str) -> str:
        messages = [Message(role='system', content=instructions),
                    Message(role='user', content=prompt)]

        response = dashscope.Generation.call(
            model=model,
            messages=messages,
            result_format='message'
        )
        if response.status_code == HTTPStatus.OK:
            self.total_input_tokens += response.usage.input_tokens
            self.total_output_tokens += response.usage.output_tokens
            self.total_usage += response.usage.total_tokens
            return response.output.choices[0].message.content
        else:
            raise ApiCallException(status_code=response.status_code,
                                   message=response.message,
                                   raw_response=response)


NODE_CLASS_MAPPINGS = {
    'AlibabaLLM': AlibabaLLM,
    'AlibabaLLMAdvanced': AlibabaLLMAdvanced
}
NODE_DISPLAY_NAME_MAPPINGS = {
    'AlibabaLLM': "Alibaba's LLM Api Call",
    'AlibabaLLMAdvanced': "Alibaba's LLM Api Call(Advanced)"
}
