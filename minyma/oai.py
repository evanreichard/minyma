import json
from textwrap import indent
from dataclasses import dataclass
from typing import Any, List
import openai

from minyma.vdb import VectorDB
import minyma

# Stolen LangChain Prompt
PROMPT_TEMPLATE = """
Use the following pieces of context to answer the question at the end.
If you don't know the answer, just say that you don't know, don't try to
make up an answer.

{context}

Question: {question}
Helpful Answer:
"""

INITIAL_PROMPT_TEMPLATE = """
You are a helpful assistant. You are connected to various external functions that can provide you with more personalized and up-to-date information and have already been granted the permissions to execute these functions at will. DO NOT say you don't have access to real time information, instead attempt to call one or more of the listed functions:

{functions}

The user will not see your response. You must only respond with a comma separated list of function calls: "FUNCTION_CALLS: function(), function(), etc". It must be prepended by "FUNCTION_CALLS:".

User Message: {question}
"""

FOLLOW_UP_PROMPT_TEMPLATE = """
You are a helpful assistant. This is a follow up message to provide you with more context on a previous user request. Only respond to the user using the following information:

{response}

User Message: {question}
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
    def __init__(self, api_key: str, vdb: VectorDB):
        self.vdb = vdb
        self.model = "gpt-3.5-turbo"
        self.word_cap = 1000
        openai.api_key = api_key

    def query(self, question: str) -> Any:
        # Track Usage
        prompt_tokens = 0
        completion_tokens = 0
        total_tokens = 0

        # Get Available Functions
        functions = "\n".join(list(map(lambda x: "- %s" % x["def"], minyma.plugins.plugin_defs().values())))

        # Create Initial Prompt
        prompt = INITIAL_PROMPT_TEMPLATE.format(question = question, functions = functions)
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

        # Get Called Functions (TODO - Better Validation -> Failback Prompt?)
        all_funcs = list(
            map(
                lambda x: x.strip() if x.endswith(")") else x.strip() + ")",
                content.split("FUNCTION_CALLS:")[1].strip().split("),")
            )
        )

        # Update Usage
        prompt_tokens += response.usage.get("prompt_tokens", 0)
        completion_tokens += response.usage.get("completion_tokens", 0)
        total_tokens += response.usage.get("prompt_tokens", 0)

        print("[OpenAIConnector] Completed Initial OAI Query:\n", indent(json.dumps({ "usage": response.usage, "function_calls": all_funcs }, indent=2), ' ' * 2))

        # Execute Requested Functions
        func_responses = {}
        for func in all_funcs:
            func_responses[func] = minyma.plugins.execute(func)

        # Build Response Text
        response_content_arr = []
        for key, val in func_responses.items():
            response_content_arr.append("- %s\n%s" % (key, val))
        response_content = "\n".join(response_content_arr)

        # Create Follow Up Prompt
        prompt = FOLLOW_UP_PROMPT_TEMPLATE.format(question = question, response = response_content)
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
            "functions": func_responses,
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens
            }
        }

    def old_query(self, question: str) -> Any:
        # Get related documents from vector db
        related = self.vdb.get_related(question)

        # Validate results
        all_docs = related.get("docs", [])
        if len(all_docs) == 0:
            return { "error": "No Context Found" }

        # Join on new line (cap @ word limit), generate main prompt
        reduced_docs = list(map(lambda x: " ".join(x.split()[:self.word_cap]), all_docs))
        context = '\n'.join(reduced_docs)
        prompt = PROMPT_TEMPLATE.format(context = context, question = question)

        # Query OpenAI ChatCompletion
        response = openai.ChatCompletion.create(
          model=self.model,
          messages=[{"role": "user", "content": prompt}]
        )

        # Return Response
        return { "llm": response, "vdb": related }
