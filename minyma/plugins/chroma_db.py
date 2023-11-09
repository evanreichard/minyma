from textwrap import indent
from minyma.plugin import MinymaPlugin
from minyma.vdb import ChromaDB


class ChromaDBPlugin(MinymaPlugin):
    """Perform Local VectorDB Lookup

    ChromDB can access multiple "collections". You can add additional functions
    here that just access a different collection (i.e. different data)
    """

    def __init__(self, config):
        self.name = "chroma_db"
        self.config = config
        self.word_cap = 1000

        if config.CHROMA_DATA_PATH is None:
            self.functions = []
        else:
            self.vdb = ChromaDB(config.CHROMA_DATA_PATH)
            self.functions = [self.lookup_pubmed_data]


    def __lookup_data(self, collection_name: str, query: str):
        # Get Related
        related = self.vdb.get_related(collection_name, query)

        # Get Metadata
        metadata = [{
                "id": related.get("ids")[i],
                "distance": related.get("distances")[i],
                "metadata": related.get("metadatas")[i],
        } for i, _ in enumerate(related.get("docs", []))]

        # Normalize Data
        return list(
            map(
                lambda x: " ".join(x.split()[:self.word_cap]),
                related.get("docs", [])
            )
        ), metadata


    def lookup_pubmed_data(self, query: str):
        COLLECTION_NAME = "pubmed"
        documents, metadata = self.__lookup_data(COLLECTION_NAME, query)
        context = '\n'.join(documents)
        return {
            "content": context,
            "metadata": metadata,
            "error": None
        }
