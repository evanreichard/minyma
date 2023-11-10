from dataclasses import dataclass
from textwrap import indent
from typing import Any, List
import json
import minyma
import openai

INITIAL_PROMPT_TEMPLATE = """
You are connected to various functions that can be used to answer the users questions. Your options are only "functions". Functions should be an array of strings containing the desired function calls (e.g. "function_name()").

Available Functions:

{functions}

You must respond in JSON only with no other fluff or bad things will happen. The JSON keys must ONLY be "functions". Be sure to call the functions with the right arguments.

User Message: {message}
"""

FOLLOW_UP_PROMPT_TEMPLATE = """
You are a helpful assistant. This is a follow up message to provide you with more context on a previous user request. Only respond to the user using the following information:

{response}

User Message: {message}
"""

@dataclass
class ChatCompletion:
    id: str
    object: str
    created: int
    model: str
    choices: List[dict]
    usage: dict


class OpenAIConnector:
    def __init__(self, api_key: str):
        self.model = "gpt-3.5-turbo"
        self.word_cap = 1000
        openai.api_key = api_key


    def query(self, message: str) -> Any:
        # Track Usage
        prompt_tokens = 0
        completion_tokens = 0
        total_tokens = 0

        # Get Available Functions
        functions = "\n".join(list(map(lambda x: "- %s" % x["def"], minyma.plugins.plugin_defs().values())))

        # Create Initial Prompt
        prompt = INITIAL_PROMPT_TEMPLATE.format(message = message, functions = indent(functions, ' ' * 2))
        messages = [{"role": "user", "content": prompt}]

        print("[OpenAIConnector] Running Initial OAI Query")

        # Run Initial
        response: ChatCompletion = openai.ChatCompletion.create( # type: ignore
          model=self.model,
          messages=messages
        )

        if len(response.choices) == 0:
            print("[OpenAIConnector] No Results -> TODO", response)

        content = response.choices[0]["message"]["content"]
        all_funcs = json.loads(content).get("functions")

        # Update Usage
        prompt_tokens += response.usage.get("prompt_tokens", 0)
        completion_tokens += response.usage.get("completion_tokens", 0)
        total_tokens += response.usage.get("prompt_tokens", 0)

        print("[OpenAIConnector] Completed Initial OAI Query:\n", indent(json.dumps({ "usage": response.usage, "function_calls": all_funcs }, indent=2), ' ' * 2))

        # Build Response Text & Metadata
        func_metadata = {}
        func_response = []

        for func in all_funcs:
            # Execute Requested Function
            resp = minyma.plugins.execute(func)

            # Unknown Response
            if resp is None:
                print("[OpenAIConnector] Invalid Function Response: %s" % func)
                continue

            # Get Response
            content = resp.get("content")
            metadata = resp.get("metadata")
            error = resp.get("error")

            # Append Responses & Metadata
            indented_val = indent(content or error or "Unknown Error", ' ' * 2)
            func_response.append("- %s\n%s" % (func, indented_val))
            func_metadata[func] = { "metadata": metadata, "error": error }

        func_response = "\n".join(func_response)

        # Create Follow Up Prompt
        prompt = FOLLOW_UP_PROMPT_TEMPLATE.format(message = message, response = func_response)
        messages = [{"role": "user", "content": prompt}]

        print("[OpenAIConnector] Running Follup Up OAI Query")

        # Run Follow Up
        response: ChatCompletion = openai.ChatCompletion.create( # type: ignore
          model=self.model,
          messages=messages
        )

        # Update Usage
        prompt_tokens += response.usage.get("prompt_tokens", 0)
        completion_tokens += response.usage.get("completion_tokens", 0)
        total_tokens += response.usage.get("prompt_tokens", 0)

        print("[OpenAIConnector] Completed Follup Up OAI Query:\n", indent(json.dumps({ "usage": response.usage }, indent=2), ' ' * 2))

        # Get Content
        content = response.choices[0]["message"]["content"]

        # Return Response
        return {
            "response": content,
            "functions": func_metadata,
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens
            }
        }
