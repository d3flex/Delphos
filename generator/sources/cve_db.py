from .base import DocumentSource


class CVEDatabaseSource(DocumentSource):
    def fetch(self, query: str) -> str:
        # TODO: Implement CVE database fetching (NVD, Mitre, etc.)
        return ""

    def is_available(self) -> bool:
        # TODO: Check if CVE database API is accessible
        return False
