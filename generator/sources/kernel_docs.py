from .base import DocumentSource


class KernelDocsSource(DocumentSource):

    def fetch(self, query: str) -> str:
        # TODO: Implement kernel.org documentation fetching
        return ""

    def is_available(self) -> bool:
        # TODO: Check if kernel docs are accessible
        return False
