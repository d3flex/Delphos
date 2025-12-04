from .base import DocumentSource


class VectorStoreSource(DocumentSource):
    def fetch(self, query: str) -> str:
        # TODO: Implement vector DB queries (ChromaDB/Pinecone)
        return ""

    def is_available(self) -> bool:
        # TODO: Check if vector store is accessible
        return False
