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
    def load_documents(self, name: str, normalizer: DataNormalizer, chunk_size: int = 10):
        raise NotImplementedError("VectorDB must implement load_documents")

    def get_related(self, name: str, question: str) -> Any:
        raise NotImplementedError("VectorDB must implement get_related")

"""
ChromaDV VectorDB Type
"""
class ChromaDB(VectorDB):
    def __init__(self, path: str):
        self.client: API = chromadb.PersistentClient(path=path)
        self.word_cap = 2500

    def get_related(self, name: str, question: str) -> Any:
        # Get or Create Collection
        collection = chromadb.Collection = self.client.create_collection(name=name, get_or_create=True)

        """Returns line separated related docs"""
        results = collection.query(
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

    def load_documents(self, name: str, normalizer: DataNormalizer, chunk_size: int = 10):
        # Get or Create Collection
        collection = chromadb.Collection = self.client.create_collection(name=name, get_or_create=True)

        # Load Items
        length = len(normalizer) / chunk_size
        for items in tqdm(chunk(normalizer, chunk_size), total=length):
            ids = []
            documents = []
            metadatas = []

            for item in items:
                documents.append(" ".join(item.get("doc").split()[:self.word_cap]))
                ids.append(item.get("id"))
                metadatas.append(item.get("metadata", {}))

            collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
            )
