from chromadb.api import API
from itertools import islice
from os import path
from tqdm.auto import tqdm
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
    def __init__(self, base_path: str):
        chroma_path = path.join(base_path, "chroma")
        self.client: API = chromadb.PersistentClient(path=chroma_path)
        self.word_limit = 1000
        self.collection_name: str = "vdb"
        self.collection: chromadb.Collection = self.client.create_collection(name=self.collection_name, get_or_create=True)

    def get_related(self, question) -> Any:
        """Returns line separated related docs"""
        results = self.collection.query(
            query_texts=[question],
            n_results=2
        )

        all_docs: list = cast(list, results.get("documents", [[]]))[0]
        all_distances: list = cast(list, results.get("distances", [[]]))[0]
        all_ids: list = cast(list, results.get("ids", [[]]))[0]

        return {
            "distances":all_distances, 
            "docs": all_docs,
            "ids": all_ids
        }

    def load_documents(self, normalizer: DataNormalizer):
        # 10 Item Chunking
        for items in tqdm(chunk(normalizer, 50)):
            ids = []
            documents = []

            # Limit words per document to accommodate context token limits
            for item in items:
                doc = " ".join(item.get("doc").split()[:self.word_limit])
                documents.append(doc)
                ids.append(item.get("id"))

            # Ideally we parse out metadata from each document
            # and pass to the metadata kwarg. However, each
            # document appears to have a slightly different format,
            # so it's difficult to parse out.
            self.collection.add(
                documents=documents,
                ids=ids
            )
