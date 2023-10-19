from chromadb.api import API
from itertools import islice
from tqdm import tqdm
from typing import Any, cast
import chromadb

from minyma.normalizer import DataNormalizer

"""
Given an iterable, chunk it by `chunk_size`
"""
def chunk(iterable, chunk_size: int):
    iterator = iter(iterable)
    while batch := list(islice(iterator, chunk_size)):
        yield batch

"""
VectorDB Interface
"""
class VectorDB:
    def load_documents(self, normalizer: DataNormalizer):
        pass

    def get_related(self, question: str) -> Any:
        pass

"""
ChromaDV VectorDB Type
"""
class ChromaDB(VectorDB):
    def __init__(self, path: str):
        self.client: API = chromadb.PersistentClient(path=path)
        self.word_cap = 2500
        self.collection_name: str = "vdb"
        self.collection: chromadb.Collection = self.client.create_collection(name=self.collection_name, get_or_create=True)

    def get_related(self, question: str) -> Any:
        """Returns line separated related docs"""
        results = self.collection.query(
            query_texts=[question.lower()],
            n_results=2
        )

        all_docs: list = cast(list, results.get("documents", [[]]))[0]
        all_metadata: list = cast(list, results.get("metadatas", [[]]))[0]
        all_distances: list = cast(list, results.get("distances", [[]]))[0]
        all_ids: list = cast(list, results.get("ids", [[]]))[0]

        return {
            "distances": all_distances,
            "metadatas": all_metadata,
            "docs": all_docs,
            "ids": all_ids
        }

    def load_documents(self, normalizer: DataNormalizer, chunk_size: int = 10):
        length = len(normalizer) / chunk_size
        for items in tqdm(chunk(normalizer, chunk_size), total=length):
            ids = []
            documents = []
            metadatas = []

            for item in items:
                documents.append(" ".join(item.get("doc").split()[:self.word_cap]))
                ids.append(item.get("id"))
                metadatas.append(item.get("metadata", {}))

            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
            )
