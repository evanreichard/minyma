from typing import Any
import openai

from minyma.vdb import VectorDB

# Stolen LangChain Prompt
PROMPT_TEMPLATE = """
Use the following pieces of context to answer the question at the end.
If you don't know the answer, just say that you don't know, don't try to
make up an answer.

{context}

Question: {question}
Helpful Answer:
"""

class OpenAIConnector:
    def __init__(self, api_key: str, vdb: VectorDB):
        self.vdb = vdb
        self.model = "gpt-3.5-turbo"
        self.word_cap = 1000
        openai.api_key = api_key

    def query(self, question: str) -> Any:
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
